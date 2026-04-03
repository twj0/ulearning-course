"""
学习记录相关 API 客户端
"""

import json
from requests import JSONDecodeError
from typing import Any, Optional

from .base import BaseClient


class StudyClient(BaseClient):
    def initialize_session(self, item_id: int) -> int:
        url = f"{self.config.UA_BASE_URL}/uaapi/studyrecord/initialize/{item_id}"
        response = self._get(url, headers=self.auth.get_ua_headers())
        return int(response.text.strip())
    
    def get_study_record(self, item_id: int) -> dict:
        url = f"{self.config.UA_BASE_URL}/uaapi/studyrecord/item/{item_id}"
        response = self._get(url, headers=self.auth.get_ua_headers(), params={"courseType": 4})
        if not response.text:
            return {}
        try:
            data = response.json()
        except JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}
    
    def send_heartbeat(self, item_id: int, study_start_time: int) -> int:
        url = f"{self.config.UA_BASE_URL}/uaapi/studyrecord/heartbeat/{item_id}/{study_start_time}"
        response = self._get(url, headers=self.auth.get_ua_headers())
        data = response.json()
        return data.get("status", -1)
    
    def sync_study_record(self, record: dict) -> int:
        from ..core import DESCipher
        
        url = f"{self.config.UA_BASE_URL}/uaapi/yws/api/personal/sync"
        params = {"courseType": 4, "platform": "PC"}
        
        cipher = DESCipher(self.config.DES_KEY)
        json_text = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        encrypted_body = cipher.encrypt(json_text)
        
        response = self._post(
            url,
            headers=self.auth.get_ua_headers(),
            params=params,
            data=encrypted_body
        )
        
        try:
            result = response.json()
            if isinstance(result, int):
                return result
            return result.get("code", -1) if isinstance(result, dict) else -1
        except:
            return -1
    
    def check_completion_status(self, item_id: int) -> int:
        record = self.get_study_record(item_id)
        if "completion_status" in record:
            return int(record.get("completion_status", 0) or 0)
        return int(record.get("complete", 0) or 0)
