from rest_framework import serializers


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=[
        'email_verification',
        'password_reset',
        'login'
    ])


