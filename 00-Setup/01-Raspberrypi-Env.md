# BÀI 1 : PI ENV + TERMINAL (Windows ↔ Linux) — MASTER NỀN TẢNG CHO IoT/AUTOMATION

## Mục lục

1. [Tổng quan môi trường Pi](#1-tổng-quan-môi-trường-pi)
2. [Terminal là gì? Vì sao phải học?](#2-terminal-là-gì-vì-sao-phải-học)
3. [Linux căn bản trên Pi (so sánh với Windows)](#3-linux-căn-bản-trên-pi-so-sánh-với-windows)
4. [Quản lý hệ thống & cập nhật](#4-quản-lý-hệ-thống--cập-nhật)
5. [Mạng & debug kết nối](#5-mạng--debug-kết-nối)
6. [Process management (app treo thì xử)](#6-process-management-app-treo-thì-xử)
7. [Logs & quan sát hệ thống (observability cơ bản)](#7-logs--quan-sát-hệ-thống-observability-cơ-bản)
8. [systemd service (chạy 24/7 chuẩn nghề)](#8-systemd-service-chạy-247-chuẩn-nghề)
9. [Storage & quyền truy cập thiết bị](#9-storage--quyền-truy-cập-thiết-bị)
10. [SSH & remote work](#10-ssh--remote-work)
11. [Time sync & timezone](#11-time-sync--timezone)
12. [Bảo mật tối thiểu trên Pi](#12-bảo-mật-tối-thiểu-trên-pi)
13. [Checkpoint cuối bài (tự test)](#13-checkpoint-cuối-bài-tự-test)
14. [(Tuỳ chọn) Bài tập tự luyện](#tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. Tổng quan môi trường Pi

### 1.1. Raspberry Pi dùng để làm gì trong IoT/Automation?

Trong hệ IoT/automation, Raspberry Pi thường đóng vai trò **máy edge** (máy tính nhỏ đặt gần thiết bị) để:

* **Edge gateway**: thu thập dữ liệu từ PLC/vi điều khiển/sensor → chuẩn hoá → đẩy lên MQTT/DB/cloud.
* **Bridge**: nối 2 thế giới OT/IT (ví dụ Modbus/OPC UA ↔ MQTT/WebSocket).
* **HMI/Web server**: chạy dashboard, server realtime, API nội bộ.
* **Data logger**: lưu log/telemetry theo thời gian.

### 1.2. Dev (chạy thử) vs Prod (chạy 24/7)

| Tiêu chí          | Dev (chạy thử)          | Prod (24/7)                              |
| ----------------- | ----------------------- | ---------------------------------------- |
| Cách chạy         | chạy tay trong terminal | chạy bằng **service** tự khởi động       |
| Log               | in ra màn hình          | log có hệ thống (`journalctl`, file log) |
| Reconnect/timeout | đôi khi bỏ qua          | bắt buộc có retry/backoff                |
| Khởi động lại     | bạn tự restart          | hệ thống tự restart khi lỗi              |
| Bảo mật           | đơn giản                | tối thiểu phải có secrets, port, quyền   |

> Lưu ý: “Pi env” không chỉ là lệnh. Nó là **cách vận hành** để app chạy bền như thiết bị công nghiệp.

---

## 2. Terminal là gì? Vì sao phải học?

**Terminal** là nơi bạn gõ lệnh để điều khiển hệ thống.

* Trên **Windows** bạn thường dùng: **PowerShell**.
* Trên **Raspberry Pi** bạn dùng: **Linux shell** (bash/zsh).

Bạn học terminal để:

* cài tool / chạy script nhanh
* debug mạng/port
* xem log khi app lỗi
* triển khai chạy 24/7 bằng service

> Note: Với IoT/automation, terminal giống như “tua vít” của kỹ sư. Không cần quá giỏi, nhưng phải cầm là làm được.

---

## 3. Linux căn bản trên Pi (so sánh với Windows)

### 3.1. Cấu trúc thư mục (Linux/Pi)

* `/home/<user>`: thư mục cá nhân (giống `C:\Users\<user>`)
* `/etc`: cấu hình hệ thống (service, network, …)
* `/var/log`: log hệ thống và log service
* `/opt`: nơi đặt ứng dụng (app chạy 24/7) hoặc vendor tools

> Lưu ý: Trên Pi, bạn nên để code/app “prod” ở `/opt/<app>` hoặc `/home/<user>/<project>` tuỳ mức độ.

### 3.2. Bộ lệnh thao tác file/folder (song song)

| Việc              | Windows PowerShell                      | Linux/Pi                                | Ý nghĩa            |
| ----------------- | --------------------------------------- | --------------------------------------- | ------------------ |
| xem đang ở đâu    | `pwd`                                   | `pwd`                                   | đường dẫn hiện tại |
| liệt kê           | `ls`                                    | `ls`                                    | xem file/folder    |
| vào thư mục       | `cd <dir>`                              | `cd <dir>`                              | đổi vị trí         |
| tạo thư mục       | `mkdir <dir>`                           | `mkdir <dir>`                           | tạo folder         |
| copy              | `cp a b`                                | `cp a b`                                | copy file          |
| di chuyển/đổi tên | `mv a b`                                | `mv a b`                                | rename/move        |
| xoá               | `rm a.txt`                              | `rm a.txt`                              | xoá file           |
| xoá thư mục       | `rm -r dir`                             | `rm -r dir`                             | xoá folder         |
| xem file          | `cat a.txt`                             | `cat a.txt`                             | in nội dung        |
| xem dài           | `more a.txt`                            | `less a.txt`                            | đọc file dài       |
| xem đầu/cuối      | `head -n 20 a.txt` / `tail -n 20 a.txt` | `head -n 20 a.txt` / `tail -n 20 a.txt` | kiểm tra nhanh     |

> Lưu ý: PowerShell có nhiều alias giống Linux (`ls`, `cp`, `mv`, `rm`, `cat`). Nhưng ý nghĩa đôi khi hơi khác. Khi lên Pi thì mọi thứ “chuẩn Linux”.

### 3.3. Tìm kiếm trong terminal

| Mục tiêu           | Linux/Pi (chuẩn)             | Windows (PowerShell)                        |
| ------------------ | ---------------------------- | ------------------------------------------- |
| tìm chữ trong file | `grep -n "keyword" file.txt` | `Select-String -Pattern "keyword" file.txt` |
| tìm file theo tên  | `find . -name "*.py"`        | `Get-ChildItem -Recurse -Filter "*.py"`     |

> Tip: Trong IoT/automation, `grep` cực mạnh để tìm lỗi trong log.

### 3.4. Editor nhanh trên máy

* Linux/Pi: `nano`, `vim`
* Windows: nên dùng VS Code (mở folder dự án)

Ví dụ (Pi):

```bash
nano /etc/hostname
```

> Note: Bạn không cần master vim ngay. `nano` đủ dùng khi chỉnh file config/service.

### 3.5. Quyền & user (phần khiến người mới hay kẹt)

* `sudo`: chạy lệnh với quyền admin (root)
* `chmod`: đổi quyền (đọc/ghi/chạy)
* `chown`: đổi owner
* `groups`: xem nhóm user (serial thường cần `dialout`)

Ví dụ (Pi):

```bash
sudo usermod -aG dialout $USER
```

> Lưu ý: Sau khi thêm nhóm, thường phải logout/login lại để có hiệu lực.

---

## 4. Quản lý hệ thống & cập nhật

### 4.1. Pi/Linux: cài gói bằng apt

* update danh sách gói:

```bash
sudo apt update
```

* nâng cấp:

```bash
sudo apt upgrade -y
```

* cài tối thiểu nên có:

```bash
sudo apt install -y git curl wget build-essential
sudo apt install -y lsof net-tools
```

### 4.2. Windows: cài tool bằng winget/choco (tham khảo)

* winget (nếu có):

```powershell
winget install Git.Git
```

> Note: Trên Windows bạn có thể làm hết bằng Python/pip. Nhưng trên Pi, `apt` là “đường chính thống”.

---

## 5. Mạng & debug kết nối

### 5.1. Vì sao mạng là phần “đi làm thật” nhất?

Giao thức (MQTT/WebSocket/OPC UA/Modbus TCP) đều chạy trên mạng. Lỗi hay gặp nhất:

* sai IP/port
* DNS lỗi
* firewall chặn
* service chưa chạy
* NAT/proxy gây drop

### 5.2. IP / route / DNS

| Mục tiêu   | Linux/Pi           | Windows          |
| ---------- | ------------------ | ---------------- |
| xem IP     | `ip a`             | `ipconfig`       |
| xem route  | `ip route`         | `route print`    |
| DNS config | `/etc/resolv.conf` | network settings |

### 5.3. Kiểm tra kết nối

| Mục tiêu   | Linux/Pi                      | Windows                       |
| ---------- | ----------------------------- | ----------------------------- |
| ping       | `ping -c 3 8.8.8.8`           | `ping 8.8.8.8`                |
| test HTTP  | `curl -I https://example.com` | `curl -I https://example.com` |
| DNS lookup | `nslookup google.com`         | `nslookup google.com`         |

### 5.4. Port/service (cực quan trọng khi debug)

* Linux/Pi (khuyên dùng `ss`):

```bash
sudo ss -tulpn
```

* hoặc:

```bash
sudo netstat -tulpn
```

* xem tiến trình đang chiếm port bằng `lsof`:

```bash
sudo lsof -i -P -n
```

* Windows:

```powershell
netstat -ano
```

> Lưu ý: Nếu bạn làm MQTT broker, bạn phải thấy port 1883 (TCP) đang LISTEN.

### 5.5. Firewall (biết khái niệm)

* Linux/Pi hay dùng `ufw` (tuỳ dự án):

```bash
sudo ufw status
```

> Note: Khi chưa quen, bạn chỉ cần hiểu: firewall có thể chặn port → kết nối không vào được.

---

## 6. Process management (app treo thì xử)

### 6.1. Xem tiến trình

* Linux/Pi:

```bash
ps aux | head
```

```bash
top
```

* Windows:

```powershell
Get-Process | Select-Object -First 10
```

### 6.2. Kill/restart

* Linux/Pi:

```bash
kill -9 <PID>
```

```bash
pkill -f "python"
```

* Windows:

```powershell
Stop-Process -Id <PID> -Force
```

### 6.3. Chạy nền (dev) vs chạy service (prod)

* Dev trên Pi:

  * `nohup` (chạy nền kiểu nhanh)
  * `tmux/screen` (giữ session khi SSH)

> Lưu ý: Đây chỉ phù hợp dev. Prod chuẩn là **systemd service** (phần 8).

---

## 7. Logs & quan sát hệ thống (observability cơ bản)

### 7.1. Log nằm ở đâu?

* Linux/Pi:

  * log hệ thống: `/var/log/*`
  * log service: `journalctl`

### 7.2. Xem log nhanh

* tail realtime:

```bash
tail -f /var/log/syslog
```

* xem 100 dòng gần nhất của journal:

```bash
journalctl -n 100 --no-pager
```

### 7.3. Cách “lần dấu” lỗi (tư duy)

1. App có chạy không? (process/service)
2. Port có mở không? (`ss`/`netstat`)
3. Log nói gì? (`journalctl`, file log)
4. Lỗi network hay permission?

> Tip: Với automation, log rõ ràng + timestamp chuẩn = cứu bạn rất nhiều.

---

## 8. systemd service (chạy 24/7 chuẩn nghề)

### 8.1. systemd là gì?

**systemd** là trình quản lý service trên Linux.

Bạn dùng nó để:

* tự chạy app khi boot
* tự restart khi app crash
* xem log tập trung bằng `journalctl`

### 8.2. Lệnh systemctl cơ bản

```bash
sudo systemctl status <service>
sudo systemctl start <service>
sudo systemctl stop <service>
sudo systemctl restart <service>
sudo systemctl enable <service>
```

### 8.3. Xem log service

```bash
journalctl -u <service> -n 200 --no-pager
```

### 8.4. (Ví dụ mẫu) File `.service` cho app Python

> Đây là mẫu để bạn hiểu cấu trúc. Khi bạn có Pi, mình sẽ chỉnh theo project thật của bạn.

```ini
[Unit]
Description=My Python Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/my-gateway
ExecStart=/opt/my-gateway/.venv/bin/python -m src.main
Restart=always
RestartSec=3
User=pi
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

> Lưu ý: `WorkingDirectory`, `ExecStart`, `User` phải đúng với máy và đường dẫn thật.

---

## 9. Storage & quyền truy cập thiết bị

### 9.1. Nơi lưu dữ liệu

* gợi ý:

  * `/data` (dữ liệu)
  * `/opt/<app>/data` (data nằm cùng app)

### 9.2. USB/Serial (PLC/MCU hay dùng)

* Thiết bị serial thường xuất hiện như:

  * `/dev/ttyUSB0`, `/dev/ttyUSB1` (USB-to-Serial)
  * `/dev/ttyACM0` (một số board)

Kiểm tra:

```bash
ls -l /dev/ttyUSB*
ls -l /dev/ttyACM*
```

* Nhóm quyền hay gặp: `dialout`.

> Note: Không vào được serial rất hay do “thiếu quyền”, không phải do code.

### 9.3. RS-485 adapter (khái niệm)

Bạn cần nắm:

* tên cổng (`/dev/ttyUSB0`)
* baudrate (9600/19200/115200)
* parity/stop bits

---

## 10. SSH & remote work

### 10.1. SSH dùng để làm gì?

* điều khiển Pi từ xa
* deploy code
* xem log / restart service

### 10.2. Lệnh cơ bản

* từ máy bạn SSH vào Pi:

```bash
ssh pi@<ip>
```

* copy file:

```bash
scp file.txt pi@<ip>:/home/pi/
```

* đồng bộ thư mục (nhanh, mạnh):

```bash
rsync -av ./project/ pi@<ip>:/opt/project/
```

> Lưu ý: SSH key (không dùng password) là best practice.

---

## 11. Time sync & timezone

### 11.1. Vì sao time quan trọng?

* telemetry/log không đúng giờ → debug cực khó
* event ordering sai

### 11.2. Kiểm tra timezone và thời gian

```bash
date
```

```bash
timedatectl
```

Set timezone (Bangkok):

```bash
sudo timedatectl set-timezone Asia/Bangkok
```

> Note: Trên Pi thường có NTP để tự sync. Bạn chỉ cần biết kiểm tra.

---

## 12. Bảo mật tối thiểu trên Pi

### 12.1. Tối thiểu phải làm

* đổi password mặc định
* ưu tiên SSH key
* chỉ mở port cần thiết
* secrets để trong `.env` (không commit)

### 12.2. Nguyên tắc “ít nhất quyền”

* app chạy bằng user thường (không chạy root nếu không cần)
* chỉ `sudo` khi cài gói/chỉnh system

> Lưu ý: Automation/OT rất nhạy cảm. “Mở hết port cho tiện” là thói quen nguy hiểm.

---

## 13. Checkpoint cuối bài (tự test)

Bạn xem như **đạt Pi env master nền** khi (trên Pi hoặc Linux/WSL):

1. Xem được IP và route:

```bash
ip a
ip route
```

2. Biết kiểm tra port đang listen:

```bash
sudo ss -tulpn
```

3. Tạo và chạy được 1 service auto start (trên Pi thật):

```bash
sudo systemctl enable <service>
sudo systemctl restart <service>
```

4. Xem được log service:

```bash
journalctl -u <service> -n 200 --no-pager
```

5. (Nếu có) nhận được serial device:

```bash
ls -l /dev/ttyUSB*
```

---

## (Tuỳ chọn) Bài tập tự luyện

1. (Terminal) Tạo thư mục `lab`, tạo file `note.txt`, rồi dùng `cat`/`less`/`tail` để xem.
2. (Network) Tự kiểm tra:

   * IP của máy
   * ping ra internet
   * liệt kê port đang listen
3. (Logs) Tạo một app Python in log mỗi 2 giây, rồi thử xem log theo thời gian.
4. (Prod mindset) Viết “checklist 8 bước debug” của riêng bạn khi thiết bị không kết nối được.

> Tip: Khi bạn có Raspberry Pi, chúng ta sẽ làm lab “tạo systemd service chạy gateway python + tự restart” để hoàn thành level prod.
