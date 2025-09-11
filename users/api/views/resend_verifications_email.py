from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from datetime import timedelta
import uuid
from users.models import EmailVerification
from django.conf import settings


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resend_verification_email(request):
    user = request.user

    if user.is_email_verified:
        return Response(
            {'error': 'Email is already verified'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Delete any existing verification tokens
    EmailVerification.objects.filter(user=user).delete()

    # Create new verification token
    token = uuid.uuid4()
    expires_at = timezone.now() + timedelta(hours=24)

    EmailVerification.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )

    # Send verification email
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
    from users.tasks import send_verification_email_task
    send_verification_email_task.delay(user.id, verification_url)
    
    return Response({'message': 'Verification email sent'})