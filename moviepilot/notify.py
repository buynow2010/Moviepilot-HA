"""MoviePilot notification service platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    BaseNotificationService,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .api import MoviePilotAPIClient
from .const import DATA_CLIENT, DOMAIN, NOTIFY_TYPE_MANUAL

_LOGGER = logging.getLogger(__name__)


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> MoviePilotNotificationService | None:
    """Get the MoviePilot notification service."""
    if discovery_info is None:
        return None

    entry_id = discovery_info.get("entry_id")
    if entry_id is None:
        _LOGGER.error("No entry_id provided for MoviePilot notify service")
        return None

    # Get client from hass.data
    client = hass.data[DOMAIN][entry_id][DATA_CLIENT]

    return MoviePilotNotificationService(hass, client, entry_id)


class MoviePilotNotificationService(BaseNotificationService):
    """Implement the notification service for MoviePilot."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MoviePilotAPIClient,
        entry_id: str,
    ) -> None:
        """Initialize the service."""
        self.hass = hass
        self.client = client
        self.entry_id = entry_id
        _LOGGER.info("MoviePilot notification service initialized for entry %s", entry_id)

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a notification to MoviePilot.

        Args:
            message: The notification message body
            **kwargs: Additional parameters
                - title: Notification title (default: "Home Assistant")
                - data: Additional data dictionary
                    - type: Notification type (default: "Manual")
        """
        # Get title from kwargs
        title = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)

        # Get additional data
        data = kwargs.get(ATTR_DATA) or {}
        notification_type = data.get("type", NOTIFY_TYPE_MANUAL)

        _LOGGER.debug(
            "Sending notification to MoviePilot: title='%s', type='%s', message_length=%d",
            title,
            notification_type,
            len(message),
        )

        try:
            success = await self.client.send_notification(
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
