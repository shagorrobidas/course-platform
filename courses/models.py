from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class Course(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    title = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taught_courses',
        limit_choices_to={'role': 'teacher'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='beginner'
    )
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        blank=True,
        null=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_total_lessons(self):
        return self.modules.aggregate(
            total_lessons=models.Count('lessons')
        )['total_lessons'] or 0

    def get_total_enrollments(self):
        return self.enrollments.count()


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)

    def get_progress_percentage(self):
        total_lessons = self.course.get_total_lessons()
        if total_lessons == 0:
            return 0
        
        completed_lessons = Progress.objects.filter(
            student=self.student,
            lesson__module__course=self.course,
            completed=True
        ).count()
        
        return round((completed_lessons / total_lessons) * 100, 2)


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_total_lessons(self):
        return self.lessons.count()


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    content = models.TextField()
    video_url = models.URLField(
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(
        default=0
    )
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
        default=0
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def get_course(self):
        return self.module.course


class Progress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress',
        limit_choices_to={'role': 'student'}
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress',
    )
    completed = models.BooleanField(
        default=False
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    last_accessed = models.DateTimeField(auto_now=True)
    time_spent = models.PositiveIntegerField(
        default=0,
        help_text="Time spent in seconds"
    )

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student} - {self.lesson.title}"

    def save(self, *args, **kwargs):
        # Set completed_at timestamp when marking as completed
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed and self.completed_at:
            self.completed_at = None

        super().save(*args, **kwargs)

    @classmethod
    def get_course_progress(cls, student, course):
        """
        Calculate overall progress percentage for a course
        """
        total_lessons = Lesson.objects.filter(module__course=course).count()
        if total_lessons == 0:
            return 0

        completed_lessons = cls.objects.filter(
            student=student,
            lesson__module__course=course,
            completed=True
        ).count()

        return round((completed_lessons / total_lessons) * 100, 2)

    @classmethod
    def get_module_progress(cls, student, module):
        """
        Calculate progress percentage for a module
        """
        total_lessons = Lesson.objects.filter(module=module).count()
        if total_lessons == 0:
            return 0

        completed_lessons = cls.objects.filter(
            student=student,
            lesson__module=module,
            completed=True
        ).count()

        return round((completed_lessons / total_lessons) * 100, 2)

    @classmethod
    def get_student_overall_progress(cls, student):
        """
        Calculate overall progress across all enrolled courses
        """
        # Get all courses the student is enrolled in
        enrolled_courses = Course.objects.filter(
            enrollments__student=student
        )

        total_progress = 0
        course_count = enrolled_courses.count()

        if course_count == 0:
            return 0

        for course in enrolled_courses:
            total_progress += cls.get_course_progress(student, course)

        return round(total_progress / course_count, 2)


class Certificate(models.Model):
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='certificate'
    )
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    download_url = models.URLField(blank=True, null=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Certificate {self.certificate_id} - {self.enrollment.student}"
