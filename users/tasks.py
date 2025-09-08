from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .utils import send_otp_email, send_verification_email

@shared_task
def send_otp_email_task(user_id, otp, purpose):
    from .models import User
    try:
        user = User.objects.get(id=user_id)
        send_otp_email(user, otp, purpose)
    except User.DoesNotExist:
        pass

@shared_task
def send_verification_email_task(user_id, verification_url):
    from .models import User
    try:
        user = User.objects.get(id=user_id)
        send_verification_email(user, verification_url)
    except User.DoesNotExist:
        pass