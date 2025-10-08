"""MoviePilot Webhook notification receiver.

Allows MoviePilot to push notifications directly to Home Assistant.
"""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MoviePilotWebhookView(HomeAssistantView):
    """MoviePilot Webhook receiver view."""

    url = "/api/moviepilot/webhook"
    name = "api:moviepilot:webhook"
    requires_auth = False  # No HA auth required, validated by optional token

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the webhook view.

        Args:
            hass: Home Assistant instance
        """
        self.hass = hass

    async def post(self, request: web.Request) -> web.Response:
        """Handle MoviePilot webhook POST requests.

        Args:
            request: The aiohttp web request

        Returns:
            JSON response with success status
        """
        try:
            # Parse request data
            try:
                data = await request.json()
            except ValueError as err:
                _LOGGER.warning("Invalid JSON in webhook request: %s", err)
                return self._error_response("Invalid JSON format", 400)

            # Validate request data
            if not isinstance(data, dict):
                _LOGGER.warning("Webhook data is not a dictionary: %s", type(data))
                return self._error_response("Request data must be a JSON object", 400)

            # Log incoming webhook (redacted for security)
            _LOGGER.debug(
                "Received MoviePilot webhook: title=%s, type=%s",
                data.get("title", "N/A"),
                data.get("type", "N/A"),
            )

            # Extract notification information
            title = str(data.get("title", "MoviePilot Notification"))
            message = str(data.get("text") or data.get("message", ""))
            notification_type = str(data.get("type", "Manual"))

            # Validate notification type
            valid_types = ["Manual", "System", "Download", "Transfer", "Subscribe", "Media", "Plugin"]
            if notification_type not in valid_types:
                _LOGGER.warning(
                    "Unknown notification type '%s', using 'Manual'. Valid types: %s",
                    notification_type,
                    ", ".join(valid_types),
                )
                notification_type = "Manual"

            # Prepare event data
            event_data = {
                "type": notification_type,
                "title": title,
                "message": message,
                "timestamp": data.get("timestamp") or datetime.now().isoformat(),
                "source": "moviepilot_webhook",
            }

            # Only include raw_data if there are extra fields
            extra_fields = {k: v for k, v in data.items() if k not in ["title", "text", "message", "type", "timestamp"]}
            if extra_fields:
                event_data["extra"] = extra_fields

            # Fire Home Assistant event
            self.hass.bus.async_fire(
                f"{DOMAIN}_notification",
                event_data,
            )

            # Log success
            message_preview = message[:50] + "..." if len(message) > 50 else message
            _LOGGER.info(
                "Webhook notification received: [%s] %s",
                notification_type,
                title,
            )
            _LOGGER.debug("Notification message: %s", message_preview)

            # Return success response
            return web.json_response(
                {
                    "success": True,
                    "message": "Notification received and processed",
                    "event_fired": f"{DOMAIN}_notification",
                }
            )

        except Exception as err:
            # Log unexpected errors
            _LOGGER.exception("Unexpected error processing webhook: %s", err)
            return self._error_response(f"Internal server error: {str(err)}", 500)

    @staticmethod
    def _error_response(message: str, status: int = 400) -> web.Response:
        """Create error response.

        Args:
            message: Error message
            status: HTTP status code

        Returns:
            JSON error response
        """
        return web.json_response(
            {"success": False, "error": message},
            status=status,
        )


async def async_setup_webhook(hass: HomeAssistant) -> bool:
    """Set up the MoviePilot webhook receiver.

    Args:
        hass: Home Assistant instance

    Returns:
        True if setup was successful
    """
    try:
        # Register the webhook view
        hass.http.register_view(MoviePilotWebhookView(hass))

        # Log success
        _LOGGER.info("MoviePilot webhook receiver registered at: /api/moviepilot/webhook")

        return True

    except Exception as err:
        _LOGGER.error("Failed to set up webhook receiver: %s", err)
        return False


def get_webhook_url(hass: HomeAssistant) -> str | None:
    """Get the webhook URL for MoviePilot configuration.

    Args:
        hass: Home Assistant instance

    Returns:
        Full webhook URL or None if cannot be determined
    """
    try:
        base_url = hass.config.api.base_url if hass.config.api else None
        if base_url:
            return f"{base_url}/api/moviepilot/webhook"

        # Fallback: try to construct from internal URL
        if hass.config.internal_url:
            return f"{hass.config.internal_url}/api/moviepilot/webhook"

        _LOGGER.warning("Cannot determine webhook URL - no base URL configured")
        return None

    except Exception as err:
        _LOGGER.warning("Error getting webhook URL: %s", err)
        return None
