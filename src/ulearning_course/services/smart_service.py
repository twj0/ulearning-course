"""
教材级智能学习编排服务
"""

from __future__ import annotations

import time
from typing import Any, Optional

from ..api import StudyClient
from ..models import Video
from .answer_service import AnswerService
from .course_service import CourseService
from .study_service import StudyService


class SmartService:
    def __init__(
        self,
        course_service: Optional[CourseService] = None,
        study_service: Optional[StudyService] = None,
        answer_service: Optional[AnswerService] = None,
        study_client: Optional[StudyClient] = None,
    ):
        self.course_service = course_service or CourseService()
        self.study_service = study_service or StudyService()
        self.answer_service = answer_service or AnswerService()
        self.study_client = study_client or StudyClient()

    def run_textbook(
        self,
        textbook_id: int,
        class_id: int,
        user_name: Optional[str] = None,
        force_tests: bool = False,
        test_interval_seconds: float = 0.8,
    ) -> dict[str, Any]:
        course, videos = self.course_service.get_course_with_videos(textbook_id, class_id)
        if not course.name:
            raise ValueError(
                f"无法获取教材 {textbook_id} 的课程信息，请确认 textbook_id/class_id 是否正确"
            )

        videos_by_chapter: dict[int, list[Video]] = {}
        for video in videos:
            videos_by_chapter.setdefault(video.chapter_node_id, []).append(video)

        chapter_results: list[dict[str, Any]] = []
        total_video_candidates = 0
        total_test_candidates = 0
        completed_videos = 0
        skipped_videos = 0
        failed_videos = 0
        completed_tests = 0
        skipped_tests = 0
        failed_tests = 0

        for chapter in course.chapters:
            chapter_videos = videos_by_chapter.get(chapter.node_id, [])
            chapter_tests = self._find_chapter_test_sections(chapter)

            total_video_candidates += len(chapter_videos)
            total_test_candidates += len(chapter_tests)

            chapter_result: dict[str, Any] = {
                "chapter_id": chapter.chapter_id,
                "chapter_node_id": chapter.node_id,
                "chapter_title": chapter.title,
                "video_count": len(chapter_videos),
                "test_section_count": len(chapter_tests),
                "videos": [],
                "tests": [],
            }

            for video in chapter_videos:
                video_result = self._run_video(video, class_id, textbook_id, user_name)
                chapter_result["videos"].append(video_result)
                status = video_result["status"]
                if status == "completed":
                    completed_videos += 1
                elif status == "skipped":
                    skipped_videos += 1
                else:
                    failed_videos += 1

            for test_section in chapter_tests:
                test_result = self._run_test_section(test_section, force=force_tests)
                test_result.setdefault("item_title", test_section["item_title"])
                chapter_result["tests"].append(test_result)
                status = test_result["status"]
                if status == "completed":
                    completed_tests += 1
                elif status == "skipped":
                    skipped_tests += 1
                else:
                    failed_tests += 1
                if test_interval_seconds > 0:
                    time.sleep(test_interval_seconds)

            chapter_result["completed_videos"] = sum(
                1 for item in chapter_result["videos"] if item["status"] == "completed"
            )
            chapter_result["skipped_videos"] = sum(
                1 for item in chapter_result["videos"] if item["status"] == "skipped"
            )
            chapter_result["failed_videos"] = sum(
                1 for item in chapter_result["videos"] if item["status"] == "failed"
            )
            chapter_result["completed_tests"] = sum(
                1 for item in chapter_result["tests"] if item["status"] == "completed"
            )
            chapter_result["skipped_tests"] = sum(
                1 for item in chapter_result["tests"] if item["status"] == "skipped"
            )
            chapter_result["failed_tests"] = sum(
                1 for item in chapter_result["tests"] if item["status"] == "failed"
            )

            chapter_results.append(chapter_result)

        success = failed_videos == 0 and failed_tests == 0
        return {
            "textbook_id": textbook_id,
            "class_id": class_id,
            "course_name": course.name,
            "chapter_count": len(course.chapters),
            "video_count": total_video_candidates,
            "test_section_count": total_test_candidates,
            "completed_videos": completed_videos,
            "skipped_videos": skipped_videos,
            "failed_videos": failed_videos,
            "completed_tests": completed_tests,
            "skipped_tests": skipped_tests,
            "failed_tests": failed_tests,
            "success": success,
            "chapters": chapter_results,
        }

    def _find_chapter_test_sections(self, chapter: Any) -> list[dict[str, Any]]:
        sections: list[dict[str, Any]] = []
        for section in chapter.sections:
            test_pages = [page for page in section.pages if int(page.content_type or 0) == 7]
            if not test_pages:
                continue

            sections.append(
                {
                    "chapter_id": chapter.chapter_id,
                    "chapter_node_id": chapter.node_id,
                    "chapter_title": chapter.title,
                    "item_id": section.item_id,
                    "item_title": section.title,
                    "test_page_count": len(test_pages),
                }
            )
        return sections

    def _run_video(
        self,
        video: Video,
        class_id: int,
        textbook_id: int,
        user_name: Optional[str],
    ) -> dict[str, Any]:
        try:
            if self.study_service.check_video_status(video):
                return {
                    "status": "skipped",
                    "item_id": video.item_id,
                    "video_id": video.video_id,
                    "title": video.title,
                    "reason": "already_completed",
                }

            ok = self.study_service.complete_video(video, class_id, textbook_id, user_name)
            return {
                "status": "completed" if ok else "failed",
                "item_id": video.item_id,
                "video_id": video.video_id,
                "title": video.title,
            }
        except Exception as exc:
            return {
                "status": "failed",
                "item_id": video.item_id,
                "video_id": video.video_id,
                "title": video.title,
                "error": str(exc),
            }

    def _run_test_section(self, test_section: dict[str, Any], force: bool = False) -> dict[str, Any]:
        item_id = int(test_section["item_id"])
        try:
            if not force and self.study_client.check_completion_status(item_id) == 1:
                record = self.study_client.get_study_record(item_id)
                return {
                    "status": "skipped",
                    "item_id": item_id,
                    "submitted_score": int(record.get("score", 0) or 0),
                    "readback_score": int(record.get("score", 0) or 0),
                    "matched": True,
                    "reason": "already_completed",
                }

            result = self.answer_service.answer_item(
                item_id,
                chapter_node_id=int(test_section.get("chapter_node_id", 0) or 0),
                chapter_title=test_section.get("chapter_title", ""),
                item_title=test_section.get("item_title", ""),
                test_page_count=int(test_section.get("test_page_count", 0) or 0),
            )
            result["status"] = "completed" if result.get("matched") else "failed"
            return result
        except Exception as exc:
            return {
                "status": "failed",
                "item_id": item_id,
                "error": str(exc),
            }
