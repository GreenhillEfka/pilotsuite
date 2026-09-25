"""Supported Home Assistant WebSocket access through the Supervisor proxy."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout, WSMsgType


LOGGER = logging.getLogger(__name__)
StateCallback = Callable[[dict[str, Any]], Awaitable[None]]
EventCallback = Callable[[dict[str, Any]], Awaitable[None]]
MAX_WS_MESSAGE_BYTES = 32 * 1024 * 1024
STABLE_STREAM_SECONDS = 60


class HomeAssistantError(RuntimeError):
    """Raised when Home Assistant rejects or cannot serve a request."""


class HomeAssistantClient:
    def __init__(self, ws_url: str, token: str) -> None:
        self._ws_url = ws_url
        self._token = token
        self._session: ClientSession | None = None

    async def start(self) -> None:
        if self._session is None or self._session.closed:
            self._session = ClientSession(timeout=ClientTimeout(total=20))

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def snapshot(self) -> dict[str, Any]:
        """Load a consistent-enough current projection through supported WS APIs."""
        if not self._token:
            raise HomeAssistantError("SUPERVISOR_TOKEN is not available")
        await self.start()
        assert self._session is not None
        async with self._session.ws_connect(
            self._ws_url,
            heartbeat=30,
            max_msg_size=MAX_WS_MESSAGE_BYTES,
        ) as socket:
            await self._authenticate(socket)
            commands = (
                ("config", {"type": "get_config"}),
                ("areas", {"type": "config/area_registry/list"}),
                ("devices", {"type": "config/device_registry/list"}),
                ("entities", {"type": "config/entity_registry/list"}),
                ("states", {"type": "get_states"}),
            )
            result: dict[str, Any] = {}
            request_id = 1
            for key, command in commands:
                result[key] = await self._command(socket, request_id, command)
                request_id += 1
            return result

    async def history(self, entity_ids, start, end, *, statistics=False):
        """Bounded read-only requests; never opens the Recorder database."""
        from datetime import datetime, UTC
        if not entity_ids or len(entity_ids) > 100:
            raise HomeAssistantError("History requires 1–100 selected sources")
        await self.start()
        result = {entity: [] for entity in entity_ids}
        count = 0
        try:
            async with asyncio.timeout(90):
                async with self._session.ws_connect(self._ws_url, heartbeat=30,
                                                    max_msg_size=MAX_WS_MESSAGE_BYTES) as socket:
                    await self._authenticate(socket)
                    request_id, cursor = 1, start
                    metadata = {}
                    if statistics:
                        meta = await self._command(socket, request_id, {
                            'type': 'recorder/get_statistics_metadata', 'statistic_ids': entity_ids})
                        if not isinstance(meta, list):
                            raise HomeAssistantError('Unsupported statistics metadata response')
                        requested = set(entity_ids)
                        for item in meta:
                            statistic_id = item.get('statistic_id') if isinstance(item, dict) else None
                            if not isinstance(statistic_id, str) or not statistic_id:
                                raise HomeAssistantError('Unsupported statistics metadata response')
                            if statistic_id in requested:
                                metadata[statistic_id] = item
                        request_id += 1
                    while cursor < end:
                        stop = min(end, cursor + 86400)
                        command = {'type': 'history/history_during_period',
                                   'start_time': datetime.fromtimestamp(cursor, UTC).isoformat(),
                                   'end_time': datetime.fromtimestamp(stop, UTC).isoformat(),
                                   'entity_ids': entity_ids, 'include_start_time_state': True,
                                   'significant_changes_only': False, 'minimal_response': False,
                                   'no_attributes': False}
                        if statistics:
                            command = {'type': 'recorder/statistics_during_period',
                                       'start_time': command['start_time'], 'end_time': command['end_time'],
                                       'statistic_ids': entity_ids, 'period': 'hour',
                                       'types': ['mean', 'min', 'max']}
                        chunk = await self._command(socket, request_id, command)
                        if not isinstance(chunk, dict):
                            raise HomeAssistantError('Unsupported history response')
                        for entity in entity_ids:
                            rows = chunk.get(entity, [])
                            if not isinstance(rows, list):
                                raise HomeAssistantError('Unsupported history rows')
                            count += len(rows)
                            if count > 50000:
                                raise HomeAssistantError('History exceeds 50,000 records; choose a shorter period')
                            result[entity].extend(rows)
                        request_id += 1
                        cursor = stop
        except TimeoutError as exc:
            raise HomeAssistantError('Home Assistant history request timed out') from exc
        except ClientError as exc:
            raise HomeAssistantError('Home Assistant history connection failed') from exc
        return {'records': result, 'metadata': metadata}

    async def related_automations(self, entity_ids):
        """Explicit bounded reference lookup, never configuration or service calls."""
        import re
        if (not isinstance(entity_ids, list) or not 1 <= len(entity_ids) <= 40
                or any(not isinstance(e, str) or len(e) > 255
                       or not re.fullmatch(r'[a-z_]+\.[a-z0-9_]+', e) for e in entity_ids)):
            raise HomeAssistantError('Automation lookup requires 1–40 entity references')
        await self.start()
        results = {}
        seen_automations = set()
        try:
            async with asyncio.timeout(30):
                async with self._session.ws_connect(self._ws_url, heartbeat=30,
                                                    max_msg_size=1024*1024) as socket:
                    await self._authenticate(socket)
                    for request_id, entity in enumerate(sorted(set(entity_ids)), 1):
                        related = await self._command(socket, request_id, {
                            'type': 'search/related', 'item_type': 'entity', 'item_id': entity})
                        if not isinstance(related, dict):
                            raise HomeAssistantError('Invalid automation relation response')
                        automations = related.get('automation', [])
                        if (not isinstance(automations, list) or len(automations) > 200
                                or any(not isinstance(e, str) or len(e) > 255
                                       or not re.fullmatch(r'automation\.[a-z0-9_]+', e) for e in automations)):
                            raise HomeAssistantError('Invalid automation relation response')
                        results[entity] = sorted(set(automations))
                        seen_automations.update(automations)
                        if len(seen_automations) > 200:
                            raise HomeAssistantError('Automation lookup exceeds 200 related automations')
        except TimeoutError as exc:
            raise HomeAssistantError('Automation lookup timed out') from exc
        except ClientError as exc:
            raise HomeAssistantError('Automation lookup connection failed') from exc
        # Discard every partial result on failure; never imply a clean comparison.
        return results

    async def automation_config(self, entity_id):
        """Read one explicitly selected automation; never use the edit REST API."""
        import re
        if not isinstance(entity_id, str) or len(entity_id) > 255 or not re.fullmatch(r'automation\.[a-z0-9_]+', entity_id):
            raise HomeAssistantError('Invalid automation identity')
        await self.start()
        try:
            async with asyncio.timeout(20):
                async with self._session.ws_connect(self._ws_url, heartbeat=30,
                                                    max_msg_size=128*1024) as socket:
                    await self._authenticate(socket)
                    result = await self._command(socket, 1, {'type':'automation/config','entity_id':entity_id})
                    if not isinstance(result, dict) or not isinstance(result.get('config'), dict):
                        raise HomeAssistantError('Invalid automation configuration response')
                    return result['config']
        except (TimeoutError, ClientError, RecursionError) as exc:
            raise HomeAssistantError('Automation details unavailable') from exc

    async def helper_collection(self, helper_type):
        """Read only four supported storage collections; no generic command proxy."""
        from pilotsuite.core.helper_inspection import SIMPLE_HELPERS
        if helper_type not in SIMPLE_HELPERS:
            raise HomeAssistantError('Unsupported helper collection')
        await self.start()
        try:
            async with asyncio.timeout(20):
                async with self._session.ws_connect(self._ws_url, heartbeat=30,
                                                    max_msg_size=1024*1024) as socket:
                    await self._authenticate(socket)
                    rows = await self._command(socket, 1, {'type': helper_type + '/list'})
                    if (not isinstance(rows, list) or len(rows) > 2000 or
                            any(not isinstance(row, dict) or not isinstance(row.get('id'), str) for row in rows)):
                        raise HomeAssistantError('Invalid helper collection response')
                    return rows
        except (TimeoutError, ClientError, RecursionError) as exc:
            raise HomeAssistantError('Helper inspection unavailable') from exc

    async def helper_create_timer(self, *, key: str, name: str, duration: str, restore: bool):
        """Create exactly one timer through HA's supported storage collection API."""
        import re
        if (not re.fullmatch(r"pilotsuite_[a-z0-9_]{1,80}", key or "")
                or not isinstance(name, str) or not 1 <= len(name) <= 120
                or not re.fullmatch(r"\d{2}:\d{2}:\d{2}", duration or "")
                or type(restore) is not bool):
            raise HomeAssistantError("Invalid bounded timer create request")
        await self.start()
        try:
            async with asyncio.timeout(20):
                async with self._session.ws_connect(self._ws_url, heartbeat=30, max_msg_size=128*1024) as socket:
                    await self._authenticate(socket)
                    result = await self._command(socket, 1, {"type":"timer/create","name":name,"id":key,
                                                            "duration":duration,"restore":restore})
                    if not isinstance(result, dict) or result.get("id") != key:
                        raise HomeAssistantError("Timer create response did not confirm identity")
                    return result
        except TimeoutError as exc:
            raise HomeAssistantError("Timer create outcome unknown") from exc
        except ClientError as exc:
            raise HomeAssistantError("Timer create connection failed") from exc

    async def helper_delete_timer(self, key: str):
        """Rollback only a transaction-owned timer identity selected by the caller."""
        import re
        if not re.fullmatch(r"pilotsuite_[a-z0-9_]{1,80}", key or ""):
            raise HomeAssistantError("Invalid bounded timer delete request")
        await self.start()
        try:
            async with asyncio.timeout(20):
                async with self._session.ws_connect(self._ws_url, heartbeat=30, max_msg_size=128*1024) as socket:
                    await self._authenticate(socket)
                    return await self._command(socket, 1, {"type":"timer/delete","timer_id":key})
        except (TimeoutError, ClientError) as exc:
            raise HomeAssistantError("Timer rollback outcome unknown") from exc

    async def listen(
        self, callback: StateCallback, stop_event: asyncio.Event,
        connection_callback: Callable[[bool], Awaitable[None]] | None = None,
        service_callback: EventCallback | None = None,
    ) -> None:
        """Subscribe to state/service events and reconnect with bounded backoff."""
        if not self._token:
            await stop_event.wait()
            return
        delay = 1
        while not stop_event.is_set():
            stream_started: float | None = None
            try:
                await self.start()
                assert self._session is not None
                async with self._session.ws_connect(
                    self._ws_url,
                    heartbeat=30,
                    max_msg_size=MAX_WS_MESSAGE_BYTES,
                ) as socket:
                    await self._authenticate(socket)
                    subscriptions = {1: "state_changed"}
                    if service_callback is not None:
                        subscriptions[2] = "call_service"
                    for request_id, event_type in subscriptions.items():
                        await socket.send_json(
                            {
                                "id": request_id,
                                "type": "subscribe_events",
                                "event_type": event_type,
                            }
                        )
                    confirmed: set[int] = set()
                    while confirmed != set(subscriptions):
                        subscribed = await self._receive_json(socket)
                        if subscribed.get("type") == "event":
                            await self._dispatch_event(
                                subscribed, callback, service_callback
                            )
                            continue
                        request_id = subscribed.get("id")
                        if request_id not in subscriptions:
                            continue
                        if not subscribed.get("success"):
                            raise HomeAssistantError(
                                f"{subscriptions[request_id]} subscription rejected"
                            )
                        confirmed.add(request_id)
                    if connection_callback:
                        await connection_callback(True)
                    stream_started = monotonic()
                    async for message in socket:
                        if stop_event.is_set():
                            break
                        if message.type is WSMsgType.TEXT:
                            payload = json.loads(message.data)
                            if payload.get("type") == "event":
                                await self._dispatch_event(
                                    payload, callback, service_callback
                                )
                        elif message.type in {
                            WSMsgType.CLOSED,
                            WSMsgType.CLOSE,
                            WSMsgType.ERROR,
                        }:
                            break
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # reconnect boundary
                LOGGER.warning("Home Assistant event stream disconnected: %s", exc)
            finally:
                # Authentication alone does not make a stream stable. Quiet homes
                # recover too: resetting the backoff must not require state events.
                if (
                    stream_started is not None
                    and monotonic() - stream_started >= STABLE_STREAM_SECONDS
                ):
                    delay = 1
                if connection_callback:
                    await connection_callback(False)
            # A graceful remote close must back off too.
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=delay)
            except TimeoutError:
                pass
            delay = min(delay * 2, 30)

    @staticmethod
    async def _dispatch_event(
        payload: dict[str, Any],
        state_callback: StateCallback,
        service_callback: EventCallback | None,
    ) -> None:
        event = payload.get("event", {})
        if not isinstance(event, dict):
            return
        event_type = event.get("event_type")
        if event_type == "call_service" or payload.get("id") == 2:
            if service_callback is not None:
                await service_callback(event)
        elif event_type == "state_changed" or payload.get("id") == 1:
            data = event.get("data", {})
            if isinstance(data, dict):
                await state_callback(data)

    async def _authenticate(self, socket: Any) -> None:
        hello = await self._receive_json(socket)
        if hello.get("type") != "auth_required":
            raise HomeAssistantError("unexpected Home Assistant auth greeting")
        await socket.send_json({"type": "auth", "access_token": self._token})
        response = await self._receive_json(socket)
        if response.get("type") != "auth_ok":
            raise HomeAssistantError("Home Assistant authentication failed")

    async def _command(
        self, socket: Any, request_id: int, command: dict[str, Any]
    ) -> Any:
        await socket.send_json({"id": request_id, **command})
        while True:
            response = await self._receive_json(socket)
            if response.get("id") != request_id:
                continue
            if not response.get("success"):
                error = response.get("error", {})
                code = error.get("code", "unknown") if isinstance(error, dict) else "unknown"
                raise HomeAssistantError(f"Home Assistant command failed: {code}")
            return response.get("result")

    @staticmethod
    async def _receive_json(socket: Any) -> dict[str, Any]:
        message = await socket.receive(timeout=20)
        if message.type is not WSMsgType.TEXT:
            detail = str(message.data or "").strip()
            if not detail and hasattr(socket, "exception"):
                detail = str(socket.exception() or "").strip()
            suffix = f": {detail}" if detail else ""
            raise HomeAssistantError(
                f"Home Assistant WebSocket returned {message.type.name}{suffix}"
            )
        try:
            value = json.loads(message.data)
        except (json.JSONDecodeError, TypeError) as exc:
            raise HomeAssistantError("invalid Home Assistant WebSocket response") from exc
        if not isinstance(value, dict):
            raise HomeAssistantError("invalid Home Assistant WebSocket response")
        return value
