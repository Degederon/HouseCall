"""Constants for HouseCall."""

DOMAIN = "housecall"
VERSION = "2.1.0"

CONF_MEMBERS = "members"  # options-screen field only
CONF_PEOPLE = "people"
CONF_CUSTOM_PEOPLE = "custom_people"
CONF_CHANNELS = "channels"  # {person_id: {"routes": ["notify.x", ...], "address": "+1555..."}}
CONF_CHANNEL_MODE = "channel_mode"
CONF_SERVICES = "services"  # {"enabled": [...], "telegram": {...}, "ntfy": {...}, "email": {...}, "chat": {...}}
CONF_PERSON_SERVICES = "person_services"  # {person_id: {"telegram": chat_id, "ntfy": topic, ...}}
CHANNEL_NEVER = "never"
CHANNEL_NO_APP = "no_app"
CHANNEL_CRITICAL = "critical"
CHANNEL_ALL = "all"
CHANNEL_MODES = [CHANNEL_CRITICAL, CHANNEL_ALL, CHANNEL_NO_APP, CHANNEL_NEVER]
DEFAULT_CHANNEL_MODE = CHANNEL_CRITICAL
TEST_ALL = "all"
TEST_APP = "app"
TEST_MESSAGING = "messaging"  # {id: {name, services, presence}}
CUSTOM_PREFIX = "housecall."  # {person_entity_id: [notify service names, without "notify."]}
CONF_QUIET_START = "quiet_start"
CONF_QUIET_END = "quiet_end"
CONF_SPEAKERS = "speakers"
CONF_TTS = "tts_entity"
CONF_BOARD_SERVICE = "board_service"
CONF_GLASS_BOARD = "glass_board"
CONF_OPEN_DASHBOARD = "open_dashboard"  # path opened when a notification is tapped
STARTER_DASHBOARD = "dashboard-housecall"
CONF_REPEAT_MINUTES = "repeat_minutes"
CONF_MAX_REPEATS = "max_repeats"

DEFAULT_QUIET_START = "22:00:00"
DEFAULT_QUIET_END = "07:00:00"
DEFAULT_REPEAT_MINUTES = 5
DEFAULT_MAX_REPEATS = 6

PRIORITY_INFO = "info"
PRIORITY_NORMAL = "normal"
PRIORITY_CRITICAL = "critical"
PRIORITIES = [PRIORITY_INFO, PRIORITY_NORMAL, PRIORITY_CRITICAL]

STATUS_SENT = "sent"
STATUS_HELD = "held"          # normal message waiting for quiet hours to end
STATUS_WAITING = "waiting"    # critical message waiting for someone to tap "I'm on it"
STATUS_ACKED = "acknowledged"
STATUS_EXPIRED = "unanswered"

EVERYONE = ("everyone", "all", "family")

ACK_PREFIX = "HOUSECALL_ACK_"
SIGNAL_UPDATE = f"{DOMAIN}_update"
EVENT_UPDATED = f"{DOMAIN}_updated"
EVENT_ACKNOWLEDGED = f"{DOMAIN}_acknowledged"

HISTORY_LIMIT = 100
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.history"

CARD_FILENAME = "housecall-card.js"
CARD_URL = f"/{DOMAIN}/{CARD_FILENAME}"
