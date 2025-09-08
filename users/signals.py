from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User, EmailVerification
from users.utils import create_otp
from users.tasks import send_verification_email_task
from django.utils import timezone
from datetime import timedelta
import uuid

@receiver(post_save, sender=User)
def create_email_verification(sender, instance, created, **kwargs):
    if created and not instance.is_email_verified:
        # Create email verification token
        token = uuid.uuid4()
        expires_at = timezone.now() + timedelta(hours=24)
        
        EmailVerification.objects.create(
            user=instance,
            token=token,
            expires_at=expires_at
        )
        
        # Send verification email
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
        send_verification_email_task.delay(instance.id, verification_url)
        
        # Also send OTP for email verification
        otp_obj = create_otp(instance, 'email_verification')
        from .tasks import send_otp_email_task
        send_otp_email_task.delay(instance.id, otp_obj.otp, 'email_verification')