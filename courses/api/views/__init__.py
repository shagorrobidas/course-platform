from .catagory import CategoryListView
from .courses import (
    CourseListView,
    CourseDetailView,
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
    CourseListView,
    CourseDetailView,
    course_analytics,
    EnrollmentCreateView,
    EnrollmentListView,
    LessonDetailView,
    ModuleListView,
    ProgressUpdateView,
    student_progress_report

)
