# Cheap Fiber Analyzer - Web Dashboard V1

Bộ Web Dashboard khung cho project `cheap-fiber-analyzer`.

## Cấu trúc

```text
Python/
├── database.py
└── web/
    ├── app.py
    ├── requirements_web.txt
    ├── run_web.bat
    ├── README_WEB.md
    ├── templates/
    │   └── index.html
    └── static/
        ├── app.js
        └── style.css
```

## Kiến trúc

```text
STM32
  ↓
Serial / RS485
  ↓
Python Client
  ↓
SQLite
  ↓
Flask Web
  ↓
Browser
```

V1 chỉ dựng Web + lớp SQLite. Protocol USART3/RS485 của STM32 chưa được cố định nên
`serial_client.py` chưa được đưa vào xử lý dữ liệu thật ở bản này.

## Chạy Web

Tại thư mục project:

```cmd
py -m pip install -r Python\web\requirements_web.txt
Python\web\run_web.bat
```

Hoặc:

```cmd
cd Python\web
py -m pip install -r requirements_web.txt
py app.py
```

Mở:

```text
http://127.0.0.1:5000
```

Database runtime sẽ được tạo tại:

```text
Python\fiber_analyzer.db
```

## API hiện có

- `GET /api/status`
- `GET /api/events?limit=20`
- `GET /api/health`

Web hiện chưa tự quyết định dữ liệu đo. Khi nối STM32 thật, Python client sẽ là nơi
nhận dữ liệu và ghi SQLite.
