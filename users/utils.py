import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import OTP


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user, otp, purpose):
    subject = f"Your OTP for {purpose.replace('_', ' ').title()}"
    
    context = {
        'user': user,
        'otp': otp,
        'purpose': purpose,
    }
    
    message = render_to_string('emails/otp_email.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.content_subtype = 'html'
    email.send()


def send_verification_email(user, verification_url):
    subject = "Verify Your Email Address"
    
    context = {
        'user': user,
        'verification_url': verification_url,
    }
    
    message = render_to_string('emails/verification_email.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.content_subtype = 'html'
    email.send()


def create_otp(user, purpose, expiry_minutes=10):
    # Delete any existing OTPs for this user and purpose
    OTP.objects.filter(user=user, purpose=purpose).delete()
    
    # Create new OTP
    otp = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
    
    otp_obj = OTP.objects.create(
        user=user,
        otp=otp,
        purpose=purpose,
        expires_at=expires_at
    )
    
    return otp_obj


def verify_otp(user, otp_code, purpose):
    try:
        otp_obj = OTP.objects.get(user=user, purpose=purpose, otp=otp_code)
        if otp_obj.is_valid():
            otp_obj.delete()  # OTP can only be used once
            return True
        return False
    except OTP.DoesNotExist:
        return False