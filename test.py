"""
SUB LEVEL 8 (BASIC)
- on_connect: subscribe status + telemetry (để reconnect tự sub lại)
- on_disconnect: reconnect
- on_message: tách status/telemetry
"""

from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage
import time

# Cấu hình tham số
CLIENT_ID = "LUHAN_SUB"
HOST, PORT, KEEPALIVE = "localhost", 1883, 60

TOPIC_STATUS_FILTER    = "devices/+/status"
TOPIC_TELEMETRY_FILTER = "devices/+/telemetry"

# kết nối
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.reconnect_delay_set(min_delay=1, max_delay=30)

def on_connect(client, userdata, flags, reason_code, properties):
    # Sử lý khi có kết nối
    pass

def on_disconnect(client, userdata, flags, reason_code, properties):
    print("Disconnect:", reason_code)
    try:
        client.reconnect()
    except:
        pass

def on_message(client, userdata, msg: MQTTMessage):
    #sử lý khi có thông tin
    pass

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(HOST, PORT, KEEPALIVE)
client.loop_start()
print("RUN... Ctrl+C to stop")


# sử lý logic 
try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    print("Stop")
finally:
    try:
        if client.is_connected():
            client.disconnect()
            time.sleep(0.2)
    except:
        pass
    client.loop_stop()
