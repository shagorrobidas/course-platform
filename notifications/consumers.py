import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.room_group_name = f"user_{self.user.id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
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
            # Handle live Q&A questions
            course_id = text_data_json.get('course_id')
            print(f"Received question from user {self.user.id} for course {course_id}: {message}")
            await self.channel_layer.group_send(
                f"course_{course_id}",
                {
                    'type': 'question_message',
                    'message': message,
                    'user': self.user.first_name or self.user.email
                }
            )
    
    async def question_message(self, event):
        # check if it's working
        print(f"Sending question to user {self.user.id}: {event['message']}")
        # Send question to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'question',
            'message': event['message'],
            'user': event['user']
        }))
    
    async def notification_message(self, event):
        # check if it's working
        print(f"Sending notification to user {self.user.id}: {event['message']}")
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))
    
    async def class_update_message(self, event):  # Fixed: added async keyword
        # check if it's working
        print(f"Sending class update to user {self.user.id}: {event['message']}")
        # Send class update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'class_update',
            'message': event['message'],
            'course_id': event['course_id']
        }))


@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()