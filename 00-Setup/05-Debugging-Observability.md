# BÀI 0: DEBUGGING & OBSERVABILITY – TÌM LỖI + THEO DÕI HỆ THỐNG (IoT/Automation)

## Mục lục

1. [Debugging & Observability là gì?](#1-debugging--observability-là-gì)
2. [Tư duy debug theo lớp (Layered Debug)](#2-tư-duy-debug-theo-lớp-layered-debug)
3. [Logs: tiêu chuẩn log để “đi làm”](#3-logs-tiêu-chuẩn-log-để-đi-làm)
4. [Metrics cơ bản (đủ cho junior)](#4-metrics-cơ-bản-đủ-cho-junior)
5. [Timeout, retry, backoff, cancellation (chống treo)](#5-timeout-retry-backoff-cancellation-chống-treo)
6. [Correlation: requestId/traceId (nối chuỗi sự kiện)](#6-correlation-requestidtraceid-nối-chuỗi-sự-kiện)
7. [Healthcheck & readiness (biết app “sống” hay “chết”)](#7-healthcheck--readiness-biết-app-sống-hay-chết)
8. [Tools debug nhanh (CLI tối thiểu)](#8-tools-debug-nhanh-cli-tối-thiểu)
9. [Playbook 10 bước khoanh vùng lỗi](#9-playbook-10-bước-khoanh-vùng-lỗi)
10. [Lỗi thường gặp trong MQTT/WS/Socket.IO/Modbus/OPC UA](#10-lỗi-thường-gặp-trong-mqttwssocketiomodbusopc-ua)
11. [(Tuỳ chọn) Bài tập tự luyện](#tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. Debugging & Observability là gì?

### 1.1. Debugging là gì?

**Debugging** là quá trình tìm nguyên nhân lỗi và sửa.

Trong IoT/automation, lỗi thường đến từ:

* **Network**: sai IP/port, DNS lỗi, firewall chặn
* **Protocol**: sai topic/QoS/retain (MQTT), sai handshake (WS), sai register/endian (Modbus), cert/security mismatch (OPC UA)
* **Concurrency**: treo event loop, deadlock, race condition
* **Env/Config**: nhầm môi trường, thiếu biến `.env`, sai path

### 1.2. Observability là gì?

**Observability** là khả năng “nhìn vào hệ thống” để biết nó đang hoạt động thế nào, mà không cần đoán.

3 trụ cột:

1. **Logs** (nhật ký): app đang làm gì, lỗi gì
2. **Metrics** (số liệu): CPU/RAM, message rate, reconnect count, latency
3. **Tracing** (dòng chảy): một message đi qua nhiều service mất bao lâu

> Lưu ý: Level junior automation, bạn chỉ cần **log tốt + vài metrics cơ bản** là đã hơn nhiều người.

---

## 2. Tư duy debug theo lớp (Layered Debug)

Khi có lỗi, luôn debug theo thứ tự:

1. **Service/Process có chạy không?**
2. **Mạng/port có thông không?**
3. **Protocol có phản hồi không?** (dùng CLI tool)
4. **Code** mới là bước cuối

Ví dụ: Web không nhận telemetry

* MQTT broker có chạy không?
* Topic có đúng không?
* Gateway có subscribe không?
* WS server có broadcast không?
* Browser client có connect không?

> Tip: Debug theo lớp giúp bạn không “đâm đầu” vào code khi vấn đề thực ra là port/firewall.

---

## 3. Logs: tiêu chuẩn log để “đi làm”

### 3.1. Log tốt cần có gì?

Một log “đi làm” phải có:

* **timestamp** (giờ)
* **level** (INFO/WARN/ERROR)
* **module/comp** (thành phần)
* **message rõ ràng**
* (khuyên) **context**: requestId, deviceId, topic, ip, port…

Ví dụ format tốt:

```
2026-02-04T10:20:11.123+07:00 INFO  mqtt.sub  connected host=localhost port=1883 clientId=gateway-01
2026-02-04T10:20:12.040+07:00 INFO  mqtt.msg  topic=lab/temp qos=1 bytes=18 payload=25.4
2026-02-04T10:20:13.500+07:00 WARN  modbus    timeout host=192.168.1.50 unit=1 fn=03 retry=1
2026-02-04T10:20:14.010+07:00 ERROR bridge    publish_failed topic=lab/state err="Connection lost"
```

> Lưu ý: Log nên viết theo kiểu “ai, làm gì, với cái gì, kết quả ra sao”.

### 3.2. Level log (đừng lạm dụng)

| Level | Khi nào dùng              | Ví dụ                       |
| ----- | ------------------------- | --------------------------- |
| DEBUG | chi tiết để debug         | raw payload, timing         |
| INFO  | hành vi bình thường       | connect/disconnect, started |
| WARN  | bất thường nhưng vẫn chạy | retry, slow response        |
| ERROR | lỗi làm mất chức năng     | publish fail, crash         |

### 3.3. Structured log (khuyên)

* Log theo dạng `key=value` hoặc JSON để dễ search/filter.
* Trong tương lai khi bạn dùng ELK/Promtail/Grafana sẽ rất lợi.

> Tip: Khi debug MQTT/OPC UA, log “host/port/topic/nodeId” là thông tin cứu bạn nhiều nhất.

---

## 4. Metrics cơ bản (đủ cho junior)

### 4.1. Nên đo những gì?

Ở mức tối thiểu:

* **uptime** (app chạy bao lâu)
* **message rate** (msg/s) theo protocol
* **reconnect count** (số lần reconnect)
* **latency** (độ trễ end-to-end)
* **error count** theo loại lỗi

### 4.2. Vì sao metrics quan trọng?

* Log cho bạn biết “chuyện gì xảy ra”
* Metrics cho bạn biết “xảy ra nhiều hay ít”

Ví dụ:

* reconnect 1 lần/ngày: chấp nhận
* reconnect 50 lần/phút: có vấn đề mạng hoặc cấu hình ping/pong

---

## 5. Timeout, retry, backoff, cancellation (chống treo)

### 5.1. Vì sao phải có timeout?

Nếu không có timeout:

* socket treo mãi
* request chờ vô hạn
* gateway đứng yên nhưng không crash → rất khó phát hiện

**Quy tắc:** mọi I/O đều phải có timeout.

### 5.2. Retry & backoff đúng cách

Retry đúng:

* giới hạn số lần
* có **backoff** (chờ tăng dần)
* có **jitter** (ngẫu nhiên nhẹ) để tránh “reconnect storm”

Ví dụ logic:

* lần 1: chờ 1s
* lần 2: chờ 2s
* lần 3: chờ 4s
* tối đa: 10s

> Lưu ý: Retry “spam liên tục” là tự phá server và phá mạng.

### 5.3. Cancellation (đặc biệt với asyncio)

* Khi stop app, bạn phải hủy task sạch
* Nếu không: app shutdown treo, hoặc rò rỉ task

---

## 6. Correlation: requestId/traceId (nối chuỗi sự kiện)

Khi hệ có nhiều lớp (PLC → gateway → web), bạn cần một ID để nối chuỗi.

### 6.1. requestId dùng làm gì?

* UI gửi command: `requestId=abc123`
* gateway nhận: log `requestId=abc123`
* thiết bị ack: log `requestId=abc123`

Bạn sẽ truy vết được “một lệnh đi đâu, mất bao lâu, fail ở đâu”.

### 6.2. Nên gắn requestId ở đâu?

* MQTT: trong payload hoặc topic con (tuỳ pattern)
* WS/Socket.IO: trong message object
* Modbus/OPC UA: trong log (vì protocol không có requestId built-in kiểu app)

> Tip: Command/Ack pattern mà bạn học chính là nền cho correlation.

---

## 7. Healthcheck & readiness (biết app “sống” hay “chết”)

### 7.1. Healthcheck là gì?

Một endpoint (hoặc lệnh) trả về trạng thái:

* app sống
* có kết nối broker chưa
* có đọc được PLC không

### 7.2. Ví dụ healthcheck (ý tưởng)

* `/health`: app còn chạy
* `/ready`: app đã connect MQTT + backend OK

> Lưu ý: Healthcheck giúp bạn viết systemd/service restart thông minh hơn.

---

## 8. Tools debug nhanh (CLI tối thiểu)

### 8.1. Network/port

Linux/Pi:

```bash
ip a
ip route
sudo ss -tulpn
sudo lsof -i -P -n | head
ping -c 3 8.8.8.8
curl -I https://example.com
```

Windows:

```powershell
ipconfig
netstat -ano
ping 8.8.8.8
curl -I https://example.com
```

### 8.2. Protocol tools (tuỳ protocol)

* MQTT: `mosquitto_pub`, `mosquitto_sub`
* WebSocket: `websocat`
* Socket.IO: `socket.io-client` (Node)
* Modbus: `mbpoll`
* OPC UA: `opcua-client`/browse tool

> Tip: Tools CLI giúp bạn xác nhận “server OK” trước khi nghi code.

---

## 9. Playbook 10 bước khoanh vùng lỗi

1. Xác định **triệu chứng** (không connect? lag? sai dữ liệu?)
2. Ghi lại **thông số**: host/port/topic/nodeId/unitId
3. Kiểm tra service/process đang chạy
4. Kiểm tra port đang listen
5. Ping/route/DNS
6. Dùng CLI tool test protocol
7. Bật log DEBUG tạm thời
8. Kiểm tra timeout/retry/backoff
9. Kiểm tra dữ liệu (schema/unit/timestamp)
10. Fix → test lại bằng CLI → test lại bằng app

> Lưu ý: Luôn kết thúc bằng “test lại bằng CLI” để chắc fix đúng.

---

## 10. Lỗi thường gặp trong MQTT/WS/Socket.IO/Modbus/OPC UA

### 10.1. MQTT

* QoS gây duplicate
* retained gây “message cũ”
* topic wildcard sai
* ACL/TLS chặn

### 10.2. WebSocket

* sai URL (`ws://` vs `wss://`)
* ping/pong timeout
* reconnect storm

### 10.3. Socket.IO

* nhầm `http://` (Socket.IO dùng HTTP handshake)
* CORS
* namespace/rooms mismatch

### 10.4. Modbus

* offset 0/1-based
* endian/word order
* line noise/timeout (đặc biệt RTU)

### 10.5. OPC UA

* security policy/mode mismatch
* cert trust issue
* browse namespace sai

> Tip: Những lỗi này nếu log tốt + CLI test thì bạn khoanh vùng rất nhanh.

---

## (Tuỳ chọn) Bài tập tự luyện

1. Viết “checklist debug” 8 bước của riêng bạn cho case: **web không nhận telemetry**.
2. Tạo một app nhỏ (Python/Node) in log mỗi 2s với level INFO/WARN.
3. Tạo tình huống lỗi giả:

   * cố tình connect sai port
   * log phải nói rõ: host/port/timeout
4. Ghi lại 5 metrics bạn muốn theo dõi khi chạy gateway 24/7.

> Tip: Sau khi học 5 protocol, bạn sẽ quay lại bài này để bổ sung metric/log theo từng protocol (reconnect count, msg rate, latency).

