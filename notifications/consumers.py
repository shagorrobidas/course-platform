import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .models import Course, Question, Notification, ClassUpdate, Answer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f"user_{self.user.id}"

        # Join user-specific group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave user-specific group
        if not self.user.is_anonymous:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        message = text_data_json.get('message')

        if message_type == 'question':
            # Handle student questions
            course_id = text_data_json.get('course_id')
            if not course_id or not message:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Missing course_id or message'
                }))
                return

            # Save question to database
            question = await self.save_question(
                self.user.id,
                course_id,
                message
            )
            if not question:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid course or user'
                }))
                return

            # Join course group to receive updates
            await self.channel_layer.group_add(
                f"course_{course_id}",
                self.channel_name
            )

            print(
                f"Received student question from user {self.user.first_name} for course {course_id}: {message}" # noqa
            )
            # Broadcast question to course group
            await self.channel_layer.group_send(
                f"course_{course_id}",
                {
                    'type': 'question_message',
                    'message': message,
                    'user': self.user.first_name or self.user.email,
                    'question_id': question.id,
                    'is_teacher_question': False
                }
            )

            # Notify teacher of the course
            teacher_id = await self.get_course_teacher(course_id)
            if teacher_id:
                await self.channel_layer.group_send(
                    f"user_{teacher_id}",
                    {
                        'type': 'notification_message',
                        'message': f"New student question in {question.course.title}: {message}" # noqa
                    }
                )

        elif message_type == 'answer':
            # Handle answers (teachers for student questions, students for teacher questions) # noqa
            question_id = text_data_json.get('question_id')
            if not question_id or not message:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Missing question_id or message'
                }))
                return

            # Check if answering a student question (only teachers) or teacher question (only students)  # noqa
            is_teacher_question = await self.is_teacher_question(question_id)
            is_teacher = await self.is_teacher(self.user.id)

            if is_teacher_question and is_teacher:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Teachers cannot answer their own questions'
                }))
                return
            if not is_teacher_question and not is_teacher:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only teachers can answer student questions'
                }))
                return

            # Save answer to database
            answer, course_id = await self.save_answer(
                self.user.id, question_id, message
            )
            if not answer:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid question or user'
                }))
                return

            # Join course group if not already joined
            await self.channel_layer.group_add(
                f"course_{course_id}",
                self.channel_name
            )

            print(
                f"Received answer from user {self.user.id} for question {question_id}: {message}" # noqa
            )
            # Broadcast answer to course group
            await self.channel_layer.group_send(
                f"course_{course_id}",
                {
                    'type': 'answer_message',
                    'message': message,
                    'user': self.user.first_name or self.user.email,
                    'question_id': question_id,
                    'answer_id': answer.id
                }
            )

            # Notify the question asker
            if is_teacher_question:
                # Notify teacher who asked
                teacher_id = await self.get_question_teacher(question_id)
                if teacher_id:
                    await self.channel_layer.group_send(
                        f"user_{teacher_id}",
                        {
                            'type': 'notification_message',
                            'message': f"New answer to your question in {answer.question.course.title}: {message}" # noqa
                        }
                    )
            else:
                # Notify student who asked
                student_id = await self.get_question_student(question_id)
                if student_id:
                    await self.channel_layer.group_send(
                        f"user_{student_id}",
                        {
                            'type': 'notification_message',
                            'message': f"Your question in {answer.question.course.title} has been answered: {message}" # noqa
                        }
                    )

        elif message_type == 'notification':
            # Handle teacher sending notification to course
            course_id = text_data_json.get('course_id')
            if not course_id or not message:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Missing course_id or message'
                }))
                return

            if not await self.is_teacher(self.user.id):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only teachers can send course notifications'
                }))
                return

            # Verify teacher is the course instructor
            if not await self.is_course_instructor(self.user.id, course_id):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You are not the instructor for this course'
                }))
                return

            # Broadcast notification to course group (reaches all connected students) # noqa
            await self.channel_layer.group_send(
                f"course_{course_id}",
                {
                    'type': 'notification_message',
                    'message': f"Notification from {self.user.first_name} in {await self.get_course_title(course_id)}: {message}", # noqa
                    'notification_id': await self.save_notification(self.user.id, f"Sent notification to course {course_id}: {message}")  # noqa
                }
            )

        elif message_type == 'teacher_question':
            # Handle teacher sending question to course
            course_id = text_data_json.get('course_id')
            if not course_id or not message:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Missing course_id or message'
                }))
                return

            if not await self.is_teacher(self.user.id):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only teachers can send questions to students'
                }))
                return

            # Verify teacher is the course instructor
            if not await self.is_course_instructor(self.user.id, course_id):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You are not the instructor for this course'
                }))
                return

            # Save question to database
            question = await self.save_question(
                self.user.id, course_id, message
            )
            if not question:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid course or user'
                }))
                return

            # Join course group
            await self.channel_layer.group_add(
                f"course_{course_id}",
                self.channel_name
            )

            print(f"Received teacher question from user {self.user.id} for course {course_id}: {message}") # noqa
            # Broadcast question to course group
            await self.channel_layer.group_send(
                f"course_{course_id}",
                {
                    'type': 'question_message',
                    'message': message,
                    'user': self.user.first_name or self.user.email,
                    'question_id': question.id,
                    'is_teacher_question': True
                }
            )

            # Notify connected students in course group
            await self.channel_layer.group_send(
                f"course_{course_id}",
                {
                    'type': 'notification_message',
                    'message': f"New question from {self.user.first_name} in {question.course.title}: {message}", # noqa
                    'notification_id': await self.save_notification(self.user.id, f"Sent question to course {course_id}: {message}")  # noqa
                }
            )

    async def question_message(self, event):
        # Send question to WebSocket
        print(f"Sending question to user {self.user.id}: {event['message']}")
        await self.send(text_data=json.dumps({
            'type': 'question',
            'message': event['message'],
            'user': event['user'],
            'question_id': event['question_id'],
            'is_teacher_question': event.get('is_teacher_question', False)
        }))

    async def answer_message(self, event):
        # Send answer to WebSocket
        print(f"Sending answer to user {self.user.id}: {event['message']}")
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'message': event['message'],
            'user': event['user'],
            'question_id': event['question_id'],
            'answer_id': event['answer_id']
        }))

    async def notification_message(self, event):
        # Save notification to database for recipient
        notification = await self.save_notification(
            self.user.id, event['message']
        )
        if notification:
            print(
                f"Sending notification to user {self.user.first_name}: {event['message']}" # noqa
            )
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'message': event['message'],
                'notification_id': notification.id
            }))

    async def class_update_message(self, event):
        # Save class update to database
        class_update = await self.save_class_update(
            event['course_id'], event['message']
        )
        if class_update:
            print(
                f"Sending class update to user {self.user.id}: {event['message']}" # noqa
            )
            await self.send(text_data=json.dumps({
                'type': 'class_update',
                'message': event['message'],
                'course_id': event['course_id'],
                'update_id': class_update.id
            }))

    @database_sync_to_async
    def save_question(self, user_id, course_id, message):
        try:
            user = get_user_model().objects.get(id=user_id)
            course = Course.objects.get(id=course_id)
            return Question.objects.create(
                user=user, course=course, message=message
            )
        except (get_user_model().DoesNotExist, Course.DoesNotExist):
            return None

    @database_sync_to_async
    def save_answer(self, user_id, question_id, message):
        try:
            user = get_user_model().objects.get(id=user_id)
            question = Question.objects.select_related(
                'course'
            ).get(id=question_id)
            answer = Answer.objects.create(
                user=user, question=question, message=message
            )
            return answer, question.course.id
        except (get_user_model().DoesNotExist, Question.DoesNotExist):
            return None, None

    @database_sync_to_async
    def save_notification(self, user_id, message):
        try:
            user = get_user_model().objects.get(id=user_id)
            return Notification.objects.create(user=user, message=message)
        except get_user_model().DoesNotExist:
            return None

    @database_sync_to_async
    def save_class_update(self, course_id, message):
        try:
            course = Course.objects.get(id=course_id)
            return ClassUpdate.objects.create(course=course, message=message)
        except Course.DoesNotExist:
            return None

    @database_sync_to_async
    def is_teacher(self, user_id):
        try:
            user = get_user_model().objects.get(id=user_id)
            return user.role == 'teacher'
        except get_user_model().DoesNotExist:
            return False

    @database_sync_to_async
    def is_course_instructor(self, user_id, course_id):
        try:
            course = Course.objects.get(id=course_id)
            return course.instructor.id == user_id
        except Course.DoesNotExist:
            return False

    @database_sync_to_async
    def get_course_teacher(self, course_id):
        try:
            course = Course.objects.get(id=course_id)
            return course.instructor.id if course.instructor.role == 'teacher' else None # noqa
        except Course.DoesNotExist:
            return None

    @database_sync_to_async
    def get_question_student(self, question_id):
        try:
            question = Question.objects.get(id=question_id)
            return question.user.id if question.user.role == 'student' else None # noqa
        except Question.DoesNotExist:
            return None

    @database_sync_to_async
    def get_question_teacher(self, question_id):
        try:
            question = Question.objects.get(id=question_id)
            return question.user.id if question.user.role == 'teacher' else None # noqa
        except Question.DoesNotExist:
            return None

    @database_sync_to_async
    def is_teacher_question(self, question_id):
        try:
            question = Question.objects.get(id=question_id)
            return question.user.role == 'teacher'
        except Question.DoesNotExist:
            return False

    @database_sync_to_async
    def get_course_title(self, course_id):
        try:
            course = Course.objects.get(id=course_id)
            return course.title
        except Course.DoesNotExist:
            return "Unknown Course"


@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()
