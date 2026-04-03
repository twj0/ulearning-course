"""
课程相关 API 客户端
"""

from typing import Any, Optional

from .base import BaseClient


class CourseClient(BaseClient):
    def get_course_info(self, textbook_id: int) -> dict:
        url = f"{self.config.UA_BASE_URL}/uaapi/course/{textbook_id}/basicinformation"
        response = self._get(url, headers=self.auth.get_ua_headers())
        if not response.text:
            return {}
        return response.json()
    
    def get_class_config(self, textbook_id: int, class_id: int) -> dict:
        url = f"{self.config.UA_BASE_URL}/uaapi/classes/{textbook_id}"
        response = self._get(url, headers=self.auth.get_ua_headers(), params={"classId": class_id})
        if not response.text:
            return {}
        return response.json()
    
    def get_course_directory(self, textbook_id: int, class_id: int) -> dict:
        url = f"{self.config.UA_BASE_URL}/uaapi/course/stu/{textbook_id}/directory"
        response = self._get(url, headers=self.auth.get_ua_headers(), params={"classId": class_id})
        if not response.text:
            return {}
        return response.json()
    
    def get_chapter_content(self, chapter_node_id: int) -> dict:
        url = f"{self.config.UA_BASE_URL}/uaapi/wholepage/chapter/stu/{chapter_node_id}"
        response = self._get(url, headers=self.auth.get_ua_headers())
        if not response.text:
            return {}
        return response.json()
    
    def get_course_list(self, publish_status: int = 1, page: int = 1, page_size: int = 15) -> dict:
        url = f"{self.config.LMS_BASE_URL}/courseapi/courses/students"
        params = {
            "keyword": "",
            "publishStatus": publish_status,
            "type": 1,
            "pn": page,
            "ps": page_size,
            "lang": "zh"
        }
        response = self._get(url, headers=self.auth.get_lms_headers(), params=params)
        if not response.text:
            return {}
        return response.json()
    
    def get_textbook_list(self, course_instance_id: int) -> list[dict]:
        url = f"{self.config.LMS_BASE_URL}/courseapi/textbook/student/{course_instance_id}/list"
        response = self._get(url, headers=self.auth.get_lms_headers(), params={"lang": "zh"})
        if not response.text:
            return []
        data = response.json()
        return data if isinstance(data, list) else []
    
    def get_all_courses(self, publish_status: int = 1) -> list[dict]:
        all_courses = []
        page = 1
        page_size = 15
        
        while True:
            result = self.get_course_list(publish_status, page, page_size)
            courses = result.get("courseList", [])
            
            if not courses:
                break
            
            all_courses.extend(courses)
            
            if len(all_courses) >= result.get("total", 0):
                break
            
            page += 1
        
        return all_courses
    
    def get_in_progress_courses(self) -> list[dict]:
        return self.get_all_courses(publish_status=1)
    
    def get_completed_courses(self) -> list[dict]:
        return self.get_all_courses(publish_status=3)
    
    def get_all_courses_list(self) -> list[dict]:
        return self.get_all_courses(publish_status=-1)
