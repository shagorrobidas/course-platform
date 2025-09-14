from .catagory import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    CatagoryDetailView
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
from .lesson import (
    LessonDetailView,
    LessonCreateView,
    LessonUpdateView,
    LessonDeleteView
)
from .module import (
    ModuleListView,
    CourseModuleCreateView,
    ModuleUpdateView,
    ModuleDeleteView
)
from .progress import (
    ProgressUpdateView,
    student_progress_report
)
from .progress_view import (
    ProgressListView,
    ProgressCreateView,
    ProgressDetailView,
    ProgressBulkUpdateView
)


__all__ = (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    CatagoryDetailView,
    CourseListView,
    CourseCreateView,
    CourseDetailView,
    CourseUpdateView,
    CourseDeleteView,
    course_analytics,
    EnrollmentCreateView,
    EnrollmentListView,
    LessonDetailView,
    LessonCreateView,
    LessonUpdateView,
    LessonDeleteView,
    ModuleListView,
    CourseModuleCreateView,
    ModuleUpdateView,
    ModuleDeleteView,
    ProgressUpdateView,
    student_progress_report,
    ProgressListView,
    ProgressCreateView,
    ProgressDetailView,
    ProgressBulkUpdateView

)
