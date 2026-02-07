
# =========================
# 1) IMPORTS
# =========================
import argparse
import signal
import sys
import time
from dataclasses import dataclass
from typing import List, Optional

import paho.mqtt.client as mqtt


# =========================
# 2) CONFIG DEFAULT
# =========================
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 1883
DEFAULT_KEEPALIVE = 60

# Publish mặc định (demo)
DEFAULT_MESSAGES = [
    # topic, payload, qos, retain
    ("testing", "hi", 0, False),
    ("test/a", "A", 0, False),
    ("test/a/b", "B", 0, False),
    ("test/qos1", "qos1-message", 1, False),
    ("test/retain", "LAST", 1, True),
]


# =========================
# 3) DATA MODEL
# =========================
@dataclass
class OutMsg:
    topic: str
    payload: str
    qos: int = 0
    retain: bool = False


# =========================
# 4) CALLBACKS
# =========================
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[CONNECT] reason_code={reason_code}")
    if reason_code != 0:
        print("[CONNECT] Failed. Check broker/port/auth.")


def on_disconnect(client, userdata, reason_code, properties):
    print(f"[DISCONNECT] reason_code={reason_code}")


def on_publish(client, userdata, mid, reason_code, properties):
    # mid = message id nội bộ của paho
    print(f"[PUBLISH-ACK] mid={mid} reason_code={reason_code}")


def on_log(client, userdata, level, buf):
    print(f"[LOG] {buf}")


# =========================
# 5) CLIENT BUILDER
# =========================
def build_client(
    client_id: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    enable_log: bool = True,
):
    client = mqtt.Client(
        client_id=client_id,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
    )

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    if enable_log:
        client.on_log = on_log

    # ===== AUTH (tuỳ chọn) =====
    if username:
        client.username_pw_set(username, password)

    # ===== TLS (tuỳ chọn) =====
    # client.tls_set(ca_certs="ca.crt")
    # client.tls_insecure_set(True)   # CHỈ dùng khi test dev

    # ===== WILL (tuỳ chọn) =====
    # client.will_set("status/luhan", payload="offline", qos=1, retain=True)

    return client


# =========================
# 6) PARSER FOR --msg
# =========================
def parse_msgs(raw_msgs: List[str]) -> List[OutMsg]:
    """
    Cho phép truyền nhiều message từ CLI bằng --msg (lặp được):
      --msg "topic|payload|qos|retain"
    retain: true/false/1/0
    qos mặc định 0, retain mặc định false nếu thiếu.

    Ví dụ:
      --msg "testing|hi"
      --msg "test/retain|LAST|1|true"
    """
    out: List[OutMsg] = []

    for item in raw_msgs:
        parts = item.split("|")
        if len(parts) < 2:
            raise ValueError("Format --msg phải có ít nhất: topic|payload")

        topic = parts[0].strip()
        payload = parts[1]

        qos = int(parts[2]) if len(parts) >= 3 and parts[2].strip() != "" else 0

        if len(parts) >= 4:
            r = parts[3].strip().lower()
            retain = r in ("1", "true", "yes", "y")
        else:
            retain = False

        out.append(OutMsg(topic=topic, payload=payload, qos=qos, retain=retain))

    return out


# =========================
# 7) PUBLISH WORKFLOW
# =========================
def publish_batch(client: mqtt.Client, messages: List[OutMsg], delay: float = 0.2):
    """
    Lưu ý cực quan trọng (đúng bài bạn đang vướng):
    - Paho cần loop chạy để dữ liệu “đi ra mạng”.
    - Ta dùng loop_start() và chờ publish xong bằng wait_for_publish().
    """
    for m in messages:
        info = client.publish(m.topic, m.payload, qos=m.qos, retain=m.retain)

        # wait_for_publish:
        # - QoS0: chờ “đẩy ra socket” (không có ACK từ broker)
        # - QoS1/2: chờ hoàn tất handshake tương ứng (có ACK)
        info.wait_for_publish()

        print(
            f"[PUB] topic='{m.topic}' qos={m.qos} retain={m.retain} payload='{m.payload}'"
        )

        if delay > 0:
            time.sleep(delay)


# =========================
# 8) MAIN
# =========================
def main():
    parser = argparse.ArgumentParser(description="MQTT Publisher - Master Template")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--keepalive", type=int, default=DEFAULT_KEEPALIVE)
    parser.add_argument("--client-id", default="pub-luhan")
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--no-log", action="store_true", help="Tắt on_log cho đỡ spam")

    parser.add_argument(
        "--msg",
        action="append",
        default=[],
        help="Message format: topic|payload|qos|retain. Can repeat.",
    )
    parser.add_argument("--delay", type=float, default=0.2, help="Delay giữa các publish")
    args = parser.parse_args()

    if args.msg:
        msgs = parse_msgs(args.msg)
    else:
        msgs = [OutMsg(*t) for t in DEFAULT_MESSAGES]

    client = build_client(
        client_id=args.client_id,
        username=args.username,
        password=args.password,
        enable_log=(not args.no_log),
    )

    # Kết nối broker
    client.connect(args.host, args.port, args.keepalive)

    # chạy network loop nền
    client.loop_start()

    try:
        publish_batch(client, msgs, delay=args.delay)

        # đệm nhẹ để chắc chắn packet cuối cùng kịp đi
        time.sleep(0.1)

    finally:
        # gửi DISCONNECT
        client.disconnect()
        time.sleep(0.1)
        client.loop_stop()
        print("[EXIT] Done.")


if __name__ == "__main__":
    main()
