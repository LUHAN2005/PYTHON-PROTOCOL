# BÀI 0: SECURITY BASICS – BẢO MẬT TỐI THIỂU CHO IoT/AUTOMATION (MQTT, Web, Modbus, OPC UA)

## Mục lục

1. [Security basics là gì? Vì sao IoT/Automation phải học?](#1-security-basics-là-gì-vì-sao-iotautomation-phải-học)
2. [Tư duy nền: Threat model đơn giản (đủ dùng)](#2-tư-duy-nền-threat-model-đơn-giản-đủ-dùng)
3. [Nguyên tắc vàng: Least privilege + giảm bề mặt tấn công](#3-nguyên-tắc-vàng-least-privilege--giảm-bề-mặt-tấn-công)
4. [Secrets: quản lý mật khẩu/token đúng cách](#4-secrets-quản-lý-mật-khẩutoken-đúng-cách)
5. [TLS/Certificates: hiểu để không sợ lỗi cert](#5-tlscertificates-hiểu-để-không-sợ-lỗi-cert)
6. [MQTT security: auth/ACL/TLS/LWT (thực chiến)](#6-mqtt-security-authacltlslwt-thực-chiến)
7. [Web security: HTTPS, CORS, auth cơ bản cho WS/Socket.IO](#7-web-security-https-cors-auth-cơ-bản-cho-wssocketio)
8. [Modbus security: vì sao phải bảo vệ bằng network](#8-modbus-security-vì-sao-phải-bảo-vệ-bằng-network)
9. [OPC UA security: policy/mode/cert/trust (khái niệm chuẩn)](#9-opc-ua-security-policymodecerttrust-khái-niệm-chuẩn)
10. [Logging an toàn: không rò rỉ secrets](#10-logging-an-toàn-không-rò-rỉ-secrets)
11. [Checklist triển khai tối thiểu (junior-ready)](#11-checklist-triển-khai-tối-thiểu-junior-ready)
12. [Lỗi thường gặp & cách xử](#12-lỗi-thường-gặp--cách-xử)
13. [(Tuỳ chọn) Bài tập tự luyện](#tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. Security basics là gì? Vì sao IoT/Automation phải học?

### 1.1. Security basics là gì?

**Security basics** là bộ kiến thức tối thiểu để hệ thống:

* không “mở toang” cho người lạ
* không lộ dữ liệu/điều khiển
* không bị phá do cấu hình sai

### 1.2. Vì sao IoT/Automation nhạy cảm hơn web thường?

* IoT/automation không chỉ “mất dữ liệu” mà có thể **ảnh hưởng thiết bị thật**.
* Nhiều protocol OT (như Modbus) **không có bảo mật** theo thiết kế cũ.
* Thiết bị chạy 24/7: nếu bị scan/đánh liên tục sẽ ảnh hưởng ổn định.

> Lưu ý: Mục tiêu bài này là “làm đúng tối thiểu” để hệ thống an toàn và vận hành bền.

---

## 2. Tư duy nền: Threat model đơn giản (đủ dùng)

### 2.1. Threat model là gì?

Là cách bạn trả lời 3 câu:

1. **Ai** có thể tấn công? (người trong LAN, người ngoài internet, thiết bị lạ)
2. **Tấn công vào đâu**? (broker MQTT, web dashboard, PLC network)
3. **Mất cái gì**? (telemetry, quyền điều khiển, dữ liệu nội bộ)

### 2.2. 3 nhóm rủi ro phổ biến trong hệ IoT

* **Unauthorized access**: ai cũng pub/sub hoặc điều khiển
* **Eavesdropping**: bị nghe lén dữ liệu (không mã hoá)
* **Misconfiguration**: tự cấu hình sai (mở port, hardcode secret)

> Tip: Nếu bạn biết threat model, bạn sẽ biết “cần bảo vệ phần nào trước”.

---

## 3. Nguyên tắc vàng: Least privilege + giảm bề mặt tấn công

### 3.1. Least privilege (ít quyền nhất có thể)

* App chạy bằng **user thường**, không chạy root nếu không cần.
* Chỉ cấp quyền device cần thiết (serial, file data).

Ví dụ trên Linux/Pi:

* chỉ thêm user vào nhóm `dialout` để dùng serial (không dùng root):

```bash
sudo usermod -aG dialout $USER
```

### 3.2. Giảm bề mặt tấn công (attack surface)

* chỉ mở những port cần thiết
* service nội bộ thì bind `127.0.0.1` hoặc LAN, không mở ra internet
* tách mạng OT/IT nếu có thể (khái niệm)

> Lưu ý: “Mở hết cho tiện” là cách nhanh nhất để rước rủi ro.

---

## 4. Secrets: quản lý mật khẩu/token đúng cách

### 4.1. Không hardcode secrets trong code

**Sai**:

```js
const MQTT_PASSWORD = "123456";
```

**Đúng**: dùng `.env` hoặc biến môi trường.

### 4.2. `.env` và `.env.example`

* `.env`: file thật chứa secrets → **KHÔNG commit**
* `.env.example`: file mẫu → commit để người khác biết cần biến gì

Ví dụ `.env.example`:

```env
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USER=demo
MQTT_PASSWORD=change_me
```

### 4.3. GitHub & secrets

* luôn thêm vào `.gitignore`:

```gitignore
.env
.venv/
```

> Tip: Lộ secret lên GitHub là lỗi rất nặng. Hãy coi `.env` như “chìa khoá nhà”.

---

## 5. TLS/Certificates: hiểu để không sợ lỗi cert

### 5.1. TLS là gì?

TLS (SSL) giúp:

* **mã hoá** dữ liệu (chống nghe lén)
* **xác thực server** (đúng broker/server thật)
* (tuỳ) **xác thực client** bằng certificate (mạnh hơn password)

### 5.2. Certificate/CA là gì?

* **Certificate**: “giấy chứng nhận” của server/client
* **CA**: nơi ký chứng nhận
* **Trust**: client tin CA/cert nào

### 5.3. Lỗi TLS hay gặp (để khỏi hoảng)

* cert **không được tin** (untrusted)
* cert **hết hạn** (expired)
* **hostname mismatch** (connect bằng IP nhưng cert cấp cho domain)

> Lưu ý: Đa số lỗi TLS là “cấu hình trust/hostname”, không phải code sai.

---

## 6. MQTT security: auth/ACL/TLS/LWT (thực chiến)

### 6.1. Các lớp bảo mật MQTT

1. **Username/Password** (cơ bản)
2. **ACL**: user nào được pub/sub topic nào
3. **TLS**: mã hoá + xác thực
4. (tuỳ) **Client cert**: xác thực mạnh

### 6.2. Vì sao cần ACL?

Nếu không có ACL:

* client lạ có thể subscribe hết dữ liệu
* hoặc publish vào topic điều khiển

Ví dụ tư duy ACL (không cần cấu hình cụ thể ở đây):

* `device-01` chỉ được publish `telemetry/device-01/#`
* UI chỉ được subscribe `telemetry/#` và publish `cmd/#` (có kiểm soát)

### 6.3. LWT (Last Will and Testament)

LWT không phải “security” trực tiếp, nhưng giúp bạn phát hiện:

* client chết bất thường
* mất kết nối

Từ đó hệ thống có thể **fail-safe**.

> Tip: Trong automation, fail-safe quan trọng ngang bảo mật.

---

## 7. Web security: HTTPS, CORS, auth cơ bản cho WS/Socket.IO

### 7.1. HTTPS vs HTTP

* HTTP: plain text → dễ bị nghe lén
* HTTPS: TLS mã hoá

### 7.2. WebSocket (`ws://` vs `wss://`)

* `ws://` giống HTTP (không mã hoá)
* `wss://` giống HTTPS (có TLS)

> Lưu ý: Nếu hệ thống có internet/public network, ưu tiên `wss://`.

### 7.3. CORS là gì? (mức hiểu đủ dùng)

CORS là cơ chế trình duyệt chặn web gọi API/Socket từ domain khác.

* Cấu hình đúng giúp:

  * không cho web lạ kết nối vào server

> Tip: CORS không thay auth, nhưng là lớp “hàng rào” tốt.

### 7.4. Auth cơ bản cho realtime

Các cách thường gặp:

* token (Bearer/JWT) gửi khi connect
* session cookie (nội bộ)

Tối thiểu bạn cần hiểu:

* “không auth” → ai vào cũng nghe/điều khiển
* nên tách event/channel:

  * telemetry: read-only
  * command: có auth chặt hơn

---

## 8. Modbus security: vì sao phải bảo vệ bằng network

### 8.1. Sự thật về Modbus

* Modbus (đặc biệt RTU/TCP) thường **không có encryption/auth**.
* Ai vào được mạng/port là có thể đọc/ghi.

### 8.2. Vậy bảo vệ Modbus bằng gì?

* không mở Modbus ra internet
* giới hạn trong LAN/VLAN
* firewall: chỉ cho gateway được truy cập
* nếu cần remote: dùng VPN/SSH tunnel (khái niệm)

> Lưu ý: Với Modbus, security chủ yếu là “bảo vệ đường đi”, không phải “bảo vệ giao thức”.

---

## 9. OPC UA security: policy/mode/cert/trust (khái niệm chuẩn)

### 9.1. OPC UA mạnh vì có security layer

OPC UA hỗ trợ:

* security policy (bộ thuật toán)
* message security mode:

  * None
  * Sign
  * SignAndEncrypt
* certificate cho client/server
* trust list

### 9.2. Lỗi hay gặp

* server yêu cầu SignAndEncrypt nhưng client để None
* cert chưa được trust
* endpoint URL/hostname mismatch

> Tip: Khi gặp lỗi OPC UA, luôn kiểm tra 3 thứ: endpoint + policy/mode + trust cert.

---

## 10. Logging an toàn: không rò rỉ secrets

### 10.1. Không log password/token

**Sai**:

* in nguyên `.env`
* log header Authorization

**Đúng**:

* log “đã có token” chứ không log token
* mask secret: `abcd...xyz`

### 10.2. Log dữ liệu điều khiển

Nếu là command nguy hiểm:

* log ai gửi (user/device)
* log requestId
* log kết quả (ack)

> Note: Log tốt giúp audit và truy vết sự cố.

---

## 11. Checklist triển khai tối thiểu (junior-ready)

1. Không commit `.env`, key, cert private
2. MQTT có username/password + ACL tối thiểu
3. Web/Realtime có auth (ít nhất token nội bộ)
4. Không mở port Modbus ra ngoài LAN
5. OPC UA dùng policy/mode phù hợp, quản lý trust cert
6. Service chạy bằng user thường, không root
7. Chỉ mở port cần thiết, document lại port list
8. Log không lộ secrets

> Tip: Checklist này đủ để bạn làm project “không sơ hở” khi demo hoặc chạy nội bộ.

---

## 12. Lỗi thường gặp & cách xử

### 12.1. Lộ secrets lên Git

* sửa ngay:

  * xoá secret khỏi repo
  * rotate (đổi) password/token
  * add `.env` vào `.gitignore`

### 12.2. TLS lỗi trust/hostname

* kiểm tra:

  * cert CA đã trust chưa
  * hostname trong cert có khớp domain không

### 12.3. MQTT bị reject

* sai user/password
* ACL chặn topic

### 12.4. OPC UA connect fail

* mismatch policy/mode
* cert chưa trust

### 12.5. “Mở port rồi mà vẫn không vào”

* firewall
* service bind localhost
* NAT/proxy

---

## (Tuỳ chọn) Bài tập tự luyện

1. Viết `.env.example` cho dự án gateway của bạn (MQTT + WS + DB nếu có).
2. Tạo `.gitignore` để bỏ `.env`, `.venv`, log.
3. Viết threat model 5 dòng cho hệ:

   * PLC/MCU → gateway → web dashboard
4. Lập checklist port:

   * MQTT 1883/8883
   * WS/HTTP 80/443/8000
   * Modbus 502 (nếu dùng)
   * OPC UA 4840 (tuỳ)

> Tip: Khi bạn làm capstone, bạn sẽ dùng nguyên bài này để “dán nhãn” dự án: an toàn tối thiểu + vận hành được.

