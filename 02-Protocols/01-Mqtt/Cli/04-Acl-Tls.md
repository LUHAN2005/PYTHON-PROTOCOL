# 04-ACL-TLS (Mosquitto) — MASTER README.md

> Mục tiêu của bài này: sau khi học xong, bạn **tự cấu hình được Mosquitto có đăng nhập (username/password), phân quyền theo topic (ACL), và chạy được kết nối mã hóa TLS**. Đây là nền tảng để triển khai MQTT “thật” cho dự án (IoT/app).

---

## Mục lục

1. [Bức tranh tổng quan: ACL vs TLS](#1-bức-tranh-tổng-quan-acl-vs-tls)
2. [Kiến thức nền cực quan trọng](#2-kiến-thức-nền-cực-quan-trọng)
3. [Cấu hình Authentication: username/password (mosquitto_passwd)](#3-cấu-hình-authentication-usernamepassword-mosquitto_passwd)
4. [Cấu hình Authorization: ACL theo topic (acl_file)](#4-cấu-hình-authorization-acl-theo-topic-acl_file)
5. [Template mosquitto.conf “chuẩn để copy” (ACL + Logs + Listener)](#5-template-mosquittoconf-chuẩn-để-copy-acl--logs--listener)
6. [TLS là gì và có những mode nào?](#6-tls-là-gì-và-có-những-mode-nào)
7. [Tạo chứng chỉ (CA → Server cert → Client cert)](#7-tạo-chứng-chỉ-ca--server-cert--client-cert)
8. [Cấu hình Mosquitto TLS listener (8883)](#8-cấu-hình-mosquitto-tls-listener-8883)
9. [Test bằng mosquitto_sub/mosquitto_pub (có TLS)](#9-test-bằng-mosquitto_submosquitto_pub-có-tls)
10. [Kết nối bằng Python (paho-mqtt) + TLS + username/password](#10-kết-nối-bằng-python-paho-mqtt--tls--usernamepassword)
11. [Bảng tổng hợp MASTER](#11-bảng-tổng-hợp-master)
12. [Lỗi thường gặp & cách debug nhanh](#12-lỗi-thường-gặp--cách-debug-nhanh)
13. [Bài tập tự luyện](#13-bài-tập-tự-luyện)

---

## 1. Bức tranh tổng quan: ACL vs TLS

Khi làm MQTT thật, bạn sẽ luôn gặp 2 câu hỏi:

* **Ai đang kết nối?** (Authentication) → username/password hoặc client certificate.
* **Người đó được phép làm gì?** (Authorization) → ACL theo topic (read/write/subscribe).
* **Dữ liệu có bị nghe lén / sửa nội dung giữa đường không?** → TLS mã hóa.

### Nhớ nhanh

* **ACL**: “Bạn được publish/subscribe topic nào?”
* **TLS**: “Đường truyền có được mã hóa và xác thực server không?”

---

## 2. Kiến thức nền cực quan trọng

### 2.1 MQTT topic là “đường dẫn logic”

Topic giống như đường dẫn:

* `home/livingroom/temp`
* `devices/deviceA/status`

Client **publish** lên topic, client khác **subscribe** topic để nhận.

### 2.2 Wildcard của MQTT vs wildcard trong ACL

**MQTT wildcard (khi subscribe):**

* `+` : 1 tầng
* `#` : nhiều tầng

Ví dụ:

* `devices/+/status`
* `devices/#`

**ACL của Mosquitto** cũng có wildcard trong rule, nhưng ý nghĩa là “khớp topic” để cho phép.

### 2.3 “Listener” là cổng broker lắng nghe

* `1883` thường là MQTT thường (plaintext)
* `8883` thường là MQTT qua TLS

Bạn có thể chạy cả 2 (khuyến nghị khi học). Lên production thường **tắt 1883** hoặc chỉ cho nội bộ.

---

## 3. Cấu hình Authentication: username/password (mosquitto_passwd)

### 3.1 Tạo file password

Mosquitto dùng file password hash (không lưu plain text).

> Ví dụ: tạo `passwords.txt`

**Windows (PowerShell/CMD):**

```bat
cd "C:\Program Files\mosquitto"

:: tạo mới (lần đầu)
mosquitto_passwd -c E:\mqtt\passwords.txt userA

:: thêm user (không -c)
mosquitto_passwd E:\mqtt\passwords.txt userB
```

Bạn sẽ được hỏi password 2 lần.

### 3.2 Bật chế độ yêu cầu đăng nhập

Trong `mosquitto.conf`:

```conf
allow_anonymous false
password_file E:/mqtt/passwords.txt
```

> Lưu ý Windows path: bạn có thể dùng `E:/...` (dễ hơn) hoặc `E:\...`.

### 3.3 Test nhanh đăng nhập

Mở 2 cửa sổ:

**Terminal 1 (sub):**

```bat
mosquitto_sub -h localhost -p 1883 -t "testing" -u userA -P "yourpass" -v
```

**Terminal 2 (pub):**

```bat
mosquitto_pub -h localhost -p 1883 -t "testing" -m "hi" -u userA -P "yourpass"
```

Nếu sai pass bạn sẽ thấy lỗi kiểu:

* `Connection Refused: bad user name or password`

---

## 4. Cấu hình Authorization: ACL theo topic (acl_file)

### 4.1 ACL là gì?

**ACL (Access Control List)** là tập luật quyết định:

* user nào được **read** (nhận message)
* user nào được **write** (publish message)
* user nào được **subscribe** (đăng ký topic)

Trong Mosquitto, ACL thường nằm trong `acl_file`.

### 4.2 Cấu trúc cơ bản của acl_file

Ví dụ file `E:/mqtt/acl.txt`:

```conf
# --- userA: chỉ publish sensor, chỉ read command ---
user userA

# publish (write)
topic write devices/userA/sensor/#

# subscribe (read)
topic read devices/userA/cmd/#


# --- userB: được read hết sensor của mọi user, nhưng không được write ---
user userB

topic read devices/+/sensor/#
```

### 4.3 Những keyword quan trọng trong ACL

* `user <username>`: áp dụng rule cho user đó
* `topic read ...`: được subscribe/nhận
* `topic write ...`: được publish
* `topic readwrite ...`: cả hai

> Ghi nhớ: Nếu bật `allow_anonymous false` mà **không có rule cho user**, user sẽ bị từ chối.

### 4.4 Placeholder cực hay: `%u` và `%c`

Trong ACL, Mosquitto hỗ trợ placeholder:

* `%u` = username
* `%c` = clientid

Ví dụ:

```conf
user userA
# userA chỉ được publish vào đúng “khu vực” của mình
# nếu username=userA thì rule này khớp devices/userA/...
topic write devices/%u/#
```

Cách này giúp bạn không phải viết 1000 user thủ công.

### 4.5 Bật ACL trong mosquitto.conf

```conf
acl_file E:/mqtt/acl.txt
```

### 4.6 Test phân quyền

Ví dụ bạn cấu hình:

* userA chỉ write `devices/userA/sensor/#`

Thử publish sai:

```bat
mosquitto_pub -h localhost -p 1883 -t "devices/userB/sensor/temp" -m "hack" -u userA -P "pass"
```

Bạn sẽ bị từ chối (thường broker sẽ đóng kết nối hoặc trả not authorised).

---

## 5. Template mosquitto.conf “chuẩn để copy” (ACL + Logs + Listener)

> Đây là phần bạn copy-paste để khởi động nhanh.

### 5.1 Cấu trúc thư mục khuyến nghị

```
E:\mqtt\
  mosquitto.conf
  passwords.txt
  acl.txt
  certs\
    ca.crt
    server.crt
    server.key
    client.crt
    client.key
```

### 5.2 MOSQUITTO.CONF (BẢN CHUẨN HỌC TẬP)

Tạo file `E:/mqtt/mosquitto.conf`:

```conf
# =========================
# MOSQUITTO MASTER CONFIG
# (ACL + TLS + Logging)
# =========================

# --- Logging (cho dễ học) ---
log_type all
log_timestamp true

# --- Persistence (tuỳ chọn) ---
persistence true
persistence_location E:/mqtt/data/

# =========================
# LISTENER 1883 (PLAINTEXT)
# =========================
listener 1883 127.0.0.1
protocol mqtt

allow_anonymous false
password_file E:/mqtt/passwords.txt
acl_file E:/mqtt/acl.txt

# =========================
# LISTENER 8883 (TLS)
# =========================
listener 8883 127.0.0.1
protocol mqtt

# TLS CA + server cert
cafile E:/mqtt/certs/ca.crt
certfile E:/mqtt/certs/server.crt
keyfile E:/mqtt/certs/server.key

# Nếu muốn bắt client đưa cert (Mutual TLS) thì bật:
# require_certificate true
# use_identity_as_username true

# Trên listener TLS, vẫn có thể dùng user/pass (tuỳ bạn)
allow_anonymous false
password_file E:/mqtt/passwords.txt
acl_file E:/mqtt/acl.txt
```

### 5.3 Chạy broker bằng file conf

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -c E:\mqtt\mosquitto.conf -v
```

> Nếu báo “Only one usage of each socket address…” nghĩa là **port đang bị chiếm** (thường do service mosquitto đang chạy). Bạn cần stop service hoặc đổi port.

---

## 6. TLS là gì và có những mode nào?

### 6.1 TLS giải quyết cái gì?

TLS giúp:

* **Mã hóa** (không ai đọc lén được)
* **Toàn vẹn** (khó sửa nội dung)
* **Xác thực server** (client biết mình đang nói chuyện đúng broker)

### 6.2 3 mode phổ biến

| Mode              | Client kiểm CA? | Client có cert không? | Dùng khi nào                       |
| ----------------- | --------------: | --------------------: | ---------------------------------- |
| TLS 1 chiều       |               ✅ |                     ❌ | Phổ biến nhất (user/pass + TLS)    |
| Mutual TLS (mTLS) |               ✅ |                     ✅ | IoT/Enterprise, xác thực bằng cert |
| Không TLS         |               ❌ |                     ❌ | Chỉ học hoặc nội bộ tuyệt đối      |

---

## 7. Tạo chứng chỉ (CA → Server cert → Client cert)

> Có nhiều cách. Ở đây dùng OpenSSL để bạn hiểu bản chất.

### 7.1 Chuẩn bị OpenSSL trên Windows

Bạn có thể có OpenSSL từ:

* Git for Windows
* hoặc cài OpenSSL riêng

Kiểm tra:

```bat
openssl version
```

### 7.2 Tạo CA (Certificate Authority)

Mở terminal tại `E:\mqtt\certs`:

```bat
cd /d E:\mqtt\certs

:: 1) tạo private key cho CA
openssl genrsa -out ca.key 2048

:: 2) tạo chứng chỉ CA (tự ký)
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=MyMQTT-CA"
```

### 7.3 Tạo Server certificate

```bat
:: 1) key cho server
openssl genrsa -out server.key 2048

:: 2) CSR
openssl req -new -key server.key -out server.csr -subj "/CN=localhost"

:: 3) ký bởi CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256
```

> Ghi chú: CN=localhost là đủ cho học local. Nếu bạn kết nối bằng IP/domain khác, bạn cần chứng chỉ đúng tên (SAN). Khi học sâu hơn sẽ chỉnh.

### 7.4 (Tuỳ chọn) Tạo Client certificate cho mTLS

```bat
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=deviceA"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256
```

---

## 8. Cấu hình Mosquitto TLS listener (8883)

Nếu bạn dùng template ở mục 5.2 thì đã có sẵn:

```conf
listener 8883 127.0.0.1
cafile E:/mqtt/certs/ca.crt
certfile E:/mqtt/certs/server.crt
keyfile E:/mqtt/certs/server.key
```

### 8.1 Bật mTLS (client bắt buộc đưa cert)

Bật thêm:

```conf
require_certificate true
use_identity_as_username true
```

Ý nghĩa:

* `require_certificate true`: client không có cert → bị từ chối
* `use_identity_as_username true`: Mosquitto lấy CN của client cert làm “username” để áp ACL

Lúc đó ACL có thể viết theo “username từ cert” luôn.

---

## 9. Test bằng mosquitto_sub/mosquitto_pub (có TLS)

### 9.1 TLS 1 chiều (client chỉ verify server)

**Subscriber:**

```bat
mosquitto_sub -h localhost -p 8883 -t "testing" -v --cafile E:\mqtt\certs\ca.crt -u userA -P "pass"
```

**Publisher:**

```bat
mosquitto_pub -h localhost -p 8883 -t "testing" -m "hello tls" --cafile E:\mqtt\certs\ca.crt -u userA -P "pass"
```

### 9.2 Mutual TLS (client đưa cert)

**Subscriber (mTLS):**

```bat
mosquitto_sub -h localhost -p 8883 -t "testing" -v \
  --cafile E:\mqtt\certs\ca.crt \
  --cert   E:\mqtt\certs\client.crt \
  --key    E:\mqtt\certs\client.key
```

**Publisher (mTLS):**

```bat
mosquitto_pub -h localhost -p 8883 -t "testing" -m "hello mtls" \
  --cafile E:\mqtt\certs\ca.crt \
  --cert   E:\mqtt\certs\client.crt \
  --key    E:\mqtt\certs\client.key
```

> Nếu bạn bật `use_identity_as_username true` thì bạn có thể không cần `-u/-P` nữa (vì broker xác thực bằng cert).

---

## 10. Kết nối bằng Python (paho-mqtt) + TLS + username/password

> Bạn đang dùng paho-mqtt 2.x, nên nhớ `callback_api_version`.

### 10.1 Subscriber tối giản (khuyến nghị có on_connect)

**Vì sao nên có `on_connect`?**

* MQTT có thể reconnect
* Nếu reconnect thì bạn muốn tự subscribe lại
* `on_connect` là chỗ “khởi tạo lại” đúng chuẩn

```py
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 8883
TOPIC = "testing"

CAFILE = r"E:\mqtt\certs\ca.crt"

USERNAME = "userA"
PASSWORD = "pass"


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[SUB] Connected: {reason_code}")
    client.subscribe(TOPIC, qos=0)
    print(f"[SUB] Subscribed: {TOPIC}")


def on_message(client, userdata, msg):
    print(f"[SUB] topic={msg.topic} qos={msg.qos} payload={msg.payload.decode(errors='ignore')}")


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="sub-1")

    # user/pass
    client.username_pw_set(USERNAME, PASSWORD)

    # TLS 1 chiều
    client.tls_set(ca_certs=CAFILE)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
```

### 10.2 Publisher tối giản (đúng chuẩn publish “thực sự đi ra mạng”)

```py
import time
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 8883
TOPIC = "testing"

CAFILE = r"E:\mqtt\certs\ca.crt"

USERNAME = "userA"
PASSWORD = "pass"


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="pub-1")
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(ca_certs=CAFILE)

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    # Bắt buộc chạy loop để network hoạt động
    client.loop_start()

    info = client.publish(TOPIC, payload="hello from python tls", qos=0)
    info.wait_for_publish()

    time.sleep(0.1)
    client.disconnect()
    time.sleep(0.1)

    client.loop_stop()


if __name__ == "__main__":
    main()
```

### 10.3 Nếu dùng Mutual TLS (mTLS)

Thêm cert/key client:

```py
client.tls_set(
    ca_certs=r"E:\mqtt\certs\ca.crt",
    certfile=r"E:\mqtt\certs\client.crt",
    keyfile=r"E:\mqtt\certs\client.key",
)
```

---

## 11. Bảng tổng hợp MASTER

### 11.1 Các option quan trọng trong mosquitto.conf

| Option                     | Ý nghĩa                   | Ví dụ                      |
| -------------------------- | ------------------------- | -------------------------- |
| `listener`                 | mở cổng lắng nghe         | `listener 1883 127.0.0.1`  |
| `allow_anonymous`          | cho phép không đăng nhập? | `false`                    |
| `password_file`            | file user/pass hash       | `E:/mqtt/passwords.txt`    |
| `acl_file`                 | file phân quyền           | `E:/mqtt/acl.txt`          |
| `cafile`                   | CA để verify              | `E:/mqtt/certs/ca.crt`     |
| `certfile`                 | server cert               | `E:/mqtt/certs/server.crt` |
| `keyfile`                  | server key                | `E:/mqtt/certs/server.key` |
| `require_certificate`      | bắt client có cert        | `true`                     |
| `use_identity_as_username` | CN thành username         | `true`                     |
| `log_type all`             | log đầy đủ                | `log_type all`             |

### 11.2 ACL rule mẫu nhanh

| Nhu cầu                       | ACL                               |
| ----------------------------- | --------------------------------- |
| user chỉ đọc 1 nhánh          | `topic read devices/userA/#`      |
| user chỉ publish 1 nhánh      | `topic write devices/userA/#`     |
| user read/write               | `topic readwrite devices/userA/#` |
| template theo username        | `topic readwrite devices/%u/#`    |
| user đọc sensor tất cả device | `topic read devices/+/sensor/#`   |

---

## 12. Lỗi thường gặp & cách debug nhanh

### 12.1 “Only one usage of each socket address…”

**Nguyên nhân:** port đang bị chiếm (mosquitto service đang chạy, hoặc broker khác đang mở).

**Cách xử lý:**

* stop service (cần admin): `sc stop mosquitto`
* hoặc đổi port listener

### 12.2 “Connection Refused: not authorised”

**Nguyên nhân:** ACL không cho phép.

**Checklist:**

* `allow_anonymous false` → đúng user chưa?
* `acl_file` đúng path chưa?
* rule có `topic read/write` đúng topic bạn đang dùng chưa?

### 12.3 “bad username or password”

* sai `-u/-P`
* password_file sai path

### 12.4 TLS: “certificate verify failed” / “unknown ca”

* client chưa đưa đúng `--cafile` (CA)
* cert server không khớp tên (CN/SAN)
* bạn connect bằng IP nhưng cert lại là CN=localhost

### 12.5 Debug log chuẩn

Khi học, luôn chạy:

```bat
mosquitto.exe -c E:\mqtt\mosquitto.conf -v
```

Vì log của broker là “chân lý” (ai kết nối, subscribe gì, publish gì, bị deny vì sao).

---

## 13. Bài tập tự luyện

1. Tạo 2 user: `sensor1`, `dashboard`.

   * `sensor1` chỉ publish `devices/sensor1/sensor/#`
   * `dashboard` chỉ read `devices/+/sensor/#`

2. Dùng placeholder `%u` để viết ACL gọn:

   * mỗi user chỉ publish dưới `devices/%u/sensor/#`

3. Chạy TLS 1 chiều:

   * tạo CA và server cert
   * mở listener 8883
   * mosquitto_pub/sub chạy được với `--cafile`

4. (Tuỳ chọn) Bật mTLS:

   * tạo client cert
   * bật `require_certificate true`
   * bật `use_identity_as_username true`
   * viết ACL theo CN của cert

---

## FORM KHỞI ĐỘNG CHUẨN (COPY/PASTE)

### A) Chạy broker

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -c E:\mqtt\mosquitto.conf -v
```

### B) Sub (plaintext 1883)

```bat
mosquitto_sub -h localhost -p 1883 -t "testing" -v -u userA -P "pass"
```

### C) Pub (plaintext 1883)

```bat
mosquitto_pub -h localhost -p 1883 -t "testing" -m "hi" -u userA -P "pass"
```

### D) Sub (TLS 8883)

```bat
mosquitto_sub -h localhost -p 8883 -t "testing" -v --cafile E:\mqtt\certs\ca.crt -u userA -P "pass"
```

### E) Pub (TLS 8883)

```bat
mosquitto_pub -h localhost -p 8883 -t "testing" -m "hi tls" --cafile E:\mqtt\certs\ca.crt -u userA -P "pass"
```

