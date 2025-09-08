from django.urls import path
from .views.catagory import CategoryListView
from .views.courses import (
    CourseListView,
    CourseDetailView
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
]