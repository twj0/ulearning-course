"""
课程相关数据模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CourseInfo:
    textbook_id: int
    name: str
    org_id: int
    course_type: int
    publish_status: int = 0


@dataclass
class Page:
    page_id: int
    relation_id: int
    title: str
    content_type: int
    videos: list = field(default_factory=list)


@dataclass
class Section:
    item_id: int
    section_id: int
    title: str
    pages: list[Page] = field(default_factory=list)


@dataclass
class Chapter:
    chapter_id: int
    node_id: int
    title: str
    sections: list[Section] = field(default_factory=list)


@dataclass
class Course:
    textbook_id: int
    class_id: int
    name: str
    chapters: list[Chapter] = field(default_factory=list)
    
    def get_all_videos(self) -> list:
        videos = []
        for chapter in self.chapters:
            for section in chapter.sections:
                for page in section.pages:
                    videos.extend(page.videos)
        return videos
    
    def get_incomplete_videos(self) -> list:
        return [v for v in self.get_all_videos() if not v.is_completed]
