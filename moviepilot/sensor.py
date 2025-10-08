"""MoviePilot sensor platform."""
from __future__ import annotations

from datetime import timedelta
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
    client: MoviePilotAPIClient = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]

    # 创建coordinator
    coordinator = MoviePilotDataUpdateCoordinator(hass, client)

    # 首次刷新数据
    await coordinator.async_config_entry_first_refresh()

    # 创建所有传感器（10个传感器）
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
    _attr_entity_category = EntityCategory.DIAGNOSTIC

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
    _attr_entity_category = EntityCategory.DIAGNOSTIC

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

