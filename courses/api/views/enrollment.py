from rest_framework import generics, permissions
from courses.models import Enrollment, Course
from courses.api.serializers import EnrollmentSerializer
from rest_framework.response import Response
from rest_framework import status
from core.tasks import send_course_enrollment_email
from django.db import transaction


class EnrollmentCreateView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = self.kwargs['course_id']
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'error': 'You are already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            enrollment = serializer.save(
                student=request.user,
                course=course
            )
        
        # Trigger enrollment email task
        send_course_enrollment_email.delay(enrollment.id)
        
        return Response(
            {
                'detail': 'Enrollment successful. Welcome email sent.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )



class EnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        )

