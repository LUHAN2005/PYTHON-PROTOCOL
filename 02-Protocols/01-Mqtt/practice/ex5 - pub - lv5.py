
from paho.mqtt import client as mqtt
import time

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN"
)

topic = [
    "devices/LUHAN/telemetry",
    "devices/LUHAN/status",
]

client.connect("localhost", 1883, 60)

client.loop_start()

try:
    while True:
        # thuộc tính retain lưu lại giá trị cuối cùng của message, thường dùng đẻ lưu lại trạng thái on/off
        client.publish(topic[0], "xin chao", qos = 1, retain = False)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Chương trình đã kết thúc")

