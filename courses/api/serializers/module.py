from rest_framework import serializers
from courses.models import Module
from courses.api.serializers.lesson import LessonSerializer


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = '__all__'
