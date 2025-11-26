# config.py

WINDOW_TITLE = "Facebook Auto Report Tool - Ultimate Version"
WINDOW_SIZE = "1100x700"
LOG_FILE = "report_logs.csv"

# --- CẤU TRÚC DỮ LIỆU BÁO CÁO (Mapping từ yêu cầu của bạn) ---
# Dictionary lồng nhau: Hạng mục -> Chi tiết -> (Logic ẩn)

REPORT_DATA = {
    "Vấn đề liên quan đến người dưới 18 tuổi": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Có vẻ giống hành vi bóc lột tình dục",
        "Chia sẻ ảnh khỏa thân của ai đó",
        "Bắt nạt hoặc quấy rối",
        "Ngược đãi thể chất"
    ],
    "Bắt nạt, quấy rối hoặc lăng mạ/lạm dụng/ngược đãi": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Có vẻ giống hành vi bóc lột tình dục",
        "Có vẻ giống hành vi buôn người",
        "Bắt nạt hoặc quấy rối"
    ],
    "Tự tử hoặc tự hại bản thân": [
        "Tự tử hoặc tự gây thương tích",
        "Chứng rối loạn ăn uống"
    ],
    "Nội dung mang tính bạo lực, thù ghét hoặc gây phiền toái": [
        "Mối đe dọa về an toàn có thể xảy ra",
        "Có vẻ giống hành vi khủng bố",
        "Kêu gọi hành vi bạo lực",
        "Có vẻ giống tội phạm có tổ chức",
        "Cổ xúy hành vi thù ghét",
        "Thể hiện hành vi bạo lực, tử vong hoặc thương tích nghiêm trọng",
        "Ngược đãi động vật"
    ],
    "Bán hoặc quảng cáo mặt hàng bị hạn chế": [
        "Chất cấm, chất gây nghiện",
        "Vũ khí",
        "Động vật"
    ],
    "Nội dung người lớn": [
        "Đe dọa chia sẻ hình ảnh khỏa thân của tôi",
        "Có vẻ giống hành vi mại dâm",
        "Hình ảnh khỏa thân của tôi đã bị chia sẻ",
        "Có vẻ giống hành vi bóc lột tình dục",
        "Ảnh khỏa thân hoặc hoạt động tình dục"
    ],
    "Thông tin sai sự thật, lừa đảo hoặc gian lận": [
        "Gian lận hoặc lừa đảo",
        "Chia sẻ thông tin sai sự thật",
        "Spam"
    ],
    "Trang giả": [
        "Tôi",
        "Một người bạn",
        "Một người nổi tiếng hoặc người của công chúng",
        "Một doanh nghiệp",
        "Tài khoản này không phải là của người thật"
    ]
}

# Danh sách hạng mục cấp 1 để hiển thị lên UI
CATEGORIES = list(REPORT_DATA.keys())