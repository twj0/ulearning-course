"""
学习记录数据模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VideoRecord:
    video_id: int
    current: float
    status: int
    record_time: float
    time: float
    start_end_time_list: list = field(default_factory=list)
    
    @property
    def is_completed(self) -> bool:
        return self.status == 1


@dataclass
class PageRecord:
    page_id: int
    complete: int
    study_time: int
    score: int
    videos: list[VideoRecord] = field(default_factory=list)
    
    @property
    def is_completed(self) -> bool:
        return self.complete == 1


@dataclass
class StudyRecord:
    item_id: int
    complete: int
    score: int
    study_start_time: Optional[int] = None
    pages: list[PageRecord] = field(default_factory=list)
    
    @property
    def is_completed(self) -> bool:
        return self.complete == 1
    
    @classmethod
    def from_dict(cls, data: dict) -> "StudyRecord":
        pages = []
        for page_data in data.get("pageStudyRecordDTOList", []):
            videos = []
            for video_data in page_data.get("videos", []):
                videos.append(VideoRecord(
                    video_id=video_data.get("videoid", 0),
                    current=video_data.get("current", 0),
                    status=video_data.get("status", 0),
                    record_time=video_data.get("recordTime", 0),
                    time=video_data.get("time", 0),
                    start_end_time_list=video_data.get("startEndTimeList", [])
                ))
            pages.append(PageRecord(
                page_id=page_data.get("pageid", 0),
                complete=page_data.get("complete", 0),
                study_time=page_data.get("studyTime", 0),
                score=page_data.get("score", 0),
                videos=videos
            ))
        
        return cls(
            item_id=data.get("itemid", 0),
            complete=data.get("complete", 0),
            score=data.get("score", 0),
            study_start_time=data.get("studyStartTime"),
            pages=pages
        )
