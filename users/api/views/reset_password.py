from rest_framework import generics, status, permissions
from rest_framework.response import Response
from users.models import User
from users.api.serializers import (
    ResetPasswordConfirmSerializer
)
from users.utils import verify_otp


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)

            if verify_otp(user, otp_code, 'password_reset'):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password reset successfully'})

            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
