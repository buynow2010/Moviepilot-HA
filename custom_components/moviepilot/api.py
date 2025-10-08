"""MoviePilot API Client - 优化版本

基于实际API测试结果重构
测试日期: 2025-10-06
参考: API_MAPPING.md
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from .const import (
    API_ENDPOINT_CPU,
    API_ENDPOINT_DOWNLOADER,
    API_ENDPOINT_MEMORY,
    API_ENDPOINT_MESSAGE,
    API_ENDPOINT_NETWORK,
    API_ENDPOINT_SCHEDULE,
    API_ENDPOINT_STATISTIC,
    API_ENDPOINT_STORAGE,
    API_ENDPOINT_TRANSFER_NOW,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class MoviePilotAPIError(Exception):
    """Base exception for MoviePilot API errors."""


class MoviePilotAuthError(MoviePilotAPIError):
    """Exception for authentication errors."""


class MoviePilotConnectionError(MoviePilotAPIError):
    """Exception for connection errors."""


class MoviePilotAPIClient:
    """MoviePilot API客户端 - 只包含已验证可用的端点"""

    def __init__(
        self,
        host: str,
        port: int,
        api_token: str,
        session: aiohttp.ClientSession,
        verify_ssl: bool = False,
    ) -> None:
        """初始化API客户端

        Args:
            host: MoviePilot主机地址
            port: 端口号(默认3000)
            api_token: API令牌 (用于URL参数认证)
            session: aiohttp会话
            verify_ssl: 是否验证SSL证书
        """
        self.host = host
        self.port = port
        self.api_token = api_token
        self.session = session
        self.verify_ssl = verify_ssl

        # 构建基础URL
        if host.startswith("http://") or host.startswith("https://"):
            self.base_url = f"{host}:{port}"
        else:
            protocol = "https" if port == 443 else "http"
            self.base_url = f"{protocol}://{host}:{port}"

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-MoviePilot/3.0",
        }

        _LOGGER.debug("MoviePilot API客户端初始化: %s", self.base_url)

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Any:
        """发送API请求

        Args:
            method: HTTP方法
            endpoint: API端点路径
            data: POST数据
            params: URL参数
            timeout: 超时时间(秒)

        Returns:
            API响应数据 (可能是dict、list、int或str)

        Raises:
            MoviePilotAuthError: 认证失败
            MoviePilotConnectionError: 连接失败
            MoviePilotAPIError: 其他API错误
        """
        url = f"{self.base_url}{endpoint}"

        # 添加token到URL参数
        if params is None:
            params = {}
        params["token"] = self.api_token

        # 记录请求(隐藏token)
        safe_params = {k: "***" if k == "token" else v for k, v in params.items()}
        _LOGGER.debug(
            "API请求: %s %s?%s",
            method,
            endpoint,
            "&".join(f"{k}={v}" for k, v in safe_params.items()),
        )

        try:
            async with async_timeout.timeout(timeout):
                async with self.session.request(
                    method,
                    url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    ssl=self.verify_ssl,
                ) as response:
                    # 处理401认证失败
                    if response.status == 401:
                        _LOGGER.error("API认证失败 %s: Token可能无效或已过期", endpoint)
                        raise MoviePilotAuthError("Authentication failed. Please check your API token.")

                    # 处理404
                    if response.status == 404:
                        _LOGGER.error("API端点不存在 %s", endpoint)
                        raise MoviePilotAPIError(f"API endpoint not found: {endpoint}")

                    # 处理其他错误
                    if response.status >= 400:
                        text = await response.text()
                        _LOGGER.warning(
                            "API请求失败 %s: HTTP %s - %s",
                            endpoint,
                            response.status,
                            text[:200],
                        )
                        raise MoviePilotAPIError(f"API request failed: HTTP {response.status}")

                    # 解析响应
                    content_type = response.headers.get("Content-Type", "")

                    if "application/json" in content_type:
                        try:
                            result = await response.json()
                            _LOGGER.debug("API响应成功: %s", endpoint)
                            return result
                        except (aiohttp.ContentTypeError, ValueError) as err:
                            _LOGGER.warning("API响应JSON解析失败 %s: %s", endpoint, err)
                            # 尝试返回文本
                            text = await response.text()
                            return text if text else None
                    else:
                        text = await response.text()
                        _LOGGER.debug("API返回非JSON响应: %s", text[:100])
                        return text if text else None

        except asyncio.TimeoutError as err:
            _LOGGER.error("API请求超时 %s (timeout=%ds)", endpoint, timeout)
            raise MoviePilotConnectionError(f"Connection timeout after {timeout}s") from err
        except aiohttp.ClientConnectorError as err:
            _LOGGER.error("API连接失败 %s: %s", endpoint, err)
            raise MoviePilotConnectionError(f"Cannot connect to MoviePilot: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("API客户端错误 %s: %s", endpoint, err)
            raise MoviePilotAPIError(f"API client error: {err}") from err
        except Exception as err:
            _LOGGER.exception("API意外错误 %s: %s", endpoint, err)
            raise MoviePilotAPIError(f"Unexpected error: {err}") from err

    # ========== 连接测试 ==========

    async def test_connection(self) -> dict[str, Any]:
        """测试连接并验证token

        Returns:
            包含连接状态的字典

        Raises:
            MoviePilotAuthError: 认证失败
            MoviePilotConnectionError: 连接失败
        """
        result = await self._request("GET", API_ENDPOINT_MESSAGE)

        if isinstance(result, dict) and result.get("status") == "OK":
            _LOGGER.info("MoviePilot连接测试成功")
            return {
                "name": "MoviePilot",
                "status": "connected",
                "endpoint": API_ENDPOINT_MESSAGE,
            }
        else:
            raise MoviePilotAPIError("Unexpected response from MoviePilot")

    # ========== Dashboard API (已验证可用) ==========

    async def get_cpu_usage(self) -> float:
        """获取CPU使用率

        Returns:
            CPU使用百分比 (0-100)
        """
        result = await self._request("GET", API_ENDPOINT_CPU)

        # API返回的是数字
        if isinstance(result, (int, float)):
            return float(result)
        else:
            _LOGGER.warning("CPU使用率返回格式异常: %s", result)
            return 0.0

    async def get_memory_usage(self) -> dict[str, Any]:
        """获取内存使用情况

        Returns:
            dict with keys:
                - used_bytes: 已用内存(字节)
                - percent: 使用百分比
        """
        result = await self._request("GET", API_ENDPOINT_MEMORY)

        # API返回: [已用字节数, 百分比]
        if isinstance(result, list) and len(result) >= 2:
            return {
                "used_bytes": int(result[0]) if result[0] else 0,
                "percent": float(result[1]) if result[1] else 0.0,
            }
        else:
            _LOGGER.warning("内存使用率返回格式异常: %s", result)
            return {"used_bytes": 0, "percent": 0.0}

    async def get_storage_usage(self) -> dict[str, Any]:
        """获取存储使用情况

        Returns:
            dict with keys:
                - total_bytes: 总存储空间(字节)
                - used_bytes: 已用存储空间(字节)
                - percent: 使用百分比
        """
        result = await self._request("GET", API_ENDPOINT_STORAGE)

        # API返回: {"total_storage": xxx, "used_storage": xxx}
        if isinstance(result, dict):
            total = float(result.get("total_storage", 0))
            used = float(result.get("used_storage", 0))
            percent = (used / total * 100) if total > 0 else 0.0

            return {
                "total_bytes": total,
                "used_bytes": used,
                "free_bytes": total - used,
                "percent": percent,
            }
        else:
            _LOGGER.warning("存储使用率返回格式异常: %s", result)
            return {"total_bytes": 0, "used_bytes": 0, "free_bytes": 0, "percent": 0.0}

    async def get_network_usage(self) -> dict[str, Any]:
        """获取网络使用情况

        Returns:
            dict with keys:
                - upload_speed: 上传速度 (bytes/s)
                - download_speed: 下载速度 (bytes/s)
        """
        result = await self._request("GET", API_ENDPOINT_NETWORK)

        # API返回: [上传速度, 下载速度]
        if isinstance(result, list) and len(result) >= 2:
            return {
                "upload_speed": float(result[0]) if result[0] else 0.0,
                "download_speed": float(result[1]) if result[1] else 0.0,
            }
        else:
            _LOGGER.warning("网络使用返回格式异常: %s", result)
            return {"upload_speed": 0.0, "download_speed": 0.0}

    async def get_statistics(self) -> dict[str, Any]:
        """获取媒体库统计信息

        Returns:
            dict with keys:
                - movie_count: 电影数量
                - tv_count: 剧集数量
                - episode_count: 集数
                - user_count: 用户数
        """
        result = await self._request("GET", API_ENDPOINT_STATISTIC)

        # API返回: {"movie_count": xx, "tv_count": xx, ...}
        if isinstance(result, dict):
            return {
                "movie_count": int(result.get("movie_count", 0)),
                "tv_count": int(result.get("tv_count", 0)),
                "episode_count": int(result.get("episode_count", 0)),
                "user_count": int(result.get("user_count", 0)),
            }
        else:
            _LOGGER.warning("统计信息返回格式异常: %s", result)
            return {
                "movie_count": 0,
                "tv_count": 0,
                "episode_count": 0,
                "user_count": 0,
            }

    async def get_downloader_info(self) -> dict[str, Any]:
        """获取下载器信息

        Returns:
            dict with keys:
                - download_speed: 当前下载速度 (bytes/s)
                - upload_speed: 当前上传速度 (bytes/s)
                - download_size: 累计下载量 (bytes)
                - upload_size: 累计上传量 (bytes)
                - free_space: 可用空间 (bytes)
        """
        result = await self._request("GET", API_ENDPOINT_DOWNLOADER)

        # API返回完整对象
        if isinstance(result, dict):
            return {
                "download_speed": float(result.get("download_speed", 0.0)),
                "upload_speed": float(result.get("upload_speed", 0.0)),
                "download_size": float(result.get("download_size", 0.0)),
                "upload_size": float(result.get("upload_size", 0.0)),
                "free_space": float(result.get("free_space", 0.0)),
            }
        else:
            _LOGGER.warning("下载器信息返回格式异常: %s", result)
            return {
                "download_speed": 0.0,
                "upload_speed": 0.0,
                "download_size": 0.0,
                "upload_size": 0.0,
                "free_space": 0.0,
            }

    async def get_scheduler_info(self) -> list[dict[str, Any]]:
        """获取计划任务信息

        Returns:
            任务列表，每个任务包含:
                - id: 任务ID
                - name: 任务名称
                - provider: 提供者
                - status: 状态
                - next_run: 下次运行时间
        """
        result = await self._request("GET", API_ENDPOINT_SCHEDULE)

        if isinstance(result, list):
            return result
        else:
            _LOGGER.warning("计划任务返回格式异常: %s", result)
            return []

    async def get_transfer_now(self) -> dict[str, Any]:
        """获取当前传输状态

        Returns:
            dict with keys:
                - success: 是否成功
                - message: 消息
                - data: 传输数据（空表示无传输）
        """
        result = await self._request("GET", API_ENDPOINT_TRANSFER_NOW)

        if isinstance(result, dict):
            return result
        else:
            _LOGGER.warning("传输状态返回格式异常: %s", result)
            return {"success": False, "message": None, "data": {}}

    # ========== 便捷方法 ==========

    async def get_dashboard_overview(self) -> dict[str, Any]:
        """获取Dashboard完整数据 (并发请求所有端点)

        Returns:
            完整的Dashboard数据字典
        """
        try:
            # 并发获取所有Dashboard数据
            results = await asyncio.gather(
                self.get_cpu_usage(),
                self.get_memory_usage(),
                self.get_storage_usage(),
                self.get_network_usage(),
                self.get_statistics(),
                self.get_downloader_info(),
                self.get_scheduler_info(),
                self.get_transfer_now(),
                return_exceptions=True,
            )

            # 解包结果
            cpu, memory, storage, network, stats, downloader, tasks, transfer = results

            # 处理异常结果
            cpu = cpu if not isinstance(cpu, Exception) else 0.0
            memory = memory if not isinstance(memory, Exception) else {"used_bytes": 0, "percent": 0.0}
            storage = storage if not isinstance(storage, Exception) else {
                "total_bytes": 0,
                "used_bytes": 0,
                "free_bytes": 0,
                "percent": 0.0,
            }
            network = network if not isinstance(network, Exception) else {
                "upload_speed": 0.0,
                "download_speed": 0.0,
            }
            stats = stats if not isinstance(stats, Exception) else {
                "movie_count": 0,
                "tv_count": 0,
                "episode_count": 0,
                "user_count": 0,
            }
            downloader = downloader if not isinstance(downloader, Exception) else {
                "download_speed": 0.0,
                "upload_speed": 0.0,
                "download_size": 0.0,
                "upload_size": 0.0,
                "free_space": 0.0,
            }
            tasks = tasks if not isinstance(tasks, Exception) else []
            transfer = transfer if not isinstance(transfer, Exception) else {
                "success": False,
                "message": None,
                "data": {},
            }

            # 统计任务状态
            running_tasks = 0
            pending_tasks = 0
            if isinstance(tasks, list):
                for task in tasks:
                    if isinstance(task, dict):
                        status = task.get("status", "")
                        if status == "运行中":
                            running_tasks += 1
                        elif status == "等待":
                            pending_tasks += 1

            # 检查是否有传输
            is_transferring = False
            if isinstance(transfer, dict) and transfer.get("data"):
                is_transferring = True

            # 检查是否在下载
            is_downloading = False
            if isinstance(downloader, dict) and downloader.get("download_speed", 0) > 0:
                is_downloading = True

            # 整合数据
            overview = {
                # 系统指标
                "cpu_percent": cpu,
                "memory_percent": memory.get("percent", 0.0),
                "memory_used_bytes": memory.get("used_bytes", 0),
                "disk_percent": storage.get("percent", 0.0),
                "disk_total_bytes": storage.get("total_bytes", 0),
                "disk_used_bytes": storage.get("used_bytes", 0),
                "disk_free_bytes": storage.get("free_bytes", 0),
                # 网络
                "network_upload_speed": network.get("upload_speed", 0.0),
                "network_download_speed": network.get("download_speed", 0.0),
                # 媒体库统计
                "movie_count": stats.get("movie_count", 0),
                "tv_count": stats.get("tv_count", 0),
                "episode_count": stats.get("episode_count", 0),
                "user_count": stats.get("user_count", 0),
                # 下载器
                "downloader_download_speed": downloader.get("download_speed", 0.0),
                "downloader_upload_speed": downloader.get("upload_speed", 0.0),
                "downloader_total_downloaded": downloader.get("download_size", 0.0),
                "downloader_total_uploaded": downloader.get("upload_size", 0.0),
                "downloader_free_space": downloader.get("free_space", 0.0),
                # 任务
                "running_tasks": running_tasks,
                "pending_tasks": pending_tasks,
                "tasks": tasks,
                # 状态
                "is_transferring": is_transferring,
                "is_downloading": is_downloading,
                "transfer_data": transfer.get("data", {}),
            }

            return overview

        except Exception as err:
            _LOGGER.error("获取Dashboard概览失败: %s", err)
            # 返回空数据而不是抛出异常
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "memory_used_bytes": 0,
                "disk_percent": 0.0,
                "disk_total_bytes": 0,
                "disk_used_bytes": 0,
                "disk_free_bytes": 0,
                "network_upload_speed": 0.0,
                "network_download_speed": 0.0,
                "movie_count": 0,
                "tv_count": 0,
                "episode_count": 0,
                "user_count": 0,
                "downloader_download_speed": 0.0,
                "downloader_upload_speed": 0.0,
                "downloader_total_downloaded": 0.0,
                "downloader_total_uploaded": 0.0,
                "downloader_free_space": 0.0,
                "running_tasks": 0,
                "pending_tasks": 0,
                "tasks": [],
                "is_transferring": False,
                "is_downloading": False,
                "transfer_data": {},
            }

    # ========== 系统信息 (兼容性方法) ==========

    async def get_system_info(self) -> dict[str, Any]:
        """获取系统信息 (用于配置流程)

        Returns:
            系统信息字典
        """
        try:
            stats = await self.get_statistics()
            return {
                "version": "moviepilot V2",
                "movie_count": stats.get("movie_count", 0),
                "tv_count": stats.get("tv_count", 0),
            }
        except Exception as err:
            _LOGGER.warning("获取系统信息失败: %s", err)
            return {"version": "unknown"}

    # ========== 通知服务 ==========

    async def send_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "Manual",
    ) -> bool:
        """发送通知到MoviePilot

        Args:
            title: 通知标题
            message: 通知内容
            notification_type: 通知类型 (默认: Manual)

        Returns:
            是否发送成功

        Raises:
            MoviePilotAPIError: 发送失败
        """
        data = {
            "title": title,
            "text": message,
            "type": notification_type,
        }

        try:
            result = await self._request("POST", API_ENDPOINT_MESSAGE, data=data)

            if isinstance(result, dict) and result.get("success"):
                _LOGGER.info("通知发送成功: %s", title)
                return True
            else:
                _LOGGER.warning("通知发送失败: %s", result)
                return False

        except Exception as err:
            _LOGGER.error("发送通知时出错: %s", err)
            raise
