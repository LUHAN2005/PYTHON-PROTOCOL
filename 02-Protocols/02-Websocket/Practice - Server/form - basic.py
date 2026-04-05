"""
LEVEL 10 - WebSocket form chuẩn (1 file hoàn chỉnh)
Mục tiêu:
- Có client_id rõ ràng
- Có topic để phân luồng message, tránh nhầm
- Có type để phân biệt command / ack / update / error
- Tách xử lý theo topic
- Có heartbeat
- Có timeout safety
- Có nhiều client kết nối cùng lúc
- Có broadcast telemetry đúng topic
- Code vẫn 1 file nhưng form phải sạch, dễ scale tiếp

THỨ TỰ CODE
1) import
2) config
3) state / storage
4) helper encode/decode
5) connection helpers
6) topic handlers
7) background loops
8) main websocket handler
9) start server
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any

import websockets


# ====== (A) Cấu hình ======
HOST = "localhost"
PORT = 8765

SERVER_CLIENT_ID = "SERVER_CORE"

HEARTBEAT_TIMEOUT = 5.0
TELEMETRY_INTERVAL = 2.0
MAIN_SLEEP = 0.5

TOPIC_WELCOME = "system/welcome"
TOPIC_REGISTER = "system/register"
TOPIC_HEARTBEAT = "system/heartbeat"
TOPIC_ERROR = "system/error"

TOPIC_CAR_CONTROL = "car/control"
TOPIC_CAR_TELEMETRY = "car/telemetry"
TOPIC_CAR_EMERGENCY = "car/emergency"

TYPE_COMMAND = "command"
TYPE_ACK = "ack"
TYPE_UPDATE = "update"
TYPE_ERROR = "error"
TYPE_EVENT = "event"


# ====== (B) State / storage ======
clients: Dict[Any, Dict[str, Any]] = {}

car_state = {
    "speed": 0.0,
    "steering": 0.0,
    "battery": 100,
    "status": "idle",
}


# ====== (C) Helper encode / decode ======
def make_message(
    topic: str,
    msg_type: str,
    payload: Dict[str, Any] | None = None,
    *,
    client_id: str = SERVER_CLIENT_ID,
    message_id: str | None = None,
) -> str:
    return json.dumps(
        {
            "topic": topic,
            "type": msg_type,
            "client_id": client_id,
            "message_id": message_id or str(uuid.uuid4())[:8],
            "payload": payload or {},
        },
        ensure_ascii=False,
    )


def parse_message(raw: str):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, "Invalid JSON"

    if not isinstance(data, dict):
        return None, "Message must be an object"

    topic = data.get("topic")
    msg_type = data.get("type")
    client_id = data.get("client_id")
    message_id = data.get("message_id")
    payload = data.get("payload", {})

    if not isinstance(topic, str) or not topic:
        return None, "Missing or invalid 'topic'"

    if not isinstance(msg_type, str) or not msg_type:
        return None, "Missing or invalid 'type'"

    if client_id is not None and not isinstance(client_id, str):
        return None, "Invalid 'client_id'"

    if message_id is not None and not isinstance(message_id, str):
        return None, "Invalid 'message_id'"

    if payload is None:
        payload = {}

    if not isinstance(payload, dict):
        return None, "'payload' must be an object"

    return {
        "topic": topic,
        "type": msg_type,
        "client_id": client_id,
        "message_id": message_id,
        "payload": payload,
    }, None


# ====== (D) Connection helpers ======
async def send_json(
    websocket,
    topic: str,
    msg_type: str,
    payload: Dict[str, Any] | None = None,
    *,
    client_id: str = SERVER_CLIENT_ID,
    message_id: str | None = None,
):
    msg = make_message(
        topic=topic,
        msg_type=msg_type,
        payload=payload,
        client_id=client_id,
        message_id=message_id,
    )
    await websocket.send(msg)


async def send_error(
    websocket,
    error_text: str,
    *,
    message_id: str | None = None,
):
    await send_json(
        websocket,
        topic=TOPIC_ERROR,
        msg_type=TYPE_ERROR,
        payload={"message": error_text},
        message_id=message_id,
    )


def get_client_info(websocket):
    return clients.get(websocket)


async def register_connection(websocket):
    temp_id = f"client_{str(uuid.uuid4())[:8]}"
    clients[websocket] = {
        "client_id": temp_id,
        "name": temp_id,
        "role": "guest",
        "connected_at": time.time(),
        "last_heartbeat": time.time(),
        "subscriptions": {TOPIC_CAR_TELEMETRY},
    }
    print(f"[CONNECT] {temp_id}")


async def unregister_connection(websocket):
    info = clients.pop(websocket, None)
    if info:
        print(f"[DISCONNECT] {info['client_id']}")


async def broadcast_to_topic(topic: str, payload: Dict[str, Any]):
    dead = []

    for ws, info in list(clients.items()):
        if topic not in info["subscriptions"]:
            continue

        try:
            await send_json(
                ws,
                topic=topic,
                msg_type=TYPE_UPDATE,
                payload=payload,
            )
        except Exception:
            dead.append(ws)

    for ws in dead:
        await unregister_connection(ws)


# ====== (E) Topic handlers ======
async def handle_register(websocket, message: Dict[str, Any]):
    payload = message["payload"]
    info = get_client_info(websocket)

    if info is None:
        return await send_error(websocket, "Connection not registered", message_id=message["message_id"])

    name = payload.get("name")
    role = payload.get("role", "viewer")
    subscriptions = payload.get("subscriptions", [TOPIC_CAR_TELEMETRY])
    requested_client_id = payload.get("client_id")

    if name is not None and not isinstance(name, str):
        return await send_error(websocket, "Field 'name' must be string", message_id=message["message_id"])

    if not isinstance(role, str):
        return await send_error(websocket, "Field 'role' must be string", message_id=message["message_id"])

    if requested_client_id is not None and not isinstance(requested_client_id, str):
        return await send_error(websocket, "Field 'client_id' must be string", message_id=message["message_id"])

    if not isinstance(subscriptions, list) or not all(isinstance(x, str) for x in subscriptions):
        return await send_error(websocket, "Field 'subscriptions' must be list[str]", message_id=message["message_id"])

    if name:
        info["name"] = name

    info["role"] = role
    info["subscriptions"] = set(subscriptions)
    info["client_id"] = requested_client_id or info["client_id"]

    print(f"[REGISTER] id={info['client_id']} name={info['name']} role={info['role']}")

    await send_json(
        websocket,
        topic=TOPIC_REGISTER,
        msg_type=TYPE_ACK,
        payload={
            "client_id": info["client_id"],
            "name": info["name"],
            "role": info["role"],
            "subscriptions": list(info["subscriptions"]),
        },
        message_id=message["message_id"],
    )


async def handle_heartbeat(websocket, message: Dict[str, Any]):
    info = get_client_info(websocket)

    if info is None:
        return await send_error(websocket, "Connection not registered", message_id=message["message_id"])

    info["last_heartbeat"] = time.time()

    await send_json(
        websocket,
        topic=TOPIC_HEARTBEAT,
        msg_type=TYPE_ACK,
        payload={"ts": info["last_heartbeat"]},
        message_id=message["message_id"],
    )


async def handle_car_control(websocket, message: Dict[str, Any]):
    info = get_client_info(websocket)

    if info is None:
        return await send_error(websocket, "Connection not registered", message_id=message["message_id"])

    if info["role"] not in {"controller", "admin"}:
        return await send_error(websocket, "Permission denied for car/control", message_id=message["message_id"])

    payload = message["payload"]
    throttle = payload.get("throttle")
    steering = payload.get("steering")

    if not isinstance(throttle, (int, float)):
        return await send_error(websocket, "'throttle' must be number", message_id=message["message_id"])

    if not isinstance(steering, (int, float)):
        return await send_error(websocket, "'steering' must be number", message_id=message["message_id"])

    car_state["speed"] = max(0.0, min(100.0, float(throttle)))
    car_state["steering"] = max(-45.0, min(45.0, float(steering)))
    car_state["status"] = "moving" if car_state["speed"] > 0 else "idle"

    await send_json(
        websocket,
        topic=TOPIC_CAR_CONTROL,
        msg_type=TYPE_ACK,
        payload={
            "accepted": True,
            "state": car_state.copy(),
        },
        message_id=message["message_id"],
    )


async def handle_car_emergency(websocket, message: Dict[str, Any]):
    info = get_client_info(websocket)

    if info is None:
        return await send_error(websocket, "Connection not registered", message_id=message["message_id"])

    if info["role"] not in {"controller", "admin"}:
        return await send_error(websocket, "Permission denied for car/emergency", message_id=message["message_id"])

    car_state["speed"] = 0.0
    car_state["status"] = "emergency_stop"

    await send_json(
        websocket,
        topic=TOPIC_CAR_EMERGENCY,
        msg_type=TYPE_ACK,
        payload={
            "accepted": True,
            "state": car_state.copy(),
        },
        message_id=message["message_id"],
    )


async def handle_car_telemetry_request(websocket, message: Dict[str, Any]):
    await send_json(
        websocket,
        topic=TOPIC_CAR_TELEMETRY,
        msg_type=TYPE_UPDATE,
        payload=car_state.copy(),
        message_id=message["message_id"],
    )


TOPIC_HANDLERS = {
    TOPIC_REGISTER: handle_register,
    TOPIC_HEARTBEAT: handle_heartbeat,
    TOPIC_CAR_CONTROL: handle_car_control,
    TOPIC_CAR_EMERGENCY: handle_car_emergency,
    TOPIC_CAR_TELEMETRY: handle_car_telemetry_request,
}


# ====== (F) Background loops ======
async def telemetry_loop():
    while True:
        await asyncio.sleep(TELEMETRY_INTERVAL)

        if car_state["battery"] > 0 and car_state["status"] == "moving":
            car_state["battery"] = max(0, car_state["battery"] - 1)

        await broadcast_to_topic(TOPIC_CAR_TELEMETRY, car_state.copy())


async def safety_loop():
    while True:
        await asyncio.sleep(1.0)
        now = time.time()

        for ws, info in list(clients.items()):
            if now - info["last_heartbeat"] > HEARTBEAT_TIMEOUT:
                print(f"[TIMEOUT] {info['client_id']} -> emergency stop")

                car_state["speed"] = 0.0
                car_state["status"] = "emergency_stop"

                try:
                    await send_json(
                        ws,
                        topic=TOPIC_CAR_EMERGENCY,
                        msg_type=TYPE_EVENT,
                        payload={"reason": "heartbeat_timeout"},
                    )
                except Exception:
                    pass

                try:
                    await ws.close()
                except Exception:
                    pass


# ====== (G) Main websocket handler ======
async def handle_client(websocket):
    await register_connection(websocket)

    try:
        await send_json(
            websocket,
            topic=TOPIC_WELCOME,
            msg_type=TYPE_EVENT,
            payload={"message": "connected"},
        )

        async for raw in websocket:
            message, error = parse_message(raw)

            if error:
                await send_error(websocket, error)
                continue

            topic = message["topic"]
            handler = TOPIC_HANDLERS.get(topic)

            if not handler:
                await send_error(
                    websocket,
                    f"Unknown topic: {topic}",
                    message_id=message["message_id"],
                )
                continue

            await handler(websocket, message)

    except Exception as e:
        if not isinstance(e, websockets.ConnectionClosed):
            print("[HANDLE CLIENT ERROR]", repr(e))

    finally:
        await unregister_connection(websocket)


# ====== (H) Start server ======
async def main():
    asyncio.create_task(telemetry_loop())
    asyncio.create_task(safety_loop())

    async with websockets.serve(handle_client, HOST, PORT):
        print(f"RUN WS SERVER on ws://{HOST}:{PORT}")
        while True:
            await asyncio.sleep(MAIN_SLEEP)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("STOP")