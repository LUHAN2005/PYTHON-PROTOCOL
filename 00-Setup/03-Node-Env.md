# BÀI 3 : NODE ENV – CÀI ĐẶT, NPM, CẤU TRÚC PROJECT, CHẠY SOCKET.IO/WEB (JavaScript)

## Mục lục

1. [Node env là gì?](#1-node-env-là-gì)
2. [Cài Node.js & kiểm tra version](#2-cài-nodejs--kiểm-tra-version)
3. [npm là gì? `package.json` là gì?](#3-npm-là-gì-packagejson-là-gì)
4. [Khởi tạo project Node chuẩn](#4-khởi-tạo-project-node-chuẩn)
5. [Cài/gỡ/kiểm tra thư viện (npm)](#5-càigỡkiểm-tra-thư-viện-npm)
6. [Scripts: `npm run` (cách chạy project như dân chuyên)](#6-scripts-npm-run-cách-chạy-project-như-dân-chuyên)
7. [ESM vs CommonJS (import/export)](#7-esm-vs-commonjs-importexport)
8. [Node env cho WebSocket/Socket.IO (bộ tối thiểu)](#8-node-env-cho-websocketsocketio-bộ-tối-thiểu)
9. [Dev tools: nodemon, eslint/prettier (junior-ready)](#9-dev-tools-nodemon-eslintprettier-junior-ready)
10. [Lỗi thường gặp & cách xử](#10-lỗi-thường-gặp--cách-xử)
11. [(Tuỳ chọn) Bài tập tự luyện](#tuỳ-chọn-bài-tập-tự-luyện)

---

## 1. Node env là gì?

**Node env** là môi trường để chạy JavaScript **ngoài trình duyệt**.

* Trong browser: JS chạy để làm UI (DOM, fetch, WebSocket client…)
* Trong Node: JS chạy để làm **server**, tool, test client, dev server…

Trong lộ trình IoT/automation của bạn, Node env giúp bạn:

* chạy **Socket.IO server/client** nhanh
* chạy **web dashboard** (frontend) để xem dữ liệu realtime
* debug gateway Python ↔ web (tách lỗi client/server dễ hơn)

> Lưu ý: WebSocket/Socket.IO học bằng JS rất “đúng bài” vì browser là môi trường tự nhiên của realtime web.

---

## 2. Cài Node.js & kiểm tra version

### 2.1. Kiểm tra đã có Node chưa

Mở terminal và chạy:

```bash
node -v
npm -v
```

* `node -v` trả về version (ví dụ `v20.x.x`)
* `npm -v` trả về version npm

### 2.2. Nên dùng Node version nào?

* Khuyên dùng **Node LTS** (ổn định, ít lỗi)
* Tránh dùng bản quá cũ (dễ lỗi với socket.io/ESM)

> Tip: Khi làm dự án nghiêm túc, bạn nên “pin” Node version (bằng `.nvmrc` hoặc ghi rõ trong README).

---

## 3. npm là gì? `package.json` là gì?

### 3.1. npm là gì?

**npm** là package manager của Node (tương tự pip của Python).

Nó giúp bạn:

* cài thư viện (`npm i socket.io`)
* quản lý dependency
* chạy script (`npm run dev`)

### 3.2. `package.json` là gì?

`package.json` là file mô tả project, thường có:

* `name`, `version`
* `scripts`: các lệnh chạy nhanh
* `dependencies`: thư viện chạy thật
* `devDependencies`: thư viện dev (nodemon, eslint…)

Ví dụ (rút gọn):

```json
{
  "name": "realtime-lab",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "node server.js",
    "start": "node server.js"
  },
  "dependencies": {
    "socket.io": "^4.7.5"
  }
}
```

> Lưu ý: `type: "module"` giúp bạn dùng `import` thay vì `require`.

---

## 4. Khởi tạo project Node chuẩn

### 4.1. Tạo thư mục project

```bash
mkdir Realtime-Lab
cd Realtime-Lab
```

### 4.2. Khởi tạo `package.json`

```bash
npm init -y
```

### 4.3. Cấu trúc thư mục gợi ý (học realtime)

```
Realtime-Lab/
├─ package.json
├─ server/
│  └─ server.js
└─ client/
   └─ index.html
```

> Tip: Chia `server/` và `client/` từ đầu giúp bạn đỡ rối khi nối Python ↔ web.

---

## 5. Cài/gỡ/kiểm tra thư viện (npm)

### 5.1. Cài thư viện

```bash
npm install socket.io
```

### 5.2. Cài thư viện dev (chỉ dùng lúc dev)

```bash
npm install -D nodemon
```

### 5.3. Gỡ thư viện

```bash
npm uninstall socket.io
```

### 5.4. Xem danh sách thư viện

```bash
npm list
```

> Lưu ý: npm cài thư viện vào `node_modules/` (khác Python là cài vào venv).

---

## 6. Scripts: `npm run` (cách chạy project như dân chuyên)

### 6.1. Vì sao nên dùng scripts?

Thay vì nhớ lệnh dài, bạn chỉ cần:

```bash
npm run dev
```

### 6.2. Ví dụ scripts thường dùng

Trong `package.json`:

```json
{
  "scripts": {
    "dev": "nodemon server/server.js",
    "start": "node server/server.js"
  }
}
```

Chạy:

```bash
npm run dev
npm start
```

> Tip: Dev dùng `dev` (auto reload), prod dùng `start`.

---

## 7. ESM vs CommonJS (import/export)

### 7.1. CommonJS (cũ, nhưng nhiều project còn dùng)

```js
const http = require('http')
module.exports = { ... }
```

### 7.2. ESM (hiện đại, khuyên dùng)

```js
import http from 'http'
export function x() {}
```

### 7.3. Chọn 1 kiểu để khỏi rối

* Nếu bạn học mới: **ESM**
* Bật ESM bằng cách thêm vào `package.json`:

```json
{ "type": "module" }
```

> Lưu ý: Socket.IO docs thường có ví dụ cả 2 kiểu. Bạn cứ thống nhất 1 kiểu là ổn.

---

## 8. Node env cho WebSocket/Socket.IO (bộ tối thiểu)

### 8.1. Bộ thư viện tối thiểu

* Socket.IO server:

```bash
npm i socket.io
```

* Socket.IO client (nếu bạn test bằng Node, không dùng browser):

```bash
npm i socket.io-client
```

### 8.2. Vì sao Socket.IO cần Node env?

Socket.IO thường dùng để:

* tạo server realtime
* quản lý event/rooms/ack
* fallback transport (tuỳ cấu hình)

Browser vẫn dùng được, nhưng Node env giúp bạn làm server/test tool nhanh.

---

## 9. Dev tools: nodemon, eslint/prettier (junior-ready)

### 9.1. nodemon (auto reload)

Cài:

```bash
npm i -D nodemon
```

Scripts:

```json
{
  "scripts": {
    "dev": "nodemon server/server.js"
  }
}
```

### 9.2. eslint/prettier (tuỳ)

* eslint: bắt lỗi code
* prettier: format code

> Note: Với lộ trình protocol, bạn có thể để sau. Quan trọng nhất là chạy được realtime và debug được.

---

## 10. Lỗi thường gặp & cách xử

### 10.1. `node` không nhận lệnh

* Node chưa cài hoặc PATH chưa đúng
* Check:

```bash
node -v
```

### 10.2. `npm` lỗi quyền (Windows)

* chạy terminal bằng quyền user thường
* tránh cài global linh tinh

### 10.3. Port đã bị chiếm (EADDRINUSE)

* đổi port hoặc tắt process đang dùng port
* Linux:

```bash
sudo ss -tulpn
```

* Windows:

```bash
netstat -ano
```

### 10.4. ESM/CJS bị lỗi import

* Bạn dùng `import` nhưng chưa bật `"type": "module"`
* Hoặc file `.cjs/.mjs` không đúng

> Tip: Mới học thì bật ESM ngay từ đầu để đồng bộ.

---

## (Tuỳ chọn) Bài tập tự luyện

1. Tạo project `Realtime-Lab`, chạy được:

   * `node -v`, `npm -v`
   * `npm init -y`

2. Cài `socket.io` và tạo script `dev` trong `package.json`.

3. Tạo 2 thư mục `server/` và `client/`, viết README 2 dòng mô tả.

4. (Nâng cấp) Cài `socket.io-client` và viết 1 file Node client kết nối vào server (chỉ cần connect + log).

> Tip: Xong bài này là bạn đủ nền để học WebSocket/Socket.IO bài thật (events/rooms/ack) và nối Python gateway vào sau.

