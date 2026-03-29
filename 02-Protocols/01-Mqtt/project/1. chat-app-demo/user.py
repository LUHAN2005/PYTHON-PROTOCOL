
# //=== 1. CÁC THƯ VIỆN ===\\
from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage
import time

# //=== 2. CẤU HÌNH THAM SỐ ===\\
User = input("Nhập tên :")
Room = input("Nhập phòng :")
Topic = f"chat/{Room}"
HOST = "localhost"
PORT = 1883
KEEPALIVE = 60


# //=== 3. KHỞI TẠO CÁC ĐỐI TƯỢNG ===\\
client_sub = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = f"{User}-sub"
)

client_pub = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id = f"{User}-pub"
)

client_pub.reconnect_delay_set(min_delay = 1, max_delay =30)
client_sub.reconnect_delay_set(min_delay = 1, max_delay =30)

# //=== 4. CALLBACK ===\\
# === SUB ===
def on_connect_sub(client : mqtt.Client, userdata, flags, reason_code, properties):
    print(User, "Connect :",reason_code)
    client.subscribe(topic = Topic, qos = 1)

def on_message_sub(client, userdata, msg):
    text = msg.payload.decode(errors="ignore")
    print("\n" + text)       # xuống dòng trước cho khỏi dính prompt
    print("Nhập: ", end="", flush=True)  # in lại prompt cho người dùng


def on_disconnect_sub(client : mqtt.Client, userdata, flags, reason_code, properties):
    print(User, "Disconnect :",reason_code)
    try:
        client.reconnect()
    except:
        pass

# === PUB ===
def on_connect_pub(client : mqtt.Client, userdata, flags, reason_code, properties):
    print(User, "Connect :",reason_code)

def on_disconnect_pub(client : mqtt.Client, userdata, flags, reason_code, properties):
    print(User, "Disconnect :",reason_code)
    try:
        client.reconnect()
    except:
        pass

# //=== 5. GẮN CALLBACK ===\\
client_pub.on_connect = on_connect_pub
client_pub.on_disconnect = on_disconnect_pub

client_sub.on_connect = on_connect_sub
client_sub.on_disconnect = on_disconnect_sub
client_sub.on_message = on_message_sub


# //=== 6. KẾT NỐI ===\\
client_sub.connect(HOST,PORT,KEEPALIVE)
client_pub.connect(HOST,PORT,KEEPALIVE)

client_sub.loop_start()
client_pub.loop_start()

try:
    while True:
        pub_text = input("Nhập: ").strip()
        if not pub_text:
            continue
        payload = f"{User}: {pub_text}"
        client_pub.publish(Topic, payload, qos=1, retain=False)
except KeyboardInterrupt:
    print("chương trình kết thúc")
finally:
    client_pub.disconnect()
    client_sub.disconnect()
    time.sleep(0.2)
    client_pub.loop_stop()
    client_sub.loop_stop()
    print("Bye!")

