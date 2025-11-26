# config.py

WINDOW_TITLE = "Facebook Report Helper Tool"
WINDOW_SIZE = "900x600"
LOG_FILE = "report_logs.csv"

# Các danh sách lựa chọn cho ComboBox
CATEGORIES = [
    "Nội dung người lớn",
    "Bạo lực / Thù ghét",
    "Lừa đảo / Gian lận",
    "Quấy rối / Bắt nạt",
    "Bán hàng cấm",
    "Thông tin sai sự thật",
    "Trang giả",
    "Tự tử hoặc tự hại bản thân",
    "Khác..."
]

# Mặc định dùng cho những lựa chọn chung
BEHAVIORS = [
    "Spam",
    "Giả mạo",
    "Ngôn từ thù ghét",
    "Hình ảnh khỏa thân",
    "Bạo lực đẫm máu",
    "Khủng bố",
    "Quấy rối tôi",
    "Quấy rối người khác",
    "Link phishing/độc hại",
    "Khác..."
]

# Mapping từ Hạng mục -> danh sách Chi tiết hành vi tương ứng
# Dựa trên các lựa chọn chi tiết mà bạn cung cấp trong cấu trúc JSON trước đó.
CATEGORY_REASONS = {
    "Nội dung người lớn": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Hình ảnh khỏa thân của tôi đã bị chia sẻ",
        "Ảnh khỏa thân hoặc hoạt động tình dục",
        "Có vẻ giống hành vi mại dâm",
        "Có vẻ giống hành vi bóc lột tình dục"
    ],
    "Bạo lực / Thù ghét": [
        "Mối đe dọa về an toàn có thể xảy ra",
        "Có vẻ giống hành vi khủng bố",
        "Kêu gọi hành vi bạo lực",
        "Có vẻ giống tội phạm có tổ chức",
        "Cổ xúy hành vi thù ghét",
        "Thể hiện hành vi bạo lực, tử vong hoặc thương tích nghiêm trọng",
        "Ngược đãi động vật"
    ],
    "Lừa đảo / Gian lận": [
        "Gian lận hoặc lừa đảo",
        "Link phishing/độc hại",
        "Chia sẻ thông tin sai sự thật",
        "Spam"
    ],
    "Quấy rối / Bắt nạt": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Có vẻ giống hành vi bóc lột tình dục",
        "Có vẻ giống hành vi buôn người",
        "Bắt nạt hoặc quấy rối",
        "Ngược đãi thể chất"
    ],
    "Bán hàng cấm": [
        "Chất cấm, chất gây nghiện",
        "Vũ khí",
        "Động vật"
    ],
    "Thông tin sai sự thật": [
        "Chia sẻ thông tin sai sự thật",
        "Gian lận hoặc lừa đảo",
        "Spam"
    ],
    "Trang giả": [
        "Tôi",
        "Một người bạn",
        "Một người nổi tiếng hoặc người của công chúng",
        "Một doanh nghiệp",
        "Tài khoản này không phải là của người thật"
    ],
    "Tự tử hoặc tự hại bản thân": [
        "Tự tử hoặc tự gây thương tích",
        "Chứng rối loạn ăn uống"
    ],
    # "Khác..." để mặc định dùng BEHAVIORS
}