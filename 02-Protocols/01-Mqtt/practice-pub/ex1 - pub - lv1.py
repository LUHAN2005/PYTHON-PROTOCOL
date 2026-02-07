
from paho.mqtt import client as mqtt    # import thư viện mqtt

# Cú pháp khởi tạo đối tượng mqtt client (dạng class) 
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2, 
    client_id = "LUHAN"
)

# Kết nối client với mqtt broker
client.connect("localhost", 1883, 60)

# Khởi tạo vòng lặp mạng, dùng khi bạn muốn chương trình chạy mãi
# client.loop_forever()

# Đẩy dữ liệu lên mqtt broker qua lệnh publish
client.publish("testing", "hi")
