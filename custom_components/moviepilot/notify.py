"""MoviePilot notification platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.notify import NotifyEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MoviePilotAPIClient
from .const import DATA_CLIENT, DOMAIN, ICON_SERVER, NOTIFY_TYPE_MANUAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MoviePilot notify entity from a config entry."""
    client: MoviePilotAPIClient = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]

    async_add_entities([MoviePilotNotifyEntity(client, entry)])

    _LOGGER.info("MoviePilot notify entity added for entry %s", entry.entry_id)


class MoviePilotNotifyEntity(NotifyEntity):
    """MoviePilot notify entity."""

    _attr_has_entity_name = True
    _attr_name = "通知"
    _attr_icon = ICON_SERVER

    def __init__(
        self,
        client: MoviePilotAPIClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the notify entity."""
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_notify"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "buynow2010",
            "model": "MoviePilot Server",
            "sw_version": "moviepilot V2",
        }

        _LOGGER.debug("MoviePilot notify entity initialized: %s", self._attr_unique_id)

    async def async_send_message(self, message: str, title: str | None = None, **kwargs: Any) -> None:
        """Send a notification to MoviePilot.

        Args:
            message: The notification message body
            title: The notification title (default: "Home Assistant")
            **kwargs: Additional parameters
                - data: Additional data dictionary
                    - type: Notification type (default: "Manual")
        """
        # Get notification title
        if title is None:
            title = "Home Assistant"

        # Get notification type from data
        data = kwargs.get("data") or {}
        notification_type = data.get("type", NOTIFY_TYPE_MANUAL)

        _LOGGER.debug(
            "Sending notification to MoviePilot: title='%s', type='%s', message_length=%d",
            title,
            notification_type,
            len(message),
        )

        try:
            success = await self._client.send_notification(
                title=title,
                message=message,
                notification_type=notification_type,
            )

            if success:
                _LOGGER.info("Successfully sent notification to MoviePilot: %s", title)
            else:
                _LOGGER.warning("Failed to send notification to MoviePilot: %s", title)

        except Exception as err:
            _LOGGER.error("Error sending notification to MoviePilot: %s", err)
            raise
