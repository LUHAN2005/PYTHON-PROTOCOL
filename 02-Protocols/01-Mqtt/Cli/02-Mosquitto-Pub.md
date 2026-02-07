# 02-Mosquitto-Pub (MASTER)

> **Mục tiêu:** Sau khi học xong, bạn có thể publish MQTT bằng `mosquitto_pub` “như pro”: gửi payload text/binary/JSON, QoS 0/1/2, retain, will message (LWT), username/password, TLS, và biết cách test end‑to‑end bằng `mosquitto_sub` + broker log.

---

## Mục lục

1. [Mosquitto_pub là gì? Dùng để làm gì?](#1-mosquitto_pub-là-gì-dùng-để-làm-gì)
2. [Workflow test chuẩn (nhìn là nhớ)](#2-workflow-test-chuẩn-nhìn-là-nhớ)
3. [Form chạy nhanh (copy/paste)](#3-form-chạy-nhanh-copypaste)
4. [Cú pháp chung & cách đọc lệnh](#4-cú-pháp-chung--cách-đọc-lệnh)
5. [Topic & payload: gửi gì lên broker?](#5-topic--payload-gửi-gì-lên-broker)
6. [QoS 0/1/2 khi publish](#6-qos-012-khi-publish)
7. [Retain: lưu trạng thái cuối](#7-retain-lưu-trạng-thái-cuối)
8. [Will Message (LWT): chết bất thường broker báo](#8-will-message-lwt-chết-bất-thường-broker-báo)
9. [Các lệnh thường dùng (kèm giải thích)](#9-các-lệnh-thường-dùng-kèm-giải-thích)
10. [Bảng tổng hợp flags phổ biến](#10-bảng-tổng-hợp-flags-phổ-biến)
11. [Debug end-to-end: broker log + mosquitto_sub](#11-debug-end-to-end-broker-log--mosquitto_sub)
12. [Lỗi thường gặp & cách xử lý nhanh](#12-lỗi-thường-gặp--cách-xử-lý-nhanh)
13. [FORM CHUẨN CODE Python Publisher (Level 8: offline queue/online flush)](#13-form-chuẩn-code-python-publisher-level-8-offline-queueonline-flush)
14. [Bài tập thực hành](#14-bài-tập-thực-hành)

---

## 1. Mosquitto_pub là gì? Dùng để làm gì?

### 1.1 `mosquitto_pub` (Publisher CLI)

`mosquitto_pub` là tool dòng lệnh để:

* Kết nối tới broker MQTT
* Publish message lên một topic

### 1.2 Vì sao phải master `mosquitto_pub`?

Vì nó là “dao mổ” debug nhanh:

* Broker có nhận message không?
* Topic đúng chưa?
* QoS/retain chạy đúng chưa?

> Khi code Python lỗi, bạn vẫn có thể test broker/topic bằng CLI trong 5 giây.

---

## 2. Workflow test chuẩn (nhìn là nhớ)

> Nhớ 3 cửa sổ (hoặc 3 tab terminal): **BROKER → SUB → PUB**

1. **BROKER (log verbose)**

* Mục tiêu: xem broker có nhận/gửi PUBLISH không

2. **SUB (nghe topic)**

* Mục tiêu: quan sát message thực tế đến subscriber

3. **PUB (bắn message)**

* Mục tiêu: gửi nhanh payload để test

---

## 3. Form chạy nhanh (copy/paste)

### 3.1 Form tối thiểu (local)

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi"
```

* `-h -p`: broker
* `-t`: topic
* `-m`: payload (string)

### 3.2 Form “chuẩn bài” (client id + QoS + retain)

```bat
mosquitto_pub -h localhost -p 1883 -t "test/retain" -m "LAST" -q 1 -r -i pub1
```

* `-q 1`: QoS 1
* `-r`: retain
* `-i pub1`: client id

### 3.3 Form remote (auth)

```bat
mosquitto_pub -h <HOST> -p 1883 -t "sensors/room1/temp" -m "27.5" -q 1 -u <USER> -P <PASS>
```

### 3.4 Form JSON (PowerShell dễ nhất)

```powershell
mosquitto_pub -h localhost -p 1883 -t sensors/room1/temp -m '{"temp":27.5,"unit":"C"}'
```

> Windows CMD escape JSON hơi mệt. Nếu cần, dùng PowerShell hoặc đưa JSON vào file rồi `-f`.

---

## 4. Cú pháp chung & cách đọc lệnh

### 4.1 Cú pháp

```text
mosquitto_pub [options]
```

### 4.2 Cách đọc 1 lệnh `mosquitto_pub` (đọc đúng thứ tự này)

1. **Publish đến đâu?** `-h`, `-p`, (TLS/auth nếu có)
2. **Topic nào?** `-t`
3. **Payload gì?** `-m` / `-n` / `-f` / stdin
4. **Độ đảm bảo?** `-q`
5. **Có lưu retained không?** `-r`

> Chỉ cần nhìn theo 5 câu hỏi này là đọc được 99% lệnh.

---

## 5. Topic & payload: gửi gì lên broker?

### 5.1 Topic

Topic là “kênh” để subscriber lọc message.

Ví dụ:

* `sensors/room1/temp`
* `devices/esp32-01/status`
* `alerts/fire`

### 5.2 Payload

Payload thực chất là **bytes**. Bạn có thể gửi:

* Text: `"hi"`
* Số (nhưng vẫn là string): `"27.5"`
* JSON: `{"temp":27.5}`
* Binary: file `.bin`

> MQTT không tự hiểu JSON. JSON chỉ là quy ước tầng ứng dụng.

---

## 6. QoS 0/1/2 khi publish

### 6.1 Ý nghĩa

* **QoS 0 (at most once):** nhanh, có thể mất, không ACK
* **QoS 1 (at least once):** có ACK, có thể trùng message
* **QoS 2 (exactly once):** đúng 1 lần, overhead cao

### 6.2 QoS thực tế ở subscriber

QoS nhận = **min(QoS publish, QoS subscribe)**.

Ví dụ:

* publish QoS1, subscribe QoS0 → nhận QoS0
* publish QoS2, subscribe QoS1 → nhận QoS1

---

## 7. Retain: lưu trạng thái cuối

### 7.1 Retain dùng khi nào?

Retain phù hợp với **trạng thái (state)**:

* `devices/x/status = online/offline`
* `sensors/room1/temp = 27.5` (nếu muốn ai vào sau cũng thấy nhiệt độ cuối)

Không phù hợp với “event spam” kiểu telemetry 10 message/giây.

### 7.2 Publish retained

```bat
mosquitto_pub -h localhost -p 1883 -t "devices/x/status" -m "online" -r
```

### 7.3 Xoá retained

Gửi **null payload** và bật `-r`:

```bat
mosquitto_pub -h localhost -p 1883 -t "devices/x/status" -n -r
```

---

## 8. Will Message (LWT): chết bất thường broker báo

### 8.1 LWT là gì?

**Last Will and Testament**: message broker sẽ publish thay bạn nếu client **mất kết nối bất thường** (crash, rớt mạng, mất điện).

### 8.2 Tư duy thiết kế online/offline chuẩn

* Khi connect thành công: publish retained `status=online`
* Set will (retained) `status=offline`
* Nếu client chết bất thường: broker publish `offline`

> Với Python (paho-mqtt) bạn dùng `will_set(...)` trước `connect()`.

> Với `mosquitto_pub`, một số bản có flags `--will-topic`, `--will-payload`, `--will-qos`, `--will-retain` (tên có thể khác tùy phiên bản). Nếu máy bạn không có, cứ ưu tiên hiểu concept và dùng Python để set will.

---

## 9. Các lệnh thường dùng (kèm giải thích)

### 9.1 Publish text (cơ bản)

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi"
```

* Dùng để test nhanh topic.

### 9.2 Publish QoS 1

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi" -q 1
```

* Dùng để thấy khác biệt QoS0 vs QoS1 (ACK, có thể trùng).

### 9.3 Publish retained state

```bat
mosquitto_pub -h localhost -p 1883 -t "devices/esp32-01/status" -m "online" -r
```

* Dùng cho trạng thái online/offline.

### 9.4 Publish JSON (PowerShell)

```powershell
mosquitto_pub -h localhost -p 1883 -t sensors/room1/temp -m '{"temp":27.5,"unit":"C"}'
```

* Dùng khi app tầng trên parse JSON.

### 9.5 Publish từ file (binary / blob)

```bat
mosquitto_pub -h localhost -p 1883 -t "files/blob" -f "path\to\data.bin"
```

* Dùng để bắn payload dạng bytes.

### 9.6 Publish null payload

```bat
mosquitto_pub -h localhost -p 1883 -t testing -n
```

* Dùng để gửi payload rỗng.

### 9.7 Loop publish (giả sensor) — PowerShell

```powershell
1..10 | % { mosquitto_pub -h localhost -p 1883 -t sensors/room1/temp -m "$_"; Start-Sleep -Milliseconds 200 }
```

* Dùng để test subscriber đang nhận liên tục.

### 9.8 Auth username/password

```bat
mosquitto_pub -h <HOST> -p 1883 -t testing -m "hi" -u <USER> -P <PASS>
```

* Dùng khi broker bật auth.

### 9.9 TLS cơ bản

**Verify CA:**

```bat
mosquitto_pub -h <HOST> -p 8883 --cafile <CA.pem> -t testing -m "hi"
```

**Mutual TLS:**

```bat
mosquitto_pub -h <HOST> -p 8883 --cafile <CA.pem> --cert <client.crt> --key <client.key> -t testing -m "hi"
```

---

## 10. Bảng tổng hợp flags phổ biến

| Mục tiêu     | Flag       | Ý nghĩa          | Ví dụ               |
| ------------ | ---------- | ---------------- | ------------------- |
| Host         | `-h`       | Broker host      | `-h localhost`      |
| Port         | `-p`       | Broker port      | `-p 1883`           |
| Topic        | `-t`       | Topic publish    | `-t testing`        |
| Message      | `-m`       | Payload string   | `-m "hi"`           |
| Null payload | `-n`       | Payload rỗng     | `-n`                |
| File payload | `-f`       | Payload từ file  | `-f data.bin`       |
| QoS          | `-q`       | QoS publish      | `-q 1`              |
| Retain       | `-r`       | Retained message | `-r`                |
| Client ID    | `-i`       | client_id        | `-i pub1`           |
| Username     | `-u`       | username         | `-u user`           |
| Password     | `-P`       | password         | `-P pass`           |
| TLS CA       | `--cafile` | CA cert          | `--cafile ca.pem`   |
| TLS cert     | `--cert`   | client cert      | `--cert client.crt` |
| TLS key      | `--key`    | client key       | `--key client.key`  |

---

## 11. Debug end-to-end: broker log + mosquitto_sub

### 11.1 Chạy broker verbose (Windows ví dụ)

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

* `-v`: verbose log
* `-p 1883`: port

### 11.2 Mở subscriber quan sát

```bat
mosquitto_sub -h localhost -p 1883 -t "#" -v
```

* `-t "#"`: nghe tất cả topic
* `-v`: in kèm topic

### 11.3 Publish test

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi"
```

**Kỳ vọng thấy:**

* SUB in: `testing hi`
* BROKER log có dòng dạng “Received PUBLISH …”

---

## 12. Lỗi thường gặp & cách xử lý nhanh

### 12.1 Publish chạy nhưng subscriber không thấy

Checklist:

1. Topic pub và topic sub có match không?

* Sub: `test/#` sẽ nhận `test/a`, `test/a/b`…

2. Sub chạy trước hay sau?

* QoS0: sub vào sau có thể không thấy cái đã gửi.
* Muốn sub vào sau vẫn thấy: dùng retain.

3. Broker có forward không?

* Mở broker `-v` để thấy log.

### 12.2 Nhầm port / broker không chạy

* Nếu broker không chạy → pub/sub sẽ báo không connect được.
* Nếu broker đang chạy service → chạy thêm broker tay có thể báo port đang bị dùng.

### 12.3 JSON lỗi dấu nháy trên Windows

* Dùng PowerShell và bọc JSON trong `'...'`.
* Hoặc viết JSON vào file rồi publish bằng `-f`.

---

## 13. FORM CHUẨN CODE Python Publisher (Level 8: offline queue/online flush)

> **Bạn nói đúng:** đưa code trần không giúp “nhớ lại”. Phần này sẽ dẫn dắt **Level 1 → Level 8**, rồi giải thích **từng khối code** đang làm gì để lần sau quên mở ra đọc là chạy được ngay.

---

### 13.0 Lộ trình Level 1 → Level 8 (tư duy tăng cấp)

> Mỗi level bạn chỉ thêm **1 ý**. Nhớ đúng “mục tiêu” của level là làm được.

* **Level 1 — Publish tối thiểu**

  * Mục tiêu: publish được 1 message.
  * Cốt lõi: `connect()` → `publish()` → `disconnect()`.

* **Level 2 — Topic/payload chuẩn**

  * Mục tiêu: phân biệt rõ **topic** (kênh) và **payload** (nội dung).
  * Cốt lõi: đặt topic theo kiểu `devices/<id>/telemetry`.

* **Level 3 — QoS**

  * Mục tiêu: biết chọn QoS 0/1/2.
  * Cốt lõi: publish telemetry thường QoS0/1, status thường QoS1.

* **Level 4 — Retain (state)**

  * Mục tiêu: subscriber vào sau vẫn thấy **trạng thái cuối**.
  * Cốt lõi: status `online/offline` **retain=True**.

* **Level 5 — Callback cơ bản**

  * Mục tiêu: biết “khi connect/disconnect/publish” thì chạy hàm nào.
  * Cốt lõi: `on_connect`, `on_disconnect`, `on_publish`.

* **Level 6 — Loop chuẩn (không bị block)**

  * Mục tiêu: client xử lý network ổn định.
  * Cốt lõi: `loop_start()` (chạy network loop nền).

* **Level 7 — Reconnect/backoff**

  * Mục tiêu: rớt mạng vẫn tự cố gắng nối lại.
  * Cốt lõi: `reconnect_delay_set(min_delay, max_delay)`.

* **Level 8 — Offline queue + Online flush**

  * Mục tiêu: **mất mạng không mất dữ liệu** (tạm thời lưu lại), có mạng lại thì **gửi bù** trước rồi gửi bình thường.
  * Cốt lõi: `if not is_connected(): queue.append(...)` và khi online `flush queue`.

---

### 13.1 Sơ đồ “đọc 10 giây là hiểu”

* **2 topic chuẩn cho device**

  * `devices/<id>/status`  → **retain** (state)
  * `devices/<id>/telemetry` → **không retain** (data chạy liên tục)

* **Luồng chạy chính**

  1. Khi **connect**: publish `status=online` (retain)
  2. Nếu **chết bất thường**: broker tự publish `status=offline` nhờ **LWT**
  3. Vòng lặp:

     * Offline → **queue lại**
     * Online → **flush queue** → publish message hiện tại

---

### 13.2 Code Level 8 (copy chạy) + Giải thích từng khối

> Mẹo học nhanh: nhìn ký hiệu **(A) → (J)** trên code, đọc giải thích ngay dưới.

```python
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
    # báo trạng thái online (retain)
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
            payload = "hi"  # TODO: thay bằng data thật / JSON

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
        payload = "hi"  # TODO: thay bằng data thật / JSON
        client.publish(TOPIC_TELEMETRY, payload, qos=1, retain=False)

        time.sleep(PUBLISH_INTERVAL)

except KeyboardInterrupt:
    print("Chương trình đã kết thúc")

finally:
    # cleanup gọn
    client.loop_stop()
    client.disconnect()
```

#### Giải thích nhanh từng phần (đọc là nhớ)

* **(A) Cấu hình**

  * `DEVICE_ID`: tên thiết bị (client_id)
  * `TOPIC_STATUS`: nơi gửi trạng thái online/offline (**retain**)
  * `TOPIC_TELEMETRY`: nơi gửi data chạy liên tục (**không retain**)
  * `PUBLISH_INTERVAL`: online thì mỗi bao lâu gửi 1 message
  * `OFFLINE_SLEEP`: offline thì ngủ để đỡ ăn CPU
  * `MAX_QUEUE`: tối đa bao nhiêu message bị “kẹt” khi offline

* **(B) queue = []**

  * Là “hàng chờ” tạm: mỗi phần tử là `(topic, payload)`.
  * Khi offline → `append(...)`.
  * Khi online → lấy ra gửi dần.

* **(C) mqtt.Client(...)**

  * Tạo client MQTT. `client_id=DEVICE_ID` để broker nhận diện thiết bị.

* **(D) will_set(status=offline)**

  * Đây là **LWT**: nếu client chết bất thường (mất điện, crash, rớt mạng) → broker tự publish `offline` lên topic status.
  * Vì vậy **phải đặt trước `connect()`**.

* **(E) Callbacks**

  * `on_connect`: chạy khi connect thành công. Ở đây bạn publish `status=online` (retain) để ai sub vào sau cũng biết thiết bị đang online.
  * `on_disconnect`: log lúc mất kết nối.
  * `on_publish`: log khi publish xong (để quan sát).

* **(F) connect + try/except**

  * Nếu broker chưa chạy, chương trình vẫn không chết ngay (vẫn vào vòng lặp và queue lại).

* **(G) loop_start()**

  * Bật network loop chạy nền, giúp client tự xử lý connect/disconnect/publish.

* **(H) Nhánh OFFLINE**

  * Điều kiện: `not client.is_connected()`.
  * Hành động:

    * Tạo `payload` (sau thay bằng JSON/data thật)
    * Nếu queue đầy → bỏ message cũ nhất
    * `queue.append(...)` để **không mất dữ liệu**
    * `client.reconnect()` để thử lên lại

* **(I) Nhánh ONLINE: flush queue**

  * Khi có mạng: gửi các message đã bị “kẹt” trước đó.
  * `time.sleep(0.01)` để không bắn dồn dập.

* **(J) Publish message hiện tại**

  * Đây là message “thực tế” của vòng lặp hiện tại (không phải message bù).

---

### 13.3 Copy chạy nhanh (test đúng bài)

**Terminal 1 (SUB quan sát):**

```bat
mosquitto_sub -h localhost -p 1883 -t "devices/LUHAN/#" -v
```

**Terminal 2 (chạy broker verbose nếu cần):**

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

**Terminal 3 (chạy Python):**

```bat
python your_file.py
```

**Cách test OFFLINE → ONLINE nhanh:**

1. Tắt broker (hoặc stop service) → Python sẽ chuyển sang nhánh OFFLINE và queue.
2. Bật broker lại → Python connect lại → **flush queue** rồi gửi bình thường.

> Nếu nhìn sub sẽ thấy: khi broker lên lại, telemetry sẽ “đổ” một loạt (flush) rồi về nhịp đều.

## 14. Bài tập thực hành

1. Publish `test/a`, `test/a/b` và dùng:

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -v
```

2. Publish QoS0 vs QoS1:

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "qos0" -q 0
mosquitto_pub -h localhost -p 1883 -t testing -m "qos1" -q 1
```

3. Retain status:

```bat
mosquitto_pub -h localhost -p 1883 -t "devices/x/status" -m "online" -r
```

Sau đó mở sub **sau** để thấy retained:

```bat
mosquitto_sub -h localhost -p 1883 -t "devices/x/status" -v
```

4. Xoá retained:

```bat
mosquitto_pub -h localhost -p 1883 -t "devices/x/status" -n -r
```

5. Publish JSON (PowerShell):

```powershell
mosquitto_pub -h localhost -p 1883 -t sensors/room1/temp -m '{"temp":27.5,"unit":"C"}'
```

---

## Notes / Tips nhớ nhanh

* **Telemetry** thường **không retain**.
* **Status** thường **retain** (online/offline).
* **QoS1** có thể trùng message → app nên chịu được trùng.
* Debug chuẩn: **BROKER (-v) → SUB (#) → PUB**.
