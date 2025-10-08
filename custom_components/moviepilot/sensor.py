"""MoviePilot sensor platform."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfDataRate,
    UnitOfInformation,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import MoviePilotAPIClient
from .const import (
    ATTR_EPISODE_COUNT,
    ATTR_FREE_STORAGE,
    ATTR_MOVIE_COUNT,
    ATTR_RUNNING_TASKS,
    ATTR_TOTAL_DOWNLOADED,
    ATTR_TOTAL_STORAGE,
    ATTR_TV_COUNT,
    ATTR_USER_COUNT,
    ATTR_USED_STORAGE,
    BYTES_TO_GB,
    DATA_CLIENT,
    DOMAIN,
    ICON_CLOUD,
    ICON_CPU,
    ICON_DISK,
    ICON_DOWNLOAD,
    ICON_MEMORY,
    ICON_MOVIE,
    ICON_SERVER,
    ICON_TASK,
    ICON_TV,
    ICON_USER,
)

_LOGGER = logging.getLogger(__name__)

# 更新间隔
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MoviePilot sensors from a config entry."""
    # 获取已创建的coordinator（在__init__.py中创建）
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # 创建所有传感器（12个传感器：10个原有 + 2个消息通知）
    sensors: list[SensorEntity] = [
        # 系统监控传感器 (4个)
        MoviePilotCPUSensor(coordinator, entry),
        MoviePilotMemorySensor(coordinator, entry),
        MoviePilotDiskSensor(coordinator, entry),
        MoviePilotDiskFreeSensor(coordinator, entry),
        # 下载器传感器 (1个)
        MoviePilotDownloaderSpeedSensor(coordinator, entry),
        # 任务传感器 (1个)
        MoviePilotRunningTasksSensor(coordinator, entry),
        # 媒体统计传感器 (4个)
        MoviePilotMovieCountSensor(coordinator, entry),
        MoviePilotTVCountSensor(coordinator, entry),
        MoviePilotEpisodeCountSensor(coordinator, entry),
        MoviePilotUserCountSensor(coordinator, entry),
        # 消息通知传感器 (2个) - 监控状态变化并触发事件
        MoviePilotDownloadMessageSensor(coordinator, entry),
        MoviePilotTransferMessageSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class MoviePilotDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching MoviePilot data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MoviePilotAPIClient,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from MoviePilot API."""
        try:
            data = await self.client.get_dashboard_overview()
            _LOGGER.debug("更新MoviePilot数据成功: %d个指标", len(data))
            return data
        except Exception as err:
            _LOGGER.error("更新MoviePilot数据失败: %s", err)
            raise UpdateFailed(f"Error communicating with MoviePilot: {err}") from err


class MoviePilotSensorBase(CoordinatorEntity[MoviePilotDataUpdateCoordinator], SensorEntity):
    """Base class for MoviePilot sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MoviePilotDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "buynow",
            "model": "MoviePilot Server",
            "sw_version": "moviepilot V2",
        }


# ========== 系统监控传感器 ==========


class MoviePilotCPUSensor(MoviePilotSensorBase):
    """CPU usage sensor."""

    _attr_name = "CPU使用率"
    _attr_icon = ICON_CPU
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "cpu")

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("cpu_percent")


class MoviePilotMemorySensor(MoviePilotSensorBase):
    """Memory usage sensor."""

    _attr_name = "内存使用率"
    _attr_icon = ICON_MEMORY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "memory")

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("memory_percent")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        used_bytes = self.coordinator.data.get("memory_used_bytes", 0)
        return {
            "used_gb": round(used_bytes / BYTES_TO_GB, 2) if used_bytes else 0,
        }


class MoviePilotDiskSensor(MoviePilotSensorBase):
    """Disk usage sensor."""

    _attr_name = "磁盘使用率"
    _attr_icon = ICON_DISK
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "disk")

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("disk_percent")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            ATTR_TOTAL_STORAGE: round(
                self.coordinator.data.get("disk_total_bytes", 0) / BYTES_TO_GB, 2
            ),
            ATTR_USED_STORAGE: round(
                self.coordinator.data.get("disk_used_bytes", 0) / BYTES_TO_GB, 2
            ),
            ATTR_FREE_STORAGE: round(
                self.coordinator.data.get("disk_free_bytes", 0) / BYTES_TO_GB, 2
            ),
        }


class MoviePilotDiskFreeSensor(MoviePilotSensorBase):
    """Disk free space sensor."""

    _attr_name = "磁盘可用空间"
    _attr_icon = ICON_DISK
    _attr_native_unit_of_measurement = UnitOfInformation.GIGABYTES
    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "disk_free")

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        free_bytes = self.coordinator.data.get("disk_free_bytes")
        return round(free_bytes / BYTES_TO_GB, 2) if free_bytes else None


# ========== 下载器传感器 ==========


class MoviePilotDownloaderSpeedSensor(MoviePilotSensorBase):
    """Downloader download speed sensor."""

    _attr_name = "下载速度"
    _attr_icon = ICON_DOWNLOAD
    _attr_native_unit_of_measurement = UnitOfDataRate.BYTES_PER_SECOND
    _attr_device_class = SensorDeviceClass.DATA_RATE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "downloader_speed")

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("downloader_download_speed")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            ATTR_TOTAL_DOWNLOADED: round(
                self.coordinator.data.get("downloader_total_downloaded", 0) / BYTES_TO_GB, 2
            ),
        }


# ========== 任务传感器 ==========


class MoviePilotRunningTasksSensor(MoviePilotSensorBase):
    """Running tasks sensor."""

    _attr_name = "运行中任务"
    _attr_icon = ICON_TASK
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "running_tasks")

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        return self.coordinator.data.get("running_tasks")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        tasks = self.coordinator.data.get("tasks", [])
        running_task_names = [
            task.get("name") for task in tasks if task.get("status") == "运行中"
        ]
        return {
            "task_names": running_task_names,
        }


# ========== 媒体统计传感器 ==========


class MoviePilotMovieCountSensor(MoviePilotSensorBase):
    """Movie count sensor."""

    _attr_name = "电影数量"
    _attr_icon = ICON_MOVIE
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "movie_count")

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        return self.coordinator.data.get("movie_count")


class MoviePilotTVCountSensor(MoviePilotSensorBase):
    """TV show count sensor."""

    _attr_name = "剧集数量"
    _attr_icon = ICON_TV
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "tv_count")

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        return self.coordinator.data.get("tv_count")


class MoviePilotEpisodeCountSensor(MoviePilotSensorBase):
    """Episode count sensor."""

    _attr_name = "剧集集数"
    _attr_icon = ICON_TV
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "episode_count")

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        return self.coordinator.data.get("episode_count")


class MoviePilotUserCountSensor(MoviePilotSensorBase):
    """User count sensor."""

    _attr_name = "用户数量"
    _attr_icon = ICON_USER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MoviePilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "user_count")

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        return self.coordinator.data.get("user_count")


# ========== 消息通知传感器 ==========


class MoviePilotDownloadMessageSensor(MoviePilotSensorBase):
    """MoviePilot 下载消息传感器 - 监控下载状态变化并触发通知事件"""

    _attr_name = "下载通知"
    _attr_icon = ICON_DOWNLOAD

    def __init__(
        self,
        coordinator: MoviePilotDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "download_message")
        self._last_downloading = None

    @property
    def native_value(self) -> str:
        """Return the state."""
        is_downloading = self.coordinator.data.get("is_downloading", False)

        if is_downloading:
            return "下载中"
        elif self._last_downloading:
            return "下载完成"
        else:
            return "空闲"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "download_speed": self.coordinator.data.get("downloader_download_speed", 0),
            "total_downloaded": self.coordinator.data.get("downloader_total_downloaded", 0),
            "is_downloading": self.coordinator.data.get("is_downloading", False),
            "last_update": datetime.now().isoformat(),
        }

    async def async_update(self) -> None:
        """Update the entity."""
        await super().async_update()

        # 检查下载状态变化
        is_downloading = self.coordinator.data.get("is_downloading", False)

        # 下载开始
        if is_downloading and not self._last_downloading:
            download_speed = self.coordinator.data.get("downloader_download_speed", 0)
            self._fire_event(
                "Download",
                "📥 开始下载",
                f"下载速度: {self._format_speed(download_speed)}",
            )

        # 下载完成
        elif not is_downloading and self._last_downloading:
            total_downloaded = self.coordinator.data.get("downloader_total_downloaded", 0)
            self._fire_event(
                "Download",
                "✅ 下载完成",
                f"累计下载: {self._format_size(total_downloaded)}",
            )

        self._last_downloading = is_downloading

    def _fire_event(self, message_type: str, title: str, message: str) -> None:
        """触发 Home Assistant 事件"""
        self.hass.bus.async_fire(
            f"{DOMAIN}_notification",
            {
                "type": message_type,
                "title": title,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "source": "moviepilot",
            },
        )

        _LOGGER.info(
            "触发通知事件: [%s] %s - %s",
            message_type,
            title,
            message,
        )

    @staticmethod
    def _format_speed(bytes_per_sec: float) -> str:
        """格式化速度"""
        if bytes_per_sec >= 1024**3:
            return f"{bytes_per_sec / 1024**3:.2f} GB/s"
        elif bytes_per_sec >= 1024**2:
            return f"{bytes_per_sec / 1024**2:.2f} MB/s"
        elif bytes_per_sec >= 1024:
            return f"{bytes_per_sec / 1024:.2f} KB/s"
        else:
            return f"{bytes_per_sec:.0f} B/s"

    @staticmethod
    def _format_size(bytes_value: float) -> str:
        """格式化大小"""
        if bytes_value >= 1024**3:
            return f"{bytes_value / 1024**3:.2f} GB"
        elif bytes_value >= 1024**2:
            return f"{bytes_value / 1024**2:.2f} MB"
        elif bytes_value >= 1024:
            return f"{bytes_value / 1024:.2f} KB"
        else:
            return f"{bytes_value:.0f} B"


class MoviePilotTransferMessageSensor(MoviePilotSensorBase):
    """MoviePilot 整理消息传感器 - 监控整理状态变化并触发通知事件"""

    _attr_name = "整理通知"
    _attr_icon = ICON_CLOUD

    def __init__(
        self,
        coordinator: MoviePilotDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "transfer_message")
        self._last_transferring = None

    @property
    def native_value(self) -> str:
        """Return the state."""
        is_transferring = self.coordinator.data.get("is_transferring", False)

        if is_transferring:
            return "整理中"
        elif self._last_transferring:
            return "整理完成"
        else:
            return "空闲"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "is_transferring": self.coordinator.data.get("is_transferring", False),
            "transfer_data": self.coordinator.data.get("transfer_data", {}),
            "movie_count": self.coordinator.data.get("movie_count", 0),
            "tv_count": self.coordinator.data.get("tv_count", 0),
            "last_update": datetime.now().isoformat(),
        }

    async def async_update(self) -> None:
        """Update the entity."""
        await super().async_update()

        # 检查整理状态变化
        is_transferring = self.coordinator.data.get("is_transferring", False)

        # 整理开始
        if is_transferring and not self._last_transferring:
            self._fire_event(
                "Transfer",
                "📁 开始整理",
                "正在整理文件到媒体库...",
            )

        # 整理完成
        elif not is_transferring and self._last_transferring:
            movie_count = self.coordinator.data.get("movie_count", 0)
            tv_count = self.coordinator.data.get("tv_count", 0)
            self._fire_event(
                "Transfer",
                "✅ 整理完成",
                f"媒体库: 电影 {movie_count} 部, 剧集 {tv_count} 部",
            )

        self._last_transferring = is_transferring

    def _fire_event(self, message_type: str, title: str, message: str) -> None:
        """触发 Home Assistant 事件"""
        self.hass.bus.async_fire(
            f"{DOMAIN}_notification",
            {
                "type": message_type,
                "title": title,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "source": "moviepilot",
            },
        )

        _LOGGER.info(
            "触发通知事件: [%s] %s - %s",
            message_type,
            title,
            message,
        )
