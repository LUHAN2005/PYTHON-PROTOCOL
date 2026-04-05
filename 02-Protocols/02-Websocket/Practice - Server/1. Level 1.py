# import thư viện xử lý bất đồng bộ
import asyncio

# import thư viện websockets
import websockets
from websockets.asyncio.server import ServerConnection

# Hàm này sẽ được gọi khi có 1 client kết nối vào server
async def handler(websocket: ServerConnection):
    # websocket đại diện cho kết nối của client hiện tại
    print("Co mot client vua ket noi")

    # Gửi dữ liệu từ server sang client
    await websocket.send("Hello from server")

    # Giữ cho handler chưa kết thúc ngay
    await asyncio.Future()


async def main():
    # Tạo đối tượng server WebSocket, lắng nghe tại 127.0.0.1:8765
    server = websockets.serve(handler, "127.0.0.1", 8765)

    # Mở server để bắt đầu nhận kết nối
    async with server:
        print("Server dang chay tai ws://127.0.0.1:8765")

        # Giữ server chạy mãi
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())