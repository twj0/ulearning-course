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
        video_retry_count: int = 2,
        video_interval_seconds: float = 1.0,
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
        total_content_candidates = 0
        completed_videos = 0
        skipped_videos = 0
        failed_videos = 0
        completed_tests = 0
        skipped_tests = 0
        failed_tests = 0
        completed_contents = 0
        skipped_contents = 0
        failed_contents = 0

        for chapter in course.chapters:
            chapter_videos = videos_by_chapter.get(chapter.node_id, [])
            chapter_tests = self._find_chapter_test_sections(chapter)
            chapter_contents = self._find_chapter_content_sections(chapter)

            total_video_candidates += len(chapter_videos)
            total_test_candidates += len(chapter_tests)
            total_content_candidates += len(chapter_contents)

            chapter_result: dict[str, Any] = {
                "chapter_id": chapter.chapter_id,
                "chapter_node_id": chapter.node_id,
                "chapter_title": chapter.title,
                "video_count": len(chapter_videos),
                "test_section_count": len(chapter_tests),
                "content_section_count": len(chapter_contents),
                "videos": [],
                "tests": [],
                "contents": [],
            }

            for video in chapter_videos:
                video_result = self._run_video(
                    video,
                    class_id,
                    textbook_id,
                    user_name,
                    retry_count=video_retry_count,
                    retry_interval_seconds=video_interval_seconds,
                )
                chapter_result["videos"].append(video_result)
                status = video_result["status"]
                if status == "completed":
                    completed_videos += 1
                elif status == "skipped":
                    skipped_videos += 1
                else:
                    failed_videos += 1
                if video_interval_seconds > 0 and status != "skipped":
                    time.sleep(video_interval_seconds)

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

            for content_section in chapter_contents:
                content_result = self._run_content_section(content_section)
                content_result.setdefault("item_title", content_section["item_title"])
                chapter_result["contents"].append(content_result)
                status = content_result["status"]
                if status == "completed":
                    completed_contents += 1
                elif status == "skipped":
                    skipped_contents += 1
                else:
                    failed_contents += 1

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
            chapter_result["completed_contents"] = sum(
                1 for item in chapter_result["contents"] if item["status"] == "completed"
            )
            chapter_result["skipped_contents"] = sum(
                1 for item in chapter_result["contents"] if item["status"] == "skipped"
            )
            chapter_result["failed_contents"] = sum(
                1 for item in chapter_result["contents"] if item["status"] == "failed"
            )

            chapter_results.append(chapter_result)

        success = failed_videos == 0 and failed_tests == 0 and failed_contents == 0
        return {
            "textbook_id": textbook_id,
            "class_id": class_id,
            "course_name": course.name,
            "chapter_count": len(course.chapters),
            "video_count": total_video_candidates,
            "test_section_count": total_test_candidates,
            "content_section_count": total_content_candidates,
            "completed_videos": completed_videos,
            "skipped_videos": skipped_videos,
            "failed_videos": failed_videos,
            "completed_tests": completed_tests,
            "skipped_tests": skipped_tests,
            "failed_tests": failed_tests,
            "completed_contents": completed_contents,
            "skipped_contents": skipped_contents,
            "failed_contents": failed_contents,
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

    def _find_chapter_content_sections(self, chapter: Any) -> list[dict[str, Any]]:
        sections: list[dict[str, Any]] = []
        for section in chapter.sections:
            if not section.pages:
                continue

            content_pages = [page for page in section.pages if int(page.content_type or 0) == 5]
            if len(content_pages) != len(section.pages):
                continue

            sections.append(
                {
                    "chapter_id": chapter.chapter_id,
                    "chapter_node_id": chapter.node_id,
                    "chapter_title": chapter.title,
                    "item_id": section.item_id,
                    "item_title": section.title,
                    "page_count": len(content_pages),
                    "pages": [
                        {
                            "page_id": page.page_id,
                            "relation_id": page.relation_id,
                            "title": page.title,
                        }
                        for page in content_pages
                    ],
                }
            )
        return sections

    def _run_video(
        self,
        video: Video,
        class_id: int,
        textbook_id: int,
        user_name: Optional[str],
        retry_count: int = 2,
        retry_interval_seconds: float = 1.0,
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

            attempts = max(1, int(retry_count or 0) + 1)
            last_error = ""
            for attempt in range(1, attempts + 1):
                try:
                    ok = self.study_service.complete_video(video, class_id, textbook_id, user_name)
                except Exception as exc:
                    last_error = str(exc)
                    ok = False

                if ok:
                    return {
                        "status": "completed",
                        "item_id": video.item_id,
                        "video_id": video.video_id,
                        "title": video.title,
                        "attempts": attempt,
                    }

                if self.study_service.check_video_status(video):
                    return {
                        "status": "completed",
                        "item_id": video.item_id,
                        "video_id": video.video_id,
                        "title": video.title,
                        "attempts": attempt,
                    }

                if attempt < attempts and retry_interval_seconds > 0:
                    time.sleep(retry_interval_seconds)

            return {
                "status": "failed",
                "item_id": video.item_id,
                "video_id": video.video_id,
                "title": video.title,
                "error": last_error or "video_sync_failed",
                "attempts": attempts,
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

    def _run_content_section(self, content_section: dict[str, Any]) -> dict[str, Any]:
        item_id = int(content_section["item_id"])
        try:
            if self.study_client.check_completion_status(item_id) == 1:
                record = self.study_client.get_study_record(item_id)
                return {
                    "status": "skipped",
                    "item_id": item_id,
                    "submitted_score": int(record.get("score", 0) or 0),
                    "readback_score": int(record.get("score", 0) or 0),
                    "matched": True,
                    "reason": "already_completed",
                }

            baseline_record = self.study_client.get_study_record(item_id)
            baseline_pages = {
                int(page.get("pageid", 0) or 0): page
                for page in baseline_record.get("pageStudyRecordDTOList", [])
            } if baseline_record else {}

            study_start_time = self.study_client.initialize_session(item_id)
            page_records: list[dict[str, Any]] = []
            for page in content_section.get("pages", []):
                relation_id = int(page.get("relation_id", 0) or 0)
                baseline_page = baseline_pages.get(relation_id, {})
                baseline_study_time = int(baseline_page.get("studyTime", 0) or 0)
                page_records.append(
                    {
                        "pageid": relation_id,
                        "complete": 1,
                        "studyTime": max(baseline_study_time, 5),
                        "score": 100,
                        "answerTime": 1,
                        "submitTimes": int(baseline_page.get("submitTimes", 0) or 0),
                        "questions": [],
                        "videos": [],
                        "speaks": [],
                    }
                )

            payload = {
                "itemid": item_id,
                "autoSave": 1,
                "withoutOld": 1,
                "complete": 1,
                "score": 100,
                "studyStartTime": study_start_time,
                "pageStudyRecordDTOList": page_records,
            }
            user_name = baseline_record.get("learner_name") if baseline_record else None
            if user_name:
                payload["userName"] = user_name

            sync_result = self.study_client.sync_study_record(payload)
            record = self.study_client.get_study_record(item_id)
            readback_score = int(record.get("score", 0) or 0)
            matched = int(record.get("completion_status", 0) or 0) == 1 and readback_score == 100
            return {
                "status": "completed" if matched else "failed",
                "item_id": item_id,
                "submitted_score": 100,
                "sync_result": sync_result,
                "readback_score": readback_score,
                "matched": matched,
                "page_count": len(page_records),
                "baseline_score": int(baseline_record.get("score", 0) or 0) if baseline_record else 0,
            }
        except Exception as exc:
            return {
                "status": "failed",
                "item_id": item_id,
                "error": str(exc),
            }
