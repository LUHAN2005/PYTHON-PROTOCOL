# BÀI 1 : MQTT (MASTER 80% – Dùng được để phát triển phần mềm)

> Mục tiêu của bài này: **đọc xong là bạn hiểu được ~80% “bề nổi” của MQTT** và có thể tự tin dùng MQTT để làm: IoT, telemetry, chat nội bộ, hệ thống event, dashboard realtime…
>
> Bài viết tổng hợp “4 phần”: **(1) Mosquitto-Sub**, **(2) Mosquitto-Pub**, **(3) QoS–Retain–Will**, **(4) ACL–TLS**.

---

## MỤC LỤC

1. [MQTT là gì? Khi nào dùng?](#1-mqtt-là-gì-khi-nào-dùng)
2. [Các khái niệm cốt lõi (Broker/Client/Topic/Message)](#2-các-khái-niệm-cốt-lõi-brokerclienttopicmessage)
3. [Topic & Wildcard: + và # (cực quan trọng)](#3-topic--wildcard--và--cực-quan-trọng)
4. [Phiên kết nối: Keepalive, Session, Clean Start](#4-phiên-kết-nối-keepalive-session-clean-start)
5. [Mosquitto trên Windows: chạy broker “đúng chuẩn”](#5-mosquitto-trên-windows-chạy-broker-đúng-chuẩn)
6. [Mosquitto SUB: lệnh, ví dụ, bài test nhanh](#6-mosquitto-sub-lệnh-ví-dụ-bài-test-nhanh)
7. [Mosquitto PUB: lệnh, ví dụ, bài test nhanh](#7-mosquitto-pub-lệnh-ví-dụ-bài-test-nhanh)
8. [QoS (0/1/2): hiểu đúng để không bị “ảo tưởng”](#8-qos-012-hiểu-đúng-để-không-bị-ảo-tưởng)
9. [Retain: “giữ trạng thái cuối” cho subscriber mới](#9-retain-giữ-trạng-thái-cuối-cho-subscriber-mới)
10. [Will (Last Will and Testament): báo offline khi rớt mạng](#10-will-last-will-and-testament-báo-offline-khi-rớt-mạng)
11. [ACL: giới hạn ai được pub/sub topic nào](#11-acl-giới-hạn-ai-được-pubsub-topic-nào)
12. [TLS: mã hoá đường truyền + mTLS (tuỳ chọn)](#12-tls-mã-hoá-đường-truyền--mtls-tuỳ-chọn)
13. [Python paho-mqtt (2.x): subscriber/publisher “chuẩn sản phẩm”](#13-python-paho-mqtt-2x-subscriberpublisher-chuẩn-sản-phẩm)
14. [Bảng tổng hợp nhanh (commands + khái niệm)](#14-bảng-tổng-hợp-nhanh-commands--khái-niệm)
15. [Checklist debug + lỗi thường gặp](#15-checklist-debug--lỗi-thường-gặp)
16. [FORM KHỞI ĐỘNG CHUẨN (COPY/PASTE)](#16-form-khởi-động-chuẩn-copypaste)
17. [(Tuỳ chọn) Bài tập tự luyện](#17-tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. MQTT là gì? Khi nào dùng?

**MQTT** (Message Queuing Telemetry Transport) là một **giao thức publish/subscribe** nhẹ, chạy trên TCP (thường), dùng để trao đổi message thông qua **Broker**.

Điểm mạnh của MQTT:

* **Pub/Sub**: producer không cần biết consumer là ai (tách rời hệ thống).
* **Nhẹ**: phù hợp IoT, mạng chập chờn.
* **Giữ trạng thái + độ tin cậy**: nhờ QoS/retain/will/session.

Khi nào dùng MQTT?

* IoT: sensor → broker → dashboard/server.
* Realtime telemetry/log: app → broker → pipeline.
* Realtime app: chat, presence, thông báo.

Khi nào *không* hợp?

* Truyền file lớn liên tục (có thể làm được nhưng không tối ưu).
* Trường hợp cần query/response “nặng” kiểu HTTP API (MQTT vẫn làm được nhưng cần thiết kế protocol).

> **Góc nhìn lập trình socket:** MQTT là **một giao thức tầng ứng dụng**. Bạn không tự viết TCP framing kiểu “raw socket”, nhưng bạn đang dùng *một protocol đã chuẩn hoá* (MQTT) để build hệ thống.

---

## 2. Các khái niệm cốt lõi (Broker/Client/Topic/Message)

### 2.1 Broker

**Broker** là “trung tâm”:

* Nhận message từ publisher.
* Route message đến đúng subscriber theo topic.
* Quản lý session, retain, QoS…

Trong bài bạn đang dùng **Mosquitto** (broker phổ biến).

### 2.2 Client

**Client** là mọi ứng dụng kết nối tới broker:

* Publisher: publish message.
* Subscriber: subscribe topic và nhận message.
* Thực tế 1 client có thể vừa pub vừa sub.

### 2.3 Topic

**Topic** là “đường dẫn” để phân loại message, dạng chuỗi phân cấp:

Ví dụ:

* `home/livingroom/temp`
* `factory/line1/motor/speed`

Topic không phải “queue” kiểu RabbitMQ. Topic giống “kênh routing”.

### 2.4 Message

Message gồm:

* **topic**
* **payload** (bytes/string/json)
* **qos** (0/1/2)
* **retain** (true/false)

---

## 3. Topic & Wildcard: + và # (cực quan trọng)

### 3.1 Quy tắc phân cấp

Topic phân cấp bằng dấu `/`:

* `test/a` và `test/a/b` là 2 topic khác nhau.

### 3.2 Wildcard

MQTT có 2 wildcard chính:

1. `+` (single-level)

* `test/+` match: `test/a`, `test/b` …
* Không match: `test/a/b` (vì nhiều hơn 1 level)

2. `#` (multi-level, phải đứng cuối)

* `test/#` match: `test/a`, `test/a/b`, `test/a/b/c`…

> **Nhớ câu này:** `+` = 1 tầng, `#` = mọi tầng.

### 3.3 Lỗi hay gặp

* Subscribe `test/+` nhưng publish vào `test/a/b` → **không nhận**.
* Dùng `#` không ở cuối → broker reject.

---

## 4. Phiên kết nối: Keepalive, Session, Clean Start

### 4.1 Keepalive là gì?

`keepalive=60` nghĩa là:

* Nếu trong ~60 giây client không gửi gì, client sẽ gửi **PINGREQ**.
* Broker trả **PINGRESP**.

Mục tiêu:

* Giữ NAT/router không cắt kết nối im lặng.
* Phát hiện kết nối chết nhanh hơn.

> Vì vậy bạn thấy log broker kiểu: `Received PINGREQ` / `Sending PINGRESP` là **bình thường**.

### 4.2 Session (phiên) và Clean Start (MQTT v5)

* Session lưu thứ như subscription + message pending (tuỳ QoS).
* Với MQTT 3.1.1 thường dùng `clean_session` (True/False).
* Với MQTT 5 dùng `clean_start` + session expiry interval.

Trong học cơ bản: cứ hiểu **Clean = kết nối mới tinh**, không giữ state.

---

## 5. Mosquitto trên Windows: chạy broker “đúng chuẩn”

### 5.1 2 cách chạy broker

1. **Chạy dạng service (Windows Service)**: chạy nền
2. **Chạy dạng console**: bạn mở terminal và chạy `mosquitto.exe -v ...` để thấy log

### 5.2 Lỗi “Only one usage of each socket address…” là gì?

Nghĩa là **port 1883 đã có process khác chiếm** (thường là mosquitto service đang chạy), nên bạn chạy thêm broker lần nữa bị trùng port.

Cách xử lý:

* Dừng service (cần quyền Admin), hoặc
* Chạy broker console bằng port khác, ví dụ `-p 1884`.

### 5.3 Lệnh hữu ích trên Windows

```bat
where mosquitto
where mosquitto_sub
where mosquitto_pub

:: xem port 1883 có ai chiếm
netstat -ano | findstr :1883

:: xem trạng thái service
sc query mosquitto

:: stop/start service (mở cmd PowerShell bằng Run as Administrator)
sc stop mosquitto
sc start mosquitto
```

### 5.4 Chạy mosquitto ở console để thấy log

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

> Note: “Starting in local only mode” nghĩa là default config chỉ cho kết nối từ máy local. Muốn cho máy khác kết nối, phải dùng config có `listener` rõ ràng.

---

## 6. Mosquitto SUB: lệnh, ví dụ, bài test nhanh

### 6.1 Lệnh cơ bản

```bat
mosquitto_sub -h localhost -p 1883 -t "testing"
```

### 6.2 Subscribe theo wildcard

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -v
```

* `-v`: in thêm topic

### 6.3 Subscribe QoS

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -q 1 -v
```

### 6.4 Subscribe và hiển thị retained

Bạn không cần cờ riêng; retained sẽ đi kèm flag “retain” (tuỳ tool). Với mosquitto CLI, bạn sẽ thấy message tới ngay sau khi subscribe nếu topic có retained.

---

## 7. Mosquitto PUB: lệnh, ví dụ, bài test nhanh

### 7.1 Publish cơ bản

```bat
mosquitto_pub -h localhost -p 1883 -t "testing" -m "hi"
```

### 7.2 Publish QoS

```bat
mosquitto_pub -h localhost -p 1883 -t "test/qos" -m "qos1" -q 1
```

### 7.3 Publish retained

```bat
mosquitto_pub -h localhost -p 1883 -t "test/retain" -m "LAST" -q 1 -r
```

* `-r` = retain

### 7.4 Xoá retained (cực hay dùng)

Publish retained với payload rỗng:

```bat
mosquitto_pub -h localhost -p 1883 -t "test/retain" -n -r
```

* `-n`: null message

---

## 8. QoS (0/1/2): hiểu đúng để không bị “ảo tưởng”

QoS là “mức đảm bảo giao hàng” giữa client ↔ broker.

### 8.1 QoS 0 — At most once

* Gửi 1 lần, **không ACK**.
* Có thể mất message.
* Nhanh nhất.

Dùng khi:

* data update liên tục, mất 1-2 bản tin không sao.

### 8.2 QoS 1 — At least once

* Có ACK.
* Có thể **nhận trùng** (duplicate).
* Phổ biến nhất cho “đủ tin cậy” mà không quá nặng.

Dùng khi:

* log/event quan trọng nhưng vẫn chấp nhận xử lý trùng (và bạn có dedupe/idempotent).

### 8.3 QoS 2 — Exactly once

* Handshake nhiều bước.
* Nặng nhất, chậm hơn.

Dùng khi:

* nghiệp vụ cực quan trọng (nhưng thường người ta vẫn chọn QoS1 + idempotency).

> **Chốt:** QoS không thay bạn thiết kế nghiệp vụ. Với QoS1, bạn vẫn cần tư duy “message có thể trùng”.

---

## 9. Retain: “giữ trạng thái cuối” cho subscriber mới

### 9.1 Retain là gì?

Khi publisher gửi message với `retain=true`, broker sẽ:

* Lưu **message cuối cùng** của topic đó.
* Khi có subscriber mới subscribe topic đó, broker gửi ngay message retained.

### 9.2 Khi nào dùng retain?

* Trạng thái hiện tại: `device/online`, `room/temp/latest`, `system/mode`.

### 9.3 Cẩn thận

* Retain không phải “history”. Nó chỉ giữ **1 message cuối**.
* Nếu bạn retain dữ liệu “rác”, subscriber mới sẽ nhận “rác” ngay.

---

## 10. Will (Last Will and Testament): báo offline khi rớt mạng

### 10.1 Will là gì?

Will message được client đăng ký khi connect:

* Nếu client **mất kết nối bất thường** (rớt mạng, crash), broker sẽ publish will message.

### 10.2 Pattern “online/offline” kinh điển

* Khi connect: publish retained `device/123/status = online`
* Will: publish retained `device/123/status = offline`

Như vậy dashboard chỉ cần subscribe `device/+/status` là biết thiết bị sống/chết.

> Lưu ý: Nếu client disconnect “tử tế” (gửi DISCONNECT), broker sẽ **không** bắn Will.

---

## 11. ACL: giới hạn ai được pub/sub topic nào

### 11.1 Vì sao cần ACL?

MQTT broker nếu mở ra mà không kiểm soát:

* ai cũng publish/sub mọi topic → lộ dữ liệu, phá hệ thống.

ACL giúp:

* user A chỉ được publish `sensor/A/#`
* user B chỉ được subscribe `sensor/+/data`

### 11.2 Password file (username/password)

Tạo file password:

```bat
mosquitto_passwd -c pwfile.txt alice
mosquitto_passwd pwfile.txt bob
```

### 11.3 ACL file (ví dụ dễ hiểu)

Ví dụ `aclfile.txt`:

```text
user alice
topic readwrite sensor/alice/#

authorized bob

topic read sensor/+/data
topic write command/bob/#

# pattern theo username (%u) hoặc clientid (%c)
pattern readwrite user/%u/#
pattern readwrite client/%c/#
```

> Gợi ý học nhanh: bắt đầu bằng 2 user, 2 topic, test pub/sub. Xong rồi mới mở rộng.

### 11.4 mosquitto.conf tối thiểu cho auth+acl

```conf
listener 1883
allow_anonymous false
password_file E:/mosquitto/pwfile.txt
acl_file E:/mosquitto/aclfile.txt

# log (giúp học)
log_type all
log_dest stdout
```

---

## 12. TLS: mã hoá đường truyền + mTLS (tuỳ chọn)

### 12.1 TLS giải quyết gì?

* Tránh bị sniff payload trên mạng.
* Xác thực broker (client biết đang nói chuyện với broker thật).

Port TLS thường dùng: **8883**.

### 12.2 TLS 1 chiều vs mTLS

* TLS 1 chiều: client verify certificate của server.
* mTLS: server cũng verify certificate của client (bảo mật mạnh hơn).

### 12.3 Tạo certificate (demo bằng OpenSSL)

> Trên Windows bạn có thể dùng OpenSSL từ Git Bash/WSL/OpenSSL for Windows.

```bash
# 1) Tạo CA
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=MyTestCA"

# 2) Tạo cert cho server
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=localhost"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256

# 3) (Tuỳ chọn) cert cho client (mTLS)
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=client1"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256
```

### 12.4 mosquitto.conf TLS tối thiểu

```conf
# MQTT plain
listener 1883
allow_anonymous false
password_file E:/mosquitto/pwfile.txt
acl_file E:/mosquitto/aclfile.txt

# MQTT TLS
listener 8883
cafile E:/mosquitto/certs/ca.crt
certfile E:/mosquitto/certs/server.crt
keyfile E:/mosquitto/certs/server.key

# mTLS (tuỳ chọn)
# require_certificate true
# use_identity_as_username true

log_type all
log_dest stdout
```

### 12.5 Test TLS bằng mosquitto_sub/pub

```bat
mosquitto_sub -h localhost -p 8883 --cafile E:\mosquitto\certs\ca.crt -t "testing" -v -u alice -P yourpass
mosquitto_pub -h localhost -p 8883 --cafile E:\mosquitto\certs\ca.crt -t "testing" -m "hi tls" -u alice -P yourpass
```

mTLS (nếu bật `require_certificate true`):

```bat
mosquitto_sub -h localhost -p 8883 --cafile E:\mosquitto\certs\ca.crt --cert E:\mosquitto\certs\client.crt --key E:\mosquitto\certs\client.key -t "testing" -v
```

---

## 13. Python paho-mqtt (2.x): subscriber/publisher “chuẩn sản phẩm”

> Bạn đang dùng `paho-mqtt 2.1.0`. Bản 2.x có thay đổi callback API so với tutorial cũ.

### 13.1 Vì sao tutorial YouTube hay bị lỗi?

* Tutorial cũ: `client = mqtt.Client(clientID)`
* paho 2.x yêu cầu khai báo callback API version hoặc dùng cú pháp mới.

**Cách “đỡ đau đầu” nhất:** dùng `mqtt.CallbackAPIVersion.VERSION2`.

### 13.2 Publisher tối thiểu (gửi 1 message rồi thoát)

```py
import time
from paho.mqtt import client as mqtt

BROKER = "localhost"
PORT = 1883

client = mqtt.Client(
    client_id="luhan",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
)

client.connect(BROKER, PORT, 60)  # keepalive là tham số thứ 3

client.loop_start()  # quan trọng: chạy network loop để gói tin thực sự đi ra

info = client.publish("testing", payload="hi", qos=0)
info.wait_for_publish()          # QoS0: chờ đẩy ra socket (không có ACK)

time.sleep(0.1)
client.disconnect()
time.sleep(0.1)

client.loop_stop()
```

> **Vì sao cần `loop_start()`?** MQTT cần một “vòng lặp mạng” để gửi/nhận packet (PUB/SUB/ACK/PING). Không chạy loop, bạn publish có thể chưa kịp đi ra.

### 13.3 Subscriber tối thiểu (đơn giản, dễ hiểu)

#### Cách A — Dễ nhất: dùng callback `on_message` (không bắt buộc on_connect)

```py
from paho.mqtt import client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "testing"

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="replace")
    print(f"[SUB] topic={msg.topic} qos={msg.qos} retain={msg.retain} payload={payload}")

client = mqtt.Client(
    client_id="sub-1",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
)

client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC, qos=0)

client.loop_forever()
```

#### Cách B — Chuẩn hơn: dùng `on_connect` để tự resubscribe khi reconnect

```py
from paho.mqtt import client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "test/#"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[SUB] Connected: {reason_code}")
    client.subscribe(TOPIC, qos=1)

def on_message(client, userdata, msg):
    print(f"[SUB] topic={msg.topic} qos={msg.qos} retain={msg.retain} payload={msg.payload!r}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
```

> Trả lời câu hỏi của bạn: **không có `on_connect` vẫn chạy được**, nhưng có `on_connect` sẽ “bền” hơn khi reconnect.

### 13.4 connect(…, keepAlive=60) bị lỗi vì sao?

* Trong Python, keyword đúng là `keepalive`, không phải `keepAlive`.
* Và nhiều khi bạn cứ dùng tham số vị trí cho chắc: `client.connect(host, port, 60)`.

### 13.5 TLS trong paho-mqtt (ví dụ)

```py
from paho.mqtt import client as mqtt

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

client.tls_set(
    ca_certs=r"E:\mosquitto\certs\ca.crt",
    certfile=None,
    keyfile=None,
)

client.connect("localhost", 8883, 60)
client.loop_start()
client.publish("testing", "hi tls")
client.loop_stop()
client.disconnect()
```

---

## 14. Bảng tổng hợp nhanh (commands + khái niệm)

### 14.1 Mosquitto CLI commands

| Mục                    | Lệnh                       | Ý nghĩa             | Ví dụ                                                      |
| ---------------------- | -------------------------- | ------------------- | ---------------------------------------------------------- |
| Start broker (console) | `mosquitto.exe -v -p 1883` | chạy broker + log   | `"C:\\Program Files\\mosquitto\\mosquitto.exe" -v -p 1883` |
| Subscribe              | `mosquitto_sub`            | nhận message        | `mosquitto_sub -h localhost -t "test/#" -v`                |
| Publish                | `mosquitto_pub`            | gửi message         | `mosquitto_pub -h localhost -t "testing" -m "hi"`          |
| QoS                    | `-q 0/1/2`                 | mức đảm bảo         | `mosquitto_pub ... -q 1`                                   |
| Retain                 | `-r`                       | lưu msg cuối        | `mosquitto_pub ... -r`                                     |
| Xoá retain             | `-n -r`                    | retain payload rỗng | `mosquitto_pub ... -n -r`                                  |
| Auth                   | `-u -P`                    | user/pass           | `mosquitto_sub ... -u alice -P 123`                        |
| TLS                    | `--cafile`                 | verify server       | `mosquitto_sub ... --cafile ca.crt`                        |
| mTLS                   | `--cert --key`             | client cert         | `mosquitto_sub ... --cert c.crt --key c.key`               |

### 14.2 MQTT concepts

| Khái niệm | Ý nghĩa “1 câu”                                        |
| --------- | ------------------------------------------------------ |
| Broker    | nơi trung chuyển message và quản lý QoS/session/retain |
| Topic     | đường dẫn phân cấp để route message                    |
| Pub/Sub   | publisher gửi lên topic, subscriber nhận theo topic    |
| QoS0      | nhanh nhất, có thể mất                                 |
| QoS1      | có ACK, có thể trùng                                   |
| QoS2      | đúng 1 lần, nặng nhất                                  |
| Retain    | giữ message cuối để subscriber mới nhận ngay           |
| Will      | broker publish nếu client rớt bất thường               |
| Keepalive | PINGREQ/PINGRESP để giữ và phát hiện sống              |
| ACL       | giới hạn quyền pub/sub theo topic                      |
| TLS       | mã hoá + xác thực broker (và client nếu mTLS)          |

---

## 15. Checklist debug + lỗi thường gặp

### 15.1 Checklist 60 giây

1. Broker có chạy không? (terminal broker có log / `sc query mosquitto`)
2. Port đúng không? (1883/8883)
3. Subscribe topic đúng chưa? (wildcard `+/#`)
4. Publisher có chạy loop chưa? (paho: `loop_start/loop_forever`)
5. QoS/retain có đúng ý không?
6. Auth/ACL có chặn không? (xem log broker)
7. TLS có đúng cafile/cert/key không?

### 15.2 Lỗi hay gặp (và cách hiểu)

* `Address already in use`: port đã bị chiếm → stop service hoặc đổi port.
* `Access is denied` khi `sc stop`: cần mở terminal **Run as Administrator**.
* `Unsupported callback API version`: tutorial cũ + paho 2.x → dùng `callback_api_version=...`.
* Publish xong thoát mà không thấy gì: bạn chưa chạy loop hoặc thoát quá nhanh → `loop_start()` + `sleep()`.
* Subscribe không nhận: sai topic/wildcard hoặc broker local-only.

---

## 16. FORM KHỞI ĐỘNG CHUẨN (COPY/PASTE)

> Mục tiêu: 3 cửa sổ terminal, chạy là thấy message ngay. Đây là “form” bạn có thể copy cho mọi bài MQTT.

### 16.1 Terminal 1 — BROKER (console, nhìn log)

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

### 16.2 Terminal 2 — SUBSCRIBE

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -v
```

### 16.3 Terminal 3 — PUBLISH

```bat
mosquitto_pub -h localhost -p 1883 -t "test/a" -m "A"
mosquitto_pub -h localhost -p 1883 -t "test/a/b" -m "B"
mosquitto_pub -h localhost -p 1883 -t "test/retain" -m "LAST" -q 1 -r
mosquitto_pub -h localhost -p 1883 -t "test/qos" -m "qos1-message" -q 1
```

### 16.4 FORM Python “chuẩn học tập”

#### SUB (Python)

```py
from paho.mqtt import client as mqtt

def on_message(client, userdata, msg):
    print(f"[SUB] {msg.topic} qos={msg.qos} retain={msg.retain} payload={msg.payload!r}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("test/#", qos=1)
client.loop_forever()
```

#### PUB (Python)

```py
import time
from paho.mqtt import client as mqtt

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)
client.loop_start()

client.publish("test/a", "A")
client.publish("test/a/b", "B")
client.publish("test/retain", "LAST", qos=1, retain=True)

time.sleep(0.2)
client.disconnect()
time.sleep(0.1)
client.loop_stop()
```

---

## 17. (Tuỳ chọn) Bài tập tự luyện

1. **Wildcard drill**

* Subscribe `home/+/temp` rồi publish vào:

  * `home/a/temp` (phải nhận)
  * `home/a/room/temp` (không nhận)
  * `home/a/humid` (không nhận)

2. **Retain drill**

* Pub retained `status=ON`.
* Tắt subscriber, mở lại subscriber → phải nhận `ON` ngay.
* Xoá retained bằng `-n -r`.

3. **QoS drill**

* Pub QoS1 nhiều lần.
* Viết subscriber lưu `msg.mid`/payload, thử restart subscriber → quan sát hành vi.

4. **Will drill**

* Set will `device/1/status=offline` retain.
* Khi connect publish retained `online`.
* Kill process client (đóng terminal đột ngột) → broker bắn `offline`.

5. **ACL drill**

* Tạo user `alice` chỉ được publish `sensor/alice/#`.
* Thử publish `sensor/bob/#` → phải bị chặn.

---

### Tài liệu chính thống (để bạn học sâu hơn)

> Mình để link trong code block để bạn tiện copy.

```text
Mosquitto: https://mosquitto.org/documentation/
MQTT (OASIS): https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
paho-mqtt: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
```

