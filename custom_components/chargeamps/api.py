"""ChargeAmps API Client"""
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

import jwt
from aiohttp import ClientResponse, ClientSession
from aiohttp.web import HTTPException
from dataclasses_json import LetterCase, dataclass_json

from .const import DOMAIN

API_BASE_URL = "https://eapi.charge.space"
API_VERSION = "v5"

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnector:
    charge_point_id: str
    connector_id: int
    type: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePoint:
    id: str
    name: str
    password: str
    type: str
    is_loadbalanced: bool
    firmware_version: str | None
    hardware_version: str | None
    connectors: list[ChargePointConnector]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointMeasurement:
    phase: str
    current: float
    voltage: float

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnectorStatus:
    charge_point_id: str
    connector_id: int
    total_consumption_kwh: float
    status: str
    measurements: list[ChargePointMeasurement] | None
    start_time: datetime | None = None
    end_time: datetime | None = None
    session_id: str | None = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointStatus:
    id: str
    status: str
    connector_statuses: list[ChargePointConnectorStatus]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=False)
class ChargePointSettings:
    id: str
    dimmer: str
    down_light: bool | None = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=False)
class ChargePointConnectorSettings:
    charge_point_id: str
    connector_id: int
    mode: str
    rfid_lock: bool
    cable_lock: bool
    max_current: float | None = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargingSession:
    id: str
    charge_point_id: str
    connector_id: int
    session_type: str
    total_consumption_kwh: float
    start_time: datetime | None = None
    end_time: datetime | None = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StartAuth:
    rfid_length: int
    rfid_format: str
    rfid: str
    external_transaction_id: str

class ChargeAmpsClient:
    def __init__(self, email: str, password: str, api_key: str, api_base_url: str | None = None):
        self._logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self._email = email
        self._password = password
        self._api_key = api_key
        self._session = ClientSession(raise_for_status=True)
        self._headers = {}
        self._base_url = api_base_url or API_BASE_URL
        self._ssl = False
        self._token = None
        self._token_expire = 0
        self._refresh_token = None

    async def shutdown(self) -> None:
        await self._session.close()

    async def _ensure_token(self) -> None:
        if self._token_expire > time.time():
            return
        self._logger.info("Refreshing token or logging in…")
        # Här kommer login/refresh logik