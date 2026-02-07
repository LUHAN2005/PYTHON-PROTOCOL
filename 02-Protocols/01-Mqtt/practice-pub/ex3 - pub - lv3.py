
from paho.mqtt import client as mqtt

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = "LUHAN"
)

client.connect("localhost", 1883, 60)

# khởi tạo luồng thread vòng lặp
client.loop_start()

# khởi tạo đối tượng info
info = client.publish("testing", "complete")

# thời gian chờ để gửi message đến mqtt broker, tránh phải dùng time.sleep
info.wait_for_publish()

client.loop_stop()

# dừng kết nối với broker
client.disconnect()