# Import thư viện xử lý bất đồng bộ
import asyncio

# Import thư viện websockets
import websockets

# Import kiểu dữ liệu connection phía server
# Chủ yếu dùng để viết type hint cho rõ và được IDE gợi ý tốt hơn
from websockets.asyncio.server import ServerConnection


# Hàm này sẽ được gọi mỗi khi có 1 client kết nối vào server
async def handler(server: ServerConnection):
    # In ra terminal để biết có client vừa kết nối
    print("Có một client vừa kết nối !!!")

    # Server chờ nhận 1 message từ client gửi sang
    message = await server.recv()

    # In message mà server vừa nhận được
    print("Server nhận : ", message)

    # Server gửi lại dữ liệu cho client
    # Đây là kiểu echo: client gửi gì thì server trả lại gần như cái đó
    await server.send("Server echo: " + message)


# Hàm chính dùng để khởi động WebSocket server
async def main():
    # Tạo đối tượng server WebSocket
    # Server sẽ lắng nghe tại địa chỉ 127.0.0.1 và port 8765
    server = websockets.serve(handler, "127.0.0.1", 8765)

    # Mở server để bắt đầu nhận kết nối từ client
    async with server:
        # In ra thông báo để biết server đã chạy
        print("Server dang chay tai ws://127.0.0.1:8765")

        # Giữ server chạy mãi, không cho hàm main kết thúc ngay
        await asyncio.Future()


# Nếu chạy trực tiếp file này thì gọi hàm main()
if __name__ == "__main__":
    # Chạy hàm bất đồng bộ main()
    asyncio.run(main())