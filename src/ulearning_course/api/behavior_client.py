"""
行为打点 API 客户端
"""

from typing import Any

from .base import BaseClient


class BehaviorClient(BaseClient):
    def watch_video(self, class_id: int, textbook_id: int, chapter_node_id: int, video_id: int) -> dict:
        url = f"{self.config.LMS_BASE_URL}/courseapi/behavior/watchVideo"
        
        payload = {
            "classId": class_id,
            "courseId": textbook_id,
            "chapterId": chapter_node_id,
            "videoId": video_id
        }
        
        response = self._post(
            url,
            headers=self.auth.get_lms_headers(),
            json_data=payload
        )
        
        try:
            return response.json()
        except:
            return {}
