from rest_framework import serializers
from courses.models import Course
from courses.api.serializers import ModuleSerializer


class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(
        source='instructor.get_full_name',
        read_only=True
    )
    modules = ModuleSerializer(
        many=True,
        read_only=True
    )
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()