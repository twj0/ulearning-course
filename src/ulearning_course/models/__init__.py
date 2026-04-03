"""
数据模型模块
"""

from .course import Course, CourseInfo, Chapter, Section, Page
from .video import Video
from .study_record import StudyRecord, VideoRecord, PageRecord

__all__ = [
    "Course", "CourseInfo", "Chapter", "Section", "Page",
    "Video",
    "StudyRecord", "VideoRecord", "PageRecord",
]
