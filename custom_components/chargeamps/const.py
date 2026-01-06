"""Constants for the Charge Amps integration."""

DOMAIN = "chargeamps"

# ---------------------------------------------------------------------
# Configuration keys
# ---------------------------------------------------------------------

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# ---------------------------------------------------------------------
# API
# ---------------------------------------------------------------------

API_BASE_URL = "https://eapi.charge.space/api/v5"

API_LOGIN_PATH = "/auth/login"
API_REFRESH_PATH = "/auth/refreshtoken"

API_CHARGEPOINTS_OWNED_PATH = "/chargepoints/owned"
API_CHARGEPOINT_PATH = "/chargepoints/{chargepoint_id}"

# ---------------------------------------------------------------------
# HTTP / Networking
# ---------------------------------------------------------------------

REQUEST_TIMEOUT = 10

# ---------------------------------------------------------------------
# Home Assistant
# ---------------------------------------------------------------------

PLATFORMS: list[str] = [
    "sensor",
    "switch",
    "number",
]

DEFAULT_SCAN_INTERVAL = 30  # seconds

# ---------------------------------------------------------------------
# Device / attributes (för senare användning)
# ---------------------------------------------------------------------

ATTR_CHARGEPOINT_ID = "chargepoint_id"
ATTR_CONNECTOR_ID = "connector_id"

# Vanliga statusvärden (bekräftas mot payload senare)
STATUS_CHARGING = "Charging"
STATUS_IDLE = "Idle"
STATUS_DISCONNECTED = "Disconnected"
STATUS_ERROR = "Error"
