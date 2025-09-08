from rest_framework import generics, permissions
from rest_framework.response import Response


from users.models import User
from users.api.serializers import (
    ResetPasswordSerializer
)
from users.utils import create_otp
from users.tasks import send_otp_email_task


class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            otp_obj = create_otp(user, 'password_reset')
            send_otp_email_task.delay(user.id, otp_obj.otp, 'password_reset')

            return Response({
                'message': 'Password reset OTP sent to your email'
            })

        except User.DoesNotExist:
            # Don't reveal that email doesn't exist for security
            return Response({
                'message': 'If the email exists, a password reset OTP has been sent'
            })
