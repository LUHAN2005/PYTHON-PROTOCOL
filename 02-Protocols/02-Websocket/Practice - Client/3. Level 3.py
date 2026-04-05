# Import thư viện xử lý bất đồng bộ
import asyncio

# Import thư viện WebSocket
import websockets


# Hàm này chuyên dùng để gửi message từ client lên server
async def send_messages(websocket):
    while True:
        # input() là hàm block, nếu gọi trực tiếp sẽ chặn event loop
        # nên ta đưa input() sang thread khác bằng asyncio.to_thread(...)
        message = await asyncio.to_thread(input, "Ban nhap: ")

        # Gửi message mà người dùng vừa nhập lên server
        await websocket.send(message)


# Hàm này chuyên dùng để nhận message từ server gửi về client
async def receive_messages(websocket):
    try:
        while True:
            # Chờ server gửi dữ liệu về
            message = await websocket.recv()

            # In dữ liệu nhận được ra màn hình
            print("Server tra ve:", message)

    # Nếu server đóng kết nối hoặc mất kết nối
    except websockets.ConnectionClosed:
        print("Server da dong ket noi")


# Hàm chính để client kết nối tới server và chạy đồng thời 2 việc:
# 1. gửi message
# 2. nhận message
async def main():
    # Địa chỉ WebSocket server mà client muốn kết nối tới
    url = "ws://127.0.0.1:8765"

    # Tạo đối tượng kết nối WebSocket
    connection = websockets.connect(url)

    # Mở kết nối và gán kết nối đang hoạt động vào biến websocket
    async with connection as websocket:
        # Tạo 1 task riêng cho việc gửi message
        send_task = asyncio.create_task(send_messages(websocket))

        # Tạo 1 task riêng cho việc nhận message
        receive_task = asyncio.create_task(receive_messages(websocket))

        # Chạy đồng thời cả 2 task và giữ chương trình sống
        await asyncio.gather(send_task, receive_task)


# Nếu chạy trực tiếp file này thì gọi hàm main()
if __name__ == "__main__":
    # Chạy hàm bất đồng bộ main()
    asyncio.run(main())