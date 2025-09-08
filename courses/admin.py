from django.contrib import admin
from .models import (
    Category,
    Course,
    Enrollment,
    Module,
    Lesson,
    Progress
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'created_at')
    search_fields = ('title', 'instructor__username', 'category__name')
    list_filter = ('category', 'created_at')
    ordering = ('id',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'completed')
    search_fields = ('student__username', 'course__title')
    list_filter = ('enrolled_at', 'completed')
    ordering = ('id',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    ordering = ('course', 'order')  

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module')
    search_fields = ('title', 'module__title')
    list_filter = ('module',)
    ordering = ('module', 'title')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'last_accessed')
    search_fields = ('student__username', 'lesson__title')
    list_filter = ('completed', 'last_accessed')
    ordering = ('student', 'lesson')
