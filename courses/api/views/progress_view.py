from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from courses.models import Progress, Lesson, Course, Module, Enrollment
from courses.api.serializers import (
    ProgressSerializer,
    ProgressCreateSerializer,
    ProgressUpdateSerializer
)
from core.tasks import generate_certificate


class ProgressListView(generics.ListAPIView):
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Progress.objects.filter(
            student=self.request.user
        ).select_related(
            'lesson__module__course',
            'student'
        ).prefetch_related('lesson__module')
        
        # Manual filtering instead of django-filter
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(lesson__module__course_id=course_id)
        
        module_id = self.request.query_params.get('module_id')
        if module_id:
            queryset = queryset.filter(lesson__module_id=module_id)
        
        completed = self.request.query_params.get('completed')
        if completed is not None:
            if completed.lower() == 'true':
                queryset = queryset.filter(completed=True)
            elif completed.lower() == 'false':
                queryset = queryset.filter(completed=False)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(lesson__title__icontains=search) |
                Q(lesson__module__title__icontains=search) |
                Q(lesson__module__course__title__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-last_accessed')
        if ordering:
            if ordering.startswith('-'):
                field = ordering[1:]
                if field in ['last_accessed', 'completed_at', 'time_spent']:
                    queryset = queryset.order_by(ordering)
            else:
                if ordering in ['last_accessed', 'completed_at', 'time_spent']:
                    queryset = queryset.order_by(ordering)
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        # Add summary information
        course_id = request.query_params.get('course_id')
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                total_lessons = Lesson.objects.filter(module__course=course).count()
                completed_lessons = Progress.objects.filter(
                    student=request.user,
                    lesson__module__course=course,
                    completed=True
                ).count()
                
                response.data['summary'] = {
                    'course_title': course.title,
                    'total_lessons': total_lessons,
                    'completed_lessons': completed_lessons,
                    'progress_percentage': round((completed_lessons / total_lessons * 100), 2) if total_lessons > 0 else 0
                }
            except Course.DoesNotExist:
                pass
        
        return response

class ProgressCreateView(generics.CreateAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        lesson_id = self.request.data.get('lesson')
        
        # Check if progress already exists
        existing_progress = Progress.objects.filter(
            student=self.request.user,
            lesson_id=lesson_id
        ).first()
        
        if existing_progress:
            # Update existing progress
            existing_progress.completed = self.request.data.get(
                'completed', 
                existing_progress.completed
            )
            existing_progress.time_spent = self.request.data.get(
                'time_spent', 
                existing_progress.time_spent
            )
            
            # Handle completion timestamp
            if existing_progress.completed and not existing_progress.completed_at:
                existing_progress.completed_at = timezone.now()
            elif not existing_progress.completed and existing_progress.completed_at:
                existing_progress.completed_at = None
                
            existing_progress.save()
            
            # Check course completion
            self.check_course_completion(existing_progress)
            
            return existing_progress
        
        # Create new progress
        progress = serializer.save(student=self.request.user)
        
        # Set completion timestamp if completed
        if progress.completed and not progress.completed_at:
            progress.completed_at = timezone.now()
            progress.save()
        
        # Check course completion
        self.check_course_completion(progress)
        
        return progress

    def check_course_completion(self, progress):
        """Check if course is completed and update enrollment"""
        course = progress.lesson.module.course
        
        try:
            enrollment = Enrollment.objects.get(
                student=progress.student,
                course=course
            )
            
            if not enrollment.completed:
                total_lessons = Lesson.objects.filter(module__course=course).count()
                completed_lessons = Progress.objects.filter(
                    student=progress.student,
                    lesson__module__course=course,
                    completed=True
                ).count()
                
                if completed_lessons == total_lessons and total_lessons > 0:
                    enrollment.completed = True
                    enrollment.completed_at = timezone.now()
                    enrollment.save()
                    
                    # Trigger certificate generation
                    generate_certificate.delay(enrollment.id)
                    
        except Enrollment.DoesNotExist:
            pass


class ProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Progress.objects.filter(student=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Get completion status before update
        was_completed = instance.completed
        
        # Update instance
        progress = serializer.save()
        
        # Handle completion timestamp if status changed
        if progress.completed and not was_completed:
            progress.completed_at = timezone.now()
            progress.save()
        elif not progress.completed and was_completed:
            progress.completed_at = None
            progress.save()
        
        # Check course completion
        self.check_course_completion(progress)
        
        return Response(ProgressSerializer(progress).data)

    def check_course_completion(self, progress):
        """Check if course is completed and update enrollment"""
        course = progress.lesson.module.course
        
        try:
            enrollment = Enrollment.objects.get(
                student=progress.student,
                course=course
            )
            
            if not enrollment.completed:
                total_lessons = Lesson.objects.filter(module__course=course).count()
                completed_lessons = Progress.objects.filter(
                    student=progress.student,
                    lesson__module__course=course,
                    completed=True
                ).count()
                
                if completed_lessons == total_lessons and total_lessons > 0:
                    enrollment.completed = True
                    enrollment.completed_at = timezone.now()
                    enrollment.save()

                    generate_certificate.delay(enrollment.id)
                    
        except Enrollment.DoesNotExist:
            pass

class ProgressBulkUpdateView(generics.CreateAPIView):
    serializer_class = ProgressCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        progress_data = request.data.get('progress', [])
        
        created_updates = []
        errors = []
        
        with transaction.atomic():
            for item in progress_data:
                lesson_id = item.get('lesson')
                completed = item.get('completed', False)
                time_spent = item.get('time_spent', 0)
                
                try:
                    # Validate lesson exists and user has access
                    lesson = Lesson.objects.get(id=lesson_id)
                    
                    if not Enrollment.objects.filter(
                        student=request.user,
                        course=lesson.module.course
                    ).exists():
                        errors.append({
                            'lesson_id': lesson_id,
                            'error': 'Not enrolled in course'
                        })
                        continue
                    
                    # Check if progress exists
                    progress, created = Progress.objects.get_or_create(
                        student=request.user,
                        lesson=lesson,
                        defaults={
                            'completed': completed,
                            'time_spent': time_spent
                        }
                    )
                    
                    if not created:
                        # Update existing progress
                        progress.completed = completed
                        progress.time_spent = time_spent
                        
                        # Handle completion timestamp
                        if progress.completed and not progress.completed_at:
                            progress.completed_at = timezone.now()
                        elif not progress.completed and progress.completed_at:
                            progress.completed_at = None
                            
                        progress.save()
                    
                    created_updates.append(progress)
                    
                    # Check course completion
                    self.check_course_completion(progress)
                    
                except Lesson.DoesNotExist:
                    errors.append({
                        'lesson_id': lesson_id,
                        'error': 'Lesson not found'
                    })
                except Exception as e:
                    errors.append({
                        'lesson_id': lesson_id,
                        'error': str(e)
                    })
        
        serializer = ProgressSerializer(created_updates, many=True)
        
        return Response({
            'success_count': len(created_updates),
            'error_count': len(errors),
            'progress': serializer.data,
            'errors': errors
        }, status=status.HTTP_200_OK)

    def check_course_completion(self, progress):
        """Check if course is completed after update"""
        course = progress.lesson.module.course
        
        try:
            enrollment = Enrollment.objects.get(
                student=progress.student,
                course=course
            )
            
            if not enrollment.completed:
                total_lessons = Lesson.objects.filter(module__course=course).count()
                completed_lessons = Progress.objects.filter(
                    student=progress.student,
                    lesson__module__course=course,
                    completed=True
                ).count()
                
                if completed_lessons == total_lessons and total_lessons > 0:
                    enrollment.completed = True
                    enrollment.completed_at = timezone.now()
                    enrollment.save()
                    
                    generate_certificate.delay(enrollment.id)
                    
        except Enrollment.DoesNotExist:
            pass

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def progress_stats(request):
    """Get progress statistics for the authenticated user"""
    from django.db.models import Sum
    
    user = request.user
    
    # Total progress records
    total_progress = Progress.objects.filter(student=user).count()
    
    # Completed progress
    completed_progress = Progress.objects.filter(
        student=user, 
        completed=True
    ).count()
    
    # Total time spent
    total_time_spent = Progress.objects.filter(
        student=user
    ).aggregate(total_time=Sum('time_spent'))['total_time'] or 0
    
    # Courses with progress
    courses_with_progress = Course.objects.filter(
        enrollments__student=user,
        modules__lessons__progress__student=user
    ).distinct().count()
    
    return Response({
        'total_progress_records': total_progress,
        'completed_lessons': completed_progress,
        'total_time_spent_seconds': total_time_spent,
        'total_time_spent_hours': round(total_time_spent / 3600, 2),
        'courses_with_progress': courses_with_progress,
        'completion_percentage': round((completed_progress / total_progress * 100), 2) if total_progress > 0 else 0
    })