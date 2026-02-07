
# =========================
# 1) IMPORTS
# =========================
import argparse
import signal
import sys
import time
from typing import List, Tuple

import paho.mqtt.client as mqtt


# =========================
# 2) CONFIG DEFAULT
# =========================
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 1883
DEFAULT_KEEPALIVE = 60

# Format: (topic, qos)
DEFAULT_TOPICS: List[Tuple[str, int]] = [
    ("testing/#", 0),
    ("test/#", 1),
]


# =========================
# 3) CALLBACKS (EVENT HANDLERS)
# =========================
def on_connect(client, userdata, flags, reason_code, properties):
    """
    Gọi khi client kết nối thành công/thất bại.
    - reason_code == 0 thường là OK (Success)
    - Subscribe trong on_connect để nếu reconnect thì tự subscribe lại.
    """
    topics: List[Tuple[str, int]] = userdata["topics"]
    print(f"[CONNECT] reason_code={reason_code}")

    if reason_code != 0:
        print("[CONNECT] Failed. Check broker/port/auth.")
        return

    # subscribe nhiều topic
    for t, q in topics:
        client.subscribe(t, qos=q)
        print(f"[SUB] topic='{t}' qos={q}")


def on_message(client, userdata, msg):
    """Gọi khi nhận được PUBLISH."""
    try:
        payload = msg.payload.decode("utf-8", errors="ignore")
    except Exception:
        payload = str(msg.payload)

    print(
        f"[MSG] topic='{msg.topic}' qos={msg.qos} retain={msg.retain} "
        f"payload='{payload}'"
    )


def on_disconnect(client, userdata, reason_code, properties):
    """Gọi khi mất kết nối / disconnect."""
    print(f"[DISCONNECT] reason_code={reason_code}")


def on_log(client, userdata, level, buf):
    """
    Log nội bộ của Paho (giống kiểu bạn thấy trong video).
    Có thể hơi nhiều -> nếu bạn thấy spam quá thì comment dòng client.on_log.
    """
    print(f"[LOG] {buf}")


# =========================
# 4) CLIENT BUILDER (TẠO CLIENT)
# =========================
def build_client(
    client_id: str,
    topics: List[Tuple[str, int]],
    username: str | None = None,
    password: str | None = None,
    enable_log: bool = True,
):
    # Paho 2.x: cần callback_api_version để tránh lỗi “Unsupported callback API version”
    client = mqtt.Client(
        client_id=client_id,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,  # bạn có thể đổi MQTTv5 nếu muốn
    )

    # userdata để callback lấy được danh sách topics
    client.user_data_set({"topics": topics})

    # gắn callback
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    if enable_log:
        client.on_log = on_log

    # ===== AUTH (tuỳ chọn) =====
    if username:
        client.username_pw_set(username, password)

    # ===== TLS (tuỳ chọn) =====
    # client.tls_set(ca_certs="ca.crt")     # hoặc dùng cert hệ thống
    # client.tls_insecure_set(True)         # CHỈ dùng khi test dev

    # ===== WILL (tuỳ chọn) =====
    # client.will_set("status/luhan", payload="offline", qos=1, retain=True)

    return client


# =========================
# 5) PARSE TOPICS (topics string -> list)
# =========================
def parse_topics(raw_topics: List[str]) -> List[Tuple[str, int]]:
    """
    Cho phép truyền nhiều topic qua CLI:
      --topic testing/#:0 --topic test/#:1
    Nếu không có :qos thì mặc định qos=0
    """
    topics: List[Tuple[str, int]] = []
    for item in raw_topics:
        if ":" in item:
            t, q = item.rsplit(":", 1)
            topics.append((t.strip(), int(q)))
        else:
            topics.append((item.strip(), 0))
    return topics


# =========================
# 6) MAIN RUN
# =========================
def main():
    parser = argparse.ArgumentParser(description="MQTT Subscriber - Master Template")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--keepalive", type=int, default=DEFAULT_KEEPALIVE)
    parser.add_argument("--client-id", default="sub-luhan")
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--no-log", action="store_true", help="Tắt on_log để đỡ spam")
    parser.add_argument(
        "--topic",
        action="append",
        default=[],
        help="Topic format: 'abc/#:1' or 'abc/#' (default qos=0). Can repeat.",
    )
    args = parser.parse_args()

    topics = parse_topics(args.topic) if args.topic else DEFAULT_TOPICS

    client = build_client(
        client_id=args.client_id,
        topics=topics,
        username=args.username,
        password=args.password,
        enable_log=(not args.no_log),
    )

    # Kết nối
    client.connect(args.host, args.port, args.keepalive)

    # Cách chạy loop:
    # - loop_forever(): block 1 thread, dễ nhất
    # - loop_start(): chạy nền (thread), bạn tự quản lý lifetime
    stop = False

    def handle_stop(sig, frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_stop)   # Ctrl+C
    signal.signal(signal.SIGTERM, handle_stop)

    client.loop_start()
    print("[RUN] Subscriber is running... Press Ctrl+C to exit.")

    try:
        while not stop:
            time.sleep(0.2)
    finally:
        print("\n[EXIT] Disconnecting...")
        client.disconnect()
        time.sleep(0.2)
        client.loop_stop()
        print("[EXIT] Done.")


if __name__ == "__main__":
    main()
