from rest_framework import generics, permissions
from courses.models import Lesson
from courses.api.serializers import LessonSerializer


class LessonDetailView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.all()