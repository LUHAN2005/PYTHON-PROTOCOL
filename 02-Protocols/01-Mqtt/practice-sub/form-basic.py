"""
LEVEL 8 - Subscriber chuẩn vị trí (match với pub Level 8)
Mục tiêu:
- Mất broker -> on_disconnect biết, tự reconnect
- Broker lên lại -> on_connect chạy lại -> tự subscribe lại
- Tách xử lý theo topic: /status vs /telemetry

THỨ TỰ CODE
1) tạo client
2) (tuỳ chọn) auth/tls
3) gắn callbacks (on_connect, on_disconnect, on_message)
4) connect(...)
5) loop_start()
"""

from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage
import time

# ====== (A) Cấu hình ======
CLIENT_ID = "LUHAN_SUB"

HOST = "localhost"
PORT = 1883
KEEPALIVE = 60

# Topic filter chuẩn IoT
TOPIC_STATUS_FILTER    = "devices/+/status"
TOPIC_TELEMETRY_FILTER = "devices/+/telemetry"

SLEEP_MAIN = 0.2

# ====== (B) 1) Tạo client ======
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID
)

# (Tuỳ chọn Level 7) backoff reconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)

# ====== (C) 3) Callbacks ======
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect:", reason_code)

    # Subscribe trong on_connect để reconnect là tự sub lại
    client.subscribe(TOPIC_STATUS_FILTER, qos=1)
    print("[SUB]", TOPIC_STATUS_FILTER, "qos=1")

    client.subscribe(TOPIC_TELEMETRY_FILTER, qos=1)
    print("[SUB]", TOPIC_TELEMETRY_FILTER, "qos=1")

def on_disconnect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Disconnect:", reason_code)

    # Thử reconnect (fail thì thôi, loop sẽ còn chạy)
    try:
        client.reconnect()
    except:
        pass

def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    # Tách xử lý theo đuôi topic (string processing)
    if topic.endswith("/status"):
        print("[STATUS]", topic, payload, "retain=", msg.retain)

    elif topic.endswith("/telemetry"):
        print("[TELE]", topic, payload, "qos=", msg.qos)

    else:
        print("[OTHER]", topic, payload)

# gắn callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# ====== (D) 4) Connect ======
client.connect(HOST, PORT, KEEPALIVE)

# ====== (E) 5) Loop start ======
client.loop_start()
print("RUN... Ctrl+C to stop")

try:
    while True:
        time.sleep(SLEEP_MAIN)

except KeyboardInterrupt:
    print("Stop")

finally:
    # cleanup gọn (disconnect trước cho ghi gói xong)
    try:
        if client.is_connected():
            client.disconnect()
            time.sleep(0.2)
    except:
        pass

    client.loop_stop()
    print("EXIT")
