"""
DGUT Ulearning 客户端
"""

from .core import Config, DESCipher, AuthManager
from .api import BaseClient, CourseClient, StudyClient, BehaviorClient
from .models import Course, Chapter, Section, Page, Video, StudyRecord
from .services import CourseService, StudyService

__version__ = "0.1.0"

__all__ = [
    "Config",
    "DESCipher",
    "AuthManager",
    "BaseClient",
    "CourseClient",
    "StudyClient",
    "BehaviorClient",
    "Course",
    "Chapter",
    "Section",
    "Page",
    "Video",
    "StudyRecord",
    "CourseService",
    "StudyService",
]
