
from paho.mqtt import client as mqtt
import time

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN"
)

topic = [
    "testing",
]

#Tên on_connect là quy ước: paho-mqtt sẽ gọi hàm này khi kết nối xong.
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected:", reason_code)

# Hàm này được gọi khi client bị ngắt kết nối (tự disconnect hoặc rớt mạng).
def on_disconnect(client, userdata, reason_code, properties):
    print("Disconnect", reason_code)

def on_publish(client, userdata, mid, reason_code, properties):
    print("Publish message id:", mid)

client.connect("localhost", 1883, 60)

# gán hàm cho thuộc tính
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

client.loop_start()

try:
    while True:
        client.publish(topic = topic[0] , payload = "hi", qos = 1, retain = False)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Chương trình đã kết thúc")