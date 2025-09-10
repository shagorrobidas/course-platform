from django.contrib import admin
from .models import Notification, Question, ClassUpdate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('created_at', 'is_read')
    ordering = ('id',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'message', 'created_at')
    search_fields = ('user__username', 'course__title', 'message')
    list_filter = ('created_at',)
    ordering = ('id',)


@admin.register(ClassUpdate)
class ClassUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'message', 'created_at')
    search_fields = ('course__title', 'message')
    list_filter = ('created_at',)
    ordering = ('id',)
# Register your models here.
