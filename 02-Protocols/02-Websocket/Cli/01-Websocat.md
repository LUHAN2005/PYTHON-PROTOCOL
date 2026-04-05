# 01-Websocat

> Mục tiêu của tài liệu này: giúp bạn **hiểu sâu và dùng thành thạo `websocat`** để test, debug, học và làm việc với WebSocket ở mức rất thực dụng.
>
> Đọc xong, bạn sẽ nắm được:
>
> * `websocat` là gì và dùng để làm gì
> * cách cài đặt
> * cách kết nối tới WebSocket server
> * cách gửi / nhận message từ terminal
> * cách dùng `websocat` để debug server Python / FastAPI / Node
> * cách pipe dữ liệu, dùng file, stdin/stdout
> * cách test `ws://` và `wss://`
> * các mode nâng cao, pattern thực chiến và lỗi thường gặp

---

## MỤC LỤC

1. [Websocat là gì?](#1-websocat-là-gì)
2. [Khi nào nên dùng websocat?](#2-khi-nào-nên-dùng-websocat)
3. [Websocat khác gì với `websockets` / browser / Postman?](#3-websocat-khác-gì-với-websockets--browser--postman)
4. [Cách cài đặt](#4-cách-cài-đặt)
5. [Chạy lệnh đầu tiên](#5-chạy-lệnh-đầu-tiên)
6. [Mô hình tư duy của websocat: nguồn vào ↔ nguồn ra](#6-mô-hình-tư-duy-của-websocat-nguồn-vào--nguồn-ra)
7. [Kết nối tới WebSocket server cơ bản](#7-kết-nối-tới-websocket-server-cơ-bản)
8. [Gửi và nhận message từ terminal](#8-gửi-và-nhận-message-từ-terminal)
9. [Test echo server](#9-test-echo-server)
10. [Test server Python `websockets`](#10-test-server-python-websockets)
11. [Test FastAPI WebSocket](#11-test-fastapi-websocket)
12. [Làm việc với JSON message](#12-làm-việc-với-json-message)
13. [Pipe dữ liệu với file, stdin, shell](#13-pipe-dữ-liệu-với-file-stdin-shell)
14. [Dùng websocat như WebSocket client thật sự](#14-dùng-websocat-như-websocket-client-thật-sự)
15. [Kết nối `wss://` và TLS](#15-kết-nối-wss-và-tls)
16. [Header, Origin, auth token, cookie](#16-header-origin-auth-token-cookie)
17. [Chế độ verbose, debug, inspect lỗi](#17-chế-độ-verbose-debug-inspect-lỗi)
18. [Mode nâng cao và pattern hữu ích](#18-mode-nâng-cao-và-pattern-hữu-ích)
19. [Hạn chế của websocat](#19-hạn-chế-của-websocat)
20. [Checklist debug WebSocket bằng websocat](#20-checklist-debug-websocket-bằng-websocat)
21. [Lỗi thường gặp](#21-lỗi-thường-gặp)
22. [FORM KHỞI ĐỘNG CHUẨN (COPY/PASTE)](#22-form-khởi-động-chuẩn-copypaste)
23. [Bài tập tự luyện](#23-bài-tập-tự-luyện)
24. [Tóm tắt một trang](#24-tóm-tắt-một-trang)

---

## 1. Websocat là gì?

`websocat` là một **công cụ dòng lệnh (CLI)** để làm việc với **WebSocket**.

Cách hiểu ngắn gọn nhất:

* `curl` rất tiện cho HTTP
* `websocat` rất tiện cho WebSocket

Nó cho phép bạn:

* mở kết nối đến một WebSocket server
* gửi message thủ công từ terminal
* nhận message trả về ngay trong terminal
* test route WebSocket mà không cần viết client code
* debug handshake, header, TLS, auth
* nối dữ liệu từ file/stdin/process vào WebSocket

### Ý tưởng cốt lõi

`websocat` là cây cầu giữa:

* **terminal / stdin / file / process**
* và **WebSocket connection**

Nghĩa là thay vì viết code Python hay JavaScript client để test, bạn chỉ cần một lệnh CLI.

---

## 2. Khi nào nên dùng websocat?

`websocat` đặc biệt hữu ích khi bạn đang:

* học WebSocket
* vừa viết xong server và muốn test nhanh
* debug route `/ws`
* kiểm tra auth token / header / origin
* gửi thử JSON message vào server
* xem server trả gì theo thời gian thực
* mô phỏng client đơn giản trong terminal
* test app realtime mà không muốn mở browser/frontend

### Những case rất hay dùng

#### Case 1: Bạn vừa viết WebSocket server bằng Python

Bạn muốn biết:

* server có chạy chưa?
* route có đúng không?
* gửi `hello` thì server trả gì?

=> `websocat` là cách nhanh nhất.

#### Case 2: Bạn có server yêu cầu token/header

Bạn muốn test:

* header có gửi đúng chưa?
* auth có pass không?

=> `websocat` giúp bạn bơm header thủ công.

#### Case 3: Bạn có stream realtime

Bạn muốn xem dữ liệu đẩy xuống liên tục trong terminal.

=> `websocat` cực hợp.

---

## 3. Websocat khác gì với `websockets` / browser / Postman?

### So với `websockets` trong Python

* `websockets` là **thư viện để lập trình** WebSocket client/server
* `websocat` là **tool để test thủ công** WebSocket

### So với browser

* browser rất tiện cho app thật
* nhưng test thủ công thì khó quan sát hơn terminal
* browser cũng bị ràng buộc bởi same-origin, cookie context, mixed content

### So với Postman / tool GUI

* Postman có thể test WebSocket theo kiểu UI
* `websocat` nhẹ, nhanh, hợp automation và shell scripting hơn
* `websocat` rất tiện khi bạn làm backend / DevOps / debug local server

### So với `curl`

* `curl` không phải công cụ chuẩn cho full WebSocket conversation
* `websocat` sinh ra đúng để làm việc với WebSocket

> **Câu nhớ nhanh:** `websocat` là “WebSocket terminal client” thực dụng nhất để học và debug.

---

## 4. Cách cài đặt

Có nhiều cách cài tuỳ hệ điều hành.

### 4.1 Cài bằng binary release

Thường đơn giản nhất là tải binary build sẵn rồi chạy trực tiếp.

Ví dụ tư duy:

* tải file binary từ release page
* giải nén
* thêm vào PATH
* chạy `websocat --help`

### 4.2 Cài bằng Cargo (nếu có Rust)

```bash
cargo install websocat
```

Cách này hợp nếu bạn đã có Rust toolchain.

### 4.3 Kiểm tra sau khi cài

```bash
websocat --help
```

Nếu thành công, bạn sẽ thấy danh sách option và mode hoạt động.

### 4.4 Kiểm tra version

```bash
websocat --version
```

---

## 5. Chạy lệnh đầu tiên

Giả sử bạn có WebSocket server ở:

```text
ws://127.0.0.1:8765
```

Lệnh đơn giản nhất:

```bash
websocat ws://127.0.0.1:8765
```

Khi đó:

* terminal của bạn trở thành nơi nhập message
* mỗi dòng bạn gõ sẽ được gửi qua WebSocket
* message server trả về sẽ hiện ra trên terminal

Ví dụ:

Bạn gõ:

```text
hello
```

Nếu server là echo server, nó có thể trả:

```text
Echo: hello
```

---

## 6. Mô hình tư duy của websocat: nguồn vào ↔ nguồn ra

Đây là phần rất quan trọng để master.

`websocat` thường hoạt động theo kiểu:

```text
endpoint A  <->  endpoint B
```

Một endpoint có thể là:

* `ws://...`
* `wss://...`
* `-` (stdin/stdout)
* file
* process
* TCP socket
* listener

### Trường hợp đơn giản nhất

```bash
websocat - ws://127.0.0.1:8765
```

Ý nghĩa:

* `-` là stdin/stdout của terminal
* bên kia là WebSocket server

Nghĩa là dữ liệu bạn gõ vào terminal sẽ đi vào WebSocket.

### Có thể viết ngắn hơn

```bash
websocat ws://127.0.0.1:8765
```

Trong nhiều tình huống, `websocat` sẽ hiểu bạn muốn dùng terminal làm đầu vào/ra.

### Vì sao tư duy “2 endpoint” quan trọng?

Vì khi hiểu nó, bạn sẽ dễ học các mode nâng cao như:

* file ↔ WebSocket
* process ↔ WebSocket
* TCP ↔ WebSocket
* listener ↔ WebSocket

---

## 7. Kết nối tới WebSocket server cơ bản

### 7.1 Kết nối local server

```bash
websocat ws://localhost:8765
```

hoặc:

```bash
websocat ws://127.0.0.1:8765
```

### 7.2 Kết nối route cụ thể

```bash
websocat ws://127.0.0.1:8000/ws
```

### 7.3 Kết nối server public

```bash
websocat wss://example.com/ws
```

### 7.4 Nếu server yêu cầu path đúng

Rất hay gặp lỗi do sai path.

Ví dụ server FastAPI mount tại `/ws/chat`, nhưng bạn lại gọi `/ws`.

=> handshake sẽ fail hoặc trả 404.

---

## 8. Gửi và nhận message từ terminal

Khi kết nối bằng `websocat`, bạn thường làm việc theo dòng.

Bạn gõ một dòng:

```text
xin chao
```

rồi nhấn Enter.

`websocat` gửi dòng đó như một WebSocket message (thường là text message).

### Điều cần nhớ

* mỗi dòng nhập thường tương ứng với một message text
* nếu server trả response, bạn sẽ thấy nó ngay
* nếu server chỉ nhận mà không trả, terminal có thể im lặng

### Kiểu server thường gặp

#### Echo server

Bạn gửi gì nó trả lại đó.

#### Broadcast server

Bạn gửi từ client A, client B nhận được.

#### Command server

Bạn gửi JSON command, server trả JSON result.

---

## 9. Test echo server

Echo server là ví dụ đẹp nhất để học `websocat`.

Nếu bạn có echo server ở `ws://127.0.0.1:8765`, chạy:

```bash
websocat ws://127.0.0.1:8765
```

Sau đó gõ:

```text
hello
```

kỳ vọng:

```text
Echo: hello
```

Gõ tiếp:

```text
123
```

kỳ vọng:

```text
Echo: 123
```

Điều này cho bạn thấy:

* connection đang mở lâu dài
* không phải mỗi message là một request mới
* nhiều message đi trên cùng một connection

---

## 10. Test server Python `websockets`

### 10.1 Server ví dụ

```python
import asyncio
import websockets

async def handler(websocket):
    async for message in websocket:
        print(f"[SERVER] {message}")
        await websocket.send(f"Echo: {message}")

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
        print("Server running at ws://127.0.0.1:8765")
        await asyncio.Future()

asyncio.run(main())
```

Chạy server:

```bash
python server.py
```

### 10.2 Test bằng websocat

```bash
websocat ws://127.0.0.1:8765
```

Gõ:

```text
hello from websocat
```

### 10.3 Bạn sẽ thấy gì?

Ở terminal server:

```text
[SERVER] hello from websocat
```

Ở terminal `websocat`:

```text
Echo: hello from websocat
```

### 10.4 Vì sao cách này rất tốt khi học?

Vì bạn tách được:

* **server logic** ở Python
* **client test tool** là `websocat`

Bạn không cần viết thêm file client Python để test.

---

## 11. Test FastAPI WebSocket

### 11.1 Server ví dụ

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"FastAPI echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

Chạy bằng Uvicorn:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 11.2 Test bằng websocat

```bash
websocat ws://127.0.0.1:8000/ws
```

Gõ:

```text
hello fastapi
```

Kỳ vọng:

```text
FastAPI echo: hello fastapi
```

### 11.3 Giá trị thực tế

Đây là combo rất mạnh khi học backend:

* viết WebSocket endpoint bằng FastAPI
* test nhanh bằng `websocat`

---

## 12. Làm việc với JSON message

Trong hệ thống thật, bạn hiếm khi chỉ gửi string đơn giản. Thường bạn sẽ gửi JSON.

Ví dụ:

```json
{"type":"ping","client":"cli","ts":1712345678}
```

Dùng `websocat`, bạn có thể paste JSON thẳng vào terminal nếu server đọc text JSON.

### Ví dụ command message

```json
{"type":"join","room":"general","user":"alice"}
```

```json
{"type":"chat","room":"general","content":"xin chao moi nguoi"}
```

### Mẹo học rất hay

Khi bạn đang thiết kế WebSocket protocol, hãy dùng `websocat` để:

* gửi thử JSON bằng tay
* xem server validate ra sao
* test message nào pass/fail

Điều này giúp bạn học protocol design rất nhanh.

### Cẩn thận

Nếu server parse JSON nghiêm, chỉ cần:

* thiếu dấu `}`
* dùng quote sai
* field thiếu

là nó có thể reject hoặc đóng connection.

---

## 13. Pipe dữ liệu với file, stdin, shell

Đây là chỗ `websocat` rất mạnh.

Bạn không chỉ gõ tay. Bạn có thể pipe dữ liệu từ command khác vào WebSocket.

### 13.1 Echo một dòng bằng shell

```bash
echo 'hello' | websocat ws://127.0.0.1:8765
```

Ý tưởng:

* `echo` tạo input
* `websocat` gửi input đó vào WebSocket

### 13.2 Gửi file line-by-line

Ví dụ file `messages.txt` có nội dung:

```text
hello
how are you
bye
```

Bạn có thể làm kiểu:

```bash
cat messages.txt | websocat ws://127.0.0.1:8765
```

### 13.3 Pipe từ process sinh dữ liệu liên tục

Ví dụ:

```bash
tail -f app.log | websocat ws://127.0.0.1:8765
```

Ý tưởng này rất mạnh về mặt tư duy:

* log stream
* sensor stream
* event stream

đều có thể bị đẩy vào WebSocket.

### 13.4 Tại sao điều này hay?

Vì `websocat` trở thành một adapter:

* dữ liệu shell/process/file
* chuyển vào WebSocket server

Đây là lý do dân backend và hệ thống rất thích tool kiểu này.

---

## 14. Dùng websocat như WebSocket client thật sự

Ở mức học master, bạn nên xem `websocat` như một **client tối giản nhưng rất mạnh**.

Nó không chỉ để “thử một câu hello”.

Bạn có thể dùng nó để:

* giữ connection mở lâu dài
* quan sát stream data
* mô phỏng client CLI
* test lifecycle disconnect/reconnect thủ công
* kiểm tra server khi không có frontend

### Ví dụ: quan sát stream realtime

Nếu server cứ vài giây gửi metric như:

```json
{"cpu": 31, "mem": 62}
```

thì chạy:

```bash
websocat ws://127.0.0.1:9000/metrics
```

Bạn sẽ thấy dòng dữ liệu đẩy xuống liên tục.

### Ví dụ: test broadcast

Mở 2 terminal:

Terminal A:

```bash
websocat ws://127.0.0.1:8765
```

Terminal B:

```bash
websocat ws://127.0.0.1:8765
```

Nếu server broadcast đúng, message từ A có thể xuất hiện ở B.

---

## 15. Kết nối `wss://` và TLS

`websocat` không chỉ làm việc với `ws://`, mà còn có thể dùng với `wss://`.

### 15.1 Ví dụ

```bash
websocat wss://example.com/ws
```

### 15.2 Khi nào phải dùng `wss://`?

* khi server ở production
* khi chạy sau HTTPS/TLS
* khi browser/app public cần mã hoá đường truyền

### 15.3 Những lỗi hay gặp với TLS

* certificate self-signed
* CA không tin cậy
* domain không khớp cert
* reverse proxy cấu hình sai

### 15.4 Học gì từ đây?

Khi `ws://` local chạy tốt nhưng `wss://` production lỗi, `websocat` là công cụ rất tốt để bóc tách vấn đề ở tầng transport/TLS.

---

## 16. Header, Origin, auth token, cookie

Một WebSocket server thật thường không “mở cửa tự do”.

Nó có thể yêu cầu:

* Authorization token
* custom header
* Origin hợp lệ
* cookie/session

`websocat` hữu ích vì bạn có thể chủ động gửi các thông tin này khi test.

### 16.1 Gửi header tùy chỉnh

Ví dụ tư duy:

* gửi `Authorization: Bearer ...`
* gửi `Origin: http://localhost:3000`
* gửi custom header nội bộ

### 16.2 Test auth token

Đây là pattern rất hay gặp:

* server reject nếu thiếu token
* `websocat` cho phép bạn thử từng biến thể token

### 16.3 Test Origin

Nhiều server browser-facing kiểm tra `Origin`.

Nếu browser connect được nhưng CLI không được, hoặc ngược lại, bạn nên nghi ngay tới:

* origin policy
* auth context
* cookie/session khác nhau

### 16.4 Vì sao phần này quan trọng?

Rất nhiều người tưởng server WebSocket hỏng, nhưng thực ra là:

* route đúng
* code đúng
* chỉ sai header/auth/origin

`websocat` là công cụ chẩn đoán cực tốt cho chuyện này.

---

## 17. Chế độ verbose, debug, inspect lỗi

Khi học sâu, bạn không chỉ muốn “nó chạy”, mà còn muốn biết **nó fail ở đâu**.

`websocat` có các mode/options hỗ trợ quan sát nhiều hơn. Ý tưởng là tăng mức log để xem:

* có connect được không
* handshake fail ở bước nào
* TLS fail hay auth fail
* connection bị close lúc nào

### Pattern học rất tốt

1. chạy server
2. chạy `websocat`
3. nếu lỗi, tăng verbosity
4. so log client và server
5. xác định lỗi nằm ở:

   * DNS / network
   * route
   * TLS
   * auth
   * protocol app

### Dấu hiệu thực tế

* connect fail ngay → route / server chưa chạy / handshake sai
* connect được rồi rớt ngay → auth timeout / ping timeout / server close
* gửi text không thấy phản hồi → server không echo hoặc server chỉ broadcast chỗ khác

---

## 18. Mode nâng cao và pattern hữu ích

Phần này là nơi bạn bắt đầu “pro” hơn.

### 18.1 Dùng websocat như bridge

Bạn có thể dùng `websocat` để bridge dữ liệu giữa 2 đầu:

* stdin ↔ WebSocket
* TCP ↔ WebSocket
* file ↔ WebSocket
* process ↔ WebSocket

Tư duy này cực mạnh trong debug và automation.

### 18.2 Listener mode

Ngoài chuyện connect ra ngoài, `websocat` còn có thể làm đầu lắng nghe trong một số pattern. Tức là nó không chỉ làm client đơn giản, mà còn có thể đứng giữa để relay.

### 18.3 Dùng để replay dữ liệu test

Bạn có thể chuẩn bị file nhiều dòng JSON rồi đẩy lần lượt vào server để test protocol.

Ví dụ file `events.jsonl`:

```text
{"type":"join","room":"dev"}
{"type":"chat","content":"hello"}
{"type":"chat","content":"second message"}
```

rồi dùng:

```bash
cat events.jsonl | websocat ws://127.0.0.1:8765
```

### 18.4 Dùng để test load nhẹ thủ công

Dù `websocat` không phải tool benchmark chuyên nghiệp, bạn vẫn có thể mở nhiều terminal để mô phỏng nhiều client thủ công.

Ví dụ:

* mở 5 terminal
* cho 5 `websocat` cùng connect
* quan sát server xử lý broadcast và cleanup connection

### 18.5 Dùng để test edge case

Ví dụ bạn muốn xem server phản ứng thế nào nếu client gửi:

* JSON sai format
* message quá dài
* message type lạ
* token sai
* room không tồn tại

`websocat` là cách làm rất nhanh.

---

## 19. Hạn chế của websocat

Dù rất tiện, `websocat` không thay thế hoàn toàn client app thật.

### Các hạn chế chính

1. **Không phải UI app thật**

   * không mô phỏng browser hoàn chỉnh
   * không có UX như frontend thật

2. **Không phải framework test end-to-end**

   * nó mạnh ở debug thủ công và scripting

3. **Không phải load testing tool chuyên nghiệp**

   * muốn benchmark lớn, thường dùng tool khác

4. **Không tự thay thế logic client phức tạp**

   * reconnect strategy
   * local state
   * protocol workflow nhiều bước
   * rendering UI

### Kết luận đúng

`websocat` rất mạnh cho:

* học
* test nhanh
* debug
* automation đơn giản

nhưng không thay hoàn toàn được app client thực tế.

---

## 20. Checklist debug WebSocket bằng websocat

Khi kết nối không chạy, hãy đi theo checklist này.

### Checklist 60 giây

1. Server có đang chạy không?
2. URL có đúng host/port/path không?
3. Dùng `ws://` hay `wss://` đúng chưa?
4. Nếu `wss://`, TLS/cert có vấn đề không?
5. Server có yêu cầu auth token không?
6. Server có kiểm tra `Origin` không?
7. Có reverse proxy ở giữa không?
8. Proxy có forward Upgrade header đúng không?
9. Server có đòi JSON đúng schema không?
10. Connection mở xong có bị đóng ngay không?

### Câu hỏi cực quan trọng

* handshake fail hay app-level fail?
* server không trả gì, hay trả rồi bạn không thấy?
* lỗi nằm ở transport, auth, hay logic protocol?

---

## 21. Lỗi thường gặp

### 21.1 `connection refused`

Thường là:

* server chưa chạy
* sai port
* sai host

### 21.2 `404` / handshake fail

Thường là:

* sai path `/ws`
* route WebSocket chưa mount đúng

### 21.3 `403` / bị đóng ngay

Thường là:

* auth fail
* origin fail
* policy violation

### 21.4 `TLS` / certificate error

Thường là:

* self-signed cert
* CA không trust
* hostname mismatch

### 21.5 Kết nối mở nhưng không thấy phản hồi

Có thể là:

* server chỉ nhận, không echo
* server đợi JSON đúng format
* server gửi sang client khác chứ không gửi lại chính bạn

### 21.6 Gửi JSON mà server báo lỗi

Thường là:

* JSON sai cú pháp
* thiếu field bắt buộc
* `type` không hợp lệ

### 21.7 Chạy local được, production không được

Thường là:

* `ws://` vs `wss://`
* reverse proxy
* auth header
* origin
* TLS/cert

---

## 22. FORM KHỞI ĐỘNG CHUẨN (COPY/PASTE)

### 22.1 Form 1 — Test echo server local

Server Python:

```python
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

Chạy:

```bash
python server.py
```

Terminal khác:

```bash
websocat ws://127.0.0.1:8765
```

Gõ:

```text
hello
```

### 22.2 Form 2 — Test FastAPI WebSocket

Server:

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        await ws.send_text(f"FastAPI echo: {data}")
```

Chạy:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Test:

```bash
websocat ws://127.0.0.1:8000/ws
```

### 22.3 Form 3 — Gửi JSON nhanh

```bash
websocat ws://127.0.0.1:8000/ws
```

Paste:

```json
{"type":"ping","client":"websocat"}
```

### 22.4 Form 4 — Pipe một message từ shell

```bash
echo '{"type":"ping"}' | websocat ws://127.0.0.1:8000/ws
```

---

## 23. Bài tập tự luyện

### Bài 1 — Echo cơ bản

* viết server echo Python
* test bằng `websocat`
* gửi 5 message khác nhau

### Bài 2 — JSON protocol

* server yêu cầu JSON có field `type`
* dùng `websocat` gửi:

  * JSON đúng
  * JSON sai
  * thiếu field
* quan sát log server

### Bài 3 — Broadcast

* viết server broadcast
* mở 2 terminal `websocat`
* terminal A gửi, terminal B nhận

### Bài 4 — Auth token

* server yêu cầu token qua header hoặc message đầu tiên
* test token đúng/sai bằng `websocat`

### Bài 5 — Route sai / path sai

* cố tình gọi sai `/ws`
* quan sát lỗi handshake

### Bài 6 — `wss://`

* chạy sau reverse proxy/TLS
* test bằng `websocat`
* phân biệt lỗi TLS với lỗi app logic

---

## 24. Tóm tắt một trang

### Websocat là gì?

Là **tool CLI để kết nối và test WebSocket**.

### Nó dùng để làm gì?

* test server WebSocket nhanh
* gửi/nhận message từ terminal
* debug auth, TLS, route, JSON protocol
* pipe dữ liệu từ shell/file/process vào WebSocket

### Khi nào nên dùng?

* đang học WebSocket
* debug backend realtime
* chưa có frontend/client hoàn chỉnh
* muốn kiểm tra server thật nhanh

### Nó không thay cái gì?

* không thay app client thật
* không thay load test tool chuyên nghiệp
* không thay framework E2E

### Câu chốt cần nhớ

> `websocat` là công cụ cực mạnh để **học bản chất WebSocket, test nhanh, và debug hệ thống realtime** mà không phải viết client code mỗi lần.

---

## Tài liệu tham khảo để học sâu hơn

```text
Websocat GitHub: https://github.com/vi/websocat
WebSocket RFC 6455: https://datatracker.ietf.org/doc/html/rfc6455
MDN WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
Python websockets docs: https://websockets.readthedocs.io/
FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
```

