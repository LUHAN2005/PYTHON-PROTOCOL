"""
LEVEL 10 - WebSocket client form chuẩn (1 file hoàn chỉnh)
Mục tiêu:
- Connect vào WebSocket server
- Tự register với client_id / name / role
- Tự gửi heartbeat định kỳ
- Tách receive theo topic
- Có menu gửi command rõ ràng
- Có reconnect mindset cơ bản
- Code 1 file nhưng form sạch, dễ mở rộng tiếp

THỨ TỰ CODE
1) import
2) config
3) helper encode/decode
4) outbound message builders
5) topic handlers
6) background loops (heartbeat / receive / send)
7) one session connect
8) reconnect loop
"""

import asyncio
import json
import uuid
from typing import Dict, Any

import websockets
from websockets.exceptions import ConnectionClosed


# ====== (A) Cấu hình ======
WS_URL = "ws://localhost:8765"

CLIENT_ID = "controller_01"
CLIENT_NAME = "Laptop điều khien"
CLIENT_ROLE = "controller"

SUBSCRIPTIONS = [
    "car/telemetry",
]

HEARTBEAT_INTERVAL = 2.0
RECONNECT_DELAY = 2.0


TOPIC_REGISTER = "system/register"
TOPIC_HEARTBEAT = "system/heartbeat"
TOPIC_ERROR = "system/error"
TOPIC_WELCOME = "system/welcome"

TOPIC_CAR_CONTROL = "car/control"
TOPIC_CAR_TELEMETRY = "car/telemetry"
TOPIC_CAR_EMERGENCY = "car/emergency"

TYPE_COMMAND = "command"
TYPE_ACK = "ack"
TYPE_UPDATE = "update"
TYPE_ERROR = "error"
TYPE_EVENT = "event"


# ====== (B) Helper encode / decode ======
def make_message(
    topic: str,
    msg_type: str,
    payload: Dict[str, Any] | None = None,
    *,
    client_id: str = CLIENT_ID,
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

    if not isinstance(topic, str):
        return None, "Missing/invalid topic"

    if not isinstance(msg_type, str):
        return None, "Missing/invalid type"

    if payload is None:
        payload = {}

    if not isinstance(payload, dict):
        return None, "Payload must be object"

    return {
        "topic": topic,
        "type": msg_type,
        "client_id": client_id,
        "message_id": message_id,
        "payload": payload,
    }, None


# ====== (C) Outbound message builders ======
def build_register():
    return make_message(
        topic=TOPIC_REGISTER,
        msg_type=TYPE_COMMAND,
        payload={
            "client_id": CLIENT_ID,
            "name": CLIENT_NAME,
            "role": CLIENT_ROLE,
            "subscriptions": SUBSCRIPTIONS,
        },
    )


def build_heartbeat():
    return make_message(
        topic=TOPIC_HEARTBEAT,
        msg_type=TYPE_COMMAND,
        payload={},
    )


def build_control(throttle: float, steering: float):
    return make_message(
        topic=TOPIC_CAR_CONTROL,
        msg_type=TYPE_COMMAND,
        payload={
            "throttle": throttle,
            "steering": steering,
        },
    )


def build_emergency():
    return make_message(
        topic=TOPIC_CAR_EMERGENCY,
        msg_type=TYPE_COMMAND,
        payload={},
    )


def build_telemetry_request():
    return make_message(
        topic=TOPIC_CAR_TELEMETRY,
        msg_type=TYPE_COMMAND,
        payload={},
    )


# ====== (D) Topic handlers ======
async def handle_welcome(message: Dict[str, Any]):
    print("[WELCOME]", message["payload"])


async def handle_register_ack(message: Dict[str, Any]):
    print("[REGISTER ACK]", message["payload"])


async def handle_heartbeat_ack(message: Dict[str, Any]):
    print("[HEARTBEAT ACK]", message["payload"])


async def handle_control_ack(message: Dict[str, Any]):
    print("[CONTROL ACK]", message["payload"])


async def handle_emergency_ack(message: Dict[str, Any]):
    print("[EMERGENCY ACK]", message["payload"])


async def handle_telemetry(message: Dict[str, Any]):
    payload = message["payload"]
    print(
        "[TELEMETRY]",
        f"speed={payload.get('speed')}",
        f"steering={payload.get('steering')}",
        f"battery={payload.get('battery')}",
        f"status={payload.get('status')}",
    )


async def handle_error(message: Dict[str, Any]):
    print("[ERROR]", message["payload"])


async def handle_emergency_event(message: Dict[str, Any]):
    print("[EMERGENCY EVENT]", message["payload"])


async def process_message(message: Dict[str, Any]):
    topic = message["topic"]
    msg_type = message["type"]

    if topic == TOPIC_WELCOME and msg_type == TYPE_EVENT:
        return await handle_welcome(message)

    if topic == TOPIC_REGISTER and msg_type == TYPE_ACK:
        return await handle_register_ack(message)

    if topic == TOPIC_HEARTBEAT and msg_type == TYPE_ACK:
        return await handle_heartbeat_ack(message)

    if topic == TOPIC_CAR_CONTROL and msg_type == TYPE_ACK:
        return await handle_control_ack(message)

    if topic == TOPIC_CAR_EMERGENCY and msg_type == TYPE_ACK:
        return await handle_emergency_ack(message)

    if topic == TOPIC_CAR_EMERGENCY and msg_type == TYPE_EVENT:
        return await handle_emergency_event(message)

    if topic == TOPIC_CAR_TELEMETRY and msg_type == TYPE_UPDATE:
        return await handle_telemetry(message)

    if topic == TOPIC_ERROR and msg_type == TYPE_ERROR:
        return await handle_error(message)

    print("[UNKNOWN MESSAGE]", message)


# ====== (E) Background loops ======
async def heartbeat_loop(websocket):
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        await websocket.send(build_heartbeat())


async def receive_loop(websocket):
    async for raw in websocket:
        message, error = parse_message(raw)

        if error:
            print("[PARSE ERROR]", error)
            continue

        await process_message(message)


async def send_loop(websocket):
    while True:
        print("\n===== MENU =====")
        print("1. Register lai")
        print("2. Gui control")
        print("3. Gui emergency stop")
        print("4. Xin telemetry ngay")
        print("5. Thoat client")
        choice = await asyncio.to_thread(input, "Choose: ")

        if choice == "1":
            await websocket.send(build_register())
            print("[SEND] register")

        elif choice == "2":
            throttle_raw = await asyncio.to_thread(input, "Throttle (0-100): ")
            steering_raw = await asyncio.to_thread(input, "Steering (-45 to 45): ")

            try:
                throttle = float(throttle_raw)
                steering = float(steering_raw)
            except ValueError:
                print("[INPUT ERROR] throttle/steering phai la so")
                continue

            await websocket.send(build_control(throttle, steering))
            print("[SEND] control")

        elif choice == "3":
            await websocket.send(build_emergency())
            print("[SEND] emergency")

        elif choice == "4":
            await websocket.send(build_telemetry_request())
            print("[SEND] telemetry request")

        elif choice == "5":
            print("Stop client by user")
            await websocket.close()
            return

        else:
            print("Lua chon khong hop le")


# ====== (F) One session connect ======
async def run_one_session():
    async with websockets.connect(WS_URL) as websocket:
        print(f"[CONNECTED] {WS_URL}")

        await websocket.send(build_register())
        print("[SEND] register on connect")

        heartbeat_task = asyncio.create_task(heartbeat_loop(websocket))
        receive_task = asyncio.create_task(receive_loop(websocket))
        send_task = asyncio.create_task(send_loop(websocket))

        done, pending = await asyncio.wait(
            [heartbeat_task, receive_task, send_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        for task in done:
            exc = task.exception()
            if exc:
                raise exc


# ====== (G) Reconnect loop ======
async def main():
    while True:
        try:
            await run_one_session()
            print("[SESSION END]")
            break

        except ConnectionClosed:
            print(f"[DISCONNECTED] reconnect after {RECONNECT_DELAY}s")
            await asyncio.sleep(RECONNECT_DELAY)

        except OSError as e:
            print(f"[CONNECT FAIL] {e} -> retry after {RECONNECT_DELAY}s")
            await asyncio.sleep(RECONNECT_DELAY)

        except KeyboardInterrupt:
            print("STOP")
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("EXIT")