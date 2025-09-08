from rest_framework import generics, permissions
from courses.models import Module
from courses.api.serializers import ModuleSerializer


class ModuleListView(generics.ListAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Module.objects.filter(course_id=course_id)
