from django.urls import path
from .views.catagory import CategoryListView
from .views.courses import (
    CourseListView,
    CourseDetailView,
    course_analytics
)
from .views.enrollment import EnrollmentCreateView

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
]