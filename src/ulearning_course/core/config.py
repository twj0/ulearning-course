"""
配置管理模块
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    UA_BASE_URL: str = "https://ua.dgut.edu.cn"
    LMS_BASE_URL: str = "https://lms.dgut.edu.cn"
    DES_KEY: bytes = b"12345678"
    AUTHORIZATION: Optional[str] = None
    COOKIE_FILE: Optional[Path] = None
    
    def __post_init__(self):
        if self.AUTHORIZATION is None:
            self.AUTHORIZATION = self._load_from_env()
        
        if self.COOKIE_FILE is None:
            self.COOKIE_FILE = Path(__file__).resolve().parents[3] / "cookie.json5"
    
    def _load_from_env(self) -> Optional[str]:
        import os
        from dotenv import load_dotenv
        
        load_dotenv(Path(__file__).resolve().parents[3] / ".env")
        return os.environ.get("AUTHORIZATION")
    
    @classmethod
    def from_env(cls) -> "Config":
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        cookie_file = os.environ.get("ULEARNING_COOKIE_FILE")
        return cls(
            AUTHORIZATION=os.environ.get("AUTHORIZATION"),
            COOKIE_FILE=Path(cookie_file) if cookie_file else None
        )
