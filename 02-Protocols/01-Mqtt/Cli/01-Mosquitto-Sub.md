# 01-Mosquitto-Sub (MASTER)

> **Mục tiêu:** Sau khi học xong, bạn dùng `mosquitto_sub` để subscribe MQTT như “pro”: **đọc hiểu lệnh**, chọn đúng **topic/wildcard**, **QoS**, **retained**, **session**, **auth/TLS**, và **debug end‑to‑end** với `mosquitto_pub` + broker log. Cuối file có **FORM CHUẨN Python Subscriber (Level 8)** để bạn copy chạy và nhớ lâu.

---

## Mục lục

1. [Mosquitto & mosquitto_sub là gì?](#1-mosquitto--mosquitto_sub-là-gì)
2. [Form khởi động chuẩn (copy/paste)](#2-form-khởi-động-chuẩn-copypaste)
3. [Cú pháp chung & tư duy đọc lệnh](#3-cú-pháp-chung--tư-duy-đọc-lệnh)
4. [Topic & Wildcards: chọn đúng để không bị “mù”](#4-topic--wildcards-chọn-đúng-để-không-bị-mù)
5. [QoS 0/1/2 khi subscribe](#5-qos-012-khi-subscribe)
6. [Retained messages: vì sao “vào sau vẫn thấy”](#6-retained-messages-vì-sao-vào-sau-vẫn-thấy)
7. [Session: clean vs persistent (cơ bản)](#7-session-clean-vs-persistent-cơ-bản)
8. [Các lệnh thường dùng (kèm giải thích + ví dụ)](#8-các-lệnh-thường-dùng-kèm-giải-thích--ví-dụ)
9. [Bảng tổng hợp flags phổ biến](#9-bảng-tổng-hợp-flags-phổ-biến)
10. [Debug end-to-end: broker log + pub/sub](#10-debug-end-to-end-broker-log--pubsub)
11. [Lỗi thường gặp & cách xử lý nhanh](#11-lỗi-thường-gặp--cách-xử-lý-nhanh)
12. [Bài tập thực hành](#12-bài-tập-thực-hành)
13. [FORM CHUẨN Python Subscriber (Level 8)](#13-form-chuẩn-python-subscriber-level-8)
14. [Roadmap 10 level Subscriber (map theo Publisher)](#14-roadmap-10-level-subscriber-map-theo-publisher)

---

## 1. Mosquitto & mosquitto_sub là gì?

### 1.1 Mosquitto (Broker)

**Mosquitto** là MQTT **broker** (máy chủ trung gian).

> **Publisher** publish lên broker → broker **forward** cho **Subscriber** theo topic.

### 1.2 mosquitto_sub (Subscriber CLI)

`mosquitto_sub` là tool CLI để:

* kết nối broker
* subscribe topic filter
* in message ra terminal

**Dùng để debug cực nhanh**:

* broker có chạy không?
* topic đúng chưa?
* wildcard match đúng chưa?
* retained có hoạt động không?
* QoS nhận có đúng không?

---

## 2. Form khởi động chuẩn (copy/paste)

> Copy dùng ngay, đổi đúng `HOST/PORT/TOPIC`.

### 2.1 Form tối thiểu (local)

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -v
```

**Giải thích (đọc là hiểu):**

* `-h localhost`: broker ở máy bạn
* `-p 1883`: port MQTT thường (không TLS)
* `-t "test/#"`: nghe mọi topic dưới nhánh `test/`
* `-v`: in **topic + payload** (rất nên bật khi debug)

### 2.2 Form “chuẩn bài” (client_id + QoS + verbose + debug)

```bat
mosquitto_sub -h localhost -p 1883 -t "devices/+/telemetry" -q 1 -i sub1 -v -d
```

* `-i sub1`: đặt client_id để broker log nhìn phát biết ai
* `-q 1`: QoS subscribe
* `-d`: bật debug log phía client (nhiều chữ, dùng khi cần)

### 2.3 Form IoT chuẩn: nghe status + telemetry (2 terminal)

**Terminal A (status):**

```bat
mosquitto_sub -h localhost -p 1883 -t "devices/+/status" -q 1 -v
```

**Terminal B (telemetry):**

```bat
mosquitto_sub -h localhost -p 1883 -t "devices/+/telemetry" -q 1 -v
```

### 2.4 Form remote (auth)

```bat
mosquitto_sub -h <HOST> -p 1883 -t "sensors/#" -q 1 -i sub1 -u <USER> -P <PASS> -v
```

### 2.5 Form TLS (cơ bản)

**Verify CA (thường port 8883):**

```bat
mosquitto_sub -h <HOST> -p 8883 --cafile <CA.pem> -t "sensors/#" -q 1 -v
```

**Mutual TLS (client cert/key):**

```bat
mosquitto_sub -h <HOST> -p 8883 --cafile <CA.pem> --cert <client.crt> --key <client.key> -t "sensors/#" -q 1 -v
```

---

## 3. Cú pháp chung & tư duy đọc lệnh

### 3.1 Cú pháp

```text
mosquitto_sub [options]
```

### 3.2 Tư duy đọc lệnh (5 câu hỏi)

Khi nhìn một lệnh `mosquitto_sub`, đọc theo thứ tự:

1. **Kết nối tới đâu?** `-h`, `-p`, (auth: `-u`, `-P`), (TLS: `--cafile`)
2. **Nghe topic nào?** `-t` + wildcard `+/#`
3. **Chọn QoS nhận?** `-q`
4. **In ra thế nào?** `-v` (topic + payload)
5. **Có cần debug?** `-d` (client debug log)

> Tip nhớ nhanh: **Sub = chỉ cần host/port + topic filter + cách in** (không có payload).

---

## 4. Topic & Wildcards: chọn đúng để không bị “mù”

### 4.1 Topic là gì?

Topic là chuỗi phân cấp dạng đường dẫn:

* `test/a`
* `sensors/room1/temp`
* `devices/esp32-01/status`

### 4.2 Wildcards (cực quan trọng)

MQTT có 2 wildcard:

#### `#` (multi-level)

* Match **tất cả cấp phía sau**
* Chỉ đứng **cuối topic filter**

Ví dụ:

* `test/#` match: `test/a`, `test/a/b`, `test/a/b/c`...

#### `+` (single-level)

* Match **đúng 1 cấp**

Ví dụ:

* `devices/+/status` match: `devices/LUHAN/status`, `devices/ESP32/status`...
* Không match: `devices/LUHAN/sensors/status` (vì nhiều cấp)

### 4.3 Best practice chọn topic

* Tách **state** và **data**:

  * `devices/<id>/status` (retain)
  * `devices/<id>/telemetry` (không retain)
* Debug toàn hệ thống thì dùng `#` tạm thời, xong nhớ thu hẹp lại.

---

## 5. QoS 0/1/2 khi subscribe

### 5.1 Ý nghĩa nhanh

* QoS 0: nhanh, có thể mất
* QoS 1: ít mất hơn, có thể trùng
* QoS 2: đúng 1 lần, nặng nhất

### 5.2 QoS trong subscribe nghĩa là gì?

Khi bạn `mosquitto_sub -q 1`, bạn nói với broker:

> “Tôi muốn nhận message với QoS tối đa là 1.”

**Quy tắc vàng:** QoS thực tế khi nhận = **min(QoS publish, QoS subscribe)**.

**Test nhanh (copy):**

1. Sub:

```bat
mosquitto_sub -h localhost -p 1883 -t test/# -q 1 -v
```

2. Pub QoS0 và QoS1:

```bat
mosquitto_pub -h localhost -p 1883 -t test/a -m "PUB_QOS0" -q 0
mosquitto_pub -h localhost -p 1883 -t test/a -m "PUB_QOS1" -q 1
```

---

## 6. Retained messages: vì sao “vào sau vẫn thấy”

### 6.1 Retain là gì?

Nếu publisher publish với `retain=true`, broker sẽ **lưu message cuối** của topic đó.
Subscriber vào sau subscribe sẽ **nhận ngay retained**.

### 6.2 Test retain nhanh (copy)

**Publish retained:**

```bat
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/status -m "online" -q 1 -r
```

**Subscribe (vào sau vẫn thấy):**

```bat
mosquitto_sub -h localhost -p 1883 -t devices/LUHAN/status -v
```

### 6.3 Xoá retained

```bat
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/status -n -r
```

> Gợi ý nhớ nhanh: **Retain dùng cho state** (status/config), **không dùng cho telemetry**.

---

## 7. Session: clean vs persistent (cơ bản)

### 7.1 Ý tưởng

* **Clean session:** vào là mới, thoát là mất trạng thái
* **Persistent session:** broker nhớ trạng thái theo `client_id` (tuỳ cấu hình broker và client)

### 7.2 Tại sao subscriber cần session?

* Muốn reconnect mà vẫn “giữ ngữ cảnh” tốt.
* Nhưng để **nhận lại data trong lúc offline**, hệ thống thường dùng:

  * **Publisher queue/flush (Level 8 publisher)**, hoặc
  * cơ chế lưu lịch sử/DB riêng (ngoài MQTT).

---

## 8. Các lệnh thường dùng (kèm giải thích + ví dụ)

### 8.1 Sub 1 topic

```bat
mosquitto_sub -h localhost -p 1883 -t testing -v
```

### 8.2 Sub theo nhánh (multi-level)

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -v
```

### 8.3 Sub đúng 1 cấp (single-level)

```bat
mosquitto_sub -h localhost -p 1883 -t "devices/+/status" -v
```

### 8.4 Debug mode (client log)

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -i sub1 -v -d
```

### 8.5 Auth

```bat
mosquitto_sub -h <HOST> -p 1883 -t "sensors/#" -u <USER> -P <PASS> -v
```

### 8.6 TLS

```bat
mosquitto_sub -h <HOST> -p 8883 --cafile <CA.pem> -t "sensors/#" -v
```

---

## 9. Bảng tổng hợp flags phổ biến

| Mục tiêu  | Flag       | Ý nghĩa                  | Ví dụ                   |
| --------- | ---------- | ------------------------ | ----------------------- |
| Host      | `-h`       | Broker host              | `-h localhost`          |
| Port      | `-p`       | Broker port              | `-p 1883`               |
| Topic     | `-t`       | Topic filter             | `-t "devices/+/status"` |
| QoS       | `-q`       | QoS subscribe (0/1/2)    | `-q 1`                  |
| Verbose   | `-v`       | In `topic payload`       | `-v`                    |
| Debug     | `-d`       | Log debug phía client    | `-d`                    |
| Client ID | `-i`       | Đặt client_id            | `-i sub1`               |
| Username  | `-u`       | Username                 | `-u user`               |
| Password  | `-P`       | Password                 | `-P pass`               |
| TLS CA    | `--cafile` | CA cert (verify server)  | `--cafile ca.pem`       |
| TLS cert  | `--cert`   | Client cert (mutual TLS) | `--cert client.crt`     |
| TLS key   | `--key`    | Client key (mutual TLS)  | `--key client.key`      |

---

## 10. Debug end-to-end: broker log + pub/sub

### 10.1 Mở broker log (verbose)

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

Bạn sẽ thấy:

* `New client connected ... as <client_id>`
* `Received SUBSCRIBE ...` + topic
* `Received PUBLISH ...`
* `Sending PUBLISH to ...`
* `PINGREQ/PINGRESP` (keepalive)

### 10.2 Mở subscriber

```bat
mosquitto_sub -h localhost -p 1883 -t "#" -v
```

### 10.3 Publish test

```bat
mosquitto_pub -h localhost -p 1883 -t test/a -m "hello"
```

---

## 11. Lỗi thường gặp & cách xử lý nhanh

### 11.1 Sub không thấy message

Checklist 10 giây:

1. Broker chạy chưa?
2. `-t` sub có match `-t` pub không?
3. Bạn có bật `-v` để thấy topic không?
4. Pub trước, sub sau: QoS0 sẽ mất → muốn “vào sau vẫn thấy” thì pub retained.

### 11.2 Nhầm topic (testing vs test)

* Sub `testing/#` nhưng pub `test/a` → không thấy.

### 11.3 Bị spam khi sub `#`

* Thu hẹp filter (vd `devices/+/telemetry`).

---

## 12. Bài tập thực hành

1. Sub `test/#`, pub `test/a` và `test/a/b`.
2. Sub `test/+`, pub `test/a` và `test/a/b` để thấy khác nhau.
3. Test QoS: sub QoS1, pub QoS0/QoS1.
4. Test retain: pub retained status, tắt sub, mở lại.
5. Xoá retained bằng `-n -r`.

---

## 13. FORM CHUẨN Python Subscriber (Level 8)

> **Ý tưởng:** Subscriber không “queue bù” được như publisher. Subscriber nhiệm vụ là: **biết disconnect**, **tự reconnect**, **resubscribe**, và **tách xử lý status/telemetry** để nhận bù do publisher flush (nếu publisher Level 8 có queue/flush).

### 13.1 Form chuẩn (copy chạy)

```python
"""
LEVEL 8 - Subscriber chuẩn vị trí (match với pub Level 8)
Mục tiêu:
- Mất broker -> on_disconnect biết, tự reconnect
- Broker lên lại -> on_connect chạy lại -> tự subscribe lại
- Tách xử lý theo topic: /status vs /telemetry

THỨ TỰ CODE
1) tạo client
2) (tuỳ chọn) auth/tls
3) gắn callbacks (on_connect, on_disconnect, on_message)
4) connect(...)
5) loop_start()
"""

from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage
import time

# ====== (A) Cấu hình ======
CLIENT_ID = "LUHAN_SUB"
HOST = "localhost"
PORT = 1883
KEEPALIVE = 60

TOPIC_STATUS_FILTER    = "devices/+/status"
TOPIC_TELEMETRY_FILTER = "devices/+/telemetry"

SLEEP_MAIN = 0.2

# ====== (B) 1) Tạo client ======
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID
)

# (Tuỳ chọn Level 7) backoff reconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)

# ====== (C) 3) Callbacks ======
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Connect:", reason_code)

    # Subscribe trong on_connect để reconnect là tự sub lại
    client.subscribe(TOPIC_STATUS_FILTER, qos=1)
    print("[SUB]", TOPIC_STATUS_FILTER, "qos=1")

    client.subscribe(TOPIC_TELEMETRY_FILTER, qos=1)
    print("[SUB]", TOPIC_TELEMETRY_FILTER, "qos=1")

def on_disconnect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Disconnect:", reason_code)

    # Thử reconnect (fail thì thôi)
    try:
        client.reconnect()
    except:
        pass

def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    if topic.endswith("/status"):
        print("[STATUS]", topic, payload, "retain=", msg.retain)

    elif topic.endswith("/telemetry"):
        print("[TELE]", topic, payload, "qos=", msg.qos)

    else:
        print("[OTHER]", topic, payload)

# gắn callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# ====== (D) 4) Connect ======
client.connect(HOST, PORT, KEEPALIVE)

# ====== (E) 5) Loop start ======
client.loop_start()
print("RUN... Ctrl+C to stop")

try:
    while True:
        time.sleep(SLEEP_MAIN)

except KeyboardInterrupt:
    print("Stop")

finally:
    # cleanup gọn (disconnect trước cho kịp gửi gói)
    try:
        if client.is_connected():
            client.disconnect()
            time.sleep(0.2)
    except:
        pass

    client.loop_stop()
    print("EXIT")
```

### 13.2 Giải thích “từng khối” (đọc là nhớ)

* **(A) Cấu hình:** host/port/keepalive + 2 filter topic

  * `devices/+/status` (state, thường retain)
  * `devices/+/telemetry` (data)
* **(B) Client:** tạo client + `client_id` để broker log dễ nhìn
* **Backoff reconnect:** khi rớt mạng, reconnect tăng dần, đỡ spam
* **on_connect:** subscribe ở đây để reconnect tự sub lại
* **on_disconnect:** biết mất kết nối và thử reconnect
* **on_message:** router theo topic → sau này bạn thay `print(...)` thành parse JSON / tính toán / lưu DB
* **loop_start + while:** loop chạy nền, `while` giữ chương trình sống
* **finally:** dọn dẹp gọn

### 13.3 Test nhanh với mosquitto_pub (copy)

**Status (retain):**

```bat
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/status -m "online" -q 1 -r
```

**Telemetry:**

```bat
mosquitto_pub -h localhost -p 1883 -t devices/LUHAN/telemetry -m "hi" -q 1
```

---

## 14. Roadmap 10 level Subscriber (map theo Publisher)

> Map theo đúng tinh thần bạn đang học (Pub 1→10). Subscriber không “queue” được thay publisher, nên Level 8 của sub là **reconnect + state recovery**.

1. **Lv1:** sub tối thiểu (`-t`, `-v`) / Python `on_message`
2. **Lv2:** wildcard `+/#` (đọc topic filter đúng)
3. **Lv3:** QoS subscribe + min(pub, sub)
4. **Lv4:** retained (status/state)
5. **Lv5:** callback chuẩn + format log (topic/qos/retain)
6. **Lv6:** loop_forever vs loop_start
7. **Lv7:** reconnect/backoff + subscribe trong on_connect
8. **Lv8:** status recovery bằng retained + nhận bù do publisher flush
9. **Lv9:** parse JSON + seq/ts để phát hiện mất gói (nếu publisher gửi)
10. **Lv10:** production: auth/TLS + logging + crash-safe + metrics
