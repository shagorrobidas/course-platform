from rest_framework import generics, status, permissions
from rest_framework.response import Response
from users.models import User
from users.api.serializers import (
    OTPSerializer,
)
from users.utils import create_otp
from users.tasks import send_otp_email_task


class RequestOTPView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        purpose = serializer.validated_data['purpose']
        
        try:
            user = User.objects.get(email=email)
            
            # For email verification, check if already verified
            if purpose == 'email_verification' and user.is_email_verified:
                return Response(
                    {'error': 'Email is already verified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create and send OTP
            otp_obj = create_otp(user, purpose)
            send_otp_email_task.delay(user.id, otp_obj.otp, purpose)
            
            return Response({
                'message': f'OTP sent to {email} for {purpose.replace("_", " ")}'
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )