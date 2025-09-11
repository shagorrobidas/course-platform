from rest_framework import generics, permissions
from courses.models import Category
from courses.api.serializers import CategorySerializer
from rest_framework.response import Response
from rest_framework import status
from courses.permissions import IsTeacherOrAdmin


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CatagoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsTeacherOrAdmin]

    def create(self, request, *args, **kwargs):
        name = request.data.get('name', '').strip()

        # Check if category already exists
        if Category.objects.filter(name__iexact=name).exists():
            return Response(
                {'error': 'Category with this name already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Let the parent class handle the actual creation
        response = super().create(request, *args, **kwargs)

        # Return custom response with the created data
        return Response(
            {
                'detail': 'Category created successfully.',
                'data': response.data
            },
            status=status.HTTP_201_CREATED
        )


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsTeacherOrAdmin]

    def update(self, request, *args, **kwargs):
        name = request.data.get('name', '').strip()
        instance = self.get_object()
        if Category.objects.filter(name__iexact=name).exclude(
            id=instance.id
        ).exists():
            return Response(
                {'error': 'Category with this name already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        responce = super().update(request, *args, **kwargs)

        return Response(
            {
                'detail': 'Category updated successfully.',
                'data': responce.data
            },
            status=status.HTTP_200_OK
        )


class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        category_name = instance.name

        # Check if category has associated courses
        if instance.course_set.exists():
            return Response(
                {'error': 'Cannot delete category with associated courses. Please reassign or delete the courses first.'}, # noqa
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(
            {'detail': f'Category {category_name} deleted successfully.'},
            status=status.HTTP_200_OK
        )
