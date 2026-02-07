
from paho.mqtt import client as mqtt
import time

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN"
)

client.connect("localhost", 1883, 60)

# Khởi tạo luồng vòng lặp sử lý mạng
client.loop_start()

client.publish("testing", "hi")
time.sleep(0.02)

# dừng luồng thread do loop_start() tạo nên
client.loop_stop()
