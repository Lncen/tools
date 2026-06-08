
import logging
import time
import hashlib
import requests
from typing import Dict, Any, Optional, Tuple



logger = logging.getLogger(__name__)

class YiLeSupClient:
    """
    Yile 供应商同步 client 实现。

    认证方式：sha1 签名
    接口风格：RESTful JSON API
    """
    def __init__(self, vendor):
        self.vendor = vendor

    def _sign(self, url: str) -> Tuple[str, int]:
        timestamp = int(time.time())
        app_key = self.vendor.app_key
        app_secret = self.vendor.app_secret
        sign_str = app_key + app_secret + url + str(timestamp)
        app_token = hashlib.sha1(sign_str.encode("utf-8")).hexdigest()
        return app_token, timestamp

    def _build_headers(self, url: str) -> Dict[str, str]:
        app_token, timestamp = self._sign(url)
        return {
            "AppId": self.vendor.app_key,
            "AppToken": app_token,
            "AppTimestamp": str(timestamp),
            "Content-Type": "application/json",
        }

    def _get_client(self) -> requests.Session:
        session = requests.Session()
        session.timeout = self.vendor.timeout_seconds
        # session.headers.update({"User-Agent": "YiLe-Supplier-Client/1.0"})
        return session

    def _request_with_status_tracking(self, method, url: str, **kwargs):
        """统一的请求方法，自动追踪连接状态"""
        try:
            response = method(url, **kwargs)

            response.raise_for_status()
            return response
        except Exception as e:
            error_msg = f"未知异常: {str(e)}"
            logger.exception("YiLe 未知异常 - URL: %s, Method: %s, ERROR:%s", url, method.__name__, error_msg)


    def _parse_response(self, response):
        try:
            print(response)
            json_data = response.json()
            if json_data.get("code") == 0:
                data = json_data.get("data")
                print(data)
                return json_data
            # 非0 code 视为业务错误
            logger.error(
                "YiLe 响应业务错误 - Status: %s, URL: %s, Data: %s",
                response.status_code,
                response.url,  # 修复：添加 URL
                json_data,
            )
        except ValueError as e:
            logger.warning(
                "YiLe 响应非 JSON 格式 - Status: %s, URL: %s, Raw: %.200s",
                response.status_code,
                response.url,
                response.text,
            )


    def _post(self, url: str, data: Dict[str, Any]):
        with self._get_client() as session:
            full_url = f"{self.vendor.base_url.rstrip('/')}{url}"
            response = self._request_with_status_tracking(
                session.post,
                full_url,
                json=data,
                headers=self._build_headers(url),
                timeout=self.vendor.timeout_seconds,
            )

            return self._parse_response(response)

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None):
        with self._get_client() as session:
            full_url = f"{self.vendor.base_url.rstrip('/')}{url}"
            response = self._request_with_status_tracking(
                session.get,
                full_url,
                params=params or {},
                headers=self._build_headers(url),
                timeout=self.vendor.timeout_seconds,
            )
        return self._parse_response(response)


    def get_category_list(self):
        return self._post("/openapi/customer/Goods/CategoryList", data={})

    def get_goods_list(self,data):
        return self._post("/openapi/customer/Goods/List", data=data)

    def health_check(self) -> Optional[Dict[str, Any]]:
        return self._get("/openapi/customer/CustomerAccount/Show")

class Task:
    app_key = 'AarUTX-cRt1jDgSZtwxwvwk2E4ZUQMzN'
    app_secret = 'qKPqiy_vMIDofvWrnncauwjagMXhIUSZ'
    timeout_seconds=20
    base_url="https://yd.dangxia.co/"

if __name__ == '__main__':
    client = YiLeSupClient(Task)
    # client.get_category_list() # 获取商品分类
    client.get_goods_list({"goods_category_id": 202 })
    # client.health_check()
