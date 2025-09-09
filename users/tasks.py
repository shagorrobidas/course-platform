from celery import shared_task
from .utils import send_otp_email, send_verification_email
from users.models import User


@shared_task
def send_otp_email_task(user_id, otp, purpose):
    try:
        user = User.objects.get(id=user_id)
        send_otp_email(user, otp, purpose)
        print(f"Sent OTP email to {user.email} for {purpose} with OTP: {otp}")  # For debugging; remove in production
    except User.DoesNotExist:
        pass


@shared_task
def send_verification_email_task(user_id, verification_url):

    try:
        user = User.objects.get(id=user_id)
        send_verification_email(user, verification_url)
    except User.DoesNotExist:
        pass
