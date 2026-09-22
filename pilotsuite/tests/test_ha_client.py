from __future__ import annotations

import unittest
import json
import asyncio
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

from aiohttp import WSMsgType

from pilotsuite.ha.client import (
    MAX_WS_MESSAGE_BYTES,
    HomeAssistantClient,
    HomeAssistantError,
)


class _Socket:
    def __init__(self, messages: list[dict[str, object]]) -> None:
        self.messages = messages
        self.sent: list[dict[str, object]] = []

    async def receive(self, timeout: int) -> SimpleNamespace:
        del timeout
        return SimpleNamespace(
            type=WSMsgType.TEXT,
            data=json.dumps(self.messages.pop(0)),
        )

    async def send_json(self, payload: dict[str, object]) -> None:
        self.sent.append(payload)


class _Connection:
    def __init__(self, socket: _Socket) -> None:
        self.socket = socket

    async def __aenter__(self) -> _Socket:
        return self.socket

    async def __aexit__(self, *_: object) -> None:
        return None


class _Session:
    closed = False

    def __init__(self, socket: _Socket) -> None:
        self.socket = socket
        self.kwargs: dict[str, object] = {}

    def ws_connect(self, url: str, **kwargs: object) -> _Connection:
        self.kwargs = {"url": url, **kwargs}
        return _Connection(self.socket)


class HomeAssistantClientTests(unittest.IsolatedAsyncioTestCase):
    async def _reconnect_delays(self, durations, *, authenticated=True):
        """Drive synthetic connections and a fake clock without real waiting."""
        clock = [0.0]
        remaining = iter(durations)

        class ClosingSocket(_Socket):
            def __aiter__(self):
                return self

            async def __anext__(self):
                clock[0] += next(remaining)
                raise StopAsyncIteration

        responses = [
            {"type": "auth_required"},
            {"type": "auth_ok" if authenticated else "auth_invalid"},
        ]
        if authenticated:
            responses.append({"id": 1, "success": True})
        socket = ClosingSocket(responses * len(durations))
        client = HomeAssistantClient(
            "ws://example.invalid/websocket", "synthetic-token"
        )
        client._session = _Session(socket)
        stop = asyncio.Event()
        connection = AsyncMock()
        delays = []

        async def wait(awaitable, timeout):
            delays.append(timeout)
            if len(delays) == len(durations):
                stop.set()
                return await awaitable
            awaitable.close()
            raise TimeoutError

        with patch(
            "pilotsuite.ha.client.asyncio.wait_for", side_effect=wait
        ), patch(
            "pilotsuite.ha.client.monotonic", side_effect=lambda: clock[0]
        ):
            await client.listen(AsyncMock(), stop, connection)
        return delays, [call.args[0] for call in connection.call_args_list]

    async def test_short_authenticated_connections_keep_exponential_backoff(self):
        delays, connections = await self._reconnect_delays([0, 1, 59, 1, 0, 1, 0])
        self.assertEqual([1, 2, 4, 8, 16, 30, 30], delays)
        self.assertEqual([True, False] * 7, connections)

    async def test_idle_stable_stream_resets_backoff_without_state_events(self):
        delays, connections = await self._reconnect_delays([0, 0, 60, 0])
        self.assertEqual([1, 2, 1, 2], delays)
        self.assertEqual([True, False] * 4, connections)

    async def test_authentication_failure_backs_off_without_connected_claim(self):
        delays, connections = await self._reconnect_delays(
            [0, 0, 0], authenticated=False
        )
        self.assertEqual([1, 2, 4], delays)
        self.assertEqual([False] * 3, connections)

    async def test_graceful_close_reports_disconnect_and_backs_off(self):
        class ClosingSocket(_Socket):
            def __aiter__(self):
                return self

            async def __anext__(self):
                raise StopAsyncIteration

        socket = ClosingSocket([
            {"type": "auth_required"}, {"type": "auth_ok"},
            {"id": 1, "success": True},
        ])
        client = HomeAssistantClient("ws://supervisor/core/websocket", "token")
        client._session = _Session(socket)
        stop = asyncio.Event()
        connection = AsyncMock()
        delays = []

        async def wait(awaitable, timeout):
            delays.append(timeout)
            stop.set()
            return await awaitable

        with patch("pilotsuite.ha.client.asyncio.wait_for", side_effect=wait):
            await client.listen(AsyncMock(), stop, connection)
        self.assertEqual([1], delays)
        self.assertEqual([True, False], [call.args[0] for call in connection.call_args_list])

    async def test_snapshot_raises_receive_limit_for_large_home_assistant(self) -> None:
        responses: list[dict[str, object]] = [
            {"type": "auth_required"},
            {"type": "auth_ok"},
        ]
        responses.extend(
            {"id": request_id, "type": "result", "success": True, "result": []}
            for request_id in range(1, 6)
        )
        socket = _Socket(responses)
        session = _Session(socket)
        client = HomeAssistantClient("ws://supervisor/core/websocket", "token")
        client._session = session  # type: ignore[assignment]

        result = await client.snapshot()

        self.assertEqual(MAX_WS_MESSAGE_BYTES, session.kwargs["max_msg_size"])
        self.assertEqual(
            {"config", "areas", "devices", "entities", "states"}, set(result)
        )

    async def test_receive_error_preserves_transport_detail(self) -> None:
        class ErrorSocket:
            async def receive(self, timeout: int) -> SimpleNamespace:
                del timeout
                return SimpleNamespace(
                    type=WSMsgType.ERROR,
                    data="Message size exceeds limit",
                )

        with self.assertRaisesRegex(
            HomeAssistantError, "ERROR: Message size exceeds limit"
        ):
            await HomeAssistantClient._receive_json(ErrorSocket())


if __name__ == "__main__":
    unittest.main()
