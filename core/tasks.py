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
from users.models import User
from django.template.exceptions import TemplateDoesNotExist
from django.utils.html import strip_tags
import logging
logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        print("Sending welcome email...")
        
        html_message = render_to_string('emails/welcome_email.html', {'user': user})
        plain_message = strip_tags(html_message)  # fallback for clients that can't render HTML

        subject = 'Welcome to Our Course Platform'

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=html_message,  # ✅ send HTML properly
        )

        print(f"Sent welcome email to {user.email}")
        
    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist")
    except TemplateDoesNotExist as e:
        logger.error(f"Template not found: {e}")
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")


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


@shared_task
def generate_certificate(enrollment_id):
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)

        # Create PDF certificate
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Add background
        if os.path.exists(settings.BASE_DIR / 'static' / 'certificate_bg.png'):
            bg = ImageReader(
                settings.BASE_DIR / 'static' / 'certificate_bg.png'
            )
            c.drawImage(bg, 0, 0, width=width, height=height)

        # Add text
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(
            width/2,
            height/2 + 50,
            "Certificate of Completion"
        )

        c.setFont("Helvetica", 18)
        c.drawCentredString(
            width/2,
            height/2,
            f"This certifies that {enrollment.student.get_full_name()}"
        )
        c.drawCentredString(
            width/2,
            height/2 - 30,
            f"has successfully completed the course {enrollment.course.title}"
        )
        c.drawCentredString(
            width/2,
            height/2 - 60,
            f"'{enrollment.course.title}'"
        )

        c.setFont("Helvetica", 12)
        c.drawCentredString(
            width/2,
            height/2 - 120,
            f"Completed on: {enrollment.completed_at.strftime('%B %d, %Y')}"
        )

        c.showPage()
        c.save()

        # Save certificate to enrollment
        certificate_file = ContentFile(buffer.getvalue())
        enrollment.certificate.save(
            f'certificate_{enrollment.id}.pdf',
            certificate_file
        )
        enrollment.save()

        # Send email with certificate
        subject = f'Certificate for {enrollment.course.title}'
        message = render_to_string('emails/certificate_email.html', {
            'user': enrollment.student,
            'course': enrollment.course
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [enrollment.student.email],
            fail_silently=False,
            html_message=message,
            attachments=[(
                f'certificate_{enrollment.id}.pdf',
                buffer.getvalue(),
                'application/pdf'
            )]
        )

    except Enrollment.DoesNotExist:
        pass


@shared_task
def send_course_update_notification(course_id, message):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"course_{course_id}",
        {
            'type': 'class_update_message',
            'message': message,
            'course_id': course_id
        }
    )
