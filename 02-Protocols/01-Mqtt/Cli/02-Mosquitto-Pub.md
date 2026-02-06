# 02-Mosquitto-Pub (MASTER)

> Mục tiêu của bài này: Sau khi học xong, bạn có thể **publish MQTT bằng `mosquitto_pub` như một “pro”**: gửi payload text/binary/JSON, QoS 0/1/2, retain, will message (LWT), username/password, TLS, và biết cách test end-to-end bằng `mosquitto_sub` + broker log.

---

## Mục lục

1. [Mosquitto_pub là gì? Dùng để làm gì?](#1-mosquitto_pub-là-gì-dùng-để-làm-gì)
2. [Form khởi động chuẩn (copy/paste)](#2-form-khởi-động-chuẩn-copypaste)
3. [Cú pháp chung & tư duy đọc lệnh](#3-cú-pháp-chung--tư-duy-đọc-lệnh)
4. [Topic & payload: gửi gì lên broker?](#4-topic--payload-gửi-gì-lên-broker)
5. [QoS 0/1/2 khi publish](#5-qos-012-khi-publish)
6. [Retain: “lưu message cuối” để subscriber vào sau vẫn thấy](#6-retain-lưu-message-cuối-để-subscriber-vào-sau-vẫn-thấy)
7. [Will Message (LWT): thiết bị chết thì broker báo](#7-will-message-lwt-thiết-bị-chết-thì-broker-báo)
8. [Các lệnh thường dùng (kèm giải thích + ví dụ)](#8-các-lệnh-thường-dùng-kèm-giải-thích--ví-dụ)
9. [Bảng tổng hợp flags phổ biến](#9-bảng-tổng-hợp-flags-phổ-biến)
10. [Debug end-to-end: broker log + mosquitto_sub](#10-debug-end-to-end-broker-log--mosquitto_sub)
11. [Lỗi thường gặp & cách xử lý nhanh](#11-lỗi-thường-gặp--cách-xử-lý-nhanh)
12. [Bài tập thực hành](#12-bài-tập-thực-hành)

---

## 1. Mosquitto_pub là gì? Dùng để làm gì?

### 1.1 mosquitto_pub (Publisher CLI)

`mosquitto_pub` là tool CLI để:

* kết nối tới broker
* publish message lên một topic

### 1.2 Tại sao phải master mosquitto_pub?

Vì nó là “dao mổ” để debug nhanh:

* broker có nhận message không?
* topic đúng chưa?
* QoS/retain hoạt động đúng chưa?

> Khi học protocol, bạn luôn cần **một cách publish nhanh** không phụ thuộc code Python.

---

## 2. Form khởi động chuẩn (copy/paste)

### 2.1 Form tối thiểu (local)

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi"
```

### 2.2 Form “chuẩn bài” (client id + QoS + retain)

```bat
mosquitto_pub -h localhost -p 1883 -t "test/retain" -m "LAST" -q 1 -r -i pub1
```

**Giải thích nhanh:**

* `-h -p`: nơi publish đến
* `-t`: topic
* `-m`: payload
* `-q 1`: QoS publish
* `-r`: retain
* `-i pub1`: client_id

### 2.3 Form remote (auth)

```bat
mosquitto_pub -h <HOST> -p 1883 -t "sensors/room1/temp" -m "27.5" -q 1 -u <USER> -P <PASS>
```

---

## 3. Cú pháp chung & tư duy đọc lệnh

### 3.1 Cú pháp

```text
mosquitto_pub [options]
```

### 3.2 Tư duy đọc lệnh

Nhìn một lệnh `mosquitto_pub`, hãy đọc theo thứ tự:

1. **Publish đến đâu?** (`-h`, `-p`, TLS, auth)
2. **Topic nào?** (`-t`)
3. **Payload gì?** (`-m`, `-n`, `-f`, stdin)
4. **Độ đảm bảo?** (`-q`)
5. **Lưu lại cho người vào sau?** (`-r`)

---

## 4. Topic & payload: gửi gì lên broker?

### 4.1 Topic

Topic là “kênh” logical để subscriber lọc message.
Ví dụ:

* `sensors/room1/temp`
* `devices/esp32-01/status`
* `alerts/fire`

### 4.2 Payload (nội dung message)

Payload thực chất là **bytes**. Bạn có thể gửi:

* string
* JSON
* số (dưới dạng string)
* binary (file)

Ví dụ payload JSON:

```json
{"temp": 27.5, "unit": "C"}
```

> MQTT không tự hiểu JSON. JSON chỉ là quy ước của bạn ở tầng ứng dụng.

---

## 5. QoS (0/1/2) khi publish

### 5.1 Ý nghĩa QoS

* **QoS 0 (at most once)**: gửi nhanh, có thể mất, không ACK
* **QoS 1 (at least once)**: broker ACK, có thể trùng (subscriber có thể nhận 2 lần)
* **QoS 2 (exactly once)**: đúng 1 lần, overhead cao

### 5.2 QoS thực tế nhận ở subscriber

QoS nhận = **min(QoS publish, QoS subscribe)**.

Ví dụ:

* publish QoS1, subscribe QoS0 → nhận QoS0
* publish QoS2, subscribe QoS1 → nhận QoS1

---

## 6. Retain: “lưu message cuối” để subscriber vào sau vẫn thấy

### 6.1 Retain là gì?

`retain` biến message thành “trạng thái cuối cùng” (last-known state) của một topic.

Ví dụ:

* `devices/esp32-01/status = online/offline`
* `sensors/room1/temp = 27.5`

Subscriber vào sau subscribe sẽ nhận ngay retained message.

### 6.2 Publish retained

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "HELLO_RETAIN" -r
```

### 6.3 Xoá retained

Gửi retained null payload:

```bat
mosquitto_pub -h localhost -p 1883 -t testing -n -r
```

---

## 7. Will Message (LWT): thiết bị chết thì broker báo

### 7.1 LWT là gì?

**Last Will and Testament**: message broker sẽ publish thay bạn nếu client **mất kết nối bất thường** (crash, rớt mạng).

Cực hữu ích cho IoT:

* thiết bị online/offline

### 7.2 Tư duy thiết kế LWT

* Khi connect: publish retained `status=online`
* Set will retained `status=offline`
* Nếu chết bất thường: broker publish `offline`

> LWT thường cấu hình ở client (Python). Nhưng bạn cần hiểu nó để đọc log hệ thống.

---

## 8. Các lệnh thường dùng (kèm giải thích + ví dụ)

### 8.1 Publish message text

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi"
```

### 8.2 Publish QoS1

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi" -q 1
```

### 8.3 Publish retained state

```bat
mosquitto_pub -h localhost -p 1883 -t "devices/esp32-01/status" -m "online" -r
```

### 8.4 Publish JSON

> Windows CMD cần escape dấu nháy. Bạn có thể dùng PowerShell sẽ dễ hơn.

**PowerShell:**

```powershell
mosquitto_pub -h localhost -p 1883 -t sensors/room1/temp -m '{"temp":27.5,"unit":"C"}'
```

### 8.5 Publish từ file

```bat
mosquitto_pub -h localhost -p 1883 -t "files/blob" -f "path\to\data.bin"
```

### 8.6 Publish payload rỗng (null payload)

```bat
mosquitto_pub -h localhost -p 1883 -t testing -n
```

### 8.7 Publish nhiều lần (loop) — ví dụ “giả sensor”

**PowerShell:**

```powershell
1..10 | % { mosquitto_pub -h localhost -p 1883 -t sensors/room1/temp -m "$_"; Start-Sleep -Milliseconds 200 }
```

### 8.8 Auth

```bat
mosquitto_pub -h <HOST> -p 1883 -t testing -m "hi" -u <USER> -P <PASS>
```

### 8.9 TLS (cơ bản)

**Verify CA:**

```bat
mosquitto_pub -h <HOST> -p 8883 --cafile <CA.pem> -t testing -m "hi"
```

**Mutual TLS:**

```bat
mosquitto_pub -h <HOST> -p 8883 --cafile <CA.pem> --cert <client.crt> --key <client.key> -t testing -m "hi"
```

---

## 9. Bảng tổng hợp flags phổ biến

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

## 10. Debug end-to-end: broker log + mosquitto_sub

### 10.1 Mở broker log (verbose)

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

### 10.2 Mở subscriber để quan sát

```bat
mosquitto_sub -h localhost -p 1883 -t "#" -v
```

### 10.3 Publish

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "hi"
```

Bạn sẽ thấy:

* subscriber in: `testing hi`
* broker log: `Received PUBLISH ...` + `Sending PUBLISH to ...` (nếu có subscriber)

---

## 11. Lỗi thường gặp & cách xử lý nhanh

### 11.1 Publish chạy nhưng subscriber không thấy

Checklist:

1. topic publish và topic subscribe có match không?
2. sub chạy trước hay sau? (QoS0 nếu sub vào sau thì mất, muốn vào sau vẫn thấy → dùng retain)
3. broker có forward không? (xem broker log)

### 11.2 Nhầm port / broker không chạy

* Nếu broker đang chạy service, bạn chạy thêm broker tay sẽ báo port đã bị dùng.

### 11.3 JSON bị lỗi dấu nháy trên Windows

* Dùng PowerShell và bọc JSON trong `'...'` như ví dụ.
* Hoặc viết JSON vào file rồi dùng `-f`.

---

## 12. Bài tập thực hành

1. Publish `test/a`, `test/a/b` và dùng `mosquitto_sub -t "test/#"` để kiểm tra.
2. Publish QoS1 và quan sát khác gì QoS0.
3. Publish retained cho `devices/x/status`, rồi mở subscriber sau để xem retained hoạt động.
4. Xoá retained bằng `-n -r`.
5. Publish JSON payload và luyện cách escape trên Windows.

---

### Gợi ý học tiếp

Sau `mosquitto_pub`, bạn sẽ hiểu code Python publish nhanh hơn vì:

* mapping 1-1: `publish(topic, payload, qos, retain)`
* hiểu QoS/retain ảnh hưởng thực tế ra sao
* debug bằng CLI khi code bị lỗi

