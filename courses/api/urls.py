from django.urls import path
from .views.catagory import CategoryListView

urlpatterns = [
    path(
        'categories/',
        CategoryListView.as_view(),
        name='category-list'
    ),
]