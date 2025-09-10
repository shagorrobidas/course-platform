from rest_framework import generics, permissions
from rest_framework.response import Response
from courses.models import Progress, Enrollment, Lesson
from courses.api.serializers import ProgressSerializer
from core.tasks import generate_certificate
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status


class ProgressUpdateView(generics.UpdateAPIView):
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Progress.objects.filter(student=user)

    def patch(self, request, *args, **kwargs):
        # Handle partial updates with PATCH
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # Handle full updates with PUT
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.completed = request.data.get('completed', instance.completed)
        instance.save()

        # Check if course is completed
        enrollment = Enrollment.objects.get(
            student=request.user, 
            course=instance.lesson.module.course
        )

        if not enrollment.completed:
            total_lessons = Lesson.objects.filter(
                module__course=enrollment.course
            ).count()
            completed_lessons = Progress.objects.filter(
                student=request.user,
                lesson__module__course=enrollment.course,
                completed=True
            ).count()
            if completed_lessons == total_lessons:
                enrollment.completed = True
                enrollment.save()

                # Trigger certificate generation
                generate_certificate.delay(enrollment.id)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_progress_report(request, course_id):
    try:
        enrollment = Enrollment.objects.get(
            student=request.user,
            course_id=course_id
        )
    except Enrollment.DoesNotExist:
        return Response(
            {'error': 'Enrollment not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    total_lessons = Lesson.objects.filter(
        module__course_id=course_id
    ).count()
    completed_lessons = Progress.objects.filter(
        student=request.user, 
        lesson__module__course_id=course_id,
        completed=True
    ).count()

    progress_percentage = (
        completed_lessons / total_lessons * 100
    ) if total_lessons > 0 else 0

    return Response({
        'course': enrollment.course.title,
        'enrolled_at': enrollment.enrolled_at,
        'completed': enrollment.completed,
        'completed_at': enrollment.completed_at,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'progress_percentage': progress_percentage
    })
