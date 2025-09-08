from rest_framework import generics, status, permissions
from rest_framework.response import Response
from users.models import EmailVerification


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, token):
        try:
            verification = EmailVerification.objects.get(token=token)

            if verification.is_valid():
                user = verification.user
                user.is_email_verified = True
                user.is_active = True
                user.save()

                verification.delete()

                return Response({'message': 'Email verified successfully'})
            else:
                return Response(
                    {'error': 'Verification link has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except EmailVerification.DoesNotExist:
            return Response(
                {'error': 'Invalid verification link'},
                status=status.HTTP_404_NOT_FOUND
            )
