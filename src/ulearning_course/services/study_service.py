"""
学习记录同步服务
"""

import time
from typing import Optional

from ..api import BehaviorClient, StudyClient
from ..models import Video


class StudyService:
    def __init__(
        self,
        study_client: Optional[StudyClient] = None,
        behavior_client: Optional[BehaviorClient] = None
    ):
        self.study_client = study_client or StudyClient()
        self.behavior_client = behavior_client or BehaviorClient()
    
    def check_video_status(self, video: Video) -> bool:
        try:
            record = self.study_client.get_study_record(video.item_id)
        except Exception as exc:
            print(f"读取学习状态失败，按未完成处理: itemid={video.item_id}, error={exc}")
            return False

        page_records = record.get("pageStudyRecordDTOList", []) if isinstance(record, dict) else []
        target_page = next(
            (
                page for page in page_records
                if int(page.get("pageid", 0) or 0) == int(video.page_id)
            ),
            None,
        )
        if target_page is not None:
            for video_record in target_page.get("videos", []):
                if int(video_record.get("videoid", 0) or 0) != int(video.video_id):
                    continue
                return int(video_record.get("status", 0) or 0) == 1
            return int(target_page.get("complete", 0) or 0) == 1

        if len(page_records) <= 1:
            if "completion_status" in record:
                return int(record.get("completion_status", 0) or 0) == 1
            return int(record.get("complete", 0) or 0) == 1

        return False
    
    def complete_video(
        self,
        video: Video,
        class_id: int,
        textbook_id: int,
        user_name: Optional[str] = None
    ) -> bool:
        print(f"\n尝试完成视频: {video.title}")
        print(f"itemid={video.item_id}, videoid={video.video_id}, duration={video.duration}")
        
        print("\n步骤1: 发送行为打点...")
        try:
            self.behavior_client.watch_video(
                class_id, textbook_id, video.chapter_node_id, video.video_id
            )
        except Exception as e:
            print(f"行为打点失败: {e}")
        
        print("\n步骤2: 初始化学习会话...")
        study_start_time = self.study_client.initialize_session(video.item_id)
        print(f"studyStartTime={study_start_time}")
        
        print("\n步骤3: 发送心跳...")
        try:
            self.study_client.send_heartbeat(video.item_id, study_start_time)
        except Exception as e:
            print(f"心跳失败: {e}")
        
        print("\n步骤4: 同步学习记录（未完成状态）...")
        incomplete_record = self._build_record(video, study_start_time, user_name, complete=False)
        result1 = self.study_client.sync_study_record(incomplete_record)
        print(f"未完成状态同步结果: {result1}")
        
        print("\n等待 3 秒...")
        time.sleep(3)
        
        print("\n步骤5: 同步学习记录（完成状态）...")
        complete_record = self._build_record(video, study_start_time, user_name, complete=True)
        result2 = self.study_client.sync_study_record(complete_record)
        print(f"完成状态同步结果: {result2}")
        
        if result2 == 1:
            print("✅ 成功完成视频学习！")
            return True
        
        print(f"⚠️ 同步返回: {result1}/{result2}，可能需要其他前置操作")
        return False
    
    def _build_record(
        self,
        video: Video,
        study_start_time: int,
        user_name: Optional[str],
        complete: bool
    ) -> dict:
        now = int(time.time())
        
        if complete:
            record_time = video.duration * 0.95
            record = {
                "itemid": video.item_id,
                "autoSave": 1,
                "withoutOld": None,
                "complete": 1,
                "studyStartTime": study_start_time,
                "score": 100,
                "pageStudyRecordDTOList": [
                    {
                        "pageid": video.page_id,
                        "complete": 1,
                        "studyTime": int(video.duration * 1.2),
                        "score": 100,
                        "answerTime": 0,
                        "submitTimes": 0,
                        "questions": [],
                        "videos": [
                            {
                                "videoid": video.video_id,
                                "current": 0,
                                "status": 1,
                                "recordTime": record_time,
                                "time": video.duration,
                                "startEndTimeList": [
                                    {
                                        "startTime": now - int(record_time),
                                        "endTime": now
                                    }
                                ]
                            }
                        ],
                        "speaks": []
                    }
                ]
            }
            if user_name is not None:
                record["userName"] = user_name
            return record
        else:
            record_time = video.duration * 0.3
            record = {
                "itemid": video.item_id,
                "autoSave": 1,
                "withoutOld": None,
                "complete": 0,
                "studyStartTime": study_start_time,
                "score": 0,
                "pageStudyRecordDTOList": [
                    {
                        "pageid": video.page_id,
                        "complete": 0,
                        "studyTime": int(record_time),
                        "score": 0,
                        "answerTime": 0,
                        "submitTimes": 0,
                        "questions": [],
                        "videos": [
                            {
                                "videoid": video.video_id,
                                "current": int(record_time),
                                "status": 0,
                                "recordTime": record_time,
                                "time": video.duration,
                                "startEndTimeList": [
                                    {
                                        "startTime": now - int(record_time),
                                        "endTime": now
                                    }
                                ]
                            }
                        ],
                        "speaks": []
                    }
                ]
            }
            if user_name is not None:
                record["userName"] = user_name
            return record
    
    def batch_complete_videos(
        self,
        videos: list[Video],
        class_id: int,
        textbook_id: int,
        user_name: Optional[str] = None
    ) -> tuple[int, int]:
        success_count = 0
        fail_count = 0
        
        for video in videos:
            try:
                if self.complete_video(video, class_id, textbook_id, user_name):
                    success_count += 1
                else:
                    fail_count += 1
                
                time.sleep(5)
            except Exception as e:
                print(f"完成视频失败: {e}")
                fail_count += 1
        
        return success_count, fail_count
