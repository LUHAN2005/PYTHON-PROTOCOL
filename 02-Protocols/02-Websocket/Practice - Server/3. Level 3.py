# Import thư viện xử lý bất đồng bộ
import asyncio

# Import thư viện WebSocket
import websockets

# Import kiểu dữ liệu connection phía server
# Dùng để viết type hint cho rõ và để IDE gợi ý tốt hơn
from websockets.asyncio.server import ServerConnection


# Hàm này sẽ được gọi mỗi khi có 1 client kết nối vào server
async def handler(websocket: ServerConnection):
    # In ra terminal để biết có client vừa kết nối
    print("Co mot client vua ket noi")

    try:
        # Vòng lặp vô hạn để server nhận message liên tục từ client
        while True:
            # Chờ client gửi message sang server
            message = await websocket.recv()

            # In message server vừa nhận được
            print("Server nhan duoc:", message)

            # Tạo nội dung phản hồi lại cho client
            reply = "Server echo: " + message

            # Gửi phản hồi từ server về client
            await websocket.send(reply)

    # Nếu client đóng kết nối hoặc ngắt kết nối đột ngột
    except websockets.ConnectionClosed:
        print("Client da ngat ket noi")


# Hàm chính để khởi động WebSocket server
async def main():
    # Tạo đối tượng server WebSocket
    # Server sẽ lắng nghe tại địa chỉ 127.0.0.1 và cổng 8765
    server = websockets.serve(handler, "127.0.0.1", 8765)

    # Mở server để bắt đầu nhận kết nối từ client
    async with server:
        # In ra thông báo để biết server đã chạy
        print("Server dang chay tai ws://127.0.0.1:8765")

        # Giữ cho server chạy mãi, không cho hàm main kết thúc ngay
        await asyncio.Future()


# Nếu chạy trực tiếp file này thì gọi hàm main()
if __name__ == "__main__":
    # Chạy hàm bất đồng bộ main()
    asyncio.run(main())