from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'role', 'bio', 'profile_picture', 'date_of_birth',
            'is_email_verified', 'created_at'
        )
        read_only_fields = ('id', 'is_email_verified', 'created_at')