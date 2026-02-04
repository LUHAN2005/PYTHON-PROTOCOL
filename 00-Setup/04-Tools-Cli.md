# BÀI 4 : TOOLS CLI – ĐỒ NGHỀ TEST/DEBUG GIAO THỨC (MQTT, WebSocket, Socket.IO, Modbus, OPC UA)

## Mục lục

1. [Tools CLI là gì? Vì sao phải học?](#1-tools-cli-là-gì-vì-sao-phải-học)
2. [Nguyên tắc debug theo lớp (Layered Debug)](#2-nguyên-tắc-debug-theo-lớp-layered-debug)
3. [Bộ tool nền tảng (cài một lần, dùng dài)](#3-bộ-tool-nền-tảng-cài-một-lần-dùng-dài)
4. [MQTT CLI (mosquitto_pub/sub)](#4-mqtt-cli-mosquitto_pubsub)
5. [WebSocket CLI (websocat)](#5-websocket-cli-websocat)
6. [Socket.IO CLI (Node client test)](#6-socketio-cli-node-client-test)
7. [Modbus CLI (mbpoll)](#7-modbus-cli-mbpoll)
8. [OPC UA CLI (opcua-client / browse/read)](#8-opc-ua-cli-opcua-client--browseread)
9. [Checklist debug nhanh (10 phút khoanh vùng lỗi)](#9-checklist-debug-nhanh-10-phút-khoanh-vùng-lỗi)
10. [Lỗi thường gặp & cách xử](#10-lỗi-thường-gặp--cách-xử)
11. [(Tuỳ chọn) Bài tập tự luyện](#tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. Tools CLI là gì? Vì sao phải học?

**Tools CLI** là các công cụ dòng lệnh giúp bạn **test và debug giao thức** nhanh, không cần viết code ngay.

Trong IoT/automation, bạn sẽ gặp tình huống:

* thiết bị không gửi dữ liệu
* server/web không nhận realtime
* PLC/OPC UA/Modbus đọc sai register

Nếu chỉ debug bằng code, bạn dễ bị “mù”: không biết lỗi do **mạng**, do **server**, hay do **code**.

CLI giúp bạn:

* test **nhanh 10 giây**
* khoanh vùng lỗi theo lớp
* xác nhận server/protocol chạy OK trước khi viết Python/JS

> Lưu ý: CLI là “đồ nghề” giống đồng hồ đo điện: không thay code, nhưng giúp bạn chẩn đoán cực nhanh.

---

## 2. Nguyên tắc debug theo lớp (Layered Debug)

Khi lỗi xảy ra, luôn debug theo thứ tự:

1. **Máy chạy dịch vụ có sống không?** (process/service)
2. **Mạng/port có thông không?** (ping, port)
3. **Giao thức có phản hồi đúng không?** (CLI protocol)
4. **Code của bạn mới là bước cuối**

Ví dụ: Web không nhận dữ liệu MQTT

* MQTT broker có chạy không?
* Topic có đúng không?
* Message có publish thật không?
* Gateway có subscribe đúng QoS/retain không?

> Tip: Khi bạn làm bridge (Modbus ↔ MQTT), CLI sẽ giúp bạn test từng phía độc lập.

---

## 3. Bộ tool nền tảng (cài một lần, dùng dài)

### 3.1. Tool nền tảng (mọi protocol đều cần)

**Linux/Pi** (khuyên dùng):

```bash
sudo apt update
sudo apt install -y curl wget git lsof net-tools
```

* `curl`: test HTTP/URL
* `lsof`, `net-tools`: xem port/process

**Windows**: có thể dùng PowerShell + `curl` có sẵn, và `netstat -ano`.

### 3.2. Quy ước “CLI-first” khi học protocol

Mỗi protocol bạn học sẽ có:

* 1–2 lệnh CLI test nhanh
* 1 script Python/JS tương đương

Bạn hiểu bản chất giao thức trước, rồi mới “bọc” bằng thư viện.

---

## 4. MQTT CLI (mosquitto_pub/sub)

### 4.1. MQTT CLI dùng để làm gì?

* publish/subcribe nhanh
* test QoS/retain/LWT
* kiểm tra broker hoạt động

### 4.2. Lệnh nền

**Subscribe**:

```bash
mosquitto_sub -h localhost -p 1883 -t "lab/#" -v
```

**Publish**:

```bash
mosquitto_pub -h localhost -p 1883 -t "lab/temp" -m "25.4"
```

### 4.3. Test retain/QoS nhanh

Publish retained:

```bash
mosquitto_pub -h localhost -t "lab/state" -m "ON" -r
```

Sub lại sẽ nhận ngay message retained.

> Lưu ý: QoS/retain là nguồn gây “trùng message” hoặc “message cũ” rất hay gặp khi làm dashboard.

---

## 5. WebSocket CLI (websocat)

### 5.1. websocat dùng để làm gì?

* kết nối WebSocket như telnet
* gửi/nhận message realtime để test server

### 5.2. Test kết nối

```bash
websocat ws://localhost:8000/ws
```

Bạn gõ text và xem server phản hồi.

> Note: WebSocket là protocol “khung” (frames). CLI giúp bạn nhìn nhanh dữ liệu vào/ra.

---

## 6. Socket.IO CLI (Node client test)

### 6.1. Vì sao Socket.IO không dùng websocat được?

Socket.IO **không phải WebSocket thuần**. Nó chạy trên Engine.IO và có handshake riêng.

Vì vậy, cách test “chuẩn” là dùng **socket.io-client**.

### 6.2. Cài client

```bash
npm i socket.io-client
```

### 6.3. One-liner test kết nối

```bash
node -e "const io=require('socket.io-client'); const s=io('http://localhost:3000'); s.on('connect',()=>console.log('connected',s.id)); s.on('msg',(d)=>console.log('msg',d));"
```

> Lưu ý: Nếu project bạn dùng ESM (`type: module`) thì one-liner sẽ khác. Khi học bài Socket.IO, mình sẽ cho cả bản ESM.

### 6.4. Test event + ack (ý tưởng)

* client emit event
* server trả ack

Điểm mạnh của Socket.IO là **event/rooms/ack** → phù hợp làm dashboard realtime.

---

## 7. Modbus CLI (mbpoll)

### 7.1. mbpoll dùng để làm gì?

* đọc/ghi register nhanh
* xác nhận mapping đúng chưa
* debug endian/word order

### 7.2. Modbus TCP (ví dụ)

```bash
mbpoll -m tcp -a 1 -r 1 -c 10 -t 3:hex 192.168.1.50
```

Giải thích nhanh:

* `-m tcp`: modbus tcp
* `-a 1`: slave id
* `-r 1`: start register
* `-c 10`: số lượng register
* `-t 3:hex`: đọc holding register hiển thị hex

> Lưu ý: Modbus rất hay sai do **address offset** (0/1-based) và **endian** (byte/word swap).

---

## 8. OPC UA CLI (opcua-client / browse/read)

### 8.1. OPC UA CLI dùng để làm gì?

* browse node (địa chỉ trong address space)
* read/write node
* debug security/cert mismatch

### 8.2. Ý tưởng thao tác OPC UA

1. Kết nối endpoint
2. Browse cây node
3. Read một node (Value)
4. Subscribe (nâng cao)

> Note: OPC UA có lớp security/cert phức tạp hơn MQTT/WS. CLI giúp bạn kiểm tra policy/mode trước khi viết code.

---

## 9. Checklist debug nhanh (10 phút khoanh vùng lỗi)

### 9.1. Kiểm tra mạng/port

* Linux/Pi:

```bash
ip a
sudo ss -tulpn
sudo lsof -i -P -n | head
```

* Windows:

```powershell
ipconfig
netstat -ano
```

### 9.2. Kiểm tra MQTT

* sub 1 topic wildcard `lab/#`
* pub 1 message
* nếu sub không nhận → broker/host/port/topic sai

### 9.3. Kiểm tra WebSocket

* dùng websocat connect
* gửi message đơn giản

### 9.4. Kiểm tra Socket.IO

* dùng node socket.io-client connect
* listen event

### 9.5. Kiểm tra Modbus

* đọc vài register
* xác nhận slave id + map

### 9.6. Kiểm tra OPC UA

* browse/read 1 node
* kiểm tra security policy

> Tip: Bạn luôn test bằng CLI trước, rồi mới viết code. Như vậy học nhanh và ít “kẹt”.

---

## 10. Lỗi thường gặp & cách xử

### 10.1. `command not found` (Linux)

* tool chưa cài
* cài bằng `apt` hoặc theo hướng dẫn tool

### 10.2. Port đúng nhưng vẫn không connect

* firewall chặn
* service crash
* endpoint khác (ws:// vs wss://)

### 10.3. Socket.IO connect fail

* nhầm URL (`http://` vs `ws://`)
* CORS/ping timeout

### 10.4. Modbus đọc “rác”

* sai register type (coil/input/holding)
* sai endian/word order
* sai offset

### 10.5. OPC UA security mismatch

* server yêu cầu sign/encrypt
* client chưa trust cert

---

## (Tuỳ chọn) Bài tập tự luyện

1. (MQTT) Viết 2 lệnh:

   * 1 lệnh sub `lab/#`
   * 1 lệnh pub `lab/temp`

2. (WebSocket) Dùng websocat connect vào 1 WS server mẫu (hoặc sau này tự viết).

3. (Socket.IO) Dùng one-liner node để connect, log `socket.id`.

4. (Modbus/OPC UA) Ghi lại checklist “thông số cần nhớ”:

   * Modbus: ip, port, slave id, register start, count, type
   * OPC UA: endpoint, namespace, nodeId, security policy/mode

> Tip: Khi bạn làm dự án thật, bạn sẽ giữ một file `tools/commands.md` để copy/paste lệnh test nhanh.

