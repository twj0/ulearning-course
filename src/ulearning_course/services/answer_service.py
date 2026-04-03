"""
测试页答题服务
"""

from __future__ import annotations

from typing import Any, Optional

from ..api import StudyClient
from .course_service import CourseService


class AnswerService:
    def __init__(
        self,
        study_client: Optional[StudyClient] = None,
        course_service: Optional[CourseService] = None,
    ):
        self.study_client = study_client or StudyClient()
        self.course_service = course_service or CourseService()

    def answer_first_test_section(
        self,
        textbook_id: int,
        class_id: int,
        chapter_id: int,
    ) -> dict[str, Any]:
        return self.answer_chapter(textbook_id, class_id, chapter_id)

    def answer_chapter(
        self,
        textbook_id: int,
        class_id: int,
        chapter_id: int,
    ) -> dict[str, Any]:
        chapter_node_id = self.course_service.resolve_chapter_node_id(
            textbook_id,
            class_id,
            chapter_id,
        )
        if chapter_node_id <= 0:
            raise ValueError(f"未找到 chapterId={chapter_id} 对应的 chapterNodeId")

        test_sections = self.course_service.find_test_sections(
            textbook_id,
            class_id,
            chapter_id,
        )
        if not test_sections:
            raise ValueError(f"chapterId={chapter_id} 下未找到测试小节")

        item_results: list[dict[str, Any]] = []
        total_question_count = 0
        total_answered_count = 0
        total_submitted_score = 0
        total_readback_score = 0
        baseline_total_score = 0

        for test_section in test_sections:
            result = self.answer_item(
                test_section["item_id"],
                chapter_node_id=test_section.get("chapter_node_id"),
                chapter_title=test_section.get("chapter_title", ""),
                item_title=test_section.get("item_title", ""),
                test_page_count=test_section.get("test_page_count"),
            )
            result["chapter_title"] = test_section.get("chapter_title", result.get("chapter_title", ""))
            result["item_title"] = test_section.get("item_title", result.get("item_title", ""))
            result["test_page_count"] = test_section.get("test_page_count", result.get("test_page_count", 0))
            item_results.append(result)
            total_question_count += int(result.get("question_count", 0) or 0)
            total_answered_count += int(result.get("answered_question_count", 0) or 0)
            total_submitted_score += int(result.get("submitted_score", 0) or 0)
            total_readback_score += int(result.get("readback_score", 0) or 0)
            baseline_total_score += int(result.get("baseline_score", 0) or 0)

        return {
            "textbook_id": textbook_id,
            "class_id": class_id,
            "chapter_id": chapter_id,
            "chapter_node_id": chapter_node_id,
            "chapter_title": test_sections[0].get("chapter_title", ""),
            "section_count": len(test_sections),
            "test_page_count": sum(int(section.get("test_page_count", 0) or 0) for section in test_sections),
            "question_count": total_question_count,
            "answered_question_count": total_answered_count,
            "baseline_score": baseline_total_score,
            "submitted_score": total_submitted_score,
            "readback_score": total_readback_score,
            "matched": all(bool(result.get("matched")) for result in item_results),
            "sync_result": ",".join(str(result.get("sync_result")) for result in item_results),
            "items": item_results,
            "item_id": item_results[0].get("item_id"),
            "item_title": item_results[0].get("item_title", ""),
        }

    def answer_item(
        self,
        item_id: int,
        chapter_node_id: Optional[int] = None,
        chapter_title: str = "",
        item_title: str = "",
        test_page_count: Optional[int] = None,
    ) -> dict[str, Any]:
        baseline_record = self.study_client.get_study_record(item_id)
        if not baseline_record and chapter_node_id is None:
            raise ValueError(f"无法读取 itemid={item_id} 的学习记录")

        resolved_chapter_node_id = int(chapter_node_id or baseline_record.get("node_id", 0) or 0)
        baseline_score = int(baseline_record.get("score", 0) or 0) if baseline_record else 0
        learner_name = baseline_record.get("learner_name") if baseline_record else None

        chapter_node_id = resolved_chapter_node_id
        if chapter_node_id <= 0:
            raise ValueError(f"itemid={item_id} 的学习记录中缺少 node_id")

        chapter_data = self.course_service.client.get_chapter_content(chapter_node_id)
        if not chapter_data:
            raise ValueError(f"无法读取 chapterNodeId={chapter_node_id} 的章节内容")

        section_info = self._find_section_info(chapter_data, item_id)
        if not section_info:
            raise ValueError(f"chapterNodeId={chapter_node_id} 中未找到 itemid={item_id} 的测试小节")
        if chapter_title:
            section_info["chapter_title"] = chapter_title
        if item_title:
            section_info["item_title"] = item_title
        if test_page_count is not None:
            section_info["test_page_count"] = test_page_count

        questions = self._parse_questions(chapter_data, item_id)
        if not questions:
            raise ValueError(f"itemid={item_id} 下未解析到题目")

        answers = self._get_all_answers(questions)
        if not answers:
            raise ValueError(f"itemid={item_id} 下未获取到任何标准答案")

        page_records, total_score, answered_count = self._build_answer_records(questions, answers)
        if not page_records:
            raise ValueError(f"itemid={item_id} 无可提交的答题记录")

        study_start_time = self.study_client.initialize_session(item_id)
        sync_data = {
            "itemid": item_id,
            "autoSave": 1,
            "withoutOld": 1,
            "complete": 1,
            "score": total_score,
            "studyStartTime": study_start_time,
            "pageStudyRecordDTOList": page_records,
        }
        if learner_name:
            sync_data["userName"] = learner_name

        sync_result = self.study_client.sync_study_record(sync_data)
        immediate_record = self.study_client.get_study_record(item_id)
        immediate_score = int(immediate_record.get("score", 0) or 0)
        matched = immediate_score == total_score

        return {
            "item_id": item_id,
            "chapter_node_id": chapter_node_id,
            "chapter_title": section_info.get("chapter_title", ""),
            "item_title": section_info.get("item_title", ""),
            "test_page_count": section_info.get("test_page_count", 0),
            "question_count": len(questions),
            "answered_question_count": answered_count,
            "submitted_score": total_score,
            "sync_result": sync_result,
            "readback_score": immediate_score,
            "matched": matched,
            "baseline_score": baseline_score,
            "record": immediate_record,
        }

    def _find_section_info(self, chapter_data: dict[str, Any], item_id: int) -> dict[str, Any]:
        chapter_node_id = int(chapter_data.get("chapterid", 0) or 0)
        for item_data in chapter_data.get("wholepageItemDTOList", []):
            if int(item_data.get("itemid", 0) or 0) != item_id:
                continue
            pages = item_data.get("wholepageDTOList", [])
            test_pages = [page for page in pages if page.get("contentType", 0) == 7]
            return {
                "chapter_node_id": chapter_node_id,
                "item_id": item_id,
                "item_title": item_data.get("title", "") or item_data.get("content", ""),
                "chapter_title": "",
                "test_page_count": len(test_pages),
            }
        return {}

    def _parse_questions(self, chapter_data: dict[str, Any], item_id: int) -> list[dict[str, Any]]:
        questions: list[dict[str, Any]] = []
        for item_data in chapter_data.get("wholepageItemDTOList", []):
            if int(item_data.get("itemid", 0) or 0) != item_id:
                continue

            for page_data in item_data.get("wholepageDTOList", []):
                if page_data.get("contentType", 0) != 7:
                    continue

                page_id = int(page_data.get("id", 0) or 0)
                page_relation_id = int(page_data.get("relationid", 0) or 0)
                for component in page_data.get("coursepageDTOList", []):
                    if component.get("type", 0) != 6:
                        continue

                    for question_dto in component.get("questionDTOList", []):
                        questions.append({
                            "page_id": page_id,
                            "page_relation_id": page_relation_id,
                            "question_id": int(question_dto.get("questionid", 0) or 0),
                            "question_type": int(question_dto.get("type", 0) or 0),
                            "question_score": float(question_dto.get("score", 1.0) or 1.0),
                        })
        return questions

    def _get_all_answers(
        self,
        questions: list[dict[str, Any]],
    ) -> dict[tuple[int, int], dict[str, Any]]:
        answers: dict[tuple[int, int], dict[str, Any]] = {}
        for question in questions:
            question_id = question["question_id"]
            page_id = question["page_id"]
            answer_key = (question_id, page_id)
            if answer_key in answers:
                continue

            answer_data = self.study_client.get_question_answer(question_id, page_id)
            if answer_data:
                answers[answer_key] = answer_data
        return answers

    def _build_answer_records(
        self,
        questions: list[dict[str, Any]],
        answers: dict[tuple[int, int], dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], int, int]:
        pages_map: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for question in questions:
            key = (question["page_id"], question["page_relation_id"])
            pages_map.setdefault(key, []).append(question)

        page_records: list[dict[str, Any]] = []
        total_score = 0
        answered_count = 0

        for (page_id, page_relation_id), page_questions in pages_map.items():
            question_records: list[dict[str, Any]] = []
            page_raw_score = 0.0
            page_total_score = 0.0

            for question in page_questions:
                question_id = question["question_id"]
                page_id = question["page_id"]
                question_type = question["question_type"]
                question_score = float(question.get("question_score", 1.0) or 1.0)
                answer_data = answers.get((question_id, page_id))
                page_total_score += question_score
                if not answer_data:
                    continue

                correct_answer = answer_data.get("correctAnswerList", [])
                if not correct_answer:
                    continue

                score, _ = self._calculate_question_score(
                    question_type,
                    correct_answer,
                    correct_answer,
                    max_score=question_score,
                )
                question_records.append({
                    "questionid": question_id,
                    "answerList": correct_answer,
                    "score": score,
                })
                page_raw_score += score
                answered_count += 1

            if not question_records:
                continue

            normalized_page_score = self._normalize_page_score(
                page_raw_score,
                page_total_score,
            )

            page_records.append({
                "pageid": page_relation_id,
                "complete": 1,
                "studyTime": 264,
                "score": normalized_page_score,
                "answerTime": 1,
                "submitTimes": 1,
                "coursepageId": page_id,
                "questions": question_records,
                "videos": [],
                "speaks": [],
            })
            total_score += normalized_page_score

        if page_records:
            total_score = int(total_score / len(page_records))

        return page_records, total_score, answered_count

    def _calculate_question_score(
        self,
        question_type: int,
        user_answer: list[str],
        correct_answer: list[str],
        max_score: float = 1.0,
    ) -> tuple[float, bool]:
        if not user_answer or not correct_answer:
            return 0.0, False

        if question_type in (1, 4):
            is_correct = user_answer == correct_answer
            return (max_score if is_correct else 0.0), is_correct

        if question_type == 2:
            user_set = set(user_answer)
            correct_set = set(correct_answer)
            is_correct = user_set == correct_set
            return (max_score if is_correct else 0.0), is_correct

        is_correct = user_answer == correct_answer
        return (max_score if is_correct else 0.0), is_correct

    def _normalize_page_score(self, raw_score: float, total_score: float) -> int:
        if total_score <= 0:
            return 0
        if int(total_score) == 100:
            return int(raw_score)
        return int((100.0 * raw_score) / total_score)
