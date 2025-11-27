# config.py
# Cấu hình ứng dụng Facebook Auto Report Tool

WINDOW_TITLE = "Facebook Auto Report Tool - Ultimate Version"
WINDOW_SIZE = "1100x700"
LOG_FILE = "report_logs.csv"

# --- CẤU TRÚC DỮ LIỆU BÁO CÁO (Mapping từ yêu cầu của bạn) ---
# Dictionary lồng nhau: Hạng mục -> Chi tiết -> (Logic ẩn)
# 
# Quy trình báo cáo Facebook:
# 1. Người dùng click nút 3 chấm "..." trên bài viết hoặc Trang
# 2. Chọn "Báo cáo bài viết" hoặc "Báo cáo Trang"
# 3. Chọn hạng mục chính (Category - Cấp 1)
# 4. Chọn chi tiết hành vi (Detail - Cấp 2)
# 5. Click "Tiếp" / "Gửi" để hoàn tất

# =============================================================================
# DỮ LIỆU BÁO CÁO BÀI VIẾT (Post Report)
# =============================================================================
# Các hạng mục này xuất hiện khi báo cáo một bài viết cụ thể
# Popup: "Tại sao bạn báo cáo bài viết này?"

REPORT_DATA = {
    # --- Bảo vệ trẻ em ---
    "Vấn đề liên quan đến người dưới 18 tuổi": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Có vẻ giống hành vi bóc lột tình dục",
        "Chia sẻ ảnh khỏa thân của ai đó",
        "Bắt nạt hoặc quấy rối",
        "Ngược đãi thể chất"
    ],
    
    # --- Bắt nạt & Quấy rối ---
    "Bắt nạt, quấy rối hoặc lăng mạ/lạm dụng/ngược đãi": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Có vẻ giống hành vi bóc lột tình dục",
        "Có vẻ giống hành vi buôn người",
        "Bắt nạt hoặc quấy rối"
    ],
    
    # --- Tự tử & Tự hại ---
    "Tự tử hoặc tự hại bản thân": [
        "Tự tử hoặc tự gây thương tích",
        "Chứng rối loạn ăn uống"
    ],
    
    # --- Bạo lực & Thù ghét ---
    "Nội dung mang tính bạo lực, thù ghét hoặc gây phiền toái": [
        "Mối đe dọa về an toàn có thể xảy ra",
        "Có vẻ giống hành vi khủng bố",
        "Kêu gọi hành vi bạo lực",
        "Có vẻ giống tội phạm có tổ chức",
        "Cổ xúy hành vi thù ghét",
        "Thể hiện hành vi bạo lực, tử vong hoặc thương tích nghiêm trọng",
        "Ngược đãi động vật"
    ],
    
    # --- Mặt hàng bị hạn chế ---
    "Bán hoặc quảng cáo mặt hàng bị hạn chế": [
        "Chất cấm, chất gây nghiện",
        "Vũ khí",
        "Động vật"
    ],
    
    # --- Nội dung người lớn ---
    "Nội dung người lớn": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Có vẻ giống hành vi mại dâm",
        "Hình ảnh khỏa thân của tôi đã bị chia sẻ",
        "Có vẻ giống hành vi bóc lột tình dục",
        "Ảnh khỏa thân hoặc hoạt động tình dục"
    ],
    
    # --- Lừa đảo & Gian lận ---
    "Thông tin sai sự thật, lừa đảo hoặc gian lận": [
        "Gian lận hoặc lừa đảo",
        "Chia sẻ thông tin sai sự thật",
        "Spam"
    ],
    
    # --- Quyền sở hữu trí tuệ ---
    "Quyền sở hữu trí tuệ": [
        "Vi phạm bản quyền",
        "Vi phạm thương hiệu",
        "Sử dụng logo/hình ảnh trái phép"
    ],
    
    # --- Không muốn xem ---
    "Tôi không muốn xem nội dung này": [
        "Ẩn bài viết",
        "Bỏ theo dõi trang/người đăng",
        "Giới hạn nội dung tương tự"
    ],
    
    # --- Trang giả mạo (dùng cho báo cáo Trang) ---
    "Trang giả": [
        "Tôi",
        "Một người bạn",
        "Một người nổi tiếng hoặc người của công chúng",
        "Một doanh nghiệp",
        "Tài khoản này không phải là của người thật"
    ]
}

# =============================================================================
# DỮ LIỆU BÁO CÁO TRANG (Page Report)
# =============================================================================
# Các hạng mục này xuất hiện khi báo cáo một Trang Facebook
# Popup: "Bạn muốn báo cáo điều gì?" -> "Thông tin về trang này"
#
# Quy trình báo cáo Trang:
# 1. Vào trang (Page) cần báo cáo
# 2. Bấm nút 3 chấm "..." cạnh nút "Tin nhắn", "Theo dõi"
# 3. Chọn "Báo cáo Trang"
# 4. Popup hiện: "Bạn muốn báo cáo điều gì?"
#    - "Thông tin về trang này" -> Tiếp tục chọn lý do bên dưới
#    - "Bài viết cụ thể" -> Dẫn đến luồng báo cáo bài viết

PAGE_REPORT_DATA = {
    # --- Trang giả mạo ---
    "Trang giả mạo": [
        "Tôi",                                              # Giả mạo chính bạn
        "Một người bạn",                                     # Giả mạo bạn bè
        "Một người nổi tiếng hoặc người của công chúng",     # Giả mạo người nổi tiếng
        "Một doanh nghiệp",                                  # Giả mạo doanh nghiệp/tổ chức
        "Tài khoản này không phải là của người thật"         # Bot, fake account
    ],
    
    # --- Lừa đảo & Spam ---
    "Chia sẻ nội dung lừa đảo, spam": [
        "Spam",
        "Nội dung gây hiểu nhầm",
        "Lừa đảo tài chính",
        "Phishing"
    ],
    
    # --- Hàng cấm ---
    "Bán hàng cấm / dịch vụ trái chính sách": [
        "Chất cấm, ma túy",
        "Vũ khí",
        "Động vật hoang dã",
        "Dịch vụ bất hợp pháp"
    ],
    
    # --- Thù ghét & Bạo lực ---
    "Nội dung thù ghét, kích động bạo lực": [
        "Ngôn từ thù ghét",
        "Kích động bạo lực",
        "Phân biệt đối xử",
        "Đe dọa"
    ],
    
    # --- Sở hữu trí tuệ ---
    "Vi phạm quyền sở hữu trí tuệ": [
        "Sử dụng logo/thương hiệu trái phép",
        "Vi phạm bản quyền",
        "Sao chép nội dung"
    ],
    
    # --- Khác ---
    "Khác": [
        "Vi phạm khác",
        "Không thuộc danh mục nào ở trên"
    ]
}

# =============================================================================
# DANH SÁCH HẠNG MỤC CHO UI
# =============================================================================

# Hạng mục cấp 1 cho báo cáo bài viết
CATEGORIES = list(REPORT_DATA.keys())

# Hạng mục cấp 1 cho báo cáo Trang
PAGE_CATEGORIES = list(PAGE_REPORT_DATA.keys())

# =============================================================================
# CÁC TỪ KHÓA ĐỂ TÌM KIẾM ELEMENT TRÊN GIAO DIỆN FACEBOOK
# =============================================================================

# Các từ khóa cho nút 3 chấm
THREE_DOTS_VARIANTS = [
    "Hành động với bài viết này",
    "Actions for this post",
    "More",
    "Xem thêm tùy chọn",
    "More options",
    "Options",
    "Tùy chọn",
    "Thêm"
]

# Các từ khóa cho nút Báo cáo
REPORT_BUTTON_TEXTS = [
    "Báo cáo",
    "Report",
    "Tìm hỗ trợ",
    "Find support",
    "Báo cáo bài viết",
    "Report post",
    "Báo cáo Trang",
    "Report Page"
]

# Các từ khóa cho nút Tiếp/Gửi
NEXT_BUTTON_TEXTS = [
    "Tiếp",
    "Next",
    "Gửi",
    "Submit",
    "Xong",
    "Done"
]

# Các lựa chọn khi báo cáo Trang
PAGE_REPORT_OPTIONS = [
    "Thông tin về trang này",
    "Information about this Page",
    "Bài viết cụ thể",
    "A specific post"
]