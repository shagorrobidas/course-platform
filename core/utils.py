from celery import core as celery_app
from core.tasks import send_course_update_notification


def trigger_course_update(course_id, message):
    send_course_update_notification.delay(course_id, message)