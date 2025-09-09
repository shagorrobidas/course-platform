from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.conf import settings
from .models import User, EmailVerification
from .utils import send_verification_email, send_otp_email
from django.utils import timezone
from datetime import timedelta
import uuid
from users.utils import create_otp

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
        
        # verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
        # send_verification_email(instance, verification_url)
        
        # Also send OTP for email verification SYNCHRONOUSLY
        
        otp_obj = create_otp(instance, 'email_verification')
        send_otp_email(instance, otp_obj.otp, 'email_verification')