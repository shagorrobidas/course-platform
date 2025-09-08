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
            bg = ImageReader(settings.BASE_DIR / 'static' / 'certificate_bg.png')
            c.drawImage(bg, 0, 0, width=width, height=height)

        # Add text
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height/2 + 50, "Certificate of Completion")

        c.setFont("Helvetica", 18)
        c.drawCentredString(width/2, height/2, f"This certifies that {enrollment.student.get_full_name()}")
        c.drawCentredString(width/2, height/2 - 30, f"has successfully completed the course")
        c.drawCentredString(width/2, height/2 - 60, f"'{enrollment.course.title}'")

        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height/2 - 120, f"Completed on: {enrollment.completed_at.strftime('%B %d, %Y')}")
        
        c.showPage()
        c.save()

        # Save certificate to enrollment
        certificate_file = ContentFile(buffer.getvalue())
        enrollment.certificate.save(f'certificate_{enrollment.id}.pdf', certificate_file)
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
            attachments=[(f'certificate_{enrollment.id}.pdf', buffer.getvalue(), 'application/pdf')]
        )

    except Enrollment.DoesNotExist:
        pass
