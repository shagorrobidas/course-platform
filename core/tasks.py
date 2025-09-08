from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
from io import BytesIO
from django.core.files.base import ContentFile
from courses.models import Enrollment


@shared_task
def send_welcome_email(user_id):
    from users.models import User
    try:
        user = User.objects.get(id=user_id)
        subject = 'Welcome to Our Course Platform'
        message = render_to_string('emails/welcome_email.html', {
            'user': user
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass

@shared_task
def send_course_enrollment_email(enrollment_id):
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        subject = f'You have enrolled in {enrollment.course.title}'
        message = render_to_string('emails/course_enrollment.html', {
            'user': enrollment.student,
            'course': enrollment.course
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [enrollment.student.email],
            fail_silently=False,
        )
    except Enrollment.DoesNotExist:
        pass