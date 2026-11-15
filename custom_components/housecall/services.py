"""Built-in messaging services for HouseCall.

Each service talks to the messaging app directly, so nothing else has to be
installed. All of them are free:

- Telegram   (Telegram Bot API, with an "I'm on it" button)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

TELEGRAM = "telegram"
SERVICES = [TELEGRAM]

# Services that need a one-time setup for the whole house.
NEEDS_SETUP = [TELEGRAM]

HELP = "https://github.com/Degederon/HouseCall#"
HELP_LINKS = {
    TELEGRAM: HELP + "telegram",
}

ACK_CALLBACK = "hc_ack:"
TIMEOUT = aiohttp.ClientTimeout(total=20)


class SendError(Exception):
    """A message couldn't be delivered; the text says why, in plain words."""


# ---------------------------------------------------------------- Telegram


class Telegram:
    """Sends through a Telegram bot and listens for /start and button taps."""

    def __init__(self, hass: HomeAssistant, token: str) -> None:
        self.hass = hass
        self.token = (token or "").strip()
        self._task: asyncio.Task | None = None
        self._offset = 0
        self.on_ack: Callable[[str, int, str], Awaitable[None]] | None = None
        self.on_chat: Callable[[int, str], Awaitable[None]] | None = None

    @property
    def _url(self) -> str:
        return f"https://api.telegram.org/bot{self.token}/"

    async def _api(self, method: str, payload: dict[str, Any] | None = None, timeout: aiohttp.ClientTimeout = TIMEOUT) -> Any:
        session = async_get_clientsession(self.hass)
        try:
            async with session.post(self._url + method, json=payload or {}, timeout=timeout) as resp:
                data = await resp.json(content_type=None)
        except asyncio.TimeoutError as err:
            raise SendError("Telegram didn't answer in time") from err
        except aiohttp.ClientError as err:
            raise SendError(f"Couldn't reach Telegram: {err}") from err
        if not data.get("ok"):
            desc = data.get("description", "unknown error")
            if data.get("error_code") == 401:
                raise SendError("The bot token isn't right. Copy it again from BotFather.")
            if "chat not found" in desc.lower() or data.get("error_code") == 403:
                raise SendError("That person hasn't started a chat with your bot yet. They need to send /start to it.")
            raise SendError(f"Telegram said: {desc}")
        return data.get("result")

    async def check(self) -> str:
        """Returns the bot's @name, or raises SendError."""
        me = await self._api("getMe")
        return me.get("username", "")

    async def send(self, chat_id: int | str, text: str, ack_id: str | None = None) -> int | None:
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
        if ack_id:
            payload["reply_markup"] = {"inline_keyboard": [[{"text": "I'm on it", "callback_data": ACK_CALLBACK + ack_id}]]}
        result = await self._api("sendMessage", payload)
        return (result or {}).get("message_id")

    async def remove_button(self, chat_id: int | str, message_id: int, note: str) -> None:
        try:
            await self._api("editMessageReplyMarkup", {"chat_id": chat_id, "message_id": message_id, "reply_markup": {"inline_keyboard": []}})
            await self._api("sendMessage", {"chat_id": chat_id, "text": note, "reply_to_message_id": message_id})
        except SendError as err:
            _LOGGER.debug("HouseCall: couldn't tidy a Telegram alert: %s", err)

    # Listening ---------------------------------------------------------

    def start(self) -> None:
        if self.token and self._task is None:
            self._task = self.hass.async_create_background_task(self._listen(), "housecall_telegram")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None

    async def _listen(self) -> None:
        warned = False
        while True:
            try:
                updates = await self._api(
                    "getUpdates",
                    {"offset": self._offset, "timeout": 50, "allowed_updates": ["message", "callback_query"]},
                    timeout=aiohttp.ClientTimeout(total=70),
                )
                warned = False
                for upd in updates or []:
                    self._offset = max(self._offset, upd["update_id"] + 1)
                    await self._handle(upd)
                if not updates:
                    await asyncio.sleep(1)  # Telegram normally waits up to 50 s; never spin
            except asyncio.CancelledError:
                raise
            except SendError as err:
                if "terminated by other getUpdates" in str(err) or "Conflict" in str(err):
                    if not warned:
                        _LOGGER.warning(
                            "HouseCall: another program is reading this Telegram bot's messages, so the "
                            "'I'm on it' button and /start won't work. Give HouseCall a bot of its own."
                        )
                        warned = True
                    await asyncio.sleep(60)
                else:
                    await asyncio.sleep(10)
            except Exception:  # noqa: BLE001 - keep listening whatever happens
                _LOGGER.exception("HouseCall: Telegram listener error")
                await asyncio.sleep(10)

    async def _handle(self, upd: dict[str, Any]) -> None:
        if cq := upd.get("callback_query"):
            data = cq.get("data") or ""
            chat_id = (cq.get("message") or {}).get("chat", {}).get("id")
            who = (cq.get("from") or {}).get("first_name") or ""
            try:
                await self._api("answerCallbackQuery", {"callback_query_id": cq["id"], "text": "Got it. Everyone's been told."})
            except SendError:
                pass
            if data.startswith(ACK_CALLBACK) and self.on_ack:
                await self.on_ack(data[len(ACK_CALLBACK):], chat_id, who)
            return
        msg = upd.get("message") or {}
        chat = msg.get("chat") or {}
        if chat.get("id") is None:
            return
        name = chat.get("first_name") or chat.get("title") or chat.get("username") or str(chat["id"])
        if chat.get("last_name"):
            name = f"{name} {chat['last_name']}"
        if self.on_chat:
            await self.on_chat(chat["id"], name)
        if (msg.get("text") or "").startswith("/start"):
            try:
                await self._api(
                    "sendMessage",
                    {
                        "chat_id": chat["id"],
                        "text": f"Hi {chat.get('first_name') or ''}! This chat is now connected to HouseCall. "
                        "Ask whoever runs your Home Assistant to pick your name for Telegram in HouseCall.",
                    },
                )
            except SendError:
                pass
