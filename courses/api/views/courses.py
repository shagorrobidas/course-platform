from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from courses.models import (
    Enrollment,
    Module,
    Lesson,
    Progress,
    Course
)
from courses.api.serializers import CourseSerializer


class CourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)

        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name=category)

        # Filter by level
        level = self.request.query_params.get('level', None)
        if level:
            queryset = queryset.filter(level=level)

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(
                    title__icontains=search
                ) | Q(description__icontains=search)
            )

        return queryset


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def course_analytics(request, course_id):
    enrollments = Enrollment.objects.filter(course_id=course_id)
    total_enrollments = enrollments.count()
    completed_enrollments = enrollments.filter(completed=True).count()
    completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0

    progress_data = []
    modules = Module.objects.filter(course_id=course_id)

    for module in modules:
        module_lessons = Lesson.objects.filter(module=module)
        module_completion = 0
        for lesson in module_lessons:
            lesson_progress = Progress.objects.filter(lesson=lesson, completed=True).count()
            if lesson_progress > 0:
                module_completion += (lesson_progress / enrollments.count() * 100) / module_lessons.count()
        
        progress_data.append({
            'module': module.title,
            'completion_rate': module_completion
        })

    return Response({
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'completion_rate': completion_rate,
        'module_progress': progress_data
    })




