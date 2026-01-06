from __future__ import annotations

import asyncio
import logging
from typing import Any

import async_timeout
from aiohttp import ClientSession, ClientResponseError

from .const import (
    API_BASE_URL,
    API_LOGIN_PATH,
    API_REFRESH_PATH,
    API_CHARGEPOINTS_OWNED_PATH,
    API_CHARGEPOINT_PATH,
    REQUEST_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class ChargeAmpsApiError(Exception):
    """Base exception for Charge Amps API errors."""


class ChargeAmpsAuthError(ChargeAmpsApiError):
    """Authentication failed."""


class ChargeAmpsApi:
    def __init__(
        self,
        session: ClientSession,
        email: str,
        password: str,
    ) -> None:
        self._session = session
        self._email = email
        self._password = password

        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._auth_lock = asyncio.Lock()

    # ---------------------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------------------

    async def _login(self) -> None:
        _LOGGER.debug("Charge Amps: logging in")
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                resp = await self._session.post(
                    f"{API_BASE_URL}{API_LOGIN_PATH}",
                    json={"email": self._email, "password": self._password},
                )
                resp.raise_for_status()
                data = await resp.json()
        except ClientResponseError as err:
            raise ChargeAmpsAuthError(f"Login failed ({err.status})") from err
        except Exception as err:
            raise ChargeAmpsAuthError("Login request failed") from err

        self._access_token = data["token"]
        self._refresh_token = data.get("refreshToken")
        _LOGGER.debug("Charge Amps: login successful")

    async def _refresh(self) -> None:
        if not self._refresh_token:
            await self._login()
            return
        _LOGGER.debug("Charge Amps: refreshing token")
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                resp = await self._session.post(
                    f"{API_BASE_URL}{API_REFRESH_PATH}",
                    json={"refreshToken": self._refresh_token},
                )
                resp.raise_for_status()
                data = await resp.json()
        except ClientResponseError:
            _LOGGER.warning("Charge Amps: refresh failed, re-authenticating")
            await self._login()
            return
        except Exception as err:
            raise ChargeAmpsAuthError("Token refresh failed") from err

        self._access_token = data["token"]
        self._refresh_token = data.get("refreshToken", self._refresh_token)
        _LOGGER.debug("Charge Amps: token refreshed")

    async def _headers(self) -> dict[str, str]:
        async with self._auth_lock:
            if not self._access_token:
                await self._login()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    # ---------------------------------------------------------------------
    # Generic request helper
    # ---------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        retry: bool = True,
    ) -> Any:
        url = f"{API_BASE_URL}{path}"
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                resp = await self._session.request(
                    method, url, headers=await self._headers(), json=json, params=params
                )
                if resp.status == 401 and retry:
                    _LOGGER.debug("Charge Amps: 401 received, refreshing token")
                    async with self._auth_lock:
                        await self._refresh()
                    return await self._request(method, path, json=json, params=params, retry=False)
                resp.raise_for_status()
                return await resp.json()
        except ClientResponseError as err:
            _LOGGER.error("Charge Amps API error %s on %s %s", err.status, method, path)
            raise ChargeAmpsApiError(err) from err
        except Exception as err:
            raise ChargeAmpsApiError("Request failed") from err

    # ---------------------------------------------------------------------
    # Public GET endpoints
    # ---------------------------------------------------------------------

    async def get_chargepoints(self) -> list[dict[str, Any]]:
        return await self._request("GET", API_CHARGEPOINTS_OWNED_PATH)

    async def get_chargepoint(self, chargepoint_id: str) -> dict[str, Any]:
        return await self._request("GET", API_CHARGEPOINT_PATH.format(chargepoint_id=chargepoint_id))

    # ---------------------------------------------------------------------
    # Public PUT endpoints (styrning)
    # ---------------------------------------------------------------------

    async def set_connector_mode(
        self, chargepoint_id: str, connector_id: int, mode: str
    ) -> dict[str, Any]:
        """Set mode of a connector (Off, Charging, etc)."""
        path = f"/chargepoints/{chargepoint_id}/connectors/{connector_id}/settings"
        payload = {"mode": mode}
        return await self._request("PUT", path, json=payload)

    async def set_connector_max_current(
        self, chargepoint_id: str, connector_id: int, max_current: int
    ) -> dict[str, Any]:
        """Set max current on a connector."""
        path = f"/chargepoints/{chargepoint_id}/connectors/{connector_id}/settings"
        payload = {"maxCurrent": max_current}
        return await self._request("PUT", path, json=payload)
