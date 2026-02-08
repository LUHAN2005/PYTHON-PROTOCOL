# README.md — MQTT Pub/Sub (PSEUDO + Giải thích) (Basic)

> Mục tiêu: File này là **tổng hợp góc nhìn bao quát** về MQTT Publisher/Subscriber.
>
> * Có **mã giả dạng form khung** để nhớ cấu trúc và điền logic vào.
> * Có **giải thích ý nghĩa** từng phần: viết ở đâu, vì sao viết như vậy.
> * Có **lệnh CLI copy/paste** để test nhanh.

---

## 1) MQTT trong 1 câu

> **Publisher** publish message lên **Broker** theo **topic** → Broker **forward** cho **Subscriber** đang subscribe topic đó.

* **Topic** = “kênh” phân cấp dạng đường dẫn (`devices/LUHAN/telemetry`)
* **Payload** = bytes (text/JSON/binary tuỳ bạn)

---

## 2) Pub vs Sub: giống & khác

### 2.1 Vì sao file pub/sub nhìn giống nhau?

Vì cả hai đều là **MQTT client**, nên đều phải:

* tạo client
* connect
* chạy loop (để nhận/gửi gói mạng)
* có callbacks (connect/disconnect/message)

=> Khác nhau chủ yếu ở **logic chính**:

* **Publisher**: tạo payload → `publish(...)`
* **Subscriber**: `subscribe(...)` → nhận message trong `on_message(...)`

### 2.2 Nhớ nhanh

* **Sub = subscribe + on_message xử lý**
* **Pub = tạo payload + publish gửi**

---

## 3) 3 khái niệm quan trọng: wildcard / QoS / retain

### 3.1 Wildcards (chỉ dùng khi SUB)

* `#` = multi-level (nhiều cấp), chỉ đứng cuối: `test/#`
* `+` = single-level (đúng 1 cấp): `devices/+/status`

### 3.2 QoS (0/1/2)

* QoS 0: nhanh, có thể mất
* QoS 1: chắc hơn, có thể trùng
* QoS 2: đúng 1 lần, nặng

**Quy tắc vàng:** QoS nhận thực tế = **min(QoS publish, QoS subscribe)**

### 3.3 Retain (giữ message cuối)

* Publisher gửi retain=True → broker lưu **message cuối** của topic
* Subscriber vào sau subscribe → nhận ngay retained

**Best practice:**

* `status` (state) → retain=True
* `telemetry` (data) → retain=False

---

## 4) Thứ tự viết code “chuẩn vị trí” (cả Pub & Sub)

> Đây là thứ tự chuẩn giúp tránh lỗi “lạ”, và reconnect/sub lại hoạt động đúng.

1. **Imports** (mqtt, time, json...)
2. **Config** (HOST/PORT/KEEPALIVE, CLIENT_ID, TOPIC...)
3. **Create client** (`mqtt.Client(...)`)
4. **Set options BEFORE connect** *(nếu cần)*

   * `will_set(...)` (LWT) → **phải trước connect**
   * `username_pw_set(...)`, TLS
   * `reconnect_delay_set(...)`
5. **Define callbacks** (`on_connect`, `on_disconnect`, ...)
6. **Attach callbacks** (`client.on_connect = ...`)
7. **connect(...)**
8. **Start loop** (`loop_forever()` hoặc `loop_start()`)
9. **Main logic**

   * Pub: tạo payload + publish + queue/flush
   * Sub: xử lý chủ yếu trong on_message
10. **Cleanup** (Ctrl+C: disconnect + stop loop)

---

## 5) Callback/hàm: dùng để làm gì?

### 5.1 `on_connect(...)`

* **Khi chạy:** khi client connect xong (thành công hoặc fail → xem `reason_code`).
* **Sub dùng để:** subscribe ở đây để reconnect tự subscribe lại.
* **Pub dùng để:** publish trạng thái `online` (retain) ở đây.

### 5.2 `on_disconnect(...)`

* **Khi chạy:** khi mất kết nối.
* **Dùng để:** log offline, set flag, thử reconnect.

> Lưu ý: signature callback phải đúng (đủ tham số) để tránh crash thread.

### 5.3 `on_message(...)` (quan trọng nhất của SUB)

* **Khi chạy:** khi nhận PUBLISH match subscription.
* **Dùng để:** decode payload, parse JSON, tách status/telemetry, tính toán/lưu/vẽ.

### 5.4 `on_publish(...)` (tuỳ chọn ở PUB)

* **Khi chạy:** khi publish hoàn tất (đặc biệt QoS1/2).
* **Dùng để:** debug/đếm mid.

---

## 6) Quy tắc đặt Topic & Payload (IoT basic mà chuẩn)

### 6.1 Topic là gì?

**Topic = chuỗi phân cấp dùng để định tuyến (routing)**.
Broker không “hiểu nghĩa” topic; broker chỉ **match topic filter** của subscriber.

Ví dụ topic:

* `devices/LUHAN/status`
* `devices/LUHAN/telemetry`
* `env/room1/temp`

### 6.2 Cấu trúc topic khuyến nghị

Mẫu phổ biến (IoT basic):

* **State (retain):** `devices/<device_id>/status`
* **Data (no retain):** `devices/<device_id>/telemetry`
* (tuỳ) **Command:** `devices/<device_id>/cmd` hoặc `devices/<device_id>/cmd/<action>`

Ví dụ:

* `devices/LUHAN/status`
* `devices/LUHAN/telemetry`
* `devices/LUHAN/cmd/reboot`

### 6.3 Best practice khi đặt topic

**(1) Tách state và data**

* `status` → retain=True (online/offline/config)
* `telemetry` → retain=False (dữ liệu liên tục)

**(2) Đặt để subscriber dễ wildcard**
Nếu theo mẫu `devices/<id>/<kind>` thì sub cực tiện:

* status của mọi device: `devices/+/status`
* telemetry của mọi device: `devices/+/telemetry`
* debug tất cả dưới devices: `devices/#`

**(3) Đừng nhét dữ liệu vào topic**
Không nên:

* `devices/LUHAN/telemetry/5cm`

Nên:

* `devices/LUHAN/telemetry` + payload chứa `h_cm=5`

**(4) Quy ước đặt tên để đỡ lỗi**

* không dấu cách
* tránh ký tự lạ
* thống nhất chữ thường nếu team thích
* không thêm dấu `/` ở cuối

### 6.4 Cách lấy/route theo topic ở Subscriber

**Cách A — Route nhanh theo đuôi topic**

* `topic.endswith("/status")` → xử lý state
* `topic.endswith("/telemetry")` → xử lý data

**Cách B — Tách cấp bằng `split("/")` để lấy device_id**
Nếu topic theo mẫu `devices/<id>/<kind>`:

* `parts = topic.split("/")`
* `parts[0]` = `devices`
* `parts[1]` = `<device_id>`
* `parts[2]` = `status` hoặc `telemetry`

**Cách C — Match chính xác (khi cần)**

* `topic == "devices/LUHAN/status"`

### 6.5 Payload là gì?

**Payload = bytes**. Bạn có thể gửi:

* text: `"hi"`
* số (dưới dạng string): `"27.5"`
* JSON: `{ "temp": 27.5 }`
* binary: file

> MQTT không tự hiểu JSON. JSON chỉ là quy ước tầng ứng dụng của bạn.

### 6.6 Quy tắc payload (dễ parse + dễ mở rộng)

**Option 1 — Text đơn giản (dễ nhất):**

* payload = `"5"` (ví dụ h_cm)

**Option 2 — JSON (chuẩn mở rộng):**

* payload = `{ "h_cm": 5, "ts": 1700000000, "seq": 12 }`

Gợi ý schema JSON tối thiểu cho telemetry:

* `ts` (timestamp)
* `seq` (số thứ tự tăng dần)
* các field data (`h_cm`, `temp`, ...)

### 6.7 Cách đọc payload ở Subscriber (tư duy)

1. `msg.payload` (bytes)
2. decode → string (nếu là text/JSON)
3. (tuỳ) `.strip()` bỏ `\n`/space thừa
4. nếu JSON → parse → lấy field
5. tính toán/lưu/vẽ

---

## 7) FORM KHUNG — Subscriber Level 8 (điền logic vào là chạy)

> Đây là **khung sườn** để bạn copy rồi **điền TODO** (logic) vào trong. Không nhồi code nâng cao.

```python
"""SUB LEVEL 8 — SKELETON
- Reconnect + resubscribe
- Router status/telemetry trong on_message
"""

from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage
import time

# ===== (A) CONFIG =====
CLIENT_ID = "SUB_1"
HOST, PORT, KEEPALIVE = "localhost", 1883, 60

TOPIC_STATUS_FILTER    = "devices/+/status"
TOPIC_TELEMETRY_FILTER = "devices/+/telemetry"

# ===== (B) CREATE CLIENT =====
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID
)

# (tuỳ chọn) backoff reconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)

# ===== (C) CALLBACKS =====
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    """Gọi khi connect xong. Sub ở đây để reconnect là tự sub lại."""
    print("Connect:", reason_code)

    # TODO: nếu connect OK thì subscribe các filter topic
    # client.subscribe(TOPIC_STATUS_FILTER, qos=1)
    # client.subscribe(TOPIC_TELEMETRY_FILTER, qos=1)


def on_disconnect(client: mqtt.Client, userdata, flags, reason_code, properties):
    """Gọi khi rớt mạng/broker down."""
    print("Disconnect:", reason_code)

    # TODO: thử reconnect (fail thì thôi)
    # try:
    #     client.reconnect()
    # except:
    #     pass


def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
    """Gọi khi nhận message match subscription."""
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    # TODO: router theo topic để xử lý
    if topic.endswith("/status"):
        # TODO: xử lý state (online/offline), dùng msg.retain để biết retained
        # print("[STATUS]", topic, payload, "retain=", msg.retain)
        pass

    elif topic.endswith("/telemetry"):
        # TODO: xử lý data (parse/tính/lưu/vẽ)
        # print("[TELE]", topic, payload, "qos=", msg.qos)
        pass

    else:
        # TODO: nếu bạn sub rộng (devices/#) thì xử lý thêm ở đây
        pass


# ===== (D) ATTACH CALLBACKS =====
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# ===== (E) CONNECT + LOOP =====
client.connect(HOST, PORT, KEEPALIVE)
client.loop_start()
print("RUN... Ctrl+C to stop")

# ===== (F) MAIN LIFETIME =====
try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    print("Stop")
finally:
    # cleanup
    try:
        if client.is_connected():
            client.disconnect()
            time.sleep(0.2)
    except:
        pass
    client.loop_stop()
```

---

## 8) FORM KHUNG — Publisher Level 8 (điền logic vào là chạy)

> Đây là **khung sườn** publisher: offline queue, online flush. Bạn chỉ việc điền TODO.

```python
"""PUB LEVEL 8 — SKELETON
- LWT offline (will_set) trước connect
- on_connect: publish status online (retain)
- offline: queue
- online: flush queue rồi publish hiện tại
"""

from paho.mqtt import client as mqtt
import time

# ===== (A) CONFIG =====
DEVICE_ID = "PUB_1"
HOST, PORT, KEEPALIVE = "localhost", 1883, 60

TOPIC_TELEMETRY = f"devices/{DEVICE_ID}/telemetry"  # retain=False
TOPIC_STATUS    = f"devices/{DEVICE_ID}/status"     # retain=True

PUBLISH_INTERVAL = 0.5
OFFLINE_SLEEP    = 0.2
MAX_QUEUE        = 500

# ===== (B) QUEUE =====
queue = []  # FIFO: (topic, payload)

# ===== (C) CREATE CLIENT =====
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=DEVICE_ID
)

# ===== (D) OPTIONS BEFORE CONNECT =====
# TODO: LWT (offline) — phải đặt TRƯỚC connect
# client.will_set(TOPIC_STATUS, "offline", qos=1, retain=True)

# (tuỳ chọn) backoff reconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)

# ===== (E) CALLBACKS =====
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect:", reason_code)

    # TODO: publish status online (retain)
    # client.publish(TOPIC_STATUS, "online", qos=1, retain=True)


def on_disconnect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Disconnect:", reason_code)


def on_publish(client: mqtt.Client, userdata, mid, reason_code, properties):
    # TODO: dùng để debug publish (tuỳ)
    pass


# ===== (F) ATTACH CALLBACKS =====
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# ===== (G) CONNECT + LOOP =====
client.connect(HOST, PORT, KEEPALIVE)
client.loop_start()

# ===== (H) MAIN LOOP =====
try:
    while True:
        # OFFLINE
        if not client.is_connected():
            # TODO: tạo payload telemetry
            # payload = ...
            payload = "TODO"

            # queue đầy -> drop cũ nhất
            if len(queue) >= MAX_QUEUE:
                queue.pop(0)
            queue.append((TOPIC_TELEMETRY, payload))

            # TODO: thử reconnect
            # try:
            #     client.reconnect()
            # except:
            #     pass

            time.sleep(OFFLINE_SLEEP)
            continue

        # ONLINE: flush queue trước
        while queue and client.is_connected():
            topic, payload = queue.pop(0)
            # TODO: publish message bù
            # client.publish(topic, payload, qos=1, retain=False)
            time.sleep(0.01)

        # ONLINE: publish message hiện tại
        # TODO: tạo payload hiện tại
        payload = "TODO"
        # client.publish(TOPIC_TELEMETRY, payload, qos=1, retain=False)

        time.sleep(PUBLISH_INTERVAL)

except KeyboardInterrupt:
    print("Stop")
finally:
    # cleanup
    try:
        if client.is_connected():
            client.disconnect()
            time.sleep(0.2)
    except:
        pass
    client.loop_stop()
```

---

## 9) COPY CLI — Test nhanh end-to-end

### 9.1 Sub (CLI)

* Nghe một nhánh:

```bat
mosquitto_sub -h localhost -p 1883 -t "devices/#" -v
```

* Nghe tất cả (debug nhanh, cẩn thận spam):

```bat
mosquitto_sub -h localhost -p 1883 -t "#" -v
```

### 9.2 Pub (CLI)

* Telemetry:

```bat
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/telemetry -m "hi" -q 1
```

* Status retained:

```bat
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/status -m "online" -q 1 -r
```

* Xoá retained:

```bat
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/status -n -r
```

* Telemetry JSON (PowerShell):

```powershell
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/telemetry -m '{"ts":1700000000,"seq":1,"h_cm":5}' -q 1
```

---

## 10) Debug broker log (khi cần nhìn hệ thống)

Chạy broker verbose:

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

Bạn sẽ thấy:

* CONNECT / DISCONNECT
* SUBSCRIBE
* PUBLISH forward
* PINGREQ/PINGRESP (keepalive)

---

## 11) Checklist nhanh khi “không nhận dữ liệu”

1. Broker chạy chưa?
2. Topic pub có match topic sub không?
3. Wildcard đúng chưa (`+` vs `#`)?
4. Có bật `-v` (CLI) hoặc in `msg.topic` (Python) chưa?
5. Sub vào sau mà muốn thấy state → pub retained.

---

## 12) Chốt ý “bù dữ liệu” để không nhầm

* **Publisher Level 8**: offline → queue → online → flush (gửi bù)
* **Subscriber**: reconnect + resubscribe → nhận bù **nếu publisher flush**

> Broker không tự bù telemetry “đã mất” nếu publisher không gửi lại.
