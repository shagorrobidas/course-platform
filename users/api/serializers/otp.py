from rest_framework import serializers


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=[
        'email_verification',
        'password_reset',
        'login'
    ])


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=[
        'email_verification',
        'password_reset',
        'login'
    ])
