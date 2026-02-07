
"""
    THỨ TỰ CODE
1. tạo client
2. will_set(...)
3. gắn callbacks (on_connect, on_disconnect, on_publish)
4. connect(...)
5. loop_start()

"""

from paho.mqtt import client as mqtt
import time

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN"
)

client.will_set("devices/LUHAN/status", "offline", qos = 1, retain = True)

# Tự động kết nối lại sau khoảng thời gian
client.reconnect_delay_set(min_delay = 1 , max_delay = 30)

def on_connect(client : mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect",reason_code)
    # Lưu  trạng thái on/off của hệ thống
    client.publish("devices/LUHAN/status", "online", qos=1, retain=True)


def on_disconnect(client : mqtt.Client, userdata, reason_code, properties):
    print("Disconnect",reason_code)
    # Lưu  trạng thái on/off của hệ thống


def on_publish(client, userdata, mid, reason_code, properties):
    print("message id ",mid)


# gán các hàm cho thuộc tính (gắn callback)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish


client.connect("localhost", 1883, 60)

client.loop_start()

try:
    while True:
        if not client.is_connected():
            time.sleep(0.5)
            continue
        else:
            info = client.publish(
                topic = "testing",
                payload = "hi",
                qos = 1,
                retain = False
            )
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Chương trình đã kết thúc")