# 00-Setup — TỔNG HỢP CỐT LÕI (Terminal • Python venv • Node env • Tools CLI • Debug • Security)

> Mục tiêu của README này: bạn chỉ cần đọc **1 file** là nắm được “đồ nghề tối thiểu” để học tiếp phần Protocol (MQTT/WebSocket/Socket.IO/Modbus/OPC UA) mà không bị kẹt môi trường.

## Mục lục

1. [Bộ lệnh thường dùng (Terminal • Python • JS)](#1-bộ-lệnh-thường-dùng-terminal--python--js)
2. [Python env (venv) — tạo & dùng đúng](#2-python-env-venv--tạo--dùng-đúng)
3. [Node env (Node.js + npm) — tạo & chạy project](#3-node-env-nodejs--npm--tạo--chạy-project)
4. [Test giao thức bằng CLI (test trước khi code)](#4-test-giao-thức-bằng-cli-test-trước-khi-code)
5. [Debugging & Observability — tư duy + checklist nhanh](#5-debugging--observability--tư-duy--checklist-nhanh)
6. [Security basics — tối thiểu để không “mở toang”](#6-security-basics--tối-thiểu-để-không-mở-toang)
7. [Đi tiếp: Link sang các bài chi tiết](#7-đi-tiếp-link-sang-các-bài-chi-tiết)

---

## 1. Bộ lệnh thường dùng (Terminal • Python • JS)

### 1.1. 20 lệnh Terminal (Linux/Pi là chuẩn, Windows PowerShell gần giống)

| Nhóm       | Lệnh                 | Dùng để làm gì          | Ví dụ                         |              |
| ---------- | -------------------- | ----------------------- | ----------------------------- | ------------ |
| Điều hướng | `pwd`                | xem đang ở đâu          | `pwd`                         |              |
|            | `ls`                 | liệt kê file/folder     | `ls`                          |              |
|            | `cd`                 | đổi thư mục             | `cd 00-Setup`                 |              |
|            | `mkdir`              | tạo thư mục             | `mkdir temp`                  |              |
| File       | `cp`                 | copy                    | `cp a.txt b.txt`              |              |
|            | `mv`                 | đổi tên/di chuyển       | `mv a.txt notes/a.txt`        |              |
|            | `rm`                 | xoá file                | `rm a.txt`                    |              |
|            | `rm -r`              | xoá folder              | `rm -r .venv`                 |              |
| Đọc file   | `cat`                | xem nhanh file          | `cat README.md`               |              |
|            | `less`               | xem file dài            | `less app.log`                |              |
|            | `head`               | xem đầu file            | `head -n 20 app.log`          |              |
|            | `tail`               | xem cuối file           | `tail -n 50 app.log`          |              |
| Tìm kiếm   | `grep`               | tìm chữ trong file      | `grep -n "error" app.log`     |              |
|            | `find`               | tìm file                | `find . -name "*.md"`         |              |
| Mạng       | `ping`               | test internet/LAN       | `ping -c 3 8.8.8.8`           |              |
|            | `curl`               | test HTTP/URL           | `curl -I https://example.com` |              |
| Port       | `ss -tulpn`          | xem port listen (Linux) | `sudo ss -tulpn`              |              |
|            | `netstat -ano`       | xem port (Windows)      | `netstat -ano`                |              |
| Process    | `ps aux`             | xem tiến trình (Linux)  | `ps aux                       | grep python` |
|            | `top`                | xem CPU/RAM realtime    | `top`                         |              |
| Device     | `ls -l /dev/ttyUSB*` | check serial (Pi)       | `ls -l /dev/ttyUSB*`          |              |

> Note: Trên Windows, `ls/cp/mv/rm/cat` thường chạy được (alias). Nhưng các lệnh như `ss`, `/dev/...` là “chuẩn Linux/Pi”.

### 1.2. 10 lệnh Python hay dùng

| Lệnh                                        | Dùng để làm gì     | Ví dụ                                                                   |
| ------------------------------------------- | ------------------ | ----------------------------------------------------------------------- |
| `python --version`                          | xem version        | `python --version`                                                      |
| `python -c "..."`                           | chạy 1 dòng Python | `python -c "print(1+1)"`                                                |
| `python -m venv .venv`                      | tạo venv           | `python -m venv .venv`                                                  |
| `activate venv`                             | bật venv           | Win: `\.venv\Scripts\Activate.ps1` / Linux: `source .venv/bin/activate` |
| `deactivate`                                | tắt venv           | `deactivate`                                                            |
| `python -m pip install X`                   | cài lib            | `python -m pip install paho-mqtt`                                       |
| `python -m pip list`                        | xem lib            | `python -m pip list`                                                    |
| `python -m pip freeze > requirements.txt`   | export deps        | `python -m pip freeze > requirements.txt`                               |
| `python -m pip install -r requirements.txt` | cài lại deps       | `python -m pip install -r requirements.txt`                             |
| `python file.py`                            | chạy file          | `python examples/publisher.py`                                          |

### 1.3. 10 lệnh Node/JS hay dùng

| Lệnh                  | Dùng để làm gì    | Ví dụ                     |
| --------------------- | ----------------- | ------------------------- |
| `node -v`             | xem version Node  | `node -v`                 |
| `npm -v`              | xem version npm   | `npm -v`                  |
| `npm init -y`         | tạo project       | `npm init -y`             |
| `npm i <pkg>`         | cài deps          | `npm i socket.io`         |
| `npm i -D <pkg>`      | cài dev deps      | `npm i -D nodemon`        |
| `npm uninstall <pkg>` | gỡ deps           | `npm uninstall socket.io` |
| `npm run <script>`    | chạy script       | `npm run dev`             |
| `npm start`           | chạy script start | `npm start`               |
| `node file.js`        | chạy file         | `node server.js`          |
| `npx <tool>`          | chạy tool nhanh   | `npx eslint --init`       |

---

## 2. Python env (venv) — tạo & dùng đúng

### 2.1. venv là gì?

* `venv` tạo **môi trường Python riêng cho từng project**.
* Cài thư viện vào venv giúp project **không bị dính** thư viện hệ thống.
* Khi share project cho người khác: chỉ cần `requirements.txt` là dựng lại được.

### 2.2. Quy trình chuẩn (3 bước)

**Bước 1 — Tạo venv**

```bash
python -m venv .venv
```

**Bước 2 — Activate**

* Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

* Linux/Pi:

```bash
source .venv/bin/activate
```

**Bước 3 — Cài thư viện**

```bash
python -m pip install -r requirements.txt
```

> NOTE: Vì sao phải activate? Vì activate giúp `python`/`pip` trỏ đúng vào `.venv` (tránh cài nhầm môi trường).

### 2.3. Check nhanh: đang chạy đúng Python chưa?

```bash
python -c "import sys; print(sys.executable)"
```

* Nếu đường dẫn có `.venv` → ✅ đúng.

### 2.4. `.venv` có push lên GitHub không?

* **Không push** `.venv/`.
* Thêm vào `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc
.env
```

---

## 3. Node env (Node.js + npm) — tạo & chạy project

### 3.1. Node env dùng để làm gì trong repo này?

* Test **Socket.IO** (server/client) đúng hệ sinh thái.
* Chạy **web dashboard** (client).
* Debug realtime: tách lỗi Python gateway vs browser client.

### 3.2. Quy trình chuẩn

**Bước 1 — Check Node/npm**

```bash
node -v
npm -v
```

**Bước 2 — Init project**

```bash
npm init -y
```

**Bước 3 — Cài deps**

```bash
npm i socket.io socket.io-client
```

**Bước 4 — Chạy script**

```bash
npm run dev
```

> Tip: Dùng `scripts` trong `package.json` để chạy gọn (`dev`, `start`).

---

## 4. Test giao thức bằng CLI (test trước khi code)

### 4.1. Tư duy

Trước khi viết Python/JS, luôn test bằng CLI để khoanh vùng:

* Server/broker có chạy không?
* Port có mở không?
* Giao thức có phản hồi đúng không?

### 4.2. MQTT

* Subscribe:

```bash
mosquitto_sub -h localhost -p 1883 -t "lab/#" -v
```

* Publish:

```bash
mosquitto_pub -h localhost -p 1883 -t "lab/temp" -m "25.4"
```

### 4.3. WebSocket

```bash
websocat ws://localhost:8000/ws
```

> Note: WebSocket là chuẩn. `websocat` giúp bạn gửi/nhận nhanh.

### 4.4. Socket.IO

Socket.IO không phải WebSocket thuần → dùng `socket.io-client` để test:

```bash
node -e "const io=require('socket.io-client'); const s=io('http://localhost:3000'); s.on('connect',()=>console.log('connected',s.id));"
```

### 4.5. Modbus

```bash
mbpoll -m tcp -a 1 -r 1 -c 10 -t 3:hex 192.168.1.50
```

> Note: Modbus hay sai do offset/endian. CLI giúp bạn xác nhận mapping trước.

### 4.6. OPC UA

Ý tưởng CLI OPC UA: connect endpoint → browse → read node.

* Khi vào bài OPC UA, bạn sẽ thực hành:

  * endpoint URL
  * policy/mode
  * trust cert

---

## 5. Debugging & Observability — tư duy + checklist nhanh

### 5.1. Debug theo lớp (cực quan trọng)

1. process/service có chạy?
2. port có listen?
3. network ok?
4. CLI protocol ok?
5. cuối cùng mới soi code

### 5.2. Log “đi làm” phải có

* timestamp
* level (INFO/WARN/ERROR)
* context: host/port/topic/nodeId/unitId/requestId

Ví dụ log tốt:

```
2026-02-04T10:20:12+07:00 INFO mqtt connected host=localhost port=1883 clientId=gateway-01
2026-02-04T10:20:13+07:00 WARN modbus timeout host=192.168.1.50 unit=1 retry=1
```

### 5.3. 10 phút khoanh vùng lỗi (mini checklist)

* `ping` / `curl`
* `ss -tulpn` (Linux) / `netstat -ano` (Windows)
* dùng CLI (mosquitto/websocat/mbpoll/opcua)
* bật log debug tạm thời
* kiểm tra timeout/retry/backoff

---

## 6. Security basics — tối thiểu để không “mở toang”

### 6.1. 6 nguyên tắc tối thiểu

1. Không commit `.env`, key, token (dùng `.env.example`)
2. MQTT có auth + ACL tối thiểu
3. Web/Realtime có auth (ít nhất token nội bộ)
4. Modbus **không mở ra internet** (bảo vệ bằng network)
5. OPC UA check policy/mode + trust cert
6. App chạy user thường, chỉ mở port cần thiết

### 6.2. TLS/cert (nhớ 3 lỗi hay gặp)

* untrusted cert
* expired cert
* hostname mismatch

---

## 7. Đi tiếp: Link sang các bài chi tiết

> Bạn học theo thứ tự: **Python env → Node env → Tools CLI → Debug → Security** (Pi env có thể học sau nếu chưa có Pi).

* **01 — Raspberrypi env (Linux/Pi basics)**: `01-Raspberrypi-Env.md`
* **02 — Python env (venv/pip/requirements/.gitignore)**: `02-Python-Env.md`
* **03 — Node env (Node/npm/scripts/ESM/CJS)**: `03-Node-Env.md`
* **04 — Tools CLI (tool test cho từng protocol)**: `04-Tools-Cli.md`
* **05 — Debugging & Observability (logs/metrics/checklist)**: `05-Debugging-Observability.md`
* **06 — Security basics (secrets/TLS/auth/ACL/checklist)**: `06-Security-Basics.md`

---

> Tip: Nếu bạn muốn “học tới đâu làm tới đó”, sau README này ta có thể bắt đầu luôn **MQTT** bằng CLI trước, rồi mới viết code Python/JS.
