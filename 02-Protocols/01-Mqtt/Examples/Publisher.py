import time
from paho.mqtt import client as mqtt

client = mqtt.Client(
    client_id = "luhan",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.connect("localhost", 1883, 60)

client.loop_start()  # BẮT BUỘC để publish thực sự đi ra mạng

info = client.publish("testing", "hi", qos=0)
info.wait_for_publish()  # chờ gửi xong

time.sleep(0.1)  # đệm nhẹ cho chắc (tùy máy)
client.loop_stop()

client.disconnect()
