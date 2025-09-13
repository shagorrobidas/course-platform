from rest_framework import generics, permissions
from courses.models import Lesson
from courses.api.serializers import LessonSerializer
from courses.permissions import IsTeacherOrAdmin
from rest_framework.response import Response
from rest_framework import status


class LessonDetailView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.all()
    

class LessonCreateView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def perform_create(self, serializer):
        module_id = self.kwargs['module_id']
        serializer.save(module_id=module_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "success": True,
                "message": "Lesson created successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LessonUpdateView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return Lesson.objects.all()
    
    def update(self, request, *args, **kwargs):
        return Response(
            {
                "success": True,
                "message": "Lesson updated successfully.",
            },
            status=status.HTTP_200_OK
        )
    

class LessonDeleteView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return Lesson.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "success": True,
                "message": f"Lesson '{instance.title}' deleted successfully."
            },
            status=status.HTTP_200_OK
        )
