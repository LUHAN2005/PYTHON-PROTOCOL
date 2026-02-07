from paho.mqtt import client as mqtt
from dotenv import load_dotenv
import os
import time
import json
import logging

# 0) Load .env TRƯỚC khi getenv
load_dotenv()

# 1) Config (Level 9)
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))

DEVICE_ID = os.getenv("DEVICE_ID", "LUHAN")
TOPIC_TELEMETRY = f"devices/{DEVICE_ID}/telemetry"
TOPIC_STATUS = f"devices/{DEVICE_ID}/status"

PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "0.5"))
MAX_QUEUE = int(os.getenv("MAX_QUEUE", "500"))

# 2) Logging (Level 9)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

# 3) Offline queue (Level 8)
queue: list[tuple[str, str]] = []  # (topic, payload_str)

# 4) seq (Level 9)
seq = 0

# 5) Create client (paho-mqtt 2.x)
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=DEVICE_ID
)

# 6) LWT must be set BEFORE connect (Level 6)
client.will_set(TOPIC_STATUS, "offline", qos=1, retain=True)

# 7) Reconnect backoff (Level 7)
client.reconnect_delay_set(min_delay=1, max_delay=30)


def build_payload(current_seq: int) -> str:
    """Level 9 payload: seq + ts + data (JSON string)."""
    payload = {
        "seq": current_seq,
        "ts": time.time(),
        "device_id": DEVICE_ID,
        "data": {"msg": "hi"}  # bạn thay phần data này bằng dữ liệu thật
    }
    return json.dumps(payload, ensure_ascii=False)


# 8) Callbacks (Level 5/6)
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    logging.info(f"Connect: {reason_code}")
    # Khi connect xong -> báo online (retain)
    client.publish(TOPIC_STATUS, "online", qos=1, retain=True)


def on_disconnect(client: mqtt.Client, userdata, reason_code, properties):
    logging.warning(f"Disconnect: {reason_code}")


def on_publish(client: mqtt.Client, userdata, mid, reason_code, properties):
    logging.info(f"Published mid={mid}")


client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# 9) Connect + loop
client.connect(MQTT_HOST, MQTT_PORT, KEEPALIVE)
client.loop_start()

try:
    while True:
        # Offline -> queue message + đợi reconnect
        if not client.is_connected():
            payload_str = build_payload(seq)
            if len(queue) >= MAX_QUEUE:
                queue.pop(0)  # drop cũ nhất
            queue.append((TOPIC_TELEMETRY, payload_str))
            seq += 1
            time.sleep(0.2)  # ngủ ngắn để đỡ CPU
            continue

        # Online -> flush queue trước
        while queue and client.is_connected():
            t, p = queue.pop(0)
            client.publish(t, p, qos=1, retain=False)
            time.sleep(0.01)  # tránh dồn dập quá

        # Gửi message hiện tại
        payload_str = build_payload(seq)
        client.publish(TOPIC_TELEMETRY, payload_str, qos=1, retain=False)
        seq += 1

        time.sleep(PUBLISH_INTERVAL)

except KeyboardInterrupt:
    logging.info("Stopped by user")

finally:
    client.loop_stop()
    client.disconnect()
