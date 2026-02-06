# 03-QoS – Retain – Will (MASTER)

> Mục tiêu: Sau bài này bạn **hiểu đúng 3 thứ quan trọng nhất của MQTT khi làm thực tế**:
>
> * **QoS**: độ đảm bảo giao hàng (0/1/2) → ảnh hưởng trực tiếp đến *mất/trùng/đúng 1 lần*
> * **Retain**: “trạng thái cuối” của topic → subscriber vào sau vẫn nhận ngay
> * **Will (LWT)**: client chết bất thường → broker publish thay để báo *offline*
>
> Học xong bạn tự thiết kế được 1 protocol IoT chuẩn: **birth/online**, **last will/offline**, **retain state**, **QoS hợp lý**.

---

## Mục lục

1. [Tổng quan 3 khái niệm](#1-tổng-quan-3-khái-niệm)
2. [Form khởi động chuẩn (copy/paste)](#2-form-khởi-động-chuẩn-copypaste)
3. [QoS là gì?](#3-qos-là-gì)
4. [QoS 0/1/2 chi tiết (có bảng + flow)](#4-qos-012-chi-tiết-có-bảng--flow)
5. [QoS trong thực tế: mất/trùng/đúng 1 lần](#5-qos-trong-thực-tế-mấttrùngđúng-1-lần)
6. [Retain là gì? Vì sao gọi là “state”](#6-retain-là-gì-vì-sao-gọi-là-state)
7. [Retain thực chiến: publish/clear + lỗi thường gặp](#7-retain-thực-chiến-publishclear--lỗi-thường-gặp)
8. [Will (LWT) là gì? Khi nào broker publish?](#8-will-lwt-là-gì-khi-nào-broker-publish)
9. [Thiết kế Online/Offline chuẩn bài (Birth + LWT)](#9-thiết-kế-onlineoffline-chuẩn-bài-birth--lwt)
10. [Keepalive, PINGREQ/PINGRESP và liên quan tới Will](#10-keepalive-pingreqpingresp-và-liên-quan-tới-will)
11. [Lab bằng Mosquitto CLI](#11-lab-bằng-mosquitto-cli)
12. [Lab bằng Python (paho-mqtt)](#12-lab-bằng-python-paho-mqtt)
13. [Bảng tổng hợp nhanh (cheat sheet)](#13-bảng-tổng-hợp-nhanh-cheat-sheet)
14. [Bài tập tự luyện](#14-bài-tập-tự-luyện)

---

## 1. Tổng quan 3 khái niệm

### 1.1 QoS (Quality of Service)

**QoS** quyết định broker và client “cam kết” mức nào để chuyển message:

* QoS0: *gửi nhanh* (có thể mất)
* QoS1: *ít nhất 1 lần* (có thể trùng)
* QoS2: *đúng 1 lần* (nặng nhất)

### 1.2 Retain

**Retain** biến message thành “giá trị cuối cùng” của topic.

* Subscriber vào sau vẫn nhận ngay.
* Rất hợp với “trạng thái”: nhiệt độ hiện tại, trạng thái device, mode hệ thống…

### 1.3 Will (LWT)

**Will** (Last Will and Testament) là message được đăng ký khi connect.

* Nếu client **mất kết nối bất thường** → broker publish Will.
* Nếu client disconnect “đúng chuẩn” → Will **không** được publish.

> QoS/Retain/Will là 3 mảnh ghép: **đảm bảo giao hàng + lưu state + phát hiện chết**.

---

## 2. Form khởi động chuẩn (copy/paste)

> Bạn nên mở 3 cửa sổ terminal để test như người làm thật.

### 2.1 Cửa sổ 1: chạy broker verbose

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

### 2.2 Cửa sổ 2: subscriber quan sát tất cả

```bat
mosquitto_sub -h localhost -p 1883 -t "#" -v
```

### 2.3 Cửa sổ 3: publish thử

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi" -q 0
```

> Nếu bạn nhìn thấy subscriber in ra và broker log có `Received PUBLISH` là setup ok.

---

## 3. QoS là gì?

### 3.1 Định nghĩa

**QoS** là mức độ đảm bảo message được chuyển từ publisher → broker → subscriber.

Điểm phải nhớ:

* QoS áp dụng cho **mỗi lần publish**.
* QoS “cuối cùng” mà subscriber nhận được là:

> **QoS_deliver = min(QoS_publish, QoS_subscribe)**

Ví dụ:

* pub QoS1, sub QoS0 → deliver QoS0
* pub QoS2, sub QoS1 → deliver QoS1

### 3.2 QoS không phải là “chắc chắn không mất dữ liệu” 100%

QoS giúp tăng độ tin cậy, nhưng bạn vẫn cần:

* thiết kế app chống trùng (idempotency)
* timeout/retry hợp lý
* logging/monitoring

---

## 4. QoS 0/1/2 chi tiết (có bảng + flow)

### 4.1 Bảng so sánh nhanh

| QoS | Tên gọi       | Cam kết           | Có thể mất? | Có thể trùng?                                  | Overhead   | Dùng khi                                    |
| --: | ------------- | ----------------- | ----------- | ---------------------------------------------- | ---------- | ------------------------------------------- |
|   0 | At most once  | gửi “best effort” | ✅           | ❌ (thường không, nhưng app vẫn có thể gửi lại) | thấp nhất  | telemetry, dữ liệu spam, realtime nhẹ       |
|   1 | At least once | broker/sub ACK    | hiếm hơn    | ✅                                              | trung bình | phần lớn case IoT (event, state quan trọng) |
|   2 | Exactly once  | handshake 4 bước  | rất khó mất | ❌                                              | cao nhất   | nghiệp vụ cực quan trọng, ít message        |

> Lưu ý: QoS2 đảm bảo “exactly once” theo giao thức MQTT, nhưng hệ thống của bạn vẫn cần thiết kế tốt ở tầng ứng dụng.

---

### 4.2 QoS 0 (Fire and forget)

**Luồng đơn giản:**

* Publisher gửi PUBLISH
* Xong. Không ACK.

**Ý nghĩa thực tế:**

* nhanh, nhẹ
* nếu mất mạng đúng lúc gửi → mất message

---

### 4.3 QoS 1 (At least once)

**Luồng chính:**

1. Publisher → Broker: `PUBLISH (QoS1)`
2. Broker → Publisher: `PUBACK`

Nếu publisher không nhận `PUBACK` (timeout), publisher **có thể gửi lại**.
→ Subscriber có thể nhận **trùng**.

> QoS1 = “tôi đảm bảo broker đã nhận”, nhưng không đảm bảo subscriber xử lý “không trùng”.

---

### 4.4 QoS 2 (Exactly once)

QoS2 dùng handshake 4 bước (nghe hơi nhiều, nhưng bạn chỉ cần nắm ý nghĩa):

1. Publisher → Broker: `PUBLISH (QoS2)`
2. Broker → Publisher: `PUBREC` (tôi đã nhận, ghi nhớ)
3. Publisher → Broker: `PUBREL` (ok, giờ release)
4. Broker → Publisher: `PUBCOMP` (hoàn tất)

Mục tiêu của chuỗi này là **tránh duplicate** ngay cả khi có retransmit.

---

## 5. QoS trong thực tế: mất/trùng/đúng 1 lần

### 5.1 Khi nào QoS1 tạo duplicate?

Kịch bản phổ biến:

* Publisher gửi QoS1
* Broker nhận và forward
* PUBACK bị mất trên đường về
* Publisher tưởng chưa ack → gửi lại

Kết quả: subscriber có thể nhận 2 lần.

### 5.2 Cách xử lý duplicate (tư duy “hệ thống thật”)

* Nếu message là **state** (ví dụ nhiệt độ hiện tại) → nhận trùng không sao.
* Nếu message là **event** (ví dụ “mở cửa”, “trừ tiền”) → phải chống trùng.

Chống trùng kiểu app:

* thêm `message_id` / `event_id`
* lưu cache ID đã xử lý (TTL)
* xử lý idempotent

### 5.3 Khi nào dùng QoS2?

QoS2 dùng khi:

* số lượng message ít
* giá trị message cực quan trọng
* overhead chấp nhận được

Ví dụ: lệnh điều khiển “unlock door”, “phát hành hoá đơn”… (tuỳ hệ thống)

---

## 6. Retain là gì? Vì sao gọi là “state”

### 6.1 Định nghĩa

**Retained message** là message broker lưu lại làm “giá trị cuối” của topic.

Khi một subscriber subscribe topic đó:

* broker gửi retained message ngay lập tức (nếu có)

### 6.2 Retain khác gì “message bình thường”?

* Message bình thường: chỉ ai đang online mới nhận.
* Retain: ai vào sau vẫn thấy *giá trị cuối*.

### 6.3 Retain cực hợp cho state

Ví dụ state:

* `devices/<id>/status = online/offline`
* `sensors/room1/temp = 27.5`
* `home/mode = away/home`

Không hợp cho event:

* `door/opened` (event) → nếu retain, người vào sau sẽ hiểu nhầm là “vừa mở cửa”.

---

## 7. Retain thực chiến: publish/clear + lỗi thường gặp

### 7.1 Publish retained

```bat
mosquitto_pub -h localhost -p 1883 -t devices/d1/status -m "online" -r -q 1
```

### 7.2 Clear retained (xoá giá trị cuối)

Gửi retained với **null payload**:

```bat
mosquitto_pub -h localhost -p 1883 -t devices/d1/status -n -r
```

### 7.3 Lỗi phổ biến

* Bạn subscribe thấy “message tự nhiên hiện ra” → đó là retained.
* Bạn tưởng subscriber “nhận message cũ” → thực ra broker gửi retained để sync state.

---

## 8. Will (LWT) là gì? Khi nào broker publish?

### 8.1 Định nghĩa

**Will** là message client đăng ký khi connect.

Broker sẽ publish Will khi:

* client **mất kết nối bất thường** (crash, rớt mạng, kill process)
* broker phát hiện client timeout keepalive

Broker KHÔNG publish Will khi:

* client gửi `DISCONNECT` đúng chuẩn.

### 8.2 Will thường dùng để báo “offline”

* Will topic: `devices/<id>/status`
* Will payload: `offline`
* Will retain: `true`
* Will QoS: `1`

---

## 9. Thiết kế Online/Offline chuẩn bài (Birth + LWT)

### 9.1 Pattern chuẩn trong IoT

1. Client connect, set Will retained = `offline`
2. Connect thành công → publish retained `online` (gọi là **birth message**)
3. Nếu client chết → broker publish retained `offline`

Kết quả:

* Ai subscribe status sẽ luôn thấy trạng thái đúng (nhờ retain)

### 9.2 Tại sao phải có “birth message”?

Nếu chỉ có Will:

* client connect xong mà không publish `online`, người khác không biết nó đang online.

Birth message là “tôi đã sống và đã vào mạng thành công”.

---

## 10. Keepalive, PINGREQ/PINGRESP và liên quan tới Will

### 10.1 Keepalive là gì?

Khi connect bạn set keepalive (ví dụ 60s):

* client phải gửi gói gì đó trong khoảng đó
* nếu im lặng, client gửi `PINGREQ`
* broker trả `PINGRESP`

Bạn đã thấy log kiểu:

* `Received PINGREQ`
* `Sending PINGRESP`

Đó là heartbeat của MQTT.

### 10.2 Vì sao bạn disconnect mà vẫn thấy PING?

Nếu bạn thấy PING sau khi publisher đã thoát:

* thường là **một client khác** (ví dụ mosquitto_sub) vẫn còn chạy
* broker log sẽ ghi client_id khác nhau

> Nhìn log: tên client sau chữ “from … as …” để biết ai đang ping.

### 10.3 Will liên quan keepalive

Nếu client chết và không gửi gì nữa:

* broker đợi quá hạn keepalive → coi như mất
* lúc đó broker trigger Will

---

## 11. Lab bằng Mosquitto CLI

### 11.1 Test QoS (0 vs 1)

**Sub:**

```bat
mosquitto_sub -h localhost -p 1883 -t qos/test -v -q 1
```

**Pub QoS0:**

```bat
mosquitto_pub -h localhost -p 1883 -t qos/test -m "qos0" -q 0
```

**Pub QoS1:**

```bat
mosquitto_pub -h localhost -p 1883 -t qos/test -m "qos1" -q 1
```

Quan sát broker log để thấy khác biệt.

---

### 11.2 Test retain

**Publish retained:**

```bat
mosquitto_pub -h localhost -p 1883 -t retain/test -m "LAST" -r
```

**Mở sub sau đó (vẫn nhận ngay):**

```bat
mosquitto_sub -h localhost -p 1883 -t retain/test -v
```

**Clear retained:**

```bat
mosquitto_pub -h localhost -p 1883 -t retain/test -n -r
```

---

## 12. Lab bằng Python (paho-mqtt)

> Lưu ý: paho-mqtt 2.x yêu cầu chỉ định callback API version nếu bạn dùng callback signature kiểu mới.

### 12.1 Subscriber đơn giản (QoS1)

```py
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "devices/#"

# MQTT v2 callback style

def on_connect(client, userdata, flags, reason_code, properties):
    print("[SUB] connected:", reason_code)
    client.subscribe(TOPIC, qos=1)


def on_message(client, userdata, msg):
    print(f"[SUB] {msg.topic} qos={msg.qos} retain={msg.retain} payload={msg.payload.decode(errors='ignore')}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
```

### 12.2 Publisher state retained (online/offline)

```py
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
DEVICE_ID = "d1"
STATUS_TOPIC = f"devices/{DEVICE_ID}/status"

# Will = offline retained
will_payload = "offline"

client = mqtt.Client(
    client_id=f"{DEVICE_ID}-client",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
)

client.will_set(STATUS_TOPIC, payload=will_payload, qos=1, retain=True)
client.connect(BROKER, PORT, 60)

client.loop_start()

# Birth message = online retained
client.publish(STATUS_TOPIC, payload="online", qos=1, retain=True)
print("[PUB] online retained")

try:
    # giữ chương trình sống để test
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

# Disconnect chuẩn → will không bị bắn
client.publish(STATUS_TOPIC, payload="offline", qos=1, retain=True)
print("[PUB] offline retained (graceful)")

client.disconnect()
client.loop_stop()
```

### 12.3 Test Will (cố tình crash)

* Chạy file 12.2
* Đang chạy, **tắt ngang** bằng cách kill process (đóng cửa sổ, End Task)
* Quan sát subscriber: sẽ thấy broker publish `offline` (Will)

---

## 13. Bảng tổng hợp nhanh (cheat sheet)

### 13.1 QoS

| QoS | Cam kết       | Thực tế      | Best for                 |
| --: | ------------- | ------------ | ------------------------ |
|   0 | nhanh nhất    | có thể mất   | telemetry, data liên tục |
|   1 | ít nhất 1 lần | có thể trùng | đa số IoT                |
|   2 | đúng 1 lần    | nặng         | nghiệp vụ cực quan trọng |

### 13.2 Retain

| Retain                       | Ý nghĩa         | Dùng cho            |
| ---------------------------- | --------------- | ------------------- |
| `retain=False`               | message “event” | sự kiện, log        |
| `retain=True`                | message “state” | trạng thái hiện tại |
| `retain=True + null payload` | xoá state       | clear retained      |

### 13.3 Will

| Will                | Khi publish?                              | Dùng cho            |
| ------------------- | ----------------------------------------- | ------------------- |
| LWT                 | disconnect bất thường / timeout keepalive | offline detection   |
| graceful DISCONNECT | WILL không publish                        | shutdown đúng chuẩn |

---

## 14. Bài tập tự luyện

1. Tạo `devices/d1/status` theo pattern birth+will, dùng retain.
2. Publish state `sensors/room1/temp` retain mỗi 1s. Sub vào sau vẫn phải thấy giá trị ngay.
3. Viết subscriber lọc retained vs non-retained: in khác nhau.
4. Test QoS1 duplicate: publish QoS1 nhiều lần, thêm `event_id` trong payload và tự dedupe phía subscriber.
5. Giải thích bằng lời: vì sao event không nên retain?

---

> Nếu bạn muốn, mình sẽ viết thêm 1 file **"Protocol Design Template for MQTT"**: naming topic chuẩn, payload schema JSON, versioning, và rule chọn QoS/retain cho từng loại message (command/event/state).

