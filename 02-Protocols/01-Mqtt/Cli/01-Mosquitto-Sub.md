# 01-Mosquitto-Sub (MASTER)

> Mục tiêu của bài này: Sau khi học xong, bạn có thể **dùng `mosquitto_sub` để subscribe MQTT như một “pro”**: hiểu topic/wildcard, QoS, retained, session, auth, TLS, debug log, và biết cách test nhanh cùng `mosquitto_pub`.

---

## Mục lục

1. [Mosquitto & mosquitto_sub là gì?](#1-mosquitto--mosquitto_sub-là-gì)
2. [Form khởi động chuẩn (copy/paste)](#2-form-khởi-động-chuẩn-copypaste)
3. [Cú pháp chung & tư duy đọc lệnh](#3-cú-pháp-chung--tư-duy-đọc-lệnh)
4. [Topic, Wildcards và cách chọn topic đúng](#4-topic-wildcards-và-cách-chọn-topic-đúng)
5. [QoS (0/1/2) khi subscribe](#5-qos-012-khi-subscribe)
6. [Retained messages: vì sao “vào sau vẫn thấy”](#6-retained-messages-vì-sao-vào-sau-vẫn-thấy)
7. [Clean session / Persistent session (cơ bản)](#7-clean-session--persistent-session-cơ-bản)
8. [Các lệnh thường dùng (kèm giải thích + ví dụ)](#8-các-lệnh-thường-dùng-kèm-giải-thích--ví-dụ)
9. [Bảng tổng hợp flags phổ biến](#9-bảng-tổng-hợp-flags-phổ-biến)
10. [Debug broker log: CONNECT / SUBSCRIBE / PUBLISH / PING](#10-debug-broker-log-connect--subscribe--publish--ping)
11. [Lỗi thường gặp & cách xử lý nhanh](#11-lỗi-thường-gặp--cách-xử-lý-nhanh)
12. [Bài tập thực hành](#12-bài-tập-thực-hành)

---

## 1. Mosquitto & mosquitto_sub là gì?

### 1.1 Mosquitto (Broker)

**Mosquitto** là một MQTT **broker** (máy chủ trung gian). Nó nhận message từ **publisher** và phân phối (forward) tới **subscriber** theo topic.

Một câu nhớ nhanh:

> **Publisher gửi lên broker → broker chuyển cho subscriber**.

### 1.2 mosquitto_sub (Subscriber CLI)

`mosquitto_sub` là công cụ dòng lệnh (CLI) để:

* kết nối tới broker
* subscribe topic
* in message ra terminal

Nó cực hữu ích để:

* test nhanh broker có chạy không
* test topic/wildcard
* debug QoS/retain
* kiểm tra message thật sự có “đi qua broker” không

---

## 2. Form khởi động chuẩn (copy/paste)

> Đây là form bạn có thể copy dùng mọi lúc, thay đúng `HOST`, `PORT`, `TOPIC`.

### 2.1 Form tối thiểu (local)

```bat
mosquitto_sub -h localhost -p 1883 -t testing -v
```

### 2.2 Form “chuẩn bài” (có client id + QoS + verbose)

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -q 1 -i sub1 -v -d
```

**Giải thích nhanh:**

* `-h localhost -p 1883`: host/port broker
* `-t "test/#"`: subscribe mọi topic dưới nhánh `test/`
* `-q 1`: QoS khi subscribe
* `-i sub1`: đặt client_id dễ debug
* `-v`: in cả topic + payload
* `-d`: debug log chi tiết ở client

### 2.3 Form remote (cần username/password)

```bat
mosquitto_sub -h <HOST> -p 1883 -t "sensors/#" -q 1 -i sub1 -u <USER> -P <PASS> -v
```

> Lưu ý: Nếu broker của bạn mở TLS (8883) thì dùng thêm `--cafile`/`--cert`/`--key` (mục 8).

---

## 3. Cú pháp chung & tư duy đọc lệnh

### 3.1 Cú pháp

```text
mosquitto_sub [options]
```

### 3.2 Tư duy đọc lệnh (rất quan trọng)

Khi nhìn một lệnh `mosquitto_sub`, hãy đọc theo thứ tự:

1. **Kết nối tới đâu?** (`-h`, `-p`, `--cafile`, `-u`, `-P`)
2. **Nghe cái gì?** (`-t`, wildcards)
3. **Chất lượng nhận?** (`-q`, session)
4. **In ra thế nào?** (`-v`, format)
5. **Debug?** (`-d`)

---

## 4. Topic, Wildcards và cách chọn topic đúng

### 4.1 Topic là gì?

Topic là chuỗi phân cấp dạng đường dẫn:

* `test/a`
* `sensors/room1/temp`
* `devices/esp32-01/status`

### 4.2 Wildcards (cực quan trọng)

MQTT có 2 wildcard:

#### `#` (multi-level)

* Match **tất cả cấp phía sau**
* Chỉ được đứng **cuối topic filter**

Ví dụ:

* `test/#` match: `test/a`, `test/a/b`, `test/anything/...`

#### `+` (single-level)

* Match **đúng 1 cấp**

Ví dụ:

* `sensors/+/temp` match: `sensors/room1/temp`, `sensors/room2/temp`
* Không match: `sensors/room1/humidity` và không match `sensors/room1/floor1/temp`

### 4.3 Best practice khi chọn topic

* Dùng nhánh rõ ràng: `env/room1/temp`, `env/room1/humidity`
* Tránh topic quá chung chung như `data` hoặc `message`
* Nếu bạn cần debug toàn hệ thống: subscribe tạm `#` (nhưng cẩn thận vì spam)

---

## 5. QoS (0/1/2) khi subscribe

### 5.1 QoS là gì?

QoS là mức đảm bảo gửi/nhận:

* **QoS 0**: nhanh nhất, có thể mất
* **QoS 1**: ít mất hơn, có thể trùng
* **QoS 2**: đúng một lần, nặng nhất

### 5.2 QoS trong subscribe có nghĩa gì?

Khi bạn `mosquitto_sub -q 1`, bạn nói với broker:

> “Tôi muốn nhận message với QoS tối đa là 1.”

**Lưu ý quan trọng:**
QoS thực tế khi bạn nhận = **min(QoS publish, QoS subscribe)**.

Ví dụ:

* publisher QoS 0, subscriber QoS 1 → nhận QoS 0
* publisher QoS 1, subscriber QoS 0 → nhận QoS 0
* publisher QoS 2, subscriber QoS 1 → nhận QoS 1

---

## 6. Retained messages: vì sao “vào sau vẫn thấy”

### 6.1 Retain là gì?

Broker sẽ **lưu lại message cuối cùng** của một topic nếu publisher gửi với `retain=true`.

Khi subscriber **vào sau** và subscribe đúng topic đó, broker sẽ **gửi lại retained message** ngay lập tức.

### 6.2 Test retain nhanh

**Publish retained:**

```bat
mosquitto_pub -h localhost -p 1883 -t testing -m "HELLO_RETAIN" -r
```

**Subscribe:**

```bat
mosquitto_sub -h localhost -p 1883 -t testing -v
```

Bạn sẽ thấy message xuất hiện ngay cả khi bạn subscribe sau.

### 6.3 Xoá retained

Publish retained message rỗng (null payload) để xoá retained:

```bat
mosquitto_pub -h localhost -p 1883 -t testing -n -r
```

---

## 7. Clean session / Persistent session (cơ bản)

### 7.1 Ý tưởng đơn giản

* **Clean session**: vào là mới, thoát là mất trạng thái
* **Persistent session**: broker nhớ trạng thái (subscription, queued messages…) theo client_id

> Trong Mosquitto CLI, bạn sẽ gặp khái niệm `clean session`/`clean start` tùy MQTT 3.1.1 hay 5.0.

### 7.2 Khi nào cần persistent?

* subscriber muốn “offline vẫn nhận lại” (kết hợp QoS1/2 + persistent session)
* hệ thống IoT có thiết bị ngủ rồi thức

---

## 8. Các lệnh thường dùng (kèm giải thích + ví dụ)

### 8.1 Subscribe 1 topic cơ bản

```bat
mosquitto_sub -h localhost -p 1883 -t testing -v
```

### 8.2 Subscribe theo nhánh

```bat
mosquitto_sub -h localhost -p 1883 -t "test/#" -v
```

### 8.3 Subscribe 1 cấp bằng `+`

```bat
mosquitto_sub -h localhost -p 1883 -t "sensors/+/temp" -v
```

### 8.4 Set QoS

```bat
mosquitto_sub -h localhost -p 1883 -t testing -q 1 -v
```

### 8.5 Đặt client_id để dễ debug broker log

```bat
mosquitto_sub -h localhost -p 1883 -t testing -i sub1 -v
```

### 8.6 Debug mode (client log)

```bat
mosquitto_sub -h localhost -p 1883 -t testing -i sub1 -v -d
```

### 8.7 Auth username/password

```bat
mosquitto_sub -h <HOST> -p 1883 -t "sensors/#" -u <USER> -P <PASS> -v
```

### 8.8 TLS (cơ bản)

Nếu broker chạy TLS port thường là **8883**.

**Chỉ verify CA:**

```bat
mosquitto_sub -h <HOST> -p 8883 --cafile <CA.pem> -t "sensors/#" -v
```

**Mutual TLS (có cert/key client):**

```bat
mosquitto_sub -h <HOST> -p 8883 --cafile <CA.pem> --cert <client.crt> --key <client.key> -t "sensors/#" -v
```

---

## 9. Bảng tổng hợp flags phổ biến

| Mục tiêu  | Flag       | Ý nghĩa               | Ví dụ               |
| --------- | ---------- | --------------------- | ------------------- |
| Host      | `-h`       | Broker host           | `-h localhost`      |
| Port      | `-p`       | Broker port           | `-p 1883`           |
| Topic     | `-t`       | Topic filter          | `-t "test/#"`       |
| QoS       | `-q`       | QoS subscribe (0/1/2) | `-q 1`              |
| Verbose   | `-v`       | In `topic payload`    | `-v`                |
| Debug     | `-d`       | Log debug client      | `-d`                |
| Client ID | `-i`       | Đặt client_id         | `-i sub1`           |
| Username  | `-u`       | Username              | `-u user`           |
| Password  | `-P`       | Password              | `-P pass`           |
| TLS CA    | `--cafile` | CA cert               | `--cafile ca.pem`   |
| TLS cert  | `--cert`   | Client cert           | `--cert client.crt` |
| TLS key   | `--key`    | Client key            | `--key client.key`  |

> Ghi nhớ: **test local** chỉ cần `-h -p -t -v`. Khi debug nâng cao, thêm `-i -d`.

---

## 10. Debug broker log: CONNECT / SUBSCRIBE / PUBLISH / PING

Khi bạn chạy broker kiểu verbose:

```bat
"C:\Program Files\mosquitto\mosquitto.exe" -v -p 1883
```

Bạn sẽ thấy:

* `New client connected ... as <client_id>`
* `Received SUBSCRIBE ...` + topic
* `Received PUBLISH ...` khi có publish
* `Sending PUBLISH to ...` khi broker forward
* `Received PINGREQ ...` / `PINGRESP ...` là heartbeat keepalive (bình thường)

### Tại sao có PINGREQ/PINGRESP?

Subscriber thường “ngồi chờ” không có traffic, nên nó gửi ping theo keepalive để giữ kết nối.

---

## 11. Lỗi thường gặp & cách xử lý nhanh

### 11.1 Không nhận được message

Checklist 10 giây:

1. Broker chạy chưa? (xem có `running`)
2. Subscribe đúng topic chưa? (nhầm `testing` vs `test`)
3. Publish có đúng topic không?
4. Nếu publish trước rồi mới sub: QoS0 sẽ mất (cần retain)

### 11.2 “Only one usage of each socket address” (port đã bị dùng)

Nghĩa là port 1883 đang có broker khác chạy.

* Tắt service mosquitto (Admin) hoặc đổi port.

### 11.3 “Access is denied” khi `sc stop mosquitto`

Bạn cần mở terminal **Run as Administrator**.

---

## 12. Bài tập thực hành

1. Subscribe `test/#`, dùng `mosquitto_pub` bắn thử `test/a`, `test/a/b` xem có nhận đủ không.
2. Test wildcard `+`: subscribe `sensors/+/temp`, publish `sensors/room1/temp` và `sensors/room1/humidity`.
3. Test retain: publish retained rồi mở subscriber sau.
4. Test QoS: publish QoS1, subscribe QoS0 và QoS1, so sánh log.

---

### Gợi ý học tiếp

Sau khi master `mosquitto_sub`, bạn sẽ làm phần Python subscriber dễ hơn rất nhiều, vì bạn đã hiểu:

* topic filter
* QoS
* retain
* keepalive ping
* broker forward log

