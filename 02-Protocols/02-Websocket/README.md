# BÀI 1 : WEBSOCKET (MASTER 80% – Dùng được để phát triển phần mềm)

> Mục tiêu của bài này: **đọc xong là bạn hiểu được ~80% “bề nổi” của WebSocket** và có thể tự tin dùng WebSocket để làm: chat realtime, dashboard live, notification, game loop cơ bản, device control panel, collaborative app…
>
> Bài viết tổng hợp “4 phần”: **(1) Lifecycle kết nối**, **(2) Message & Broadcast**, **(3) Ping/Pong–Reconnect–Backpressure**, **(4) Auth–TLS–Scale**.

---

## MỤC LỤC

1. [WebSocket là gì? Khi nào dùng?](#1-websocket-là-gì-khi-nào-dùng)
2. [Các khái niệm cốt lõi (Client/Server/Connection/Message)](#2-các-khái-niệm-cốt-lõi-clientserverconnectionmessage)
3. [HTTP vs Polling vs Long Polling vs WebSocket](#3-http-vs-polling-vs-long-polling-vs-websocket)
4. [Handshake & nâng cấp kết nối (HTTP Upgrade)](#4-handshake--nâng-cấp-kết-nối-http-upgrade)
5. [Phiên kết nối: Open, Message, Close, Ping/Pong](#5-phiên-kết-nối-open-message-close-pingpong)
6. [Message format: text, binary, JSON protocol](#6-message-format-text-binary-json-protocol)
7. [Python `websockets`: server/client “chuẩn học tập”](#7-python-websockets-serverclient-chuẩn-học-tập)
8. [Broadcast, room, multi-client](#8-broadcast-room-multi-client)
9. [Reconnect, heartbeat, timeout, backpressure](#9-reconnect-heartbeat-timeout-backpressure)
10. [Auth: token, cookie, origin, permission](#10-auth-token-cookie-origin-permission)
11. [TLS: `wss://`, reverse proxy, production setup](#11-tls-wss-reverse-proxy-production-setup)
12. [Scale: nhiều server, Redis pub/sub, sticky session](#12-scale-nhiều-server-redis-pubsub-sticky-session)
13. [FastAPI WebSocket: khi nào nên dùng thay `websockets`](#13-fastapi-websocket-khi-nào-nên-dùng-thay-websockets)
14. [Bảng tổng hợp nhanh (khái niệm + lỗi hay gặp)](#14-bảng-tổng-hợp-nhanh-khái-niệm--lỗi-hay-gặp)
15. [Checklist debug + lỗi thường gặp](#15-checklist-debug--lỗi-thường-gặp)
16. [FORM KHỞI ĐỘNG CHUẨN (COPY/PASTE)](#16-form-khởi-động-chuẩn-copypaste)
17. [(Tuỳ chọn) Bài tập tự luyện](#17-tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. WebSocket là gì? Khi nào dùng?

**WebSocket** là một **giao thức cho phép client và server giữ một kết nối hai chiều, lâu dài, realtime**. Kết nối thường bắt đầu từ HTTP rồi **upgrade** sang WebSocket.

Điểm mạnh của WebSocket:

* **Full-duplex**: client và server đều có thể chủ động gửi data.
* **Realtime**: không cần polling liên tục.
* **Ít overhead hơn HTTP request lặp lại** trong các bài toán dữ liệu thay đổi thường xuyên.
* **Phù hợp web/app realtime**: chat, dashboard, notification, collaborative editing.

Khi nào dùng WebSocket?

* Chat realtime.
* Dashboard live (sensor, stock, telemetry, logs).
* Notification/presence (online/offline).
* Game multiplayer mức cơ bản.
* Điều khiển thiết bị theo thời gian thực từ web/app.

Khi nào *không* hợp?

* API request/response thông thường → HTTP/REST dễ hơn.
* Tác vụ cần retry/offline queue/pub-sub chuẩn chỉnh → có khi MQTT, Kafka, RabbitMQ hợp hơn.
* Truyền file lớn/stream media nặng → thường có giao thức tối ưu hơn.

> **Góc nhìn lập trình socket:** WebSocket là **giao thức tầng ứng dụng** chạy trên TCP. Nó không phải “raw socket”, và cũng không phải Socket.IO.

---

## 2. Các khái niệm cốt lõi (Client/Server/Connection/Message)

### 2.1 Client

**Client** thường là:

* browser (`new WebSocket(...)`)
* mobile app
* desktop app
* service khác

Client mở kết nối đến server và có thể:

* gửi message
* nhận message
* reconnect khi mất mạng

### 2.2 Server

**Server** là nơi chấp nhận kết nối WebSocket và quản lý:

* danh sách connection đang online
* route/broadcast message
* auth/permission
* heartbeat/timeouts

### 2.3 Connection

**Connection** là “đường dây đang mở” giữa client và server.

Mỗi connection có lifecycle:

* mở kết nối
* trao đổi message
* ping/pong/keepalive
* đóng kết nối

### 2.4 Message

Message WebSocket có thể là:

* **text frame** (string / JSON)
* **binary frame** (bytes)

Trong ứng dụng thực tế, bạn gần như luôn tự định nghĩa protocol ở tầng app, ví dụ JSON:

```json
{
  "type": "chat_message",
  "room": "general",
  "sender": "alice",
  "content": "xin chao",
  "ts": 1712345678
}
```

> **Nhớ câu này:** WebSocket chỉ là **đường ống**; ý nghĩa message là do **bạn tự thiết kế**.

---

## 3. HTTP vs Polling vs Long Polling vs WebSocket

### 3.1 HTTP thông thường

* Client gửi request.
* Server trả response.
* Kết thúc.

Phù hợp khi:

* user bấm nút lấy dữ liệu
* CRUD API
* request/response ngắn gọn

### 3.2 Polling

Client cứ vài giây lại hỏi:

* “Có dữ liệu mới chưa?”

Nhược điểm:

* tốn request
* có độ trễ giữa các lần poll

### 3.3 Long Polling

Client gửi request và server giữ request mở cho tới khi có data mới rồi mới trả.

Tốt hơn polling thường, nhưng vẫn là mô hình request/response “giả realtime”.

### 3.4 WebSocket

* Kết nối mở lâu dài.
* Cả hai bên chủ động gửi bất cứ lúc nào.

> **Chốt:** HTTP hợp cho API; WebSocket hợp cho **realtime 2 chiều**.

---

## 4. Handshake & nâng cấp kết nối (HTTP Upgrade)

### 4.1 WebSocket bắt đầu từ HTTP

Trình duyệt/client ban đầu gửi HTTP request với header kiểu:

```http
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: ...
Sec-WebSocket-Version: 13
```

Nếu server chấp nhận, nó trả `101 Switching Protocols` và từ đó kết nối được chuyển thành WebSocket.

### 4.2 Ý nghĩa của bước upgrade

Điều này giúp WebSocket:

* đi qua hạ tầng web quen thuộc hơn
* tận dụng domain/port/reverse proxy hiện có
* dễ tích hợp với app web

### 4.3 Lỗi hay gặp ở handshake

* route sai (`/ws` không tồn tại)
* reverse proxy không forward header upgrade
* auth/origin bị chặn
* dùng `ws://` ở site `https://` → browser chặn mixed content

---

## 5. Phiên kết nối: Open, Message, Close, Ping/Pong

### 5.1 Open

Khi handshake thành công:

* connection mở
* client/server bắt đầu gửi nhận data

### 5.2 Message

Trong suốt thời gian mở kết nối:

* client có thể gửi nhiều message
* server có thể gửi nhiều message
* message cũ hay mới đều gửi được nếu app gọi `send`

> WebSocket **không tự kiểm tra “data đổi chưa”**. App gọi `send` thì gửi.

### 5.3 Ping/Pong

Đây là cơ chế keepalive/heartbeat ở protocol level:

* một bên gửi **ping**
* bên kia trả **pong**

Mục tiêu:

* phát hiện connection chết
* giữ NAT/proxy không cắt đường truyền im lặng

### 5.4 Close

Kết nối có thể đóng vì:

* client chủ động đóng
* server chủ động đóng
* timeout/mất mạng
* lỗi protocol/auth

Có thể đi kèm **close code** và reason.

Một vài nhóm code hay gặp:

* `1000` – normal closure
* `1001` – going away
* `1008` – policy violation
* `1011` – internal error

> **Chốt:** muốn app “bền”, bạn phải hiểu rõ lúc nào connection mở, chết, stale, hoặc reconnect.

---

## 6. Message format: text, binary, JSON protocol

### 6.1 Text vs Binary

* **text**: dễ debug, thường là JSON/string
* **binary**: gọn hơn, có thể nhanh hơn, dùng khi payload là bytes/protobuf/msgpack…

Giai đoạn học + product đầu tiên: dùng JSON text là hợp lý nhất.

### 6.2 Tự thiết kế protocol ứng dụng

WebSocket **không có sẵn** khái niệm:

* room
  n* event name
* retry id
* ack nghiệp vụ
* version message

Bạn nên tự chuẩn hóa message. Ví dụ:

```json
{
  "type": "join_room",
  "room": "room-1",
  "request_id": "abc-123",
  "ts": 1712345678
}
```

Ví dụ chat message:

```json
{
  "type": "chat_message",
  "room": "room-1",
  "sender": "alice",
  "content": "hello",
  "message_id": "m-001",
  "ts": 1712345679
}
```

### 6.3 Những field rất nên có

* `type`: phân biệt message loại gì
* `request_id` / `message_id`: debug, dedupe, correlate
* `ts`: timestamp
* `room` / `channel` / `target`
* `payload`: dữ liệu chính
* `version`: khi protocol lớn dần

### 6.4 Cẩn thận

* JSON sai schema → server/client crash nếu parse ẩu
* payload quá lớn → tốn RAM, có thể bị cắt kết nối
* không validate `type`/permission → lộ lỗ hổng

---

## 7. Python `websockets`: server/client “chuẩn học tập”

> Đây là thư viện rất hợp để học **WebSocket thuần** trong Python.

Cài đặt:

```bash
pip install websockets
```

### 7.1 Server tối thiểu (echo)

```py
import asyncio
import websockets

async def handler(websocket):
    async for message in websocket:
        print(f"[SERVER] recv: {message}")
        await websocket.send(f"Echo: {message}")

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
        print("Server running at ws://127.0.0.1:8765")
        await asyncio.Future()

asyncio.run(main())
```

### 7.2 Client tối thiểu

```py
import asyncio
import websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        await ws.send("hello")
        reply = await ws.recv()
        print(f"[CLIENT] {reply}")

asyncio.run(main())
```

### 7.3 Vì sao ví dụ echo quan trọng?

Vì nó giúp bạn hiểu 3 điều nền:

* connection mở một lần
* gửi nhiều message trên cùng một connection
* `recv` / `send` là bất đồng bộ

---

## 8. Broadcast, room, multi-client

### 8.1 Một server nhiều client

Khi app có nhiều client cùng online, server cần quản lý tập kết nối:

```py
connected = set()
```

Khi client connect:

* thêm vào `connected`

Khi disconnect:

* remove khỏi `connected`

### 8.2 Broadcast cơ bản

```py
import asyncio
import websockets

connected = set()

async def handler(websocket):
    connected.add(websocket)
    try:
        async for message in websocket:
            tasks = [ws.send(f"BROADCAST: {message}") for ws in connected if ws != websocket]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        connected.discard(websocket)

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
        await asyncio.Future()

asyncio.run(main())
```

### 8.3 Room là gì?

Room chỉ là một abstraction do **bạn tự làm**:

* room A chứa tập client A
* room B chứa tập client B

WebSocket **không có room built-in** như Socket.IO.

Ví dụ:

```py
rooms = {
    "room-1": set(),
    "room-2": set(),
}
```

### 8.4 Lỗi hay gặp

* broadcast vào socket đã chết → exception
* không remove connection khi disconnect → memory leak
* gửi message tuần tự cho 1000 client → chậm; thường phải `gather`

---

## 9. Reconnect, heartbeat, timeout, backpressure

### 9.1 Reconnect

Trong mạng thật, connection sẽ chết vì:

* đổi Wi-Fi
* mất Internet
* server restart
* proxy timeout

Vì vậy client gần như luôn cần chiến lược reconnect:

* retry với backoff
* giới hạn số lần thử
* re-auth/resubscribe/state sync sau khi nối lại

Ví dụ client reconnect đơn giản:

```py
import asyncio
import websockets

async def run_forever():
    while True:
        try:
            async with websockets.connect("ws://127.0.0.1:8765") as ws:
                print("Connected")
                while True:
                    msg = await ws.recv()
                    print(msg)
        except Exception as e:
            print("Disconnected:", e)
            await asyncio.sleep(2)

asyncio.run(run_forever())
```

### 9.2 Heartbeat

Ngoài ping/pong của protocol, app lớn đôi khi còn có heartbeat ở tầng business:

```json
{ "type": "heartbeat", "ts": 1712345678 }
```

Dùng khi muốn:

* đo latency
* theo dõi user presence
* kiểm tra state app-level

### 9.3 Timeout

Bạn nên định nghĩa rõ:

* handshake timeout
* idle timeout
* write timeout
* auth timeout sau khi connect

### 9.4 Backpressure là gì?

Nếu server gửi nhanh hơn client đọc, buffer sẽ phình lên.

Hậu quả:

* RAM tăng
* latency tăng
* connection bị drop

Cách xử lý:

* giới hạn tốc độ gửi
* drop message cũ nếu là data realtime không cần history
* tách “hot path” / “slow consumer”
* queue per-connection có giới hạn

> **Chốt:** demo local thường mượt; production thường chết ở reconnect, timeout, backpressure.

---

## 10. Auth: token, cookie, origin, permission

### 10.1 Vì sao WebSocket cần auth?

Nếu không auth/authorize:

* ai cũng kết nối được
* ai cũng nhận data của người khác
* ai cũng gửi lệnh bậy

### 10.2 Các cách auth phổ biến

1. **Cookie/session**

   * hợp nếu cùng web app và server đã có login session

2. **Token/JWT**

   * query string hoặc header ở handshake (tuỳ hạ tầng/client)

3. **Auth message đầu tiên**

   * vừa connect xong phải gửi:

```json
{ "type": "auth", "token": "..." }
```

Nếu fail → close connection.

### 10.3 Origin check

Với browser, bạn nên kiểm tra `Origin` để tránh bị site lạ mở WebSocket đến server của bạn theo ngữ cảnh người dùng.

### 10.4 Permission

Auth xong chưa đủ; còn phải check quyền:

* user nào được join room nào?
* user nào được nhận event nào?
* user nào được gửi command nào?

Ví dụ:

* admin được gửi `shutdown_server`
* user thường thì không

> **Chốt:** WebSocket “mở được” không có nghĩa là “nên cho nói gì cũng được”.

---

## 11. TLS: `wss://`, reverse proxy, production setup

### 11.1 `ws://` vs `wss://`

* `ws://` = WebSocket plain, không mã hóa
* `wss://` = WebSocket over TLS, mã hóa như HTTPS

Production/public Internet gần như luôn dùng **`wss://`**.

### 11.2 Browser rule rất hay gặp

Nếu website của bạn chạy bằng `https://`, thì browser thường **không cho** mở `ws://` (mixed content). Bạn phải dùng `wss://`.

### 11.3 Reverse proxy

Triển khai thực tế thường là:

* Nginx / Traefik / Caddy terminate TLS
* forward request upgrade vào app server nội bộ

Ví dụ Nginx cần forward các header upgrade đúng:

```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

### 11.4 Production setup tối thiểu nên có

* TLS (`wss://`)
* auth
* origin/host validation
* size limit cho message
* timeout/heartbeat
* logging connection open/close/error

---

## 12. Scale: nhiều server, Redis pub/sub, sticky session

### 12.1 Vấn đề khi scale ngang

Giả sử có 2 server WebSocket:

* Client A nối vào Server 1
* Client B nối vào Server 2

Nếu A gửi tin nhắn cho B, Server 1 phải somehow chuyển event sang Server 2.

### 12.2 Tại sao 1 máy chạy được chưa đủ?

Vì broadcast/local memory chỉ biết client đang nối vào **chính process đó**.

Khi scale nhiều process/server, bạn cần **shared bus**.

### 12.3 Giải pháp phổ biến

* **Redis pub/sub**
* Kafka / NATS / RabbitMQ (tuỳ bài toán)
* database/event log cho state/history

Một pattern phổ biến:

```text
Client <-> WS Server 1 <-\
                        Redis pub/sub
Client <-> WS Server 2 <-/
```

### 12.4 Sticky session có cần không?

Có thể cần nếu app giữ state per-connection/per-process và load balancer cần gửi user quay lại đúng instance. Nhưng sticky session **không thay thế** được shared pub/sub cho broadcast liên server.

### 12.5 Chốt kiến trúc

* WebSocket giỏi truyền realtime tới frontend.
* Redis/broker giỏi phát event liên process.
* Database giỏi lưu history/state.

> **Nhớ:** WebSocket không thay database, không thay broker, không thay queue.

---

## 13. FastAPI WebSocket: khi nào nên dùng thay `websockets`

### 13.1 `websockets`

Hợp khi:

* muốn học WebSocket thuần
* làm service nhỏ, focused
* ít phụ thuộc framework web

### 13.2 FastAPI WebSocket

Hợp khi:

* app của bạn đã có REST API bằng FastAPI
* muốn auth, dependency, route, HTTP + WS cùng chỗ
* muốn dễ tích hợp với backend web hiện có

Ví dụ FastAPI tối thiểu:

```py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
clients = set()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            message = await ws.receive_text()
            for client in list(clients):
                await client.send_text(f"Broadcast: {message}")
    except WebSocketDisconnect:
        clients.discard(ws)
```

### 13.3 Chọn cái nào?

* muốn hiểu bản chất trước → `websockets`
* đang build product web/backend → FastAPI thường thực dụng hơn

---

## 14. Bảng tổng hợp nhanh (khái niệm + lỗi hay gặp)

### 14.1 WebSocket concepts

| Khái niệm    | Ý nghĩa “1 câu”                              |
| ------------ | -------------------------------------------- |
| Handshake    | bắt đầu bằng HTTP rồi upgrade sang WebSocket |
| Connection   | đường truyền 2 chiều được giữ mở             |
| Text frame   | message dạng string/JSON                     |
| Binary frame | message dạng bytes                           |
| Ping/Pong    | keepalive/heartbeat ở protocol level         |
| Close code   | mã lý do đóng kết nối                        |
| Broadcast    | gửi 1 message cho nhiều client               |
| Room         | nhóm client do app tự quản lý                |
| Reconnect    | client tự nối lại khi connection chết        |
| Backpressure | server gửi nhanh hơn client tiêu thụ         |
| Auth         | xác minh ai được kết nối                     |
| `wss://`     | WebSocket chạy qua TLS                       |

### 14.2 WebSocket vs thứ khác

| Công nghệ     | Vai trò chính                                              |
| ------------- | ---------------------------------------------------------- |
| HTTP          | request/response API                                       |
| WebSocket     | realtime 2 chiều client-server                             |
| Socket.IO     | library realtime mức cao, có room/event/reconnect tiện hơn |
| MQTT          | pub/sub qua broker, rất hợp IoT/device telemetry           |
| Redis pub/sub | bus nội bộ giữa các server/process                         |

---

## 15. Checklist debug + lỗi thường gặp

### 15.1 Checklist 60 giây

1. Server có đang chạy không?
2. URL đúng chưa? (`ws://host:port/path`)
3. Route `/ws` có tồn tại không?
4. Có bị mixed content không? (`https://` nhưng lại gọi `ws://`)
5. Reverse proxy có forward `Upgrade`/`Connection` header không?
6. Token/cookie/auth có hợp lệ không?
7. Có parse JSON lỗi không?
8. Có heartbeat/timeout làm connection bị đá không?
9. Có gửi payload quá lớn không?
10. Có socket đã chết mà vẫn broadcast vào đó không?

### 15.2 Lỗi hay gặp (và cách hiểu)

* `403` / handshake fail: auth/origin/policy chặn.
* `404` khi connect: sai route WebSocket.
* Kết nối mở rồi tự rớt sau vài chục giây: proxy idle timeout / không có ping-pong.
* Chạy local được, qua Nginx hỏng: thiếu header upgrade.
* Client vào sau không thấy message cũ: WebSocket không tự lưu history.
* Server đơ khi broadcast: slow client / backpressure / không giới hạn queue.
* Browser site `https` nhưng WS `ws://`: mixed content bị chặn.

---

## 16. FORM KHỞI ĐỘNG CHUẨN (COPY/PASTE)

> Mục tiêu: 2 terminal, chạy là thấy message ngay. Đây là “form” bạn có thể copy cho mọi bài WebSocket cơ bản.

### 16.1 Terminal 1 — SERVER (`server.py`)

```py
import asyncio
import websockets

async def handler(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"[SERVER] recv: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
        print("Server running at ws://127.0.0.1:8765")
        await asyncio.Future()

asyncio.run(main())
```

Chạy:

```bash
python server.py
```

### 16.2 Terminal 2 — CLIENT (`client.py`)

```py
import asyncio
import websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        await ws.send("hello")
        print("[CLIENT] sent: hello")

        reply = await ws.recv()
        print(f"[CLIENT] recv: {reply}")

asyncio.run(main())
```

Chạy:

```bash
python client.py
```

### 16.3 FORM Python broadcast “chuẩn học tập”

```py
import asyncio
import websockets

connected = set()

async def handler(websocket):
    connected.add(websocket)
    print(f"Connected: {len(connected)} client(s)")
    try:
        async for message in websocket:
            print(f"[SERVER] {message}")
            await asyncio.gather(
                *[ws.send(message) for ws in connected if ws.open],
                return_exceptions=True,
            )
    finally:
        connected.discard(websocket)
        print(f"Disconnected: {len(connected)} client(s)")

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
        await asyncio.Future()

asyncio.run(main())
```

---

## 17. (Tuỳ chọn) Bài tập tự luyện

1. **Lifecycle drill**

* In log khi `connect`, `message`, `disconnect`.
* Rút mạng / kill client / restart server để quan sát.

2. **Broadcast drill**

* Mở 2 client cùng lúc.
* Một client gửi, client kia phải nhận.

3. **JSON protocol drill**

* Định nghĩa 3 loại message:

  * `join`
  * `chat`
  * `leave`
* Validate `type` trước khi xử lý.

4. **Reconnect drill**

* Viết client tự reconnect sau 2 giây khi server tắt/bật lại.

5. **Auth drill**

* Bắt client gửi message auth đầu tiên.
* Token sai → close với reason phù hợp.

6. **History drill**

* Lưu 20 message gần nhất trong memory hoặc DB.
* Client mới connect nhận history ngay.

7. **Scale drill**

* Chạy 2 process server.
* Dùng Redis pub/sub để chuyển message giữa 2 process.

---

### Tài liệu chính thống (để bạn học sâu hơn)

> Mình để link trong code block để bạn tiện copy.

```text
MDN WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
MDN Writing WebSocket client applications: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications
Python websockets docs: https://websockets.readthedocs.io/
FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
RFC 6455 (WebSocket Protocol): https://datatracker.ietf.org/doc/html/rfc6455
```
