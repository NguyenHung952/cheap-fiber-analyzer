
# Cheap Fiber Analyzer 🔬

Dự án thiết bị phân tích sợi quang giá rẻ, sử dụng vi điều khiển **STM32F207VCT6**. Hệ thống tập trung vào việc thu thập tín hiệu tương tự thông qua ADC, cấu hình DAC và truyền dữ liệu đo lường đến máy tính bằng giao tiếp UART.

Dự án được phát triển nhằm nghiên cứu, thử nghiệm và xây dựng nền tảng phần cứng – phần mềm phục vụ việc đo lường và phân tích tín hiệu quang.

## 📌 Giới thiệu

Cheap Fiber Analyzer là một mô hình thử nghiệm thiết bị phân tích sợi quang với bộ điều khiển trung tâm là STM32F207VCT6.

Vi điều khiển thực hiện việc đọc dữ liệu từ các kênh ADC, xử lý và định dạng dữ liệu đo, sau đó truyền kết quả đến máy tính thông qua giao tiếp USART1.

Phần mềm Python được sử dụng để hỗ trợ giao tiếp nối tiếp, kiểm tra dữ liệu và quản lý dữ liệu đo lường.

## ✨ Chức năng chính

- Đọc tín hiệu tương tự từ hai kênh ADC:
  - ADC1 Channel 12
  - ADC1 Channel 13
- Sử dụng ADC độ phân giải 12-bit.
- Cấu hình hai kênh DAC:
  - DAC Channel 1
  - DAC Channel 2
- Truyền dữ liệu qua USART1 UART.
- Tốc độ truyền UART: `115200 baud`.
- Gửi dữ liệu đo lường định kỳ.
- Hỗ trợ công cụ giao tiếp nối tiếp bằng Python.
- Hỗ trợ thành phần cơ sở dữ liệu và giao diện web.
- Cấu hình phần cứng thông qua STM32CubeMX.

## 🛠️ Phần cứng và công nghệ

| Thành phần | Thông tin |
|---|---|
| Vi điều khiển | STM32F207VCT6 |
| ADC | ADC1 |
| Độ phân giải ADC | 12-bit |
| Kênh ADC | Channel 12 và Channel 13 |
| DAC | Channel 1 và Channel 2 |
| Giao tiếp | USART1 UART |
| Tốc độ UART | 115200 baud |
| IDE | STM32CubeIDE |
| Công cụ cấu hình | STM32CubeMX |
| Ngôn ngữ firmware | C |
| Phần mềm máy tính | Python |

## 📁 Cấu trúc thư mục

```text
cheap-fiber-analyzer/
├── Core/
│   ├── Inc/
│   └── Src/
│       ├── main.c
│       ├── stm32f2xx_hal_msp.c
│       ├── stm32f2xx_it.c
│       ├── syscalls.c
│       ├── sysmem.c
│       └── system_stm32f2xx.c
│
├── Drivers/
│   └── Thư viện HAL và CMSIS
│
├── Debug/
│
├── Python/
│   ├── database.py
│   ├── serial_client.py
│   ├── requirements_serial.txt
│   ├── run_serial_test.bat
│   ├── fiber_analyzer.db
│   └── web/
│
├── cheap-fiber-analyzer.ioc
├── STM32F207VCTX_FLASH.ld
├── STM32F207VCTX_RAM.ld
└── README.md
```

## ⚙️ Nguyên lý hoạt động của Firmware

Firmware trên STM32 thực hiện các bước chính:

1. Khởi tạo thư viện HAL.
2. Cấu hình hệ thống clock.
3. Khởi tạo GPIO, ADC, DAC và USART.
4. Bắt đầu quá trình chuyển đổi ADC.
5. Đọc dữ liệu từ ADC Channel 12 và Channel 13.
6. Định dạng dữ liệu đo thành chuỗi ký tự.
7. Truyền dữ liệu qua USART1.
8. Chờ một khoảng thời gian và lặp lại quá trình đo.

### Định dạng dữ liệu UART

Dữ liệu được truyền theo định dạng:

```text
ADC12=<giá trị>;ADC13=<giá trị>;DAC1=0;DAC2=0
```

Ví dụ:

```text
ADC12=2048;ADC13=1560;DAC1=0;DAC2=0
```

Mỗi bản tin được kết thúc bằng `CRLF`.

> **Lưu ý:** Các giá trị DAC trong định dạng hiện tại đang được gán bằng `0`. Chức năng điều khiển DAC và thuật toán phân tích sợi quang có thể cần được phát triển thêm.

## 🐍 Phần mềm Python

Thư mục `Python` chứa các thành phần hỗ trợ giao tiếp giữa máy tính và vi điều khiển.

| Tệp / Thư mục | Chức năng |
|---|---|
| `serial_client.py` | Giao tiếp và kiểm tra dữ liệu qua cổng Serial |
| `database.py` | Các chức năng liên quan đến cơ sở dữ liệu |
| `requirements_serial.txt` | Danh sách thư viện Python cần thiết |
| `run_serial_test.bat` | Tập lệnh chạy kiểm tra Serial trên Windows |
| `web/` | Các thành phần liên quan đến giao diện web |
| `fiber_analyzer.db` | Cơ sở dữ liệu SQLite |

## 🚀 Hướng dẫn cài đặt và sử dụng

### 1. Clone repository

```bash
git clone https://github.com/NguyenHung952/cheap-fiber-analyzer.git
cd cheap-fiber-analyzer
```

### 2. Mở dự án STM32

1. Mở STM32CubeIDE.
2. Chọn **File → Import**.
3. Import dự án vào Workspace.
4. Kiểm tra cấu hình trong tệp `.ioc`.
5. Build dự án.
6. Kết nối bo mạch STM32 với máy tính.
7. Nạp firmware vào vi điều khiển.

### 3. Cấu hình giao tiếp UART

Sử dụng phần mềm Serial Terminal hoặc công cụ Python với thông số:

| Thông số | Giá trị |
|---|---|
| Baud rate | 115200 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |

> Tên cổng COM phụ thuộc vào thiết bị chuyển đổi USB-UART và cấu hình máy tính.

### 4. Cài đặt thư viện Python

Mở Terminal trong thư mục `Python`:

```bash
cd Python
pip install -r requirements_serial.txt
```

### 5. Chạy chương trình kiểm tra Serial

Trên Windows:

```bash
run_serial_test.bat
```

Hoặc chạy trực tiếp bằng Python:

```bash
python serial_client.py
```

> Kiểm tra và thiết lập đúng tên cổng COM trong chương trình Python trước khi chạy.

## 🔬 Trạng thái phát triển

Dự án hiện đang được phát triển theo hướng xây dựng mô hình thử nghiệm thiết bị phân tích sợi quang giá rẻ.

### Phạm vi hiện tại

- [x] Cấu hình vi điều khiển STM32F207VCT6.
- [x] Cấu hình ADC và đọc dữ liệu từ hai kênh.
- [x] Cấu hình DAC.
- [x] Truyền dữ liệu đo qua UART.
- [x] Xây dựng công cụ giao tiếp Serial bằng Python.
- [x] Thành phần cơ sở dữ liệu và web ở mức phát triển.

### Định hướng phát triển

- [ ] Hoàn thiện thuật toán phân tích tín hiệu sợi quang.
- [ ] Phát triển chức năng điều khiển đầu ra DAC.
- [ ] Hiệu chuẩn hệ thống đo lường.
- [ ] Bổ sung bộ lọc và xử lý nhiễu tín hiệu.
- [ ] Cải thiện khả năng hiển thị dữ liệu theo thời gian thực.
- [ ] Bổ sung chức năng xuất dữ liệu đo.
- [ ] Hoàn thiện tài liệu kết nối phần cứng.
- [ ] Bổ sung quy trình kiểm thử và đánh giá kết quả.

## ⚠️ Lưu ý

- Kiểm tra kết nối phần cứng trước khi cấp nguồn.
- Đảm bảo điện áp đầu vào ADC nằm trong phạm vi cho phép.
- Sử dụng đúng cổng UART và thông số giao tiếp.
- Dự án hiện đang ở giai đoạn thử nghiệm.
- Cần thực hiện hiệu chuẩn và kiểm thử trước khi sử dụng kết quả cho các phép đo sợi quang chính xác.

## 📄 Giấy phép

Hiện tại, dự án chưa quy định giấy phép riêng.

Một số tệp mã nguồn được tạo bởi STM32CubeIDE có thể chứa thông tin giấy phép của STMicroelectronics. Hãy kiểm tra phần thông báo bản quyền trong từng tệp trước khi phân phối lại dự án.

## 👤 Tác giả

**NguyenHung952**

GitHub: https://github.com/NguyenHung952

## 🔗 Repository

https://github.com/NguyenHung952/cheap-fiber-analyzer
