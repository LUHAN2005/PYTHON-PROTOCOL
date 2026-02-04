# BÀI 2 : PYTHON ENV – CÀI ĐẶT, VENV, PIP, QUẢN LÝ THƯ VIỆN (Python)

## Mục lục

1. [Python env là gì?](#1-python-env-là-gì)
2. [Cài Python & kiểm tra version](#2-cài-python--kiểm-tra-version)
3. [Tạo và dùng môi trường ảo (venv)](#3-tạo-và-dùng-môi-trường-ảo-venv)
4. [Pip: cài/gỡ/kiểm tra thư viện](#4-pip-cài-gỡkiểm-tra-thư-viện)
5. [Requirements & pin version (chuẩn junior)](#5-requirements--pin-version-chuẩn-junior)
6. [Poetry / pip-tools (tuỳ chọn để “master”)](#6-poetry--pip-tools-tuỳ-chọn-để-master)
7. [Cấu trúc project tối thiểu để học protocol](#7-cấu-trúc-project-tối-thiểu-để-học-protocol)
8. [Lỗi thường gặp & cách xử](#8-lỗi-thường-gặp--cách-xử)
9. [(Tuỳ chọn) Bài tập tự luyện](#tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. Python env là gì?

**Python env (environment)** là “môi trường chạy Python” của dự án, bao gồm:

* **Python interpreter** (python.exe)
* **Thư viện (packages)** bạn cài bằng pip
* **Biến môi trường** (PATH, .env)
* (Tuỳ) công cụ quản lý dependency: **requirements.txt / pip-tools / poetry**

👉 Mục tiêu của env là:

* **Mỗi project có bộ thư viện riêng**, không “đụng” nhau.
* **Cài đúng – chạy đúng – deploy đúng** (không kiểu “máy em chạy được mà máy anh không chạy”).

> Lưu ý: Khi làm IoT/automation, project thường chạy lâu dài (24/7). Pin version giúp tránh “hôm nay chạy, mai update lỗi”.

---

## 2. Cài Python & kiểm tra version

### 2.1. Kiểm tra Python đã có chưa
> [!NOTE]
> `python3` thường dùng cho **linux/macOS**
>
> `python` thường dùng cho **window**

Mở **PowerShell/CMD/Terminal** và chạy:

```bash
python --version
pip --version
```

Nếu máy bạn dùng `python3` thay vì `python`:

```bash
python3 --version
pip3 --version
```

### 2.2. Kiểm tra đường dẫn Python đang chạy (cực quan trọng)

```bash
python -c "import sys; print(sys.executable)"
```

* Nếu bạn đang bật venv đúng, đường dẫn sẽ trỏ vào thư mục `.venv`.
* Nếu chưa bật venv, nó trỏ vào Python hệ thống.

> Lưu ý: 80% lỗi “cài rồi mà import không được” là do bạn đang chạy nhầm Python / nhầm pip.

### 2.3. (Windows) Nếu gõ `python` bị lỗi

* Cài Python từ **python.org** (khuyên) và tick **Add Python to PATH**
* Hoặc dùng **py launcher**:

```bash
py --version
py -3 --version
```

---

## 3. Tạo và dùng môi trường ảo (venv)

### 3.1. Vì sao cần venv?

Nếu không dùng venv:

* Project A cài `pymodbus==2.x`
* Project B cài `pymodbus==3.x`

→ 2 project “đạp” nhau, dễ crash.

**venv** giúp mỗi project có thư viện riêng.

> [!NOTE]
> Khi đẩy lên github ta phải bỏ đi thư mục **.venv** vì nó rất nặng
>
> Ta phải tạo file **.gitignore** để loại bỏ những file không muốn commit

### 3.2. Tạo venv

Trong thư mục dự án:

```bash
python -m venv .venv
```

> Note: `.venv` là tên phổ biến (dễ nhận ra, dễ ignore trong git).

### 3.3. Kích hoạt venv
Activate venv là để bảo đảm mọi thứ bạn chạy/cài (python, pip, libraries) đều nằm trong “môi trường riêng” của project, không dính tới Python hệ thống.

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```bat
.\.venv\Scripts\activate.bat
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Khi active đúng, terminal thường hiện thêm `(.venv)`.

### 3.4. Tắt venv

Tắt venv (deactivate) không phải “bắt buộc”, nhưng nên làm trong vài trường hợp để tránh bạn chạy/cài nhầm vào project khác.

> [!TIP] Vì sao cần tắt venv?
> (1) Bạn chuyển sang project khác
Mỗi project có venv riêng. Nếu bạn vẫn đang bật venv của project A mà chạy lệnh trong project B, bạn có thể:
cài thư viện nhầm vào venv A
chạy code B bằng thư viện của A → lỗi rất khó hiểu
>
> (2) Bạn muốn chạy Python “hệ thống”
Ví dụ bạn cần chạy tool global (hiếm), hoặc kiểm tra python ngoài venv.
>
>(3) Giữ terminal “sạch”
VenV chỉ ảnh hưởng cửa sổ terminal hiện tại. Tắt xong là terminal quay về trạng thái bình thường.

### Cú pháp :

```bash
deactivate
```

### 3.5. (Windows) Nếu PowerShell chặn Activate

Chạy 1 lần:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Rồi activate lại.

> Lưu ý: Không nên set policy ở mức `LocalMachine` nếu bạn không chắc.

---

## 4. Pip: cài/gỡ/kiểm tra thư viện

### 4.1. Nâng cấp pip (nên làm ngay sau khi active venv)

```bash
python -m pip install -U pip
```

### 4.2. Luật vàng: luôn dùng `python -m pip`

```bash
python -m pip install <package>
```

Vì `pip` đôi khi trỏ sai môi trường, còn `python -m pip` luôn chắc chắn đi theo interpreter hiện tại.

### 4.3. Cài / gỡ / liệt kê thư viện

Cài:

```bash
python -m pip install requests
```

Gỡ:

```bash
python -m pip uninstall requests
```

Liệt kê:

```bash
python -m pip list
```

Xem chi tiết:

```bash
python -m pip show requests
```

### 4.4. Kiểm tra import nhanh

```bash
python -c "import requests; print(requests.__version__)"
```

---

## 5. Requirements & pin version (chuẩn junior)

### 5.1. Vì sao cần pin version?

* Bạn học xong, vài tháng sau cài lại project → vẫn chạy như cũ
* Deploy lên máy khác / Raspberry Pi → không lệch version

### 5.2. Tạo `requirements.txt` (cách đơn giản)

Khi bạn đã cài đủ thư viện trong venv:

```bash
python -m pip freeze > requirements.txt
```

Cài lại từ requirements:

```bash
python -m pip install -r requirements.txt
```

> Lưu ý: `pip freeze` thường pin hết mọi thứ (kể cả dependency phụ). Với project nhỏ học tập thì ok.

### 5.3. Quy ước file (gợi ý)

* `requirements.txt` : bản pin đầy đủ
* (Tuỳ) `requirements-dev.txt` : tool dev (pytest, ruff, mypy)

Ví dụ `requirements-dev.txt`:

```txt
pytest
ruff
mypy
```

---

## 6. Poetry / pip-tools (tuỳ chọn để “master”)

Phần này không bắt buộc khi mới học, nhưng rất “đúng chuẩn” khi làm project lớn.

### 6.1. pip-tools (nhẹ, hợp Windows)

Ý tưởng:

* `requirements.in` chứa “dependency chính”
* compile ra `requirements.txt` pin phiên bản

Cài pip-tools:

```bash
python -m pip install pip-tools
```

Tạo `requirements.in`:

```txt
paho-mqtt
websockets
python-socketio
pymodbus
asyncua
```

Compile:

```bash
pip-compile requirements.in
```

Cài:

```bash
python -m pip install -r requirements.txt
```

### 6.2. Poetry (đẹp, nhiều tính năng)

* quản lý dependency + lock
* tạo project chuẩn

Nếu dùng Poetry thì bạn sẽ có `pyproject.toml` + `poetry.lock`.

> Note: Nếu bạn muốn “đi làm nhanh”, pip-tools là quá đủ. Poetry dùng khi project lớn và team dùng chung.

---

## 7. Cấu trúc project tối thiểu để học protocol

### 7.1. Tạo workspace học (gợi ý)

```bash
mkdir IoT-Lab
cd IoT-Lab
python -m venv .venv
```

Activate venv, rồi tạo cấu trúc:

```bash
mkdir src
mkdir notes
```

Tạo file:

* `src/main.py`

Nội dung `src/main.py`:

```python
print("Hello IoT Lab")
```

Chạy:

```bash
python src/main.py
```

### 7.2. Cài bộ thư viện để học 5 protocol (bạn đang học)

Cài trong venv:

```bash
python -m pip install paho-mqtt websockets "python-socketio[client]" pymodbus asyncua
```

Test import:

```bash
python -c "import paho.mqtt.client, websockets, socketio, pymodbus, asyncua; print('OK')"
```

> Lưu ý: Trên Windows, nếu gặp lỗi build khi cài một số package (hiếm với nhóm này), cài thêm “Microsoft C++ Build Tools” là giải quyết.

---

## 8. Lỗi thường gặp & cách xử

### 8.1. `pip install ...` xong nhưng `import ...` báo lỗi

**Nguyên nhân phổ biến:** cài vào môi trường khác.

Cách xử (luôn dùng):

```bash
python -c "import sys; print(sys.executable)"
python -m pip -V
```

* `sys.executable` và `pip -V` phải cùng trỏ vào `.venv`.

### 8.2. Không activate được venv (Windows)

* PowerShell bị chặn script → dùng:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Hoặc dùng CMD với `activate.bat`.

### 8.3. Cài thư viện bị lỗi “permission denied”

* Bạn đang cài vào Python hệ thống (không phải venv)
* Hãy tạo venv và cài lại trong venv

### 8.4. Không biết đang dùng `python` hay `python3`

* Windows: có thể dùng `py -3`
* Linux/macOS: thường dùng `python3`

### 8.5. “Thư mục dự án” bị rối

Gợi ý quy ước:

* Code: `src/`
* Note: `notes/`
* Test: `tests/`
* Config: `.env` (không commit)

---

## (Tuỳ chọn) Bài tập tự luyện

1. Tạo project `IoT-Lab` + `.venv` và chạy được `src/main.py` in `Hello IoT Lab`.
2. Cài 5 thư viện: `paho-mqtt`, `websockets`, `python-socketio`, `pymodbus`, `asyncua`.
3. Tạo `requirements.txt` bằng `pip freeze` và thử xoá venv rồi cài lại từ requirements.
4. Viết 1 file `src/check_env.py` in ra:

   * `sys.version`
   * `sys.executable`
   * danh sách 5 package và version của chúng.

> Tip: Bài 3 là bài quan trọng nhất để bạn “deploy lại không sợ” khi chuyển máy hoặc lên Raspberry Pi sau này.
