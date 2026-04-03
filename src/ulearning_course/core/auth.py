"""
认证管理模块
"""

import json
import os
from pathlib import Path
from typing import Optional

import requests


class AuthManager:
    def __init__(self, authorization: Optional[str] = None, cookie_file: Optional[Path] = None):
        self._cookies: dict[str, str] = {}
        self._token: str = ""
        self._authorization = authorization
        self.cookie_file = cookie_file
        self._load_auth()
    
    def _load_auth(self) -> None:
        if self._authorization:
            self._token = self._authorization
            self._cookies = {"token": self._token, "AUTHORIZATION": self._token}
            return
        
        if self.cookie_file and self.cookie_file.exists():
            self._load_cookies()
            return
        
        from dotenv import load_dotenv
        load_dotenv()
        
        env_token = os.environ.get("AUTHORIZATION")
        if env_token:
            self._token = env_token
            self._cookies = {"token": self._token, "AUTHORIZATION": self._token}
            return
        
        raise ValueError("未找到认证信息，请设置 AUTHORIZATION 环境变量或提供 cookie.json5 文件")
    
    def _load_cookies(self) -> None:
        with open(self.cookie_file, "r", encoding="utf-8") as f:
            cookies_list = json.load(f)
        
        self._cookies = {cookie["name"]: cookie["value"] for cookie in cookies_list}
        self._token = self._cookies.get("token", "") or self._cookies.get("AUTHORIZATION", "")
    
    @property
    def cookies(self) -> dict[str, str]:
        return self._cookies
    
    @property
    def token(self) -> str:
        return self._token
    
    def get_ua_headers(self) -> dict[str, str]:
        return {
            "AUTHORIZATION": self._token,
            "UA-AUTHORIZATION": self._token,
            "Content-Type": "application/json",
            "Origin": "https://ua.dgut.edu.cn",
            "Referer": "https://ua.dgut.edu.cn/learnCourse.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
    
    def get_lms_headers(self) -> dict[str, str]:
        return {
            "Authorization": self._token,
            "Content-Type": "application/json",
            "Origin": "https://ua.dgut.edu.cn",
            "Referer": "https://ua.dgut.edu.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
    
    def create_session(self) -> requests.Session:
        session = requests.Session()
        session.cookies.update(self._cookies)
        return session
