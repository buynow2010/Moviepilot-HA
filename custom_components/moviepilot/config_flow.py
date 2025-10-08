"""Config flow for MoviePilot integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_TOKEN, CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MoviePilotAPIClient
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# Validation schema with better defaults and constraints
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
        vol.Required(CONF_API_TOKEN): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    client = MoviePilotAPIClient(
        data[CONF_HOST],
        data[CONF_PORT],
        data[CONF_API_TOKEN],
        session,
        verify_ssl=False,  # MoviePilot 通常使用自签名证书
    )

    # Test connection with API token
    try:
        # Test connection
        await client.test_connection()

        # Get system info for version
        system_info = await client.get_system_info()
        version = system_info.get("version", "unknown")

        return {
            "title": f"{data[CONF_NAME]} ({version})",
            "version": version,
        }

    except aiohttp.ClientResponseError as err:
        if err.status == 401:
            raise InvalidAuth from err
        elif err.status == 404:
            raise CannotConnect("API endpoint not found. Please check MoviePilot version.") from err
        else:
            raise CannotConnect(f"HTTP {err.status}: {err.message}") from err

    except aiohttp.ClientConnectorError as err:
        raise CannotConnect(f"Connection failed: {err}") from err

    except asyncio.TimeoutError as err:
        raise CannotConnect("Connection timeout. Please check host and port.") from err

    except Exception as err:
        _LOGGER.exception("Unexpected exception")
        raise CannotConnect(f"Unexpected error: {err}") from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MoviePilot."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if already configured with same host
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)

                # Create entry with additional info
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                    options={
                        "version": info["version"],
                    }
                )

            except CannotConnect as err:
                errors["base"] = "cannot_connect"
                _LOGGER.error("Cannot connect: %s", err)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
                _LOGGER.error("Invalid authentication")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form with errors if any
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "default_port": str(DEFAULT_PORT),
            },
        )

    async def async_step_reauth(self, user_input: dict[str, Any]) -> FlowResult:
        """Handle reauth flow."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reauth confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Use existing host and port, update API token
            data = {
                CONF_HOST: self._reauth_entry.data[CONF_HOST],
                CONF_PORT: self._reauth_entry.data[CONF_PORT],
                CONF_API_TOKEN: user_input[CONF_API_TOKEN],
                CONF_NAME: self._reauth_entry.data.get(CONF_NAME, DEFAULT_NAME),
            }

            try:
                info = await validate_input(self.hass, data)

                # Update the existing entry
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data=data,
                    options={
                        "version": info["version"],
                    }
                )

                # Reload the entry
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)

                return self.async_abort(reason="reauth_successful")

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_TOKEN): str}),
            errors=errors,
            description_placeholders={
                "host": self._reauth_entry.data[CONF_HOST],
                "port": str(self._reauth_entry.data[CONF_PORT]),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return MoviePilotOptionsFlowHandler(config_entry)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

    def __init__(self, message: str = "Cannot connect") -> None:
        """Initialize error."""
        super().__init__()
        self.message = message


class MoviePilotOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle MoviePilot options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the MoviePilot options."""
        if user_input is not None:
            interval = max(
                MIN_SCAN_INTERVAL,
                min(MAX_SCAN_INTERVAL, user_input[CONF_SCAN_INTERVAL]),
            )
            return self.async_create_entry(
                title="",
                data={CONF_SCAN_INTERVAL: interval},
            )

        current = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)

    def __str__(self) -> str:
        """Return error message."""
        return self.message


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
