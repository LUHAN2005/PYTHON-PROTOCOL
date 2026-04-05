# import thư viện bất đồng bộ
import asyncio

# import thư viện websocket
import websockets


# Khai báo một hàm bất đồng bộ
async def main():
    # Đây là địa chỉ WebSocket server mà client muốn kết nối tới
    url = "ws://127.0.0.1:8765"

    # Tạo đối tượng kết nối WebSocket
    connection = websockets.connect(url)

    # Mở kết nối và gán kết nối đang hoạt động vào biến websocket
    async with connection as websocket:
        # Nhận 1 message từ server gửi sang
        message = await websocket.recv()
        print("Nhan tu server:", message)


if __name__ == "__main__":
    asyncio.run(main())