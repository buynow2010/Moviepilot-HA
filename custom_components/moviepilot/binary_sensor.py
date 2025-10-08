"""MoviePilot binary sensor platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ICON_CLOUD,
    ICON_DOWNLOAD,
    ICON_TASK,
)
from .sensor import MoviePilotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MoviePilot binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors: list[BinarySensorEntity] = [
        MoviePilotOnlineSensor(coordinator, entry),
        MoviePilotTasksRunningSensor(coordinator, entry),
        MoviePilotDownloadingSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class MoviePilotBinarySensorBase(
    CoordinatorEntity[MoviePilotDataUpdateCoordinator], BinarySensorEntity
):
    """Base class for MoviePilot binary sensors."""

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


class MoviePilotOnlineSensor(MoviePilotBinarySensorBase):
    """MoviePilot online status sensor."""

    _attr_name = "在线状态"
    _attr_icon = ICON_CLOUD
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: MoviePilotDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "online")

    @property
    def is_on(self) -> bool:
        """Return True if MoviePilot is online."""
        return self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True  # 始终可用以显示离线状态


class MoviePilotTasksRunningSensor(MoviePilotBinarySensorBase):
    """Tasks running sensor."""

    _attr_name = "有任务运行"
    _attr_icon = ICON_TASK
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: MoviePilotDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "tasks_running")

    @property
    def is_on(self) -> bool:
        """Return True if tasks are running."""
        running_tasks = self.coordinator.data.get("running_tasks", 0)
        return running_tasks > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "running_count": self.coordinator.data.get("running_tasks", 0),
            "pending_count": self.coordinator.data.get("pending_tasks", 0),
        }


class MoviePilotDownloadingSensor(MoviePilotBinarySensorBase):
    """Downloading status sensor."""

    _attr_name = "下载中"
    _attr_icon = ICON_DOWNLOAD
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: MoviePilotDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "downloading")

    @property
    def is_on(self) -> bool:
        """Return True if downloading."""
        return self.coordinator.data.get("is_downloading", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "download_speed": self.coordinator.data.get("downloader_download_speed", 0),
            "upload_speed": self.coordinator.data.get("downloader_upload_speed", 0),
        }
