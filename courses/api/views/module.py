from rest_framework import generics, permissions
from courses.models import Module
from courses.api.serializers import ModuleSerializer
from courses.permissions import IsTeacherOrAdmin
from rest_framework.response import Response
from rest_framework import status


class ModuleListView(generics.ListAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Module.objects.filter(course_id=course_id)
    

class CourseModuleCreateView(generics.CreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsTeacherOrAdmin]

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        serializer.save(course_id=course_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "success": True,
                "message": "Module created successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class ModuleUpdateView(generics.UpdateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return Module.objects.all()
    
    def update(self, request, *args, **kwargs):
        return Response(
            {
                "success": True,
                "message": "Module updated successfully.",
            },
            status=status.HTTP_200_OK
        )


class ModuleDeleteView(generics.DestroyAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return Module.objects.all()

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "success": True,
                "message": "Module deleted successfully.",
            },
            status=status.HTTP_200_OK
        )
