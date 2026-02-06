# BÀI 1 : NETWORKING – BASIC

> Mục tiêu của bài này: bạn hiểu **mạng đủ chắc** để không “mơ hồ” khi đọc OSI/TCP‑IP, và quan trọng nhất là biết cách **code giao thức (protocol) chạy thật**: TCP/UDP • framing • heartbeat • reconnect • retry/idempotency.

---

## MỤC LỤC

1. [Tổng quan về mạng](#1-tổng-quan-về-mạng)
2. [Các nguyên lý cơ bản của mạng máy tính](#2-các-nguyên-lý-cơ-bản-của-mạng-máy-tính)
3. [Kiến trúc mạng máy tính](#3-kiến-trúc-mạng-máy-tính)
4. [Mô hình mạng: OSI & TCP/IP](#4-mô-hình-mạng-osi--tcpip)
5. [Socket & Port (góc nhìn lập trình)](#5-socket--port-góc-nhìn-lập-trình)
6. [TCP/UDP theo góc nhìn lập trình socket](#6-tcpudp-theo-góc-nhìn-lập-trình-socket)
7. [Framing: biến TCP stream thành message](#7-framing-biến-tcp-stream-thành-message)
8. [Thiết kế message cơ bản cho một protocol](#8-thiết-kế-message-cơ-bản-cho-một-protocol)
9. [Heartbeat / Keepalive](#9-heartbeat--keepalive)
10. [Reconnect: kết nối lại bền vững](#10-reconnect-kết-nối-lại-bền-vững)
11. [Retry, ACK/RESULT, Idempotency](#11-retry-ackresult-idempotency)
12. [Timeout, giới hạn kích thước và lưu ý MTU](#12-timeout-giới-hạn-kích-thước-và-lưu-ý-mtu)
13. [Checklist debug + Bài tập tự luyện](#13-checklist-debug--bài-tập-tự-luyện)

---

## 1. Tổng quan về mạng

### 1.1 Khái niệm

**Mạng máy tính** là hệ thống các thiết bị được kết nối với nhau (máy tính, máy chủ, điện thoại, máy in, IoT…) để **giao tiếp và trao đổi dữ liệu**. Các thiết bị có thể giao tiếp qua kết nối **có dây** hoặc **không dây**, và mạng có thể mở rộng từ mạng nhỏ trong gia đình đến Internet toàn cầu.

Điểm quan trọng nhất khi học mạng để làm protocol là: *mạng là môi trường không hoàn hảo*. Dữ liệu có thể đến chậm, bị mất (đặc biệt với UDP), hoặc kết nối có thể rớt bất kỳ lúc nào. Vì thế khi thiết kế giao thức, bạn phải nghĩ đến **lỗi và phục hồi**, chứ không chỉ “gửi/nhận cho xong”.

### 1.2 Tại sao chúng ta cần mạng máy tính?

* **Chia sẻ tài nguyên**: chia sẻ máy in, thiết bị lưu trữ…
* **Chia sẻ dữ liệu**: chia sẻ file, ứng dụng, cơ sở dữ liệu.
* **Giao tiếp**: email, hội nghị video, nhắn tin, truy cập web.
* **Quản lý dữ liệu**: lưu trữ tập trung, bảo mật, sao lưu.
* **Truy cập từ xa**: dùng dịch vụ cloud từ bất cứ đâu.
* **Hợp tác**: làm việc nhóm và trao đổi thông tin nhanh.

---

## 2. Các nguyên lý cơ bản của mạng máy tính

Bạn có thể học mạng theo “xương sống” sau: **Node ↔ Link ↔ Protocol ↔ Addressing**. Hiểu 4 khái niệm này thì đọc bất kỳ protocol nào cũng đỡ bị ngợp.

### 2.1 Kiến thức cơ bản về mạng máy tính

#### 2.1.1 Khái niệm

Mạng máy tính là một nhóm thiết bị được kết nối và giao tiếp để **chia sẻ dữ liệu** và **tài nguyên**. Nó hỗ trợ các dịch vụ như email, chia sẻ tập tin và truy cập Internet.

* Kết nối nhiều thiết bị (máy tính, máy chủ, máy in…).
* Cho phép chia sẻ dữ liệu/tài nguyên.
* Hỗ trợ dịch vụ liên lạc (email, nhắn tin).
* Nền tảng cho các ứng dụng chạy trên mạng.

#### 2.1.2 Thuật ngữ cơ bản

* **Node (Nút)**: bất kỳ thiết bị nào có thể gửi/nhận/chuyển tiếp dữ liệu.
* **Link (Liên kết)**: đường kết nối giữa các node (cáp, Wi‑Fi…).
* **Protocol (Giao thức)**: tập quy tắc quy định:

  * dữ liệu **được đóng gói** như thế nào,
  * gửi/nhận theo **trình tự** nào,
  * lỗi thì **xử lý** ra sao.
* **IP**: địa chỉ logic để định danh thiết bị và định tuyến.
* **Port**: số để định danh ứng dụng/tiến trình (lớp vận chuyển).
* **Firewall**: kiểm soát cho phép/chặn lưu lượng.

> [!NOTE]
> Khi bạn học protocol, câu hỏi luôn quay về: “**bên nhận làm sao biết đây là message gì, dài bao nhiêu, thuộc request nào, lỗi thì retry ra sao?**”

#### 2.1.3 Nguyên lý hoạt động (tư duy đóng gói)

Nói đơn giản: ứng dụng tạo dữ liệu → hệ thống mạng **đóng gói** thêm thông tin cần thiết → truyền qua mạng → bên kia **mở gói** ngược lại.

* Ứng dụng tạo **Data** (message logic).
* TCP/UDP thêm **port** và thông tin vận chuyển.
* IP thêm **địa chỉ IP** để định tuyến.
* Lớp liên kết đóng gói thành **frame** để đi trong LAN.

Đây là lý do bạn thấy nhiều thuật ngữ “đơn vị dữ liệu” khác nhau:

| Tầng       | Tên thường gặp của “đơn vị dữ liệu” |
| ---------- | ----------------------------------- |
| Vật lý     | Bit                                 |
| Liên kết   | Frame                               |
| Mạng       | Packet                              |
| Vận chuyển | Segment (TCP) / Datagram (UDP)      |
| Ứng dụng   | Message / Data                      |

---

## 3. Kiến trúc mạng máy tính

Kiến trúc nói về “ai nói chuyện với ai” và “vai trò mỗi bên”. Khi học protocol, bạn sẽ gặp các dạng kiến trúc này liên tục.

### 3.1 Kiến trúc Client–Server

* **Client**: khởi tạo giao tiếp (gửi request).
* **Server**: lắng nghe (listen), xử lý request, trả response; thường phục vụ nhiều client.

Điểm quan trọng: với mô hình client‑server, rất nhiều protocol được xây theo **request/response** hoặc **publish/subscribe**.

### 3.2 Kiến trúc ngang hàng (Peer‑to‑Peer)

Trong P2P không có máy chủ trung tâm cố định. Mỗi thiết bị có thể vừa đóng vai trò client vừa là server.

Điểm quan trọng: P2P thường phức tạp hơn ở chỗ **khó NAT traversal**, khó đồng bộ trạng thái, và thường phải có cơ chế phát hiện peer.

---

## 4. Mô hình mạng: OSI & TCP/IP

Phần này giữ đúng “nền” của bạn, nhưng gọn hơn và mạch lạc để dùng khi debug.

### 4.1 Mô hình OSI

Mô hình OSI (Open Systems Interconnection) do ISO phát triển, gồm **7 lớp**, mỗi lớp có trách nhiệm riêng. OSI rất hữu ích khi bạn cần xác định sự cố đang nằm ở tầng nào.

#### 4.1.1 7 lớp OSI (tóm tắt đủ dùng)

| Lớp | Tên lớp          | Bạn cần nhớ gì?         | Ví dụ                   |
| --: | ---------------- | ----------------------- | ----------------------- |
|   7 | Ứng dụng         | logic protocol/app      | HTTP, DNS, SMTP         |
|   6 | Trình bày        | định dạng/mã hoá/nén    | TLS, UTF‑8, JSON        |
|   5 | Phiên            | quản lý phiên giao tiếp | (thường “ẩn” trong app) |
|   4 | Vận chuyển       | TCP/UDP, port           | TCP, UDP                |
|   3 | Mạng             | IP, định tuyến          | IP                      |
|   2 | Liên kết dữ liệu | frame, MAC trong LAN    | Ethernet                |
|   1 | Vật lý           | bit/tín hiệu            | cáp/sóng                |

#### 4.1.2 Dữ liệu lưu chuyển trong OSI

* Phía gửi: lớp 7 → 1 (đóng gói dần).
* Phía nhận: lớp 1 → 7 (mở gói dần).

Cách tư duy này giúp bạn debug theo tầng:

* không ping được → nghi lớp 1–3,
* ping được nhưng TCP connect fail → nghi lớp 4,
* connect được nhưng protocol lỗi → nghi lớp 7.

### 4.2 Mô hình TCP/IP

TCP/IP là mô hình thực tế của Internet, thường gộp lớp theo 4 tầng.

| Lớp TCP/IP  | Vai trò            | Ví dụ           |
| ----------- | ------------------ | --------------- |
| Application | giao thức ứng dụng | HTTP, DNS, MQTT |
| Transport   | TCP/UDP, port      | TCP, UDP        |
| Internet    | IP, định tuyến     | IP, ICMP        |
| Link        | truyền trong LAN   | Ethernet, Wi‑Fi |

> [!NOTE]
> Từ giờ khi bạn đọc protocol, hãy tự hỏi: “đây là vấn đề ở **Transport** (TCP/UDP) hay **Application** (message/framing/state)?” — đa số lỗi protocol nằm ở **Application**.

---

## 5. Socket & Port (góc nhìn lập trình)

Từ đây trở đi là phần “cực cần” để bạn code protocol.

### 5.1 Socket là gì?

**Socket** là một đối tượng do hệ điều hành quản lý, đại diện cho “đầu mút” giao tiếp mạng.

* Với lập trình viên: socket là thứ bạn gọi `send()`/`recv()`.
* Với OS: socket có buffer, trạng thái TCP, timeout, và cơ chế xử lý gói.

### 5.2 Port là gì?

* **IP** định danh *máy*.
* **Port** định danh *ứng dụng/tiến trình* trên máy.

Ví dụ: `203.0.113.10:443` là máy 203.0.113.10 và dịch vụ HTTPS ở cổng 443.

### 5.3 TCP server làm gì? (bind → listen → accept)

Một server TCP cơ bản luôn có 3 bước:

1. **bind(ip, port)**: “giữ” cổng để nhận kết nối.
2. **listen(backlog)**: bắt đầu chờ client.
3. **accept()**: nhận từng client; *mỗi client có một socket riêng*.

> Khi bạn thiết kế protocol, hãy nhớ: 1 server có thể có rất nhiều client; vì vậy server thường cần loop + concurrency (thread/async) để không bị “kẹt”.

### 5.4 Client làm gì? (connect)

Client thường:

* `connect(server_ip, server_port)`

OS sẽ tự chọn một **ephemeral port** cho client. Vì vậy hàng nghìn client vẫn kết nối vào cùng `server:port` được.

### 5.5 5‑tuple: định danh kết nối

Một kết nối TCP thường được định danh bởi:

* `(src_ip, src_port, dst_ip, dst_port, protocol)`

Vì thế reconnect thường tạo **kết nối mới** (src_port đổi).

---

## 6. TCP/UDP theo góc nhìn lập trình socket

### 6.1 TCP stream vs UDP datagram

* **TCP (stream)**: dữ liệu là **dòng byte liên tục**.
* **UDP (datagram)**: dữ liệu là **gói rời**, ranh giới gói được giữ.

### 6.2 So sánh nhanh

| Tiêu chí          | TCP                            | UDP                         |
| ----------------- | ------------------------------ | --------------------------- |
| Ranh giới message | ❌ Không có                     | ✅ Có (theo gói)             |
| Độ tin cậy        | ✅ Có (truyền lại, đúng thứ tự) | ❌ Không đảm bảo             |
| Khi dùng          | web, file, API, chat cần đúng  | realtime: voice/video, game |

### 6.3 TCP: những hiểu lầm “cực hay dính”

#### 6.3.1 `recv()` không tương ứng 1 message

Vì TCP là stream nên 1 lần `recv()`:

* có thể trả **một phần** message,
* hoặc **gộp nhiều** message.

Ví dụ: bạn gửi 2 message `HELLO` và `WORLD`, bên nhận có thể nhận `HELLOWO` rồi sau đó `RLD`.

> Kết luận: trên TCP, **bạn phải tự định nghĩa framing** để tách message (mục 7).

#### 6.3.2 `send()` có thể gửi chưa đủ

Một số API cho phép `send()` gửi ít hơn số byte bạn đưa vào. Thực hành an toàn:

* dùng `sendall()` (Python) hoặc loop đến khi gửi đủ.

#### 6.3.3 TCP vẫn cần timeout/heartbeat

TCP “tin cậy” về truyền dữ liệu, nhưng không đảm bảo bạn phát hiện rớt mạng ngay. Mạng có thể chết ngầm (Wi‑Fi rớt, NAT timeout). Vì vậy protocol nghiêm túc vẫn cần **heartbeat + timeout**.

### 6.4 UDP: “nhanh” nhưng rủi ro

UDP có thể:

* **mất gói**,
* **đảo thứ tự**,
* **trùng gói**.

Nếu bài toán cần đúng 100% dữ liệu, hoặc có tiền/đơn hàng, thường chọn TCP hoặc tự thêm `seq/ack/retry`.

### 6.5 Code tối thiểu (Python) để bạn hình dung

#### 6.5.1 TCP client/server cực ngắn

```python
# server.py
import socket

s = socket.socket()
s.bind(("0.0.0.0", 9000))
s.listen(5)
conn, addr = s.accept()
print("client:", addr)
conn.sendall(b"hello")
conn.close()
```

```python
# client.py
import socket

c = socket.socket()
c.connect(("127.0.0.1", 9000))
print(c.recv(1024))
c.close()
```

> Đây chỉ là demo. Khi làm protocol thật, bạn sẽ thêm **framing**, loop đọc/ghi, và xử lý lỗi.

---

## 7. Framing: biến TCP stream thành message

### 7.1 Framing là gì?

**Framing** là cách bạn quy định để bên nhận biết:

* message bắt đầu ở đâu,
* message kết thúc ở đâu,
* và message dài bao nhiêu.

Nếu bạn không có framing, bạn sẽ không thể parse ổn định (vì TCP cắt/gộp dữ liệu).

### 7.2 Các kiểu framing phổ biến

#### 7.2.1 Delimiter‑based

Message kết thúc bằng ký tự như `
`.

* Ưu: dễ debug bằng telnet/netcat.
* Nhược: payload chứa delimiter thì phải escape hoặc cấm.

#### 7.2.2 Length‑prefix (khuyên dùng)

Cấu trúc:

* `[len: 4 bytes big‑endian][payload: len bytes]`

* Ưu: rõ ràng, payload chứa gì cũng được.

* Nhược: phải đọc đủ N byte và giới hạn size.

#### 7.2.3 Fixed header + body (mở rộng tốt)

Ví dụ: header cố định 12 bytes gồm `version/type/flags/len/request_id`, sau đó là body theo `len`.

* Ưu: dễ mở rộng version/protocol.
* Nhược: code parse dài hơn.

### 7.3 Quy tắc an toàn khi parse frame

* **Giới hạn kích thước**: `MAX_FRAME` (vd 1MB).
* Validate `len` trước khi đọc body.
* Khi socket đóng (`recv == b""`) → coi như connection closed.
* Đừng tin dữ liệu từ client: luôn check.

### 7.4 Hai cách implement nhận frame

#### Cách A: `recv_exact` (dễ hiểu)

```python
import struct

MAX_FRAME = 1024 * 1024

def recv_exact(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf += chunk
    return buf

def recv_frame(sock) -> bytes:
    header = recv_exact(sock, 4)
    (length,) = struct.unpack("!I", header)
    if length > MAX_FRAME:
        raise ValueError("frame too large")
    return recv_exact(sock, length)
```

#### Cách B: buffer + parse nhiều frame (thực tế hơn)

Cách này phù hợp khi:

* dữ liệu về theo “cục” lớn,
* bạn muốn parse được *nhiều frame* từ 1 lần recv.

```python
import struct

MAX_FRAME = 1024 * 1024

class FrameParser:
    def __init__(self):
        self.buf = bytearray()

    def feed(self, data: bytes):
        self.buf.extend(data)

    def pop_frames(self):
        frames = []
        while True:
            if len(self.buf) < 4:
                break
            length = struct.unpack("!I", self.buf[:4])[0]
            if length > MAX_FRAME:
                raise ValueError("frame too large")
            if len(self.buf) < 4 + length:
                break
            payload = bytes(self.buf[4:4+length])
            del self.buf[:4+length]
            frames.append(payload)
        return frames
```

> [!NOTE]
> Với TCP, cách B thường “đẹp” hơn vì bạn xử lý được trường hợp *gộp nhiều message* trong một lần recv.

---

## 8. Thiết kế message cơ bản cho một protocol

Framing cho bạn “vỏ hộp”. Còn **message format** cho bạn “nội dung trong hộp”. Thiết kế message tốt sẽ giúp:

* debug dễ (log nhìn là hiểu),
* ghép đúng request/response,
* tránh xử lý trùng khi retry,
* dễ nâng cấp version.

### 8.1 Trường cơ bản nên có

Một message tối thiểu thường có:

* `type`: loại message (PING, PONG, CMD, RESULT, ERROR…)
* `request_id` (hoặc `msg_id`): để ghép request ↔ response
* `payload`: dữ liệu chính

Nếu bạn muốn “chắc hơn” thì thêm:

* `version`: phiên bản protocol
* `timestamp` (tuỳ): đo latency/log
* `command_id` (nếu có retry): chống trùng

### 8.2 JSON hay Binary?

* **JSON**: dễ nhìn, dễ debug (rất phù hợp khi học).
* **Binary**: gọn/nhanh hơn nhưng khó debug.

Khi mới học protocol, bạn có thể làm:

* framing length‑prefix + payload là JSON bytes.

Ví dụ payload JSON:

```json
{"type":"CMD","request_id":12,"command_id":"uuid-...","payload":{"action":"sum","a":1,"b":2}}
```

---

## 9. Heartbeat / Keepalive

### 9.1 Vì sao cần heartbeat?

Dù TCP “ổn”, bạn vẫn có thể gặp:

* Wi‑Fi rớt nhưng socket chưa báo ngay,
* NAT/firewall timeout nếu lâu không có traffic,
* server restart.

Heartbeat giúp bạn **phát hiện mất kết nối sớm** và chủ động reconnect.

### 9.2 Thiết kế heartbeat mẫu

* Client gửi `PING` mỗi `interval` (vd 5–10s).
* Server trả `PONG` ngay.
* Nếu quá `timeout` (vd 3×interval) không thấy PONG → coi như dead.

### 9.3 Lưu ý thực tế

* Nếu connection có data thường xuyên, data đó có thể coi như “alive signal” và giảm heartbeat.
* Heartbeat nên chạy độc lập để không bị kẹt bởi xử lý nghiệp vụ.

---

## 10. Reconnect: kết nối lại bền vững

### 10.1 Tại sao reconnect phải có chiến lược?

Nếu rất nhiều client reconnect cùng lúc, server có thể bị “bão kết nối”. Ngoài ra reconnect quá nhanh còn làm mạng thêm nghẽn.

### 10.2 Exponential backoff + jitter

Một chiến lược thực dụng:

* delay = min(2^k, 30s)
* delay += random(0..300ms)  *(jitter)*

Ví dụ (pseudo):

```text
k=0: 1s + jitter
k=1: 2s + jitter
k=2: 4s + jitter
...
cap: 30s
```

### 10.3 Khi reconnect, thường phải làm lại gì?

* **Handshake / Auth** lại (nếu protocol yêu cầu).
* **Resubscribe** (nếu kiểu pub/sub).
* **Resend các request chưa chắc nhận** (kết hợp idempotency để an toàn).

> [!NOTE]
> Reconnect không chỉ là “connect lại”, mà là “**khôi phục trạng thái**” để protocol tiếp tục chạy đúng.

---

## 11. Retry, ACK/RESULT, Idempotency

### 11.1 Vì sao retry gây nguy hiểm?

Kịch bản kinh điển:

* Client gửi lệnh.
* Server xử lý xong.
* ACK/response bị mất.
* Client timeout rồi retry.

Nếu server xử lý lại → **trùng nghiệp vụ** (nguy hiểm nếu liên quan tiền/đơn hàng).

### 11.2 ACK khác RESULT thế nào?

* **ACK**: “tôi đã nhận request”.
* **RESULT/RESPONSE**: “tôi đã xử lý xong và đây là kết quả”.

Tuỳ bài toán bạn có thể:

* gộp ACK + RESULT (đơn giản), hoặc
* tách (khi xử lý lâu, muốn báo “đã nhận” trước).

### 11.3 Idempotency bằng `command_id`

Giải pháp phổ biến nhất:

* Mỗi command có `command_id` duy nhất (UUID) do client tạo.
* Server lưu `command_id` đã xử lý (TTL hoặc DB).
* Nếu nhận lại cùng `command_id` → trả kết quả cũ, **không xử lý lại**.

> [!TIP]
> Nếu bạn làm bài tập protocol nghiêm túc, `command_id` gần như là “điều kiện bắt buộc” để retry an toàn.

### 11.4 `request_id` để ghép request/response

* `request_id` giúp client biết response thuộc request nào, nhất là khi nhiều request “bay” cùng lúc trên 1 connection.

---

## 12. Timeout, giới hạn kích thước và lưu ý MTU

### 12.1 Các loại timeout nên có (tối thiểu)

* **Connect timeout**: connect quá lâu thì fail.
* **Read timeout / frame timeout**: đọc header/body quá lâu thì fail.
* **Heartbeat timeout**: mất PONG quá lâu thì dead.
* **Request timeout**: request quá lâu không có response thì retry/abort.

Gợi ý đặt timeout:

* timeout ≈ **3–5×** độ trễ dự kiến, hoặc
* heartbeat_timeout ≈ **3× interval**.

### 12.2 Giới hạn kích thước (an toàn)

* đặt `MAX_FRAME`.
* validate length trước khi cấp phát.
* reject frame quá lớn ngay.

### 12.3 MTU (biết vừa đủ)

* Ethernet MTU thường ~1500 bytes.
* UDP gói quá lớn dễ bị fragmentation; mất 1 mảnh là mất cả gói.

**Kết luận thực hành**:

* TCP: có thể gửi lớn nhưng vẫn nên giới hạn theo ứng dụng.
* UDP: giữ payload nhỏ, tránh vượt MTU.

---

## 13. Checklist debug + Bài tập tự luyện

### 13.1 Checklist debug nhanh

1. Bạn đang dùng TCP hay UDP?
2. Nếu TCP: đã có framing chưa?
3. `recv()` có xử lý “thiếu/gộp” chưa? (`recv_exact` hoặc buffer parser)
4. `send()` có đảm bảo gửi đủ chưa? (`sendall`)
5. Có `MAX_FRAME` chưa?
6. Có heartbeat + timeout chưa?
7. Reconnect có backoff + jitter chưa?
8. Retry có `command_id` để chống trùng chưa?
9. Log có đủ `type/id/len/timestamp/state` để debug chưa?

### 13.2 (Tuỳ chọn) Bài tập tự luyện

1. Viết TCP client/server gửi nhận chuỗi theo delimiter `
   `.
2. Đổi sang length‑prefix 4 bytes và viết `recv_exact()`.
3. Viết parser kiểu buffer để parse được **nhiều frame** trong 1 lần recv.
4. Thêm `MAX_FRAME` (test gửi > MAX_FRAME phải bị reject).
5. Thiết kế message JSON có `type`, `request_id`, `payload`.
6. Thêm `PING/PONG` và heartbeat timeout.
7. Thêm reconnect: exponential backoff + jitter (cap 30s).
8. Mô phỏng “ACK mất”: client retry nhưng server không xử lý trùng nhờ `command_id`.
9. Thêm `ERROR` message (server trả lỗi có code + message) và client xử lý đúng.

---

> Nếu bạn muốn mình viết **thậm chí chi tiết hơn nữa**, mình có thể mở rộng theo hướng “như sách” bằng cách thêm:
>
> * một **mini‑protocol hoàn chỉnh** (HELLO/AUTH → CMD/RESULT → PING/PONG),
> * sơ đồ state machine (INIT/CONNECTING/RUNNING/RECONNECTING),
> * và một mục “lỗi thường gặp & cách fix” theo từng phần.
