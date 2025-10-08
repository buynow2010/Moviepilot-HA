"""The MoviePilot integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN, CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MoviePilotAPIClient, MoviePilotAuthError, MoviePilotConnectionError
from .const import DATA_CLIENT, DOMAIN
from .sensor import MoviePilotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Platforms to set up
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NOTIFY,
]

# Service schema
SERVICE_SEND_NOTIFICATION_SCHEMA = vol.Schema(
    {
        vol.Required("title"): cv.string,
        vol.Required("message"): cv.string,
        vol.Optional("type", default="Manual"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MoviePilot from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass, verify_ssl=False)

    api_token = entry.data.get(CONF_API_TOKEN, "")

    _LOGGER.info("设置 MoviePilot 集成: %s:%s", entry.data[CONF_HOST], entry.data[CONF_PORT])

    client = MoviePilotAPIClient(
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        api_token,
        session,
        verify_ssl=False,
    )

    try:
        _LOGGER.info("验证连接到 MoviePilot...")
        result = await client.test_connection()
        _LOGGER.info("成功连接到 MoviePilot: %s", result.get("name", "unknown"))
    except MoviePilotAuthError as err:
        _LOGGER.error("MoviePilot认证失败: %s", err)
        raise ConfigEntryNotReady(f"Authentication failed: {err}") from err
    except MoviePilotConnectionError as err:
        _LOGGER.error("无法连接到 MoviePilot: %s", err)
        raise ConfigEntryNotReady(f"Cannot connect: {err}") from err
    except Exception as err:
        _LOGGER.error("连接MoviePilot时出现未知错误: %s", err)
        raise ConfigEntryNotReady(f"Unknown error: {err}") from err

    # 创建coordinator
    coordinator = MoviePilotDataUpdateCoordinator(hass, client)

    # 首次刷新数据
    await coordinator.async_config_entry_first_refresh()

    # 保存到hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_CLIENT: client,
        "coordinator": coordinator,
    }

    # 设置平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # 注册服务
    async def handle_send_notification(call: ServiceCall) -> None:
        """Handle send notification service call."""
        title = call.data.get("title")
        message = call.data.get("message")
        notification_type = call.data.get("type", "Manual")

        try:
            success = await client.send_notification(title, message, notification_type)
            if success:
                _LOGGER.info("通知发送成功: %s", title)
            else:
                _LOGGER.warning("通知发送失败: %s", title)
        except Exception as err:
            _LOGGER.error("发送通知时出错: %s", err)

    # 只在第一个实例时注册服务
    if not hass.services.has_service(DOMAIN, "send_notification"):
        hass.services.async_register(
            DOMAIN,
            "send_notification",
            handle_send_notification,
            schema=SERVICE_SEND_NOTIFICATION_SCHEMA,
        )
        _LOGGER.info("已注册 moviepilot.send_notification 服务")

    # 监听配置更新
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("MoviePilot集成设置完成")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # 卸载所有平台
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # 如果没有其他实例，移除服务
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "send_notification")
            _LOGGER.info("已移除 moviepilot.send_notification 服务")

        _LOGGER.info("MoviePilot集成已卸载")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

