"""
API 客户端基类
"""

from typing import Any, Optional

import requests

from ..core import AuthManager, Config


class BaseClient:
    def __init__(self, config: Optional[Config] = None, auth: Optional[AuthManager] = None):
        self.config = config or Config()
        self.auth = auth or AuthManager(
            authorization=self.config.AUTHORIZATION,
            cookie_file=self.config.COOKIE_FILE
        )
        self.session = self.auth.create_session()
        self.session.trust_env = False
    
    def _request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
    ) -> requests.Response:
        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            data=data,
        )
        response.raise_for_status()
        return response
    
    def _get(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None) -> requests.Response:
        return self._request("GET", url, headers=headers, params=params)
    
    def _post(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
    ) -> requests.Response:
        return self._request("POST", url, headers=headers, params=params, json_data=json_data, data=data)
