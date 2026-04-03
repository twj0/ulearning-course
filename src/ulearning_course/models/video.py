"""
视频数据模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Video:
    video_id: int
    item_id: int
    page_id: int
    chapter_node_id: int
    duration: int
    title: str = ""
    resource_url: str = ""
    is_completed: bool = False
    record_time: float = 0.0
    current_position: float = 0.0
    
    def to_study_record(self, study_start_time: int, user_name: Optional[str] = None) -> dict:
        import time
        
        now = int(time.time())
        record_time = self.duration * 0.95
        
        record = {
            "itemid": self.item_id,
            "autoSave": 1,
            "withoutOld": None,
            "complete": 1,
            "studyStartTime": study_start_time,
            "score": 100,
            "pageStudyRecordDTOList": [
                {
                    "pageid": self.page_id,
                    "complete": 1,
                    "studyTime": int(self.duration * 1.2),
                    "score": 100,
                    "answerTime": 0,
                    "submitTimes": 0,
                    "questions": [],
                    "videos": [
                        {
                            "videoid": self.video_id,
                            "current": 0,
                            "status": 1,
                            "recordTime": record_time,
                            "time": self.duration,
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
