"""Constants for the MoviePilot integration."""
from datetime import timedelta
from typing import Final

# Integration domain
DOMAIN: Final = "moviepilot"

# Configuration keys
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Default values
DEFAULT_NAME: Final = "MoviePilot"
DEFAULT_PORT: Final = 3000
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds
MIN_SCAN_INTERVAL: Final = 10  # seconds
MAX_SCAN_INTERVAL: Final = 300  # seconds (5 minutes)
DEFAULT_TIMEOUT: Final = 30  # seconds

# Update intervals for different data types
UPDATE_INTERVAL_DASHBOARD: Final = timedelta(seconds=30)  # System metrics

# API endpoints (all tested and verified)
API_ENDPOINT_MESSAGE: Final = "/api/v1/message/"
API_ENDPOINT_CPU: Final = "/api/v1/dashboard/cpu2"
API_ENDPOINT_MEMORY: Final = "/api/v1/dashboard/memory2"
API_ENDPOINT_STORAGE: Final = "/api/v1/dashboard/storage2"
API_ENDPOINT_NETWORK: Final = "/api/v1/dashboard/network2"
API_ENDPOINT_STATISTIC: Final = "/api/v1/dashboard/statistic2"
API_ENDPOINT_DOWNLOADER: Final = "/api/v1/dashboard/downloader2"
API_ENDPOINT_SCHEDULE: Final = "/api/v1/dashboard/schedule2"
API_ENDPOINT_TRANSFER_NOW: Final = "/api/v1/transfer/now"

# Sensor types (only used sensors)
SENSOR_TYPE_CPU: Final = "cpu"
SENSOR_TYPE_MEMORY: Final = "memory"
SENSOR_TYPE_DISK: Final = "disk"
SENSOR_TYPE_DISK_FREE: Final = "disk_free"
SENSOR_TYPE_DOWNLOADER_SPEED: Final = "downloader_speed"
SENSOR_TYPE_RUNNING_TASKS: Final = "running_tasks"

# Binary sensor types (only used sensors)
BINARY_SENSOR_TYPE_ONLINE: Final = "online"
BINARY_SENSOR_TYPE_TASKS_RUNNING: Final = "tasks_running"
BINARY_SENSOR_TYPE_DOWNLOADING: Final = "downloading"

# Sensor attributes (additional information)
ATTR_MOVIE_COUNT: Final = "movie_count"
ATTR_TV_COUNT: Final = "tv_count"
ATTR_EPISODE_COUNT: Final = "episode_count"
ATTR_USER_COUNT: Final = "user_count"
ATTR_TOTAL_STORAGE: Final = "total_storage"
ATTR_USED_STORAGE: Final = "used_storage"
ATTR_FREE_STORAGE: Final = "free_storage"
ATTR_TOTAL_DOWNLOADED: Final = "total_downloaded"
ATTR_RUNNING_TASKS: Final = "running_tasks"
ATTR_PENDING_TASKS: Final = "pending_tasks"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_API_VERSION: Final = "api_version"

# Icons (only used icons)
ICON_CPU: Final = "mdi:chip"
ICON_MEMORY: Final = "mdi:memory"
ICON_DISK: Final = "mdi:harddisk"
ICON_DOWNLOAD: Final = "mdi:download"
ICON_TASK: Final = "mdi:calendar-clock"
ICON_SERVER: Final = "mdi:server"
ICON_CLOUD: Final = "mdi:cloud"
ICON_MOVIE: Final = "mdi:movie"
ICON_TV: Final = "mdi:television"
ICON_USER: Final = "mdi:account-multiple"

# Device information
MANUFACTURER: Final = "MoviePilot"
MODEL: Final = "MoviePilot Server"
SW_VERSION: Final = "v2.0"

# Error messages
ERROR_AUTH_FAILED: Final = "Authentication failed. Please check your API token."
ERROR_CANNOT_CONNECT: Final = "Cannot connect to MoviePilot. Please check host and port."
ERROR_TIMEOUT: Final = "Connection timeout. MoviePilot may be unreachable."
ERROR_UNKNOWN: Final = "An unknown error occurred."

# Status values
STATUS_ONLINE: Final = "online"
STATUS_OFFLINE: Final = "offline"
STATUS_RUNNING: Final = "运行中"
STATUS_WAITING: Final = "等待"
STATUS_OK: Final = "OK"

# Data conversion constants
BYTES_TO_GB: Final = 1024 ** 3
BYTES_TO_MB: Final = 1024 ** 2
BYTES_TO_KB: Final = 1024

# Coordinator data keys
DATA_COORDINATOR: Final = "coordinator"
DATA_CLIENT: Final = "client"

# Platforms (notification service removed)
PLATFORMS: Final = ["sensor", "binary_sensor"]

# Notification defaults
NOTIFY_DEFAULT_TITLE: Final = "Home Assistant"
NOTIFY_TYPE_MANUAL: Final = "Manual"
NOTIFY_TYPE_SYSTEM: Final = "System"
NOTIFY_TYPE_DOWNLOAD: Final = "Download"
NOTIFY_TYPE_TRANSFER: Final = "Transfer"
