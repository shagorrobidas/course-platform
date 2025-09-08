from rest_framework import serializers
from courses.models import Progress


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = '__all__'