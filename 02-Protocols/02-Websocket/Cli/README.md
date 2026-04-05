# WebSocket Python — README form chuẩn (server + client 1 file)

> **Mục tiêu:** Đây là README kiểu “master form chuẩn” cho 2 file WebSocket server/client bạn đang dùng. Tài liệu này gom lại **toàn bộ lệnh / hàm / method / cấu trúc quan trọng** xuất hiện trong 2 form chuẩn, giải thích theo kiểu:
>
> * cú pháp
> * cách dùng
> * tham số truyền vào
> * ví dụ
> * có phân luồng / bất đồng bộ không
> * dùng trong trường hợp nào
>
> README này tập trung vào các thư viện và phần bạn thật sự dùng trong form chuẩn:
>
> * `websockets`
> * `asyncio`
> * `json`
> * `time`
> * `uuid`
> * `typing`
> * Python built-ins liên quan như `print`, `input`, `max`, `min`, `float`, `isinstance`
>
> Ngoài ra có thêm:
>
> * form message chuẩn
> * flow chuẩn client/server
> * bảng chọn nhanh “khi nào dùng cái gì”
> * lệnh chạy project
>
> **Triết lý nhớ nhanh:**
>
> * `websockets` = lớp giao tiếp WebSocket
> * `asyncio` = lớp điều phối bất đồng bộ / song song
> * `json` = lớp protocol message
> * `time` = timeout / heartbeat / timestamp đơn giản
> * `uuid` = tạo id ngắn cho message / client

---

# Mục lục

1. [Cài đặt và chạy](#1-cài-đặt-và-chạy)
2. [Form message chuẩn](#2-form-message-chuẩn)
3. [Luồng hoạt động chuẩn](#3-luồng-hoạt-động-chuẩn)
4. [Thư viện `websockets`](#4-thư-viện-websockets)
5. [Thư viện `asyncio`](#5-thư-viện-asyncio)
6. [Thư viện `json`](#6-thư-viện-json)
7. [Thư viện `time`](#7-thư-viện-time)
8. [Thư viện `uuid`](#8-thư-viện-uuid)
9. [Thư viện `typing`](#9-thư-viện-typing)
10. [Built-ins hay dùng](#10-built-ins-hay-dùng)
11. [Các hàm chuẩn trong server form](#11-các-hàm-chuẩn-trong-server-form)
12. [Các hàm chuẩn trong client form](#12-các-hàm-chuẩn-trong-client-form)
13. [Topic / type / role / subscriptions](#13-topic--type--role--subscriptions)
14. [Heartbeat / timeout / reconnect](#14-heartbeat--timeout--reconnect)
15. [Khi nào dùng hàm nào](#15-khi-nào-dùng-hàm-nào)
16. [Checklist nhớ bài](#16-checklist-nhớ-bài)

---

# 1. Cài đặt và chạy

## 1.1 Cài thư viện

```bash
pip install websockets
```

### Dùng khi nào

Khi máy chưa có thư viện `websockets`.

### Giải thích

Form chuẩn server/client của bạn dùng thư viện `websockets` để:

* tạo WebSocket server
* kết nối WebSocket client
* gửi / nhận text frame
* đóng kết nối

---

## 1.2 Chạy server

```bash
python server.py
```

### Dùng khi nào

Khi muốn mở server lắng nghe client kết nối vào.

---

## 1.3 Chạy client

```bash
python client.py
```

### Dùng khi nào

Khi muốn kết nối tới server, register, gửi heartbeat, nhận telemetry, gửi control.

---

## 1.4 Chạy nhiều client cùng lúc

Mở nhiều terminal:

```bash
python client.py
```

### Dùng khi nào

Khi test multi-client:

* nhiều viewer
* nhiều controller
* broadcast telemetry
* timeout từng client

---

# 2. Form message chuẩn

Form message chuẩn mà server/client của bạn đang dùng:

```json
{
  "topic": "car/control",
  "type": "command",
  "client_id": "controller_01",
  "message_id": "msg001",
  "payload": {
    "throttle": 40,
    "steering": -10
  }
}
```

## 2.1 Ý nghĩa từng field

### `topic`

Luồng message thuộc nhánh nào.

Ví dụ:

* `system/register`
* `system/heartbeat`
* `system/error`
* `car/control`
* `car/telemetry`
* `car/emergency`

### `type`

Hành động cụ thể trong topic đó.

Ví dụ:

* `command`
* `ack`
* `update`
* `error`
* `event`

### `client_id`

Ai gửi message.

### `message_id`

ID của message để đối chiếu request/response.

### `payload`

Dữ liệu thật của message.

---

## 2.2 Vì sao phải có `topic` và `type`

### `topic`

Dùng để **route** message đúng handler.

### `type`

Dùng để **phân biệt trạng thái hành động**:

* client gửi `command`
* server trả `ack`
* server broadcast `update`
* server báo lỗi `error`
* server phát sự kiện `event`

### Có phân luồng không

Có.

Nhưng đây là **phân luồng logic theo topic**, không phải luồng CPU/thread.

---

# 3. Luồng hoạt động chuẩn

## 3.1 Luồng server

1. server mở cổng với `websockets.serve(...)`
2. client kết nối vào
3. server gọi `handle_client(websocket)`
4. server thêm client vào `clients`
5. client gửi `system/register`
6. server validate rồi trả `ack`
7. client gửi heartbeat định kỳ
8. server cập nhật `last_heartbeat`
9. client gửi `car/control`
10. server xử lý và trả `ack`
11. server broadcast `car/telemetry` cho client subscribe đúng topic
12. client disconnect thì server cleanup

## 3.2 Luồng client

1. client dùng `websockets.connect(...)`
2. kết nối thành công
3. gửi register ngay sau connect
4. chạy song song:

   * `heartbeat_loop`
   * `receive_loop`
   * `send_loop`
5. nếu mất kết nối thì reconnect loop thử kết nối lại

## 3.3 Có phân luồng không

Có **bất đồng bộ / concurrency** bằng `asyncio`, không phải đa luồng hệ điều hành.

Cụ thể:

* `heartbeat_loop()` chạy song song với `receive_loop()`
* `send_loop()` chạy song song với 2 loop trên
* server có `telemetry_loop()` và `safety_loop()` chạy nền
* mỗi client kết nối vào server sẽ có coroutine riêng

---

# 4. Thư viện `websockets`

## 4.1 `websockets.serve()`

### Cú pháp

```python
websockets.serve(handler, host, port)
```

### Cách dùng

Tạo WebSocket server để lắng nghe client kết nối vào.

### Tham số

* `handler`: hàm async xử lý mỗi client
* `host`: địa chỉ host, ví dụ `"localhost"`
* `port`: cổng, ví dụ `8765`

### Ví dụ

```python
async with websockets.serve(handle_client, HOST, PORT):
    print(f"RUN WS SERVER on ws://{HOST}:{PORT}")
    while True:
        await asyncio.sleep(0.5)
```

### Giải thích chi tiết

Mỗi khi có client kết nối, thư viện sẽ tạo một `websocket connection object` và gọi handler của bạn.

### Có phân luồng không

Có bất đồng bộ. Mỗi kết nối được xử lý bằng coroutine riêng.

### Dùng trong trường hợp nào

Khi bạn viết **server**.

---

## 4.2 `websockets.connect()`

### Cú pháp

```python
websockets.connect(uri)
```

### Cách dùng

Kết nối từ client tới WebSocket server.

### Tham số

* `uri`: chuỗi địa chỉ WebSocket, ví dụ `"ws://localhost:8765"`

### Ví dụ

```python
async with websockets.connect(WS_URL) as websocket:
    print("connected")
```

### Giải thích chi tiết

Sau khi connect thành công, bạn nhận được `websocket` object để:

* `send(...)`
* `recv(...)` hoặc `async for raw in websocket`
* `close()`

### Có phân luồng không

Không tự phân luồng, nhưng thường được dùng bên trong coroutine async và phối hợp với `asyncio`.

### Dùng trong trường hợp nào

Khi bạn viết **client**.

---

## 4.3 `websocket.send()`

### Cú pháp

```python
await websocket.send(data)
```

### Cách dùng

Gửi message từ client lên server hoặc từ server xuống client.

### Tham số

* `data`: chuỗi text hoặc bytes

### Ví dụ

```python
await websocket.send(build_register())
```

### Giải thích chi tiết

Trong form chuẩn của bạn, dữ liệu gửi đi là **JSON string** đã tạo bởi `make_message(...)`.

### Có phân luồng không

Là thao tác async, cần `await`.

### Dùng trong trường hợp nào

Mỗi khi cần gửi:

* register
* heartbeat
* control
* emergency
* telemetry update
* error

---

## 4.4 `websocket.close()`

### Cú pháp

```python
await websocket.close()
```

### Cách dùng

Đóng kết nối WebSocket.

### Ví dụ

```python
await websocket.close()
```

### Giải thích chi tiết

Server dùng khi client timeout. Client dùng khi user chọn thoát.

### Có phân luồng không

Là thao tác async.

### Dùng trong trường hợp nào

* timeout heartbeat
* user muốn stop client
* cleanup khi không dùng connection nữa

---

## 4.5 `websockets.ConnectionClosed`

### Cú pháp

```python
except websockets.ConnectionClosed:
    ...
```

### Cách dùng

Bắt lỗi khi kết nối bị đóng.

### Ví dụ

```python
except ConnectionClosed:
    print("disconnected")
```

hoặc bản an toàn theo version:

```python
except Exception as e:
    if not isinstance(e, websockets.ConnectionClosed):
        print(repr(e))
```

### Giải thích chi tiết

Do version `websockets` khác nhau, đôi lúc cách import exception khác nhau. Bản form chuẩn tối ưu portability thường sẽ dùng `websockets.ConnectionClosed` hoặc kiểm tra `isinstance`.

### Có phân luồng không

Không. Đây là exception handling.

### Dùng trong trường hợp nào

Khi cần phân biệt:

* disconnect bình thường
* lỗi lạ khác bình thường

---

# 5. Thư viện `asyncio`

## 5.1 `async def`

### Cú pháp

```python
async def func_name(...):
    ...
```

### Cách dùng

Định nghĩa coroutine async.

### Ví dụ

```python
async def handle_client(websocket):
    ...
```

### Giải thích chi tiết

Hầu hết code WebSocket chuẩn trong Python đi cùng `asyncio`, nên các hàm gửi/nhận/loop nền đều là `async def`.

### Có phân luồng không

Đây là nền tảng để chạy bất đồng bộ.

### Dùng trong trường hợp nào

Mọi hàm có `await` bên trong.

---

## 5.2 `await`

### Cú pháp

```python
await some_async_call()
```

### Cách dùng

Chờ một thao tác async hoàn thành mà không block toàn bộ event loop.

### Ví dụ

```python
await websocket.send(msg)
await asyncio.sleep(1)
```

### Giải thích chi tiết

`await` không giống `time.sleep()`. Trong lúc chờ, event loop có thể cho coroutine khác chạy.

### Có phân luồng không

Có bất đồng bộ / cooperative scheduling.

### Dùng trong trường hợp nào

Khi gọi:

* `websocket.send()`
* `asyncio.sleep()`
* `websocket.close()`
* handler async khác

---

## 5.3 `asyncio.run()`

### Cú pháp

```python
asyncio.run(main())
```

### Cách dùng

Chạy coroutine gốc của chương trình.

### Ví dụ

```python
if __name__ == "__main__":
    asyncio.run(main())
```

### Giải thích chi tiết

Đây là entry point chuẩn cho app async đơn giản.

### Có phân luồng không

Nó khởi động event loop, không tạo thread mới.

### Dùng trong trường hợp nào

Ở cuối file server hoặc client.

---

## 5.4 `asyncio.create_task()`

### Cú pháp

```python
task = asyncio.create_task(coro())
```

### Cách dùng

Tạo task chạy song song trong event loop.

### Ví dụ

```python
heartbeat_task = asyncio.create_task(heartbeat_loop(websocket))
receive_task = asyncio.create_task(receive_loop(websocket))
send_task = asyncio.create_task(send_loop(websocket))
```

### Giải thích chi tiết

Đây là chìa khóa của full-duplex:

* vừa gửi
* vừa nhận
* vừa heartbeat

Server cũng dùng để chạy loop nền:

* `telemetry_loop()`
* `safety_loop()`

### Có phân luồng không

Có concurrency kiểu async task, không phải OS thread.

### Dùng trong trường hợp nào

Khi muốn nhiều coroutine cùng chạy song song.

---

## 5.5 `asyncio.sleep()`

### Cú pháp

```python
await asyncio.sleep(seconds)
```

### Cách dùng

Tạm nghỉ không-block trong app async.

### Ví dụ

```python
await asyncio.sleep(TELEMETRY_INTERVAL)
```

### Giải thích chi tiết

Dùng cho:

* nhịp gửi heartbeat
* nhịp phát telemetry
* main loop giữ server sống
* delay reconnect

### Có phân luồng không

Có. Nó nhường CPU logic cho task khác.

### Dùng trong trường hợp nào

Khi muốn chờ mà không đóng băng app async.

> **Không dùng `time.sleep()` trong coroutine async.**

---

## 5.6 `asyncio.wait()`

### Cú pháp

```python
done, pending = await asyncio.wait(tasks, return_when=...)
```

### Cách dùng

Chờ nhiều task và quyết định khi nào thoát.

### Tham số hay dùng

* danh sách task
* `return_when=asyncio.FIRST_COMPLETED`

### Ví dụ

```python
done, pending = await asyncio.wait(
    [heartbeat_task, receive_task, send_task],
    return_when=asyncio.FIRST_COMPLETED,
)
```

### Giải thích chi tiết

Khi một task kết thúc trước:

* receive loop chết vì disconnect
* send loop kết thúc vì user chọn thoát

thì bạn có thể huỷ các task còn lại.

### Có phân luồng không

Có async coordination.

### Dùng trong trường hợp nào

Khi quản lý nhiều task sống/chết theo nhóm.

---

## 5.7 `task.cancel()`

### Cú pháp

```python
task.cancel()
```

### Cách dùng

Hủy task đang chạy.

### Ví dụ

```python
for task in pending:
    task.cancel()
```

### Giải thích chi tiết

Rất quan trọng để tránh zombie task khi kết nối đã chết mà loop nền vẫn còn chạy.

### Có phân luồng không

Có liên quan lifecycle task async.

### Dùng trong trường hợp nào

Khi session kết thúc, disconnect, hoặc một task chính đã chết.

---

## 5.8 `asyncio.to_thread()`

### Cú pháp

```python
await asyncio.to_thread(func, *args)
```

### Cách dùng

Đẩy code block đồng bộ sang thread để tránh chặn event loop.

### Ví dụ

```python
choice = await asyncio.to_thread(input, "Choose: ")
```

### Giải thích chi tiết

`input()` là blocking. Nếu gọi thẳng trong async app thì receive loop/heartbeat loop có thể bị đứng. `asyncio.to_thread()` giải quyết việc đó.

### Có phân luồng không

Có. Đây là chỗ hiếm hoi dùng thread phụ để bọc code blocking.

### Dùng trong trường hợp nào

Khi cần gọi:

* `input()`
* file I/O blocking nhỏ
* hàm sync ngắn mà bạn chưa muốn refactor

---

# 6. Thư viện `json`

## 6.1 `json.dumps()`

### Cú pháp

```python
json.dumps(obj, ensure_ascii=False)
```

### Cách dùng

Chuyển Python dict thành JSON string.

### Ví dụ

```python
msg = json.dumps({
    "topic": "system/register",
    "type": "command",
    "payload": {}
}, ensure_ascii=False)
```

### Giải thích chi tiết

Server/client của bạn luôn gửi **string JSON** qua WebSocket.

### Có phân luồng không

Không.

### Dùng trong trường hợp nào

Trong `make_message(...)` trước khi gửi.

---

## 6.2 `json.loads()`

### Cú pháp

```python
json.loads(raw)
```

### Cách dùng

Parse JSON string về Python object.

### Ví dụ

```python
data = json.loads(raw)
```

### Giải thích chi tiết

Sau khi nhận message từ WebSocket, bạn cần parse để lấy `topic`, `type`, `payload`.

### Có phân luồng không

Không.

### Dùng trong trường hợp nào

Trong `parse_message(...)`.

---

## 6.3 `json.JSONDecodeError`

### Cú pháp

```python
except json.JSONDecodeError:
    ...
```

### Cách dùng

Bắt lỗi JSON sai format.

### Ví dụ

```python
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    return None, "Invalid JSON"
```

### Giải thích chi tiết

Đây là lớp bảo vệ đầu tiên để protocol không vỡ khi client/server gửi rác.

### Có phân luồng không

Không.

### Dùng trong trường hợp nào

Khi parse dữ liệu nhận vào.

---

# 7. Thư viện `time`

## 7.1 `time.time()`

### Cú pháp

```python
time.time()
```

### Cách dùng

Lấy timestamp hiện tại dạng số giây Unix.

### Ví dụ

```python
info["last_heartbeat"] = time.time()
```

### Giải thích chi tiết

Trong form chuẩn bạn dùng `time.time()` để:

* lưu lúc client kết nối
* lưu heartbeat cuối
* so timeout

### Có phân luồng không

Không.

### Dùng trong trường hợp nào

Khi cần so sánh thời gian nhanh và đơn giản.

---

## 7.2 Không dùng `time.sleep()` trong coroutine async

### Sai

```python
time.sleep(1)
```

### Đúng

```python
await asyncio.sleep(1)
```

### Giải thích chi tiết

`time.sleep()` sẽ block toàn bộ event loop nếu gọi trong coroutine.

### Dùng trong trường hợp nào

Chỉ dùng `time.sleep()` ở app sync, không dùng trong loop async WebSocket chuẩn.

---

# 8. Thư viện `uuid`

## 8.1 `uuid.uuid4()`

### Cú pháp

```python
uuid.uuid4()
```

### Cách dùng

Tạo UUID ngẫu nhiên.

### Ví dụ

```python
str(uuid.uuid4())[:8]
```

### Giải thích chi tiết

Trong form chuẩn bạn dùng để tạo:

* `message_id`
* `client_id` tạm cho connection mới

### Có phân luồng không

Không.

### Dùng trong trường hợp nào

Khi cần ID đủ khác biệt mà không muốn tự đếm số.

---

# 9. Thư viện `typing`

## 9.1 `Dict`

### Cú pháp

```python
from typing import Dict
```

### Cách dùng

Type hint cho dict.

### Ví dụ

```python
clients: Dict[Any, Dict[str, Any]] = {}
```

### Giải thích chi tiết

Giúp code dễ đọc hơn, không làm đổi logic runtime.

### Có phân luồng không

Không.

### Dùng trong trường hợp nào

Khi muốn code rõ cấu trúc dữ liệu.

---

## 9.2 `Any`

### Cú pháp

```python
from typing import Any
```

### Cách dùng

Type hint khi kiểu dữ liệu linh hoạt.

### Ví dụ

```python
payload: Dict[str, Any]
```

### Giải thích chi tiết

Trong protocol JSON, payload có thể chứa số, chuỗi, dict con, nên `Any` khá tiện ở giai đoạn học.

### Có phân luồng không

Không.

### Dùng trong trường hợp nào

Khi chưa muốn ép schema chặt.

---

# 10. Built-ins hay dùng

## 10.1 `print()`

### Cú pháp

```python
print(...)
```

### Dùng để

* log connect / disconnect
* log ack / telemetry
* debug flow

### Trường hợp dùng

Giai đoạn học, demo, debug nhanh.

---

## 10.2 `input()`

### Cú pháp

```python
input("prompt")
```

### Dùng để

Nhận lệnh từ bàn phím ở client.

### Lưu ý

Trong async app, nên bọc bằng `await asyncio.to_thread(input, ...)`.

---

## 10.3 `isinstance()`

### Cú pháp

```python
isinstance(value, type_or_tuple)
```

### Dùng để

Validate dữ liệu nhận vào.

### Ví dụ

```python
if not isinstance(throttle, (int, float)):
    ...
```

### Trường hợp dùng

Validate protocol field.

---

## 10.4 `max()` / `min()`

### Cú pháp

```python
max(a, b)
min(a, b)
```

### Dùng để

Clamp giá trị vào khoảng an toàn.

### Ví dụ

```python
car_state["speed"] = max(0.0, min(100.0, float(throttle)))
```

### Trường hợp dùng

Giới hạn throttle, steering, battery.

---

## 10.5 `float()`

### Cú pháp

```python
float(value)
```

### Dùng để

Chuyển input sang số thực.

### Trường hợp dùng

Khi user nhập throttle / steering từ terminal.

---

# 11. Các hàm chuẩn trong server form

## 11.1 `make_message()`

### Mục tiêu

Đóng gói message JSON chuẩn trước khi gửi.

### Cú pháp

```python
def make_message(topic, msg_type, payload=None, *, client_id=..., message_id=None) -> str:
```

### Tham số

* `topic`: topic logic
* `msg_type`: loại message
* `payload`: dữ liệu
* `client_id`: ai gửi
* `message_id`: id của message

### Ví dụ

```python
msg = make_message(
    topic="system/error",
    msg_type="error",
    payload={"message": "Invalid JSON"},
)
```

### Có phân luồng không

Không.

### Dùng khi nào

Trước mọi lần gửi message.

---

## 11.2 `parse_message()`

### Mục tiêu

Parse + validate message nhận vào.

### Output chuẩn

```python
(message_dict, None)
```

hoặc

```python
(None, "error text")
```

### Dùng khi nào

Ngay sau khi nhận raw text từ socket.

### Có phân luồng không

Không.

---

## 11.3 `send_json()`

### Mục tiêu

Bọc `make_message()` + `websocket.send()` cho gọn.

### Dùng khi nào

Khi muốn gửi message chuẩn mà không lặp code.

### Có phân luồng không

Có vì bên trong có `await websocket.send(...)`.

---

## 11.4 `send_error()`

### Mục tiêu

Tạo response lỗi thống nhất.

### Dùng khi nào

Khi:

* JSON sai
* thiếu field
* sai type
* topic không hỗ trợ
* không đủ quyền

### Có phân luồng không

Có, vì gọi `send_json()`.

---

## 11.5 `register_connection()`

### Mục tiêu

Thêm client mới vào `clients`.

### Dùng khi nào

Khi client vừa kết nối vào server.

### Dữ liệu thường lưu

* `client_id`
* `name`
* `role`
* `connected_at`
* `last_heartbeat`
* `subscriptions`

### Có phân luồng không

Không trực tiếp, nhưng chạy trong coroutine `handle_client()`.

---

## 11.6 `unregister_connection()`

### Mục tiêu

Xóa client khỏi danh sách đang sống.

### Dùng khi nào

Khi disconnect hoặc socket chết.

### Có phân luồng không

Không trực tiếp.

---

## 11.7 `broadcast_to_topic()`

### Mục tiêu

Gửi message cho mọi client subscribe đúng topic.

### Cách hoạt động

1. lặp qua `clients`
2. kiểm tra `topic in subscriptions`
3. gửi message
4. client nào chết thì gom vào `dead`
5. cleanup sau vòng lặp

### Có phân luồng không

Có thao tác async gửi qua nhiều client, nhưng theo vòng lặp tuần tự trong một coroutine.

### Dùng khi nào

Khi broadcast telemetry hoặc event hệ thống.

---

## 11.8 `handle_register()`

### Mục tiêu

Xử lý topic `system/register`.

### Công việc

* đọc `name`, `role`, `subscriptions`, `client_id`
* validate
* cập nhật metadata client
* trả `ack`

### Có phân luồng không

Không riêng, chỉ là handler async.

### Dùng khi nào

Khi client vừa connect hoặc muốn register lại.

---

## 11.9 `handle_heartbeat()`

### Mục tiêu

Cập nhật thời điểm heartbeat cuối.

### Công việc

* set `last_heartbeat = time.time()`
* trả `ack`

### Dùng khi nào

Khi client gửi `system/heartbeat`.

---

## 11.10 `handle_car_control()`

### Mục tiêu

Xử lý lệnh điều khiển xe.

### Công việc

* check role phải là `controller` hoặc `admin`
* validate `throttle`, `steering`
* cập nhật `car_state`
* trả `ack`

### Có phân luồng không

Không riêng, nhưng là một nhánh logic điều khiển thời gian thực.

### Dùng khi nào

Khi client gửi `car/control`.

---

## 11.11 `handle_car_emergency()`

### Mục tiêu

Dừng khẩn cấp.

### Công việc

* check quyền
* set speed = 0
* set status = `emergency_stop`
* trả `ack`

### Dùng khi nào

Khi client gửi `car/emergency` hoặc server ép stop vì timeout.

---

## 11.12 `handle_car_telemetry_request()`

### Mục tiêu

Trả telemetry ngay lập tức cho client yêu cầu.

### Dùng khi nào

Khi client muốn xin state hiện tại ngay, không chờ broadcast định kỳ.

---

## 11.13 `telemetry_loop()`

### Mục tiêu

Gửi telemetry định kỳ cho các client subscribe.

### Công việc

* `await asyncio.sleep(TELEMETRY_INTERVAL)`
* cập nhật battery nếu xe đang chạy
* `broadcast_to_topic(...)`

### Có phân luồng không

Có. Đây là background task chạy song song với handler client.

### Dùng khi nào

Luôn chạy nền trong server.

---

## 11.14 `safety_loop()`

### Mục tiêu

Phát hiện client timeout heartbeat.

### Công việc

* duyệt toàn bộ client
* nếu quá timeout:

  * emergency stop
  * gửi event
  * đóng socket

### Có phân luồng không

Có background async task.

### Dùng khi nào

Luôn chạy nền để bảo vệ hệ thống realtime.

---

## 11.15 `handle_client()`

### Mục tiêu

Đây là entry point xử lý một client cụ thể.

### Công việc

* register connection tạm
* gửi welcome
* nhận message liên tục
* parse
* route theo `topic`
* gọi handler phù hợp
* cleanup khi thoát

### Có phân luồng không

Có. Mỗi client kết nối sẽ có một phiên `handle_client()` riêng.

### Dùng khi nào

Tự động được gọi bởi `websockets.serve()` khi có client mới.

---

## 11.16 `main()` của server

### Mục tiêu

Khởi chạy server và các background loop.

### Công việc

* `asyncio.create_task(telemetry_loop())`
* `asyncio.create_task(safety_loop())`
* mở `websockets.serve(...)`

### Có phân luồng không

Có async concurrency.

---

# 12. Các hàm chuẩn trong client form

## 12.1 `build_register()`

### Mục tiêu

Tạo message register chuẩn.

### Payload thường có

* `client_id`
* `name`
* `role`
* `subscriptions`

### Dùng khi nào

Ngay sau khi connect hoặc khi muốn register lại.

---

## 12.2 `build_heartbeat()`

### Mục tiêu

Tạo heartbeat message.

### Dùng khi nào

Gửi định kỳ theo `HEARTBEAT_INTERVAL`.

---

## 12.3 `build_control()`

### Mục tiêu

Tạo message điều khiển xe.

### Tham số

* `throttle`
* `steering`

### Dùng khi nào

Khi user chọn gửi lệnh control.

---

## 12.4 `build_emergency()`

### Mục tiêu

Tạo message emergency stop.

### Dùng khi nào

Khi cần dừng khẩn cấp.

---

## 12.5 `build_telemetry_request()`

### Mục tiêu

Xin telemetry ngay lập tức.

### Dùng khi nào

Khi user muốn xem trạng thái hiện tại ngay.

---

## 12.6 `process_message()`

### Mục tiêu

Route message nhận được theo `topic` + `type`.

### Cách hoạt động

* welcome event -> `handle_welcome`
* register ack -> `handle_register_ack`
* heartbeat ack -> `handle_heartbeat_ack`
* telemetry update -> `handle_telemetry`
* error -> `handle_error`

### Có phân luồng không

Không riêng, nhưng chạy trong receive loop.

### Dùng khi nào

Mỗi lần client nhận message mới.

---

## 12.7 `heartbeat_loop()`

### Mục tiêu

Gửi heartbeat định kỳ để server biết client còn sống.

### Có phân luồng không

Có background task async.

### Dùng khi nào

Sau khi client connect thành công.

---

## 12.8 `receive_loop()`

### Mục tiêu

Nhận message liên tục từ server.

### Cách hoạt động

* `async for raw in websocket`
* parse
* process

### Có phân luồng không

Có background task async.

### Dùng khi nào

Luôn chạy sau khi client connect.

---

## 12.9 `send_loop()`

### Mục tiêu

Cho user nhập lệnh từ terminal.

### Công việc

* hiện menu
* đọc `input()` bằng `asyncio.to_thread()`
* tạo message tương ứng
* gửi đi

### Có phân luồng không

Có, nhưng input blocking được đưa sang thread phụ.

### Dùng khi nào

Client terminal dùng để test / demo.

---

## 12.10 `run_one_session()`

### Mục tiêu

Quản lý một phiên kết nối client.

### Công việc

* connect
* gửi register
* tạo 3 task: heartbeat / receive / send
* chờ task nào chết trước
* hủy task còn lại

### Có phân luồng không

Có async concurrency.

### Dùng khi nào

Mỗi lần reconnect thành công.

---

## 12.11 `main()` của client

### Mục tiêu

Tạo reconnect loop.

### Công việc

* gọi `run_one_session()`
* nếu disconnect thì ngủ `RECONNECT_DELAY`
* thử lại
* nếu user stop thì thoát

### Có phân luồng không

Có async flow control.

### Dùng khi nào

Entry point chính của client.

---

# 13. Topic / type / role / subscriptions

## 13.1 `topic`

### Dùng để làm gì

Chia message theo kênh logic.

### Ví dụ

* `system/register`
* `system/heartbeat`
* `system/error`
* `car/control`
* `car/telemetry`
* `car/emergency`

### Khi nào quan trọng

Khi project có nhiều loại message khác nhau.

---

## 13.2 `type`

### Dùng để làm gì

Phân biệt hành vi trong cùng topic.

### Ví dụ

* client gửi `command`
* server trả `ack`
* server đẩy `update`
* server báo `error`
* server phát `event`

---

## 13.3 `role`

### Dùng để làm gì

Phân quyền client.

### Ví dụ

* `viewer`
* `controller`
* `admin`

### Khi nào dùng

Khi không muốn ai cũng được gửi lệnh control.

---

## 13.4 `subscriptions`

### Dùng để làm gì

Cho biết client muốn nhận topic nào.

### Ví dụ

```python
subscriptions = ["car/telemetry"]
```

### Khi nào dùng

Khi server broadcast có chọn lọc.

### Có phân luồng không

Đây là phân luồng message logic.

---

# 14. Heartbeat / timeout / reconnect

## 14.1 Heartbeat là gì

Client gửi định kỳ:

```json
{
  "topic": "system/heartbeat",
  "type": "command",
  "payload": {}
}
```

Server nhận và cập nhật `last_heartbeat`.

### Dùng khi nào

Khi cần biết client còn sống.

---

## 14.2 Timeout là gì

Nếu quá `HEARTBEAT_TIMEOUT` mà server không thấy heartbeat mới, server coi client đã mất.

### Server thường làm gì

* emergency stop
* gửi event
* đóng kết nối

---

## 14.3 Reconnect là gì

Client nếu bị disconnect sẽ đợi một lúc rồi connect lại.

### Dùng khi nào

Khi mạng chập chờn hoặc server restart.

---

# 15. Khi nào dùng hàm nào

## 15.1 Tôi muốn mở server

Dùng:

* `asyncio.run(main())`
* `websockets.serve(...)`

## 15.2 Tôi muốn client kết nối vào server

Dùng:

* `websockets.connect(...)`

## 15.3 Tôi muốn gửi message chuẩn JSON

Dùng:

* `make_message()`
* `json.dumps()`
* `await websocket.send(...)`

## 15.4 Tôi muốn parse message nhận được

Dùng:

* `json.loads()`
* `parse_message()`
* `isinstance()`

## 15.5 Tôi muốn chạy nhiều việc cùng lúc

Dùng:

* `asyncio.create_task()`
* `asyncio.wait()`
* `task.cancel()`

## 15.6 Tôi muốn chờ mà không block app

Dùng:

* `await asyncio.sleep(...)`

## 15.7 Tôi muốn nhận input terminal mà không đứng app

Dùng:

* `await asyncio.to_thread(input, ...)`

## 15.8 Tôi muốn timeout client

Dùng:

* `time.time()`
* `HEARTBEAT_TIMEOUT`
* `safety_loop()`

## 15.9 Tôi muốn gửi telemetry cho nhiều client cùng lúc

Dùng:

* `broadcast_to_topic()`
* `subscriptions`

---

# 16. Checklist nhớ bài

## Server phải có

* [ ] `websockets.serve(...)`
* [ ] `handle_client()`
* [ ] `clients` storage
* [ ] `make_message()` / `parse_message()`
* [ ] handler map theo `topic`
* [ ] `telemetry_loop()`
* [ ] `safety_loop()`
* [ ] cleanup khi disconnect

## Client phải có

* [ ] `websockets.connect(...)`
* [ ] gửi register ngay sau connect
* [ ] `heartbeat_loop()`
* [ ] `receive_loop()`
* [ ] `send_loop()`
* [ ] reconnect loop
* [ ] parse + route theo `topic/type`

## Protocol phải có

* [ ] `topic`
* [ ] `type`
* [ ] `client_id`
* [ ] `message_id`
* [ ] `payload`

## Tư duy đúng sau 10 level

* [ ] không nhét mọi thứ vào 1 `if/elif` khổng lồ
* [ ] biết tách message theo `topic`
* [ ] biết tách hành động theo `type`
* [ ] biết dùng `asyncio` để gửi/nhận song song
* [ ] biết heartbeat / timeout / reconnect
* [ ] biết multi-client không chỉ là “nhiều kết nối”, mà còn là metadata + subscription + role

---

# Kết luận ngắn

Nếu nhớ đúng README này, bạn sẽ nắm được bộ khung chuẩn của một app WebSocket Python dạng terminal:

* server lắng nghe và quản lý nhiều client
* client kết nối, register, heartbeat, nhận telemetry
* protocol JSON rõ ràng
* xử lý bất đồng bộ bằng `asyncio`
* tránh nhầm message bằng `topic + type`
* tránh lỗi runtime bằng validate + timeout + cleanup

Đây là nền rất tốt để đi tiếp lên:

* FastAPI WebSocket
* schema validation bằng Pydantic
* logging chuẩn
* auth/token
* room/device manager
* dashboard realtime
