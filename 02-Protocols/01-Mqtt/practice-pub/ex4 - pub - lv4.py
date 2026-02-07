
from paho.mqtt import client as mqtt
import time

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN"
)

client.connect("localhost", 1883, 60)

client.loop_start()

try:
    while True:
        info = client.publish("testing", "loop")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Chương trình đã dừng lại")


# client.loop_stop()
# client.disconnect()