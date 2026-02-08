

from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage
import time

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN_SUB"
)

client.reconnect_delay_set(min_delay=1, max_delay=30)

def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    if topic.endswith("/status"):
        print("[STATUS]", topic, payload, "retain=", msg.retain)

    elif topic.endswith("/telemetry"):
        print("[TELE]", topic, payload, "qos=", msg.qos)

    else:
        print("[OTHER]", topic, payload)


def on_connect(client : mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect:",reason_code)
    client.subscribe("devices/+/status", qos=1)     # state (retain)
    client.subscribe("devices/+/telemetry", qos=1)  # data (không retain)


def on_disconnect(client: mqtt.Client, userdata,flags, reason_code, properties):
    print("Disconnect:", reason_code)
    try:
        client.reconnect()
    except:
        pass

client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect("localhost", 1883, 60)

client.loop_start()
print("RUN... Ctrl+C to stop")

try:
    while True:
        # chỗ này sau này bạn có thể làm việc khác (vd in thống kê)
        time.sleep(0.2)
except KeyboardInterrupt:
    print("Stop")
finally:
    client.loop_stop()
    time.sleep(0.2)
    client.disconnect()
