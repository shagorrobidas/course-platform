from rest_framework import serializers
from courses.models import Progress, Enrollment
from django.utils import timezone


class ProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(
        source='lesson.title', read_only=True
    )
    module_title = serializers.CharField(
        source='lesson.module.title', read_only=True
    )
    course_title = serializers.CharField(
        source='lesson.module.course.title', read_only=True
    )
    course_id = serializers.IntegerField(
        source='lesson.module.course.id', read_only=True
    )
    module_id = serializers.IntegerField(
        source='lesson.module.id', read_only=True
    )
    student_name = serializers.CharField(
        source='student.get_full_name', read_only=True
    )

    class Meta:
        model = Progress
        fields = [
            'id', 'student', 'student_name', 'lesson', 'lesson_title',
            'module_id', 'module_title', 'course_id', 'course_title',
            'completed', 'completed_at', 'last_accessed', 'time_spent'
        ]
        read_only_fields = ['student', 'completed_at', 'last_accessed']


class ProgressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['lesson', 'completed', 'time_spent']

    def validate(self, data):
        user = self.context['request'].user
        lesson = data.get('lesson')

        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(
            student=user,
            course=lesson.module.course
        ).exists():
            raise serializers.ValidationError(
                "You are not enrolled in this course."
            )

        return data


class ProgressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['completed', 'time_spent']

    def update(self, instance, validated_data):
        completed = validated_data.get('completed', instance.completed)

        # Handle completion timestamp
        if completed and not instance.completed:
            instance.completed_at = timezone.now()
        elif not completed and instance.completed:
            instance.completed_at = None

        instance.completed = completed
        instance.time_spent = validated_data.get(
            'time_spent', instance.time_spent
        )
        instance.save()
        return instance
