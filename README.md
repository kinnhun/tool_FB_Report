# Facebook Auto Report Tool

Công cụ hỗ trợ tự động hóa quy trình báo cáo bài viết và Trang Facebook.

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Quy trình báo cáo bài viết](#1-báo-cáo-bài-viết-cụ-thể)
- [Quy trình báo cáo Trang](#2-báo-cáo-trang-page)
- [Thao tác xử lý sau khi báo cáo](#3-thao-tác-xử-lý-sau-khi-báo-cáo)
- [Cài đặt và sử dụng](#cài-đặt-và-sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)

---

## Giới thiệu

Đây là hệ thống **"Báo cáo" (Report)** của Facebook cho **Trang** và **bài viết cụ thể**. Tài liệu này giúp bạn nắm rõ luồng thao tác và logic của Facebook để có thể sử dụng tool một cách hiệu quả.

---

## 1. Báo cáo bài viết cụ thể

### Cách mở màn hình báo cáo bài viết

**Trên giao diện web (máy tính):**

1. Tới bài viết cần báo cáo.
2. Bấm nút **ba chấm "…"** ở góc trên bên phải post.
3. Chọn **"Tìm hỗ trợ hoặc báo cáo bài viết"** (hoặc "Báo cáo bài viết").
4. Hiện ra popup: **"Tại sao bạn báo cáo bài viết này?"**.

**Trên app điện thoại:** thao tác tương tự: chạm `…` → `Tìm hỗ trợ hoặc báo cáo bài viết`.

### Các nhóm lý do chính trong popup "Tại sao bạn báo cáo bài viết này?"

| Hạng mục | Mô tả |
|----------|-------|
| **Vấn đề liên quan đến người dưới 18 tuổi** | Bảo vệ trẻ em, chống lạm dụng |
| **Bắt nạt, quấy rối hoặc lăng mạ/lạm dụng/ngược đãi** | Hành vi bắt nạt, quấy rối trực tuyến |
| **Tự tử hoặc tự hại bản thân** | Nội dung liên quan đến tự tử, tự gây thương tích |
| **Nội dung mang tính bạo lực, thù ghét hoặc gây phiền toái** | Bạo lực, ngôn từ thù ghét, kích động |
| **Bán hoặc quảng cáo mặt hàng bị hạn chế** | Ma túy, vũ khí, hàng cấm |
| **Nội dung người lớn** | Ảnh/clip 18+, khỏa thân, khiêu dâm |
| **Thông tin sai sự thật, lừa đảo hoặc gian lận** | Scam, giả mạo, phishing |
| **Quyền sở hữu trí tuệ** | Vi phạm bản quyền, thương hiệu |
| **Tôi không muốn xem nội dung này** | Ẩn, giảm hiển thị |

### Sau khi chọn một lý do

Thường sẽ có **bước con** chi tiết hơn:

- **Ví dụ chọn "Bạo lực / thù ghét"** → nó hỏi chi tiết:
  - Bạo lực đẫm máu
  - Ngôn từ thù ghét
  - Đe dọa, kích động, v.v.

- **Hoặc chọn "Tôi không muốn xem"** → nó gợi ý:
  - Ẩn bài viết
  - Bỏ theo dõi trang/người đăng
  - Thêm tùy chọn giới hạn

Cuối màn sẽ có nút **"Tiếp" / "Gửi"** để xác nhận báo cáo. Bài viết sẽ được đưa vào hàng chờ để đội ngũ Facebook kiểm tra.

Bạn có thể theo dõi trạng thái trong **Hộp thư hỗ trợ (Support Inbox)** của tài khoản.

---

## 2. Báo cáo Trang (Page)

### Cách mở màn hình báo cáo Trang

1. Vào trang (Page) cần báo cáo.
2. Trên giao diện web: bấm nút **ba chấm "…"** ngay cạnh nút `Tin nhắn`, `Theo dõi`…
3. Chọn **"Báo cáo Trang"**.
4. Facebook hiện popup **"Bạn muốn báo cáo điều gì?"** với 2 lựa chọn:
   - **Thông tin về trang này**
   - **Bài viết cụ thể**

### Nếu chọn "Bài viết cụ thể"

Sẽ dẫn bạn quay lại luồng báo cáo post như phần 1.

### Nếu chọn "Thông tin về trang này"

Bước tiếp theo là chọn lý do:

| Lý do | Mô tả |
|-------|-------|
| **Trang giả mạo** | Giả mạo người/tổ chức khác (fake page, mạo danh) |
| **Chia sẻ nội dung lừa đảo, spam** | Spam, gây hiểu nhầm |
| **Bán hàng cấm / dịch vụ trái chính sách** | Sản phẩm, dịch vụ bị cấm |
| **Nội dung thù ghét, kích động bạo lực** | Ngôn từ thù ghét, kích động |
| **Vi phạm quyền sở hữu trí tuệ** | Dùng logo/thương hiệu trái phép |
| **Khác** | Các trường hợp khác |

### Chi tiết cho lý do "Trang giả mạo"

Khi chọn **"Trang giả"**, Facebook sẽ hỏi trang đang giả mạo ai:

- **Tôi** - Trang giả mạo chính bạn
- **Một người bạn** - Giả mạo bạn bè của bạn
- **Một người nổi tiếng hoặc người của công chúng** - Giả mạo người nổi tiếng
- **Một doanh nghiệp** - Giả mạo doanh nghiệp/tổ chức
- **Tài khoản này không phải là của người thật** - Bot, fake account

Cuối cùng, bấm **"Tiếp" / "Gửi"** để hoàn tất.

---

## 3. Thao tác xử lý sau khi báo cáo

Có 2 lớp xử lý:

### 3.1. Tạm thời cho chính bạn

Ngay trong luồng báo cáo, Facebook thường gợi ý vài hành động **tự bảo vệ** mà không cần chờ họ duyệt:

- **Ẩn bài viết** khỏi News Feed
- **Bỏ theo dõi** trang/người đăng (không hủy kết bạn nhưng không còn thấy bài)
- **Chặn** (block) trang/người dùng
- **Báo cáo – đồng thời chặn** (vừa gửi report, vừa chặn luôn)

> ⚡ Đây là những thao tác **100% thực hiện ngay lập tức** trên tài khoản bạn.

### 3.2. Xử lý phía Facebook

Sau khi bạn bấm gửi:

1. **Tự động lọc (Machine Learning)**: Hệ thống kiểm tra xem case có giống pattern vi phạm rõ rệt không (nội dung 18+, bạo lực cực nặng…)

2. **Moderator người thật**: Nếu nghiêm trọng/khó phân loại, case sẽ được chuyển cho moderator xem

3. **Kết quả có thể là:**
   - ❌ Không làm gì (nếu họ kết luận "không vi phạm")
   - ⚠️ Gỡ bài viết, giảm phân phối, gắn nhãn cảnh báo
   - 🚫 Hạn chế tính năng của tài khoản/trang (cấm đăng, giảm reach)
   - 🔒 Khóa tài khoản/trang trong trường hợp nghiêm trọng

4. **Thông báo kết quả**: Bạn sẽ thấy thông báo trong **Hộp thư hỗ trợ** hoặc notification

---

## Cài đặt và sử dụng

### Yêu cầu hệ thống

- Python 3.7+
- Google Chrome (hoặc Chromium)
- Các thư viện Python:
  - `selenium`
  - `webdriver-manager`
  - `tkinter` (thường đã có sẵn với Python)

### Cài đặt

```bash
# Clone repository
git clone https://github.com/kinnhun/tool_FB_Report.git
cd tool_FB_Report/FBReportHelper

# Cài đặt dependencies
pip install selenium webdriver-manager
```

### Chạy ứng dụng

```bash
python main.py
```

### Hướng dẫn sử dụng

1. **Khởi động trình duyệt**: Bấm nút "KHỞI ĐỘNG BROWSER"
2. **Cấu hình Proxy** (tùy chọn): Nhập proxy theo định dạng `IP:Port` hoặc `User:Pass@IP:Port`
3. **Inject Cookie**: Paste cookie Facebook vào ô Cookie để đăng nhập tự động
4. **Nhập URL**: Điền link bài viết hoặc Trang cần báo cáo
5. **Chọn hạng mục**: Chọn loại vi phạm từ dropdown
6. **Chọn chi tiết**: Chọn chi tiết hành vi vi phạm
7. **Chạy báo cáo**: Bấm "CHẠY AUTO REPORT"

---

## Cấu trúc dự án

```
FBReportHelper/
├── main.py          # Entry point - khởi chạy ứng dụng
├── ui.py            # Giao diện người dùng (Tkinter)
├── browser.py       # Quản lý trình duyệt và automation (Selenium)
├── config.py        # Cấu hình và dữ liệu báo cáo
├── logger.py        # Ghi log các báo cáo
└── report_logs.csv  # File log lịch sử báo cáo
```

### Mô tả các module

| File | Chức năng |
|------|-----------|
| `main.py` | Khởi tạo ứng dụng Tkinter |
| `ui.py` | Xử lý giao diện, event handlers |
| `browser.py` | Selenium WebDriver, tự động click/điền form |
| `config.py` | Định nghĩa hạng mục và chi tiết báo cáo |
| `logger.py` | Ghi log CSV cho từng lần báo cáo |

---

## Luồng hoạt động của Tool

```
┌─────────────────┐
│   Khởi động     │
│   Browser       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Inject Cookie  │
│  (Đăng nhập)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Navigate đến   │
│  URL cần report │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tìm & Click    │
│  nút 3 chấm     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Click "Báo cáo"│
│  hoặc "Report"  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Chọn Hạng mục  │
│  (Category)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Click "Tiếp"   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Chọn Chi tiết  │
│  (Detail)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Click "Gửi"    │
│  Hoàn tất       │
└────────┴────────┘
```

---

## Lưu ý quan trọng

⚠️ **Disclaimer**: Tool này chỉ dùng cho mục đích học tập và nghiên cứu. Vui lòng sử dụng có trách nhiệm và tuân thủ các điều khoản dịch vụ của Facebook.

- Không lạm dụng để báo cáo sai sự thật
- Sử dụng proxy để tránh bị phát hiện và hạn chế tài khoản
- Cookie có thể hết hạn hoặc bị checkpoint

---

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo Pull Request hoặc Issue để thảo luận.

## License

MIT License
