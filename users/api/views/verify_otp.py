from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from users.api.serializers import (
    UserSerializer,
    OTPVerificationSerializer, 
)
from users.utils import verify_otp


class VerifyOTPView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPVerificationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        purpose = serializer.validated_data['purpose']
        
        try:
            user = User.objects.get(email=email)
            
            if verify_otp(user, otp_code, purpose):
                # Handle different purposes
                if purpose == 'email_verification':
                    user.is_email_verified = True
                    user.is_active = True
                    user.save()
                    return Response({'message': 'Email verified successfully'})
                
                elif purpose == 'password_reset':
                    # Return a token or flag that allows password reset
                    return Response({
                        'message': 'OTP verified. You can now reset your password.',
                        'can_reset_password': True
                    })
                
                elif purpose == 'login':
                    # Generate JWT tokens for OTP login
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'message': 'Login successful',
                        'user': UserSerializer(user).data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
            
            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
