from .catagory import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView
)
from .courses import (
    CourseListView,
    CourseCreateView,
    CourseDetailView,
    CourseUpdateView,
    CourseDeleteView,
    course_analytics
)
from .enrollment import (
    EnrollmentCreateView,
    EnrollmentListView
)
from .lesson import LessonDetailView
from .module import ModuleListView
from .progress import (
    ProgressUpdateView,
    student_progress_report
)


__all__ = (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    CourseListView,
    CourseCreateView,
    CourseDetailView,
    CourseUpdateView,
    CourseDeleteView,
    course_analytics,
    EnrollmentCreateView,
    EnrollmentListView,
    LessonDetailView,
    ModuleListView,
    ProgressUpdateView,
    student_progress_report

)
