# Import thư viện bất đồng bộ của Python
import asyncio

# Import thư viện WebSocket
import websockets

# Import kiểu dữ liệu connection của phía client
# Dòng này chủ yếu để viết type hint cho dễ nhìn và được IDE gợi ý tốt hơn
from websockets.asyncio.client import ClientConnection


# Khai báo một hàm bất đồng bộ
async def main():
    # Địa chỉ WebSocket server mà client muốn kết nối tới
    url = "ws://127.0.0.1:8765"

    # Tạo đối tượng kết nối tới server
    # Lúc này mới chỉ là đối tượng kết nối, chưa dùng trực tiếp ngay
    connection = websockets.connect(url)

    # Mở kết nối WebSocket và gán kết nối đang hoạt động vào biến websocket
    async with connection as websocket:
        # Client gửi một message lên server
        await websocket.send("Xin chao server")
        print("Client da gui message")

        # Client chờ server phản hồi lại
        message = await websocket.recv()

        # In dữ liệu client vừa nhận được từ server
        print("Client nhan ve:", message)


# Nếu chạy trực tiếp file này thì gọi hàm main()
if __name__ == "__main__":
    # Chạy hàm bất đồng bộ main()
    asyncio.run(main())