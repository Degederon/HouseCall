"""Constants for HouseCall."""

DOMAIN = "housecall"
VERSION = "0.1.1"

CONF_PEOPLE = "people"  # {person_entity_id: [notify service names, without "notify."]}
CONF_QUIET_START = "quiet_start"
CONF_QUIET_END = "quiet_end"
CONF_SPEAKERS = "speakers"
CONF_TTS = "tts_entity"
CONF_BOARD_SERVICE = "board_service"
CONF_GLASS_BOARD = "glass_board"
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
