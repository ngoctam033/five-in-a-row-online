# MÔN HỌC: LẬP TRÌNH MẠNG
# GIẢNG VIÊN HƯỚNG DẪN: Mai Ngọc Châu
# NHÓM THỰC HIỆN: Nhóm 6 
    - Nguyễn Ngọc Tâm (NT)
    - Nguyễn Tuấn Cường
    - Lê Gia Bảo
    - Ngô Công Thành
    - Nguyễn Huỳnh Hữu Huy
# Chủ Đề: Lập trình game Cờ Caro (Client-Server)
Đây là một dự án game Cờ Caro (Gomoku) được lập trình bằng Python, xây dựng theo mô hình Client-Server. Dự án cho phép hai người chơi kết nối đến một máy chủ trung tâm, tìm kiếm đối thủ và chơi game trong thời gian thực.

    1. Tính năng chính
        - Kiến trúc Client-Server: Server quản lý trạng thái, Client hiển thị giao diện và gửi hành động.

        - Giao tiếp WebSocket: Sử dụng websockets (phía server) và websocket-client (phía client) để giao tiếp real-time.

        - Sảnh chờ (Lobby):
        *  Người chơi đăng nhập (tạo tài khoản) bằng tên.
        *  Server quản lý danh sách người chơi đang online.
        *  Client có thể yêu cầu và nhận danh sách người chơi online.

        - Chơi game 1v1:
        *  Người chơi có thể tạo phòng game với một đối thủ.
        *  Server quản lý trạng thái của từng phòng game (Room) và logic của ván cờ (GameManager).

        - Giao diện đồ họa (GUI): Xây dựng bằng tkinter phía Client, tách biệt rõ ràng logic (logic/) và giao diện (ui/).

        - Logging: Hệ thống logger.py chuyên nghiệp để ghi log chi tiết ra file, giúp dễ dàng debug.

    2. Công nghệ sử dụng
        - Ngôn ngữ: Python 3
        - Server: websockets, asyncio
        - Client: tkinter (GUI), websocket-client
        - Cấu hình: python-dotenv (phía Client)

    3. Cấu trúc thư mục
        FIVE-IN-A-ROW-ONLINE/
        ├── Client/
        │   ├── logic/
        │   │   └── board.py         # Logic kiểm tra thắng/thua, nước đi
        │   ├── network/
        │   │   └── client_network.py  # Quản lý kết nối WebSocket (Client)
        │   ├── player/
        │   │   ├── aiplayer.py      # (Mở rộng) Logic cho AI
        │   │   └── player.py        # Class đại diện người chơi (Client)
        │   ├── ui/
        │   │   ├── board.py         # (board_ui.py) Logic VẼ bàn cờ và Data Model
        │   │   ├── game_ui.py       # Giao diện chính của ván cờ
        │   │   └── login_ui.py      # Giao diện Đăng nhập / Sảnh chờ
        │   ├── logger.py            # Cấu hình logging
        │   └── main.py              # Điểm khởi động của Client
        │
        ├── Common/
        │   └── protocol.py          # (Hiện không dùng) Định nghĩa giao thức
        │
        └── Server/
            ├── game_manager.py      # Bộ máy logic (Rule Engine) cho 1 ván cờ
            ├── main.py              # Điểm khởi động của Server
            ├── player.py            # Class đại diện người chơi (Server)
            ├── room.py              # Quản lý 1 phiên game (1 ván đấu)
            └── server.py            # Quản lý kết nối, sảnh chờ, và các phòng

    4. Cài đặt
        4.1 Clone dự án:
        * git clone https://github.com/ngoctam033/five-in-a-row-online.git

        4.2 Tạo môi trường ảo (khuyến nghị):
        * python -m venv venv
        * source venv/bin/activate  # Trên Windows: venv\Scripts\activate

        4.3 Cài đặt các thư viện cần thiết: (Bạn cần cd vào đúng thư mục Client và Server hoặc cài chung)
        # Cài đặt cho Server
        pip install websockets

        # Cài đặt cho Client
        pip install websocket-client python-dotenv

        4.4 Cấu hình Client:
        - Trong thư mục Client/, tạo một file tên là .env.
        - Thêm nội dung sau vào file, trỏ đến địa chỉ server của bạn (nếu chạy local thì dùng localhost hoặc 127.0.0.1): server=ws://localhost:9000 

    5. Hướng dẫn chạy
        Bước 1. Khởi động Server: Mở một terminal, di chuyển đến thư mục Server/ và chạy:
        * Bash
        python main.py

        -> Server sẽ bắt đầu lắng nghe tại localhost:9000.

        Bước 2. Khởi động Client 1: Mở một terminal mới, di chuyển đến thư mục Client/ và chạy:
        * Bash
        python main.py

        -> Một cửa sổ LoginUI sẽ hiện lên.
        -> Nhập tên (ví dụ: PlayerA) và nhấn một nút (ví dụ: "Đăng nhập" - logic này cần được hoàn thiện trong UI để gửi create_account).

        Bước 2. Khởi động Client 2: Mở một terminal thứ ba, di chuyển đến thư mục Client/ và chạy:
        * Bash
        python main.py

        -> Một cửa sổ LoginUI thứ hai sẽ hiện lên.
        -> Nhập tên (ví dụ: PlayerB) và nhấn nút "Đăng nhập".

        Bắt đầu trận đấu:

        * Tại cửa sổ của PlayerA, (giả sử UI đã có) chọn PlayerB từ danh sách người chơi online.

        * Nhấn nút "Play" (hoặc "Thách đấu").

        * Hành động này sẽ gửi tin nhắn create_room đến server.

        * Server (server.py) nhận yêu cầu, tạo một Room mới, và gửi tin nhắn GAME_START cho cả hai client.

        * Cả hai client sẽ tự động chuyển sang giao diện GameUI (ChessboardApp) và ván cờ bắt đầu.

    5. Tính năng cần phát triển (To-Do)
    Dựa trên yêu cầu ban đầu của đề tài, đây là các mục cần được cãi thiện:

        5.1. Hoàn thiện Hệ thống Thách đấu:

        - Logic hiện tại (create_room) đang tạo phòng trực tiếp.
        - Cần kích hoạt lại và hoàn thiện logic "mời-chấp nhận-từ chối" (đã có code bị comment out trong server.py).

        5.2. Đếm thời gian (Server-side):

        - Hiện tại game_ui.py đang đếm thời gian (client-side), điều này không đáng tin cậy.
        - Cần implement một bộ đếm thời gian (timer) bên trong class Room (phía server). Khi hết giờ, server phải tự động xử thua và thông báo cho client.

        5.3. Lưu lịch sử trận đấu:

        - Khi một ván cờ kết thúc (trong Room hoặc GameManager), server cần ghi lại kết quả (ai thắng, ai thua, ngày giờ) vào một file (ví dụ: history.json) hoặc một cơ sở dữ liệu.

        5.4. Chuẩn hóa Giao thức (Protocol):

        - File Common/protocol.py (dùng |) đang không được sử dụng.
        - Toàn bộ hệ thống đang chạy bằng JSON (ad-hoc). Cần định nghĩa rõ ràng các cấu trúc JSON này trong Common/ để cả Client và Server cùng tuân theo.
        