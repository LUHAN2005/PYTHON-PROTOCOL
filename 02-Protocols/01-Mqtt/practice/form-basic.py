"""
LEVEL 8 - Publisher chuẩn vị trí
Mục tiêu: offline thì queue lại, online thì flush rồi gửi bình thường

THỨ TỰ CODE
1) tạo client
2) will_set(...)
3) gắn callbacks (on_connect, on_disconnect, on_publish)
4) connect(...)
5) loop_start()
"""

from paho.mqtt import client as mqtt
import time

# ====== (A) Cấu hình LEVEL 8 (bạn có thể đổi) ======
DEVICE_ID = "LUHAN"
TOPIC_TELEMETRY = f"devices/{DEVICE_ID}/telemetry"   # <-- telemetry (KHÔNG retain)
TOPIC_STATUS    = f"devices/{DEVICE_ID}/status"      # <-- status (retain)

HOST = "localhost"
PORT = 1883
KEEPALIVE = 60

PUBLISH_INTERVAL = 0.5       # <-- chu kỳ gửi bình thường (online)
OFFLINE_SLEEP    = 0.2       # <-- ngủ khi offline (đỡ CPU)
MAX_QUEUE = 500              # <-- giới hạn queue

# ====== (B) Queue LEVEL 8 ======
queue = []  # lưu tuple (topic, payload)

# ====== (C) 1) Tạo client ======
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=DEVICE_ID
)

# ====== (D) 2) LWT: phải đặt TRƯỚC connect ======
client.will_set(TOPIC_STATUS, "offline", qos=1, retain=True)

# (Tuỳ chọn Level 7) backoff reconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)

# ====== (E) 3) Callbacks ======
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect:", reason_code)
    # <-- chỗ này viết gì?
    # Gợi ý: báo trạng thái online (retain)
    client.publish(TOPIC_STATUS, "online", qos=1, retain=True)

def on_disconnect(client: mqtt.Client, userdata, reason_code, properties):
    print("Disconnect:", reason_code)

def on_publish(client: mqtt.Client, userdata, mid, reason_code, properties):
    print("Published mid:", mid)

# gắn callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# ====== (F) 4) Connect ======
try:
    client.connect(HOST, PORT, KEEPALIVE)
except Exception as e:
    print("Kết nối thất bại:", e)


# ====== (G) 5) Loop start ======
client.loop_start()

try:
    while True:
        # ====== (H) Nhánh OFFLINE ======
        if not client.is_connected():
            # <-- chỗ này viết gì?
            # Bạn tạo dữ liệu muốn gửi (payload) rồi queue lại
            payload = "hi"  # sau này thay bằng data thật / JSON

            # queue đầy thì drop cái cũ nhất
            if len(queue) >= MAX_QUEUE:
                queue.pop(0)

            # lưu message vào queue (FIFO)
            queue.append((TOPIC_TELEMETRY, payload))

            # thử kết nối lại
            try:
                client.reconnect()   # thử reconnect (nếu fail thì thôi)
            except:
                pass

            time.sleep(OFFLINE_SLEEP)
            continue

        # ====== (I) Nhánh ONLINE: flush queue trước ======
        while queue and client.is_connected():
            topic, payload = queue.pop(0)
            client.publish(topic, payload, qos=1, retain=False)
            time.sleep(0.01)  # chống dồn dập quá

        # ====== (J) Gửi message hiện tại (online) ======
        # <-- chỗ này viết gì?
        # Đây là message "thực tế" của vòng lặp hiện tại (không phải message bù)
        payload = "hi"  # sau này thay bằng data thật / JSON
        client.publish(TOPIC_TELEMETRY, payload, qos=1, retain=False)

        time.sleep(PUBLISH_INTERVAL)

except KeyboardInterrupt:
    print("Chương trình đã kết thúc")

finally:
    # cleanup gọn
    client.loop_stop()
    client.disconnect()
