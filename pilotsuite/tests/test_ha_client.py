from __future__ import annotations

import unittest
import json
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
