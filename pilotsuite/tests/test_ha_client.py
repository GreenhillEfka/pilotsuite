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
    async def test_helper_collection_is_allowlisted_read_only_and_bounded(self):
        socket = _Socket([{'type':'auth_required'},{'type':'auth_ok'},
                          {'id':1,'success':True,'result':[{'id':'original','restore':False}]}])
        client = HomeAssistantClient('ws://example.invalid/websocket','synthetic')
        client._session = _Session(socket)
        self.assertEqual('original',(await client.helper_collection('timer'))[0]['id'])
        self.assertEqual({'id':1,'type':'timer/list'},socket.sent[-1])
        before=list(socket.sent)
        for invalid in ('timer/create','input_text','automation',None):
            with self.assertRaises(HomeAssistantError):await client.helper_collection(invalid)
        self.assertEqual(before,socket.sent)

    async def test_helper_collection_rejects_malformed_rows(self):
        for result in ({},[{'name':'missing_id'}],[{'id':'x'}]*2001):
            socket=_Socket([{'type':'auth_required'},{'type':'auth_ok'},{'id':1,'success':True,'result':result}])
            client=HomeAssistantClient('ws://example.invalid/websocket','synthetic');client._session=_Session(socket)
            with self.assertRaises(HomeAssistantError):await client.helper_collection('timer')

    async def test_malformed_text_frame_is_a_domain_error(self):
        class MalformedSocket:
            async def receive(self, timeout):
                self.timeout = timeout
                return SimpleNamespace(type=WSMsgType.TEXT, data='{broken')
        socket=MalformedSocket()
        with self.assertRaisesRegex(HomeAssistantError,'invalid Home Assistant WebSocket response'):
            await HomeAssistantClient._receive_json(socket)
        self.assertEqual(20,socket.timeout)

    async def test_listen_subscribes_to_both_event_types_and_preserves_service_context(self):
        stop = asyncio.Event()
        service_event = {
            "event_type": "call_service",
            "data": {"domain": "light", "service": "turn_on"},
            "context": {"id": "opaque", "parent_id": "parent"},
        }
        state_data = {"entity_id": "binary_sensor.motion"}

        class StreamingSocket(_Socket):
            def __init__(self):
                super().__init__([
                    {"type": "auth_required"},
                    {"type": "auth_ok"},
                    {"id": 1, "type": "result", "success": True},
                    {"id": 2, "type": "result", "success": True},
                ])
                self.stream = iter([
                    {"id": 2, "type": "event", "event": service_event},
                    {"id": 1, "type": "event", "event": {
                        "event_type": "state_changed", "data": state_data
                    }},
                ])

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    payload = next(self.stream)
                except StopIteration:
                    raise StopAsyncIteration
                return SimpleNamespace(type=WSMsgType.TEXT, data=json.dumps(payload))

        socket = StreamingSocket()
        client = HomeAssistantClient("ws://example.invalid/websocket", "token")
        client._session = _Session(socket)
        async def state_changed(_: dict[str, object]) -> None:
            stop.set()

        state = AsyncMock(side_effect=state_changed)
        service = AsyncMock()
        await client.listen(state, stop, service_callback=service)

        self.assertIn(
            {"id": 1, "type": "subscribe_events", "event_type": "state_changed"},
            socket.sent,
        )
        self.assertIn(
            {"id": 2, "type": "subscribe_events", "event_type": "call_service"},
            socket.sent,
        )
        service.assert_awaited_once_with(service_event)
        state.assert_awaited_once_with(state_data)

    async def test_dispatches_state_data_and_full_service_event_separately(self):
        state = AsyncMock()
        service = AsyncMock()
        service_event = {
            "event_type": "call_service",
            "data": {"domain": "light", "service": "turn_on"},
            "context": {"id": "opaque", "parent_id": "parent"},
        }
        await HomeAssistantClient._dispatch_event(
            {"id": 2, "type": "event", "event": service_event}, state, service
        )
        service.assert_awaited_once_with(service_event)
        state.assert_not_awaited()

        state_data = {"entity_id": "binary_sensor.motion"}
        await HomeAssistantClient._dispatch_event(
            {
                "id": 1,
                "type": "event",
                "event": {"event_type": "state_changed", "data": state_data},
            },
            state,
            service,
        )
        state.assert_awaited_once_with(state_data)

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


    async def test_bounded_timer_write_transport_emits_only_allowlisted_commands(self):
        key="pilotsuite_hz_living_anwesenheitsnachlauf"
        socket=_Socket([{"type":"auth_required"},{"type":"auth_ok"},
                        {"id":1,"success":True,"result":{"id":key}}])
        client=HomeAssistantClient("ws://example.invalid/websocket","synthetic");client._session=_Session(socket)
        await client.helper_create_timer(key=key,name="PilotSuite · hz_living · Anwesenheitsnachlauf",
                                         duration="00:05:00",restore=True)
        self.assertEqual("timer/create",socket.sent[-1]["type"])
        self.assertEqual(key,socket.sent[-1]["id"])

        socket=_Socket([{"type":"auth_required"},{"type":"auth_ok"},
                        {"id":1,"success":True,"result":None}])
        client._session=_Session(socket)
        await client.helper_delete_timer(key)
        self.assertEqual({"id":1,"type":"timer/delete","timer_id":key},socket.sent[-1])

    async def test_bounded_timer_write_rejects_non_pilotsuite_identity_before_network(self):
        client=HomeAssistantClient("ws://example.invalid/websocket","synthetic")
        client._session=_Session(_Socket([]))
        with self.assertRaises(HomeAssistantError):
            await client.helper_create_timer(key="foreign_timer",name="x",duration="00:05:00",restore=True)
        self.assertEqual([],client._session.socket.sent)


    async def test_presence_service_transport_is_tiny_allowlist(self):
        key="timer.pilotsuite_room_anwesenheitsnachlauf"
        socket=_Socket([{"type":"auth_required"},{"type":"auth_ok"},{"id":1,"success":True,"result":None}])
        client=HomeAssistantClient("ws://example.invalid/websocket","token");client._session=_Session(socket)
        await client.call_bounded_service("timer","start",key)
        self.assertEqual("call_service",socket.sent[-1]["type"])
        self.assertEqual({"entity_id":key},socket.sent[-1]["target"])
        before=list(socket.sent)
        for domain,service,target in [("light","turn_on","light.room"),("timer","finish",key),
                                      ("input_boolean","turn_on","input_boolean.Bad-ID")]:
            with self.assertRaises(HomeAssistantError):
                await client.call_bounded_service(domain,service,target)
        self.assertEqual(before,socket.sent)


if __name__ == "__main__":
    unittest.main()
