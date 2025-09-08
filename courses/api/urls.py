from django.urls import path
from .views.catagory import CategoryListView
from .views.courses import (
    CourseListView,
    CourseDetailView,
    course_analytics
)
from .views.enrollment import (
    EnrollmentCreateView,
    EnrollmentListView
)
from .views import ModuleListView
from .views.lesson import LessonDetailView
from .views.progress import (
    ProgressUpdateView,
    student_progress_report
)

urlpatterns = [
    path(
        'categories/',
        CategoryListView.as_view(),
        name='category-list'
    ),
    path(
        '',
        CourseListView.as_view(),
        name='course-list'
    ),
    path(
        '<int:pk>/',
        CourseDetailView.as_view(),
        name='course-detail'
    ),
    path(
        '<int:course_id>/analytics/',
        course_analytics,
        name='course-analytics'
    ),
    path(
        '<int:course_id>/enroll/',
        EnrollmentCreateView.as_view(),
        name='enroll'
    ),
    path(
        'enrollments/',
        EnrollmentListView.as_view(),
        name='enrollment-list'
    ),
    path(
        '<int:course_id>/modules/',
        ModuleListView.as_view(),
        name='module-list'
    ),
    path(
        'lessons/<int:pk>/',
        LessonDetailView.as_view(),
        name='lesson-detail'
    ),
    path(
        'progress/<int:pk>/',
        ProgressUpdateView.as_view(),
        name='progress-update'
    ),
    path(
        '<int:course_id>/progress-report/',
        student_progress_report,
        name='progress-report'
    ),

]