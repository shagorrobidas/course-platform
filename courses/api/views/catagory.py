from rest_framework import generics, permissions
from courses.models import Category
from courses.api.serializers import CategorySerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
