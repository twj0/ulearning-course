"""
课程管理服务
"""

from typing import Optional

from ..api import CourseClient
from ..models import Course, Chapter, Section, Page, Video


class CourseService:
    def __init__(self, client: Optional[CourseClient] = None):
        self.client = client or CourseClient()
    
    def get_course(self, textbook_id: int, class_id: int) -> Course:
        directory = self.client.get_course_directory(textbook_id, class_id)
        
        course = Course(
            textbook_id=textbook_id,
            class_id=class_id,
            name=directory.get("coursename", "")
        )
        
        for chapter_data in directory.get("chapters", []):
            chapter = Chapter(
                chapter_id=chapter_data.get("id", 0),
                node_id=chapter_data.get("nodeid", 0),
                title=chapter_data.get("nodetitle", "")
            )
            
            for item_data in chapter_data.get("items", []):
                section = Section(
                    item_id=item_data.get("itemid", 0),
                    section_id=item_data.get("id", 0),
                    title=item_data.get("title", "")
                )
                
                for page_data in item_data.get("coursepages", []):
                    page = Page(
                        page_id=page_data.get("id", 0),
                        relation_id=page_data.get("relationid", 0),
                        title=page_data.get("title", ""),
                        content_type=page_data.get("contentType", 0)
                    )
                    section.pages.append(page)
                
                chapter.sections.append(section)
            
            course.chapters.append(chapter)
        
        return course
    
    def load_chapter_videos(self, course: Course) -> list[Video]:
        videos = []
        
        for chapter in course.chapters:
            content = self.client.get_chapter_content(chapter.node_id)
            
            for item_data in content.get("wholepageItemDTOList", []):
                item_id = item_data.get("itemid", 0)
                
                for page_data in item_data.get("wholepageDTOList", []):
                    page_id = page_data.get("relationid", 0)
                    
                    for component in page_data.get("coursepageDTOList", []):
                        if component.get("type") == 4:
                            video = Video(
                                video_id=component.get("resourceid", 0),
                                item_id=item_id,
                                page_id=page_id,
                                chapter_node_id=chapter.node_id,
                                duration=component.get("videoLength", 0),
                                title=page_data.get("content", ""),
                                resource_url=component.get("resourceFullurl", "")
                            )
                            videos.append(video)
        
        return videos
    
    def get_course_with_videos(self, textbook_id: int, class_id: int) -> tuple[Course, list[Video]]:
        course = self.get_course(textbook_id, class_id)
        videos = self.load_chapter_videos(course)
        return course, videos
    
    def resolve_textbooks(self, course_instance_id: int) -> list[dict]:
        return self.client.get_textbook_list(course_instance_id)
    
    def get_in_progress_courses(self) -> list[dict]:
        return self.client.get_in_progress_courses()
    
    def get_completed_courses(self) -> list[dict]:
        return self.client.get_completed_courses()
    
    def get_all_courses(self) -> list[dict]:
        return self.client.get_all_courses_list()
