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
        {"Cổ xúy hành vi thù ghét": [
            "Nội dung này bắt nguồn từ nhóm thù ghét có tổ chức",
            "Đăng ngôn từ gây thù ghét"
        ]},
        "Thể hiện hành vi bạo lực, tử vong hoặc thương tích nghiêm trọng",
        "Ngược đãi động vật"
    ],
    "Bán hoặc quảng cáo mặt hàng bị hạn chế": [
        {"Chất cấm, chất gây nghiện": [
            "Các loại chất cấm, chất gây nghiện nặng như cocaine, heroin hoặc fentanyl",
            "Các loại chất cấm, chất gây nghiện khác"
        ]},
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

# Mapping Vietnamese -> English
TRANSLATIONS = {
    # Categories
    "Vấn đề liên quan đến người dưới 18 tuổi": "Problem involving someone under 18",
    "Bắt nạt, quấy rối hoặc lăng mạ/lạm dụng/ngược đãi": "Bullying, harassment or abuse",
    "Tự tử hoặc tự hại bản thân": "Suicide or self-harm",
    "Nội dung mang tính bạo lực, thù ghét hoặc gây phiền toái": "Violent, hateful or disturbing content",
    "Bán hoặc quảng cáo mặt hàng bị hạn chế": "Selling or promoting restricted items",
    "Nội dung người lớn": "Adult content",
    "Thông tin sai sự thật, lừa đảo hoặc gian lận": "Scam, fraud or false information",
    "Trang giả": "Fake Page",

    # Details
    "Đe dọa chia sẻ hình ảnh khỏa thân của tôi": "Threatening to share my nude images",
    "Có vẻ giống hành vi bóc lột tình dục": "Sexual exploitation",
    "Chia sẻ ảnh khỏa thân của ai đó": "Sharing private images",
    "Bắt nạt hoặc quấy rối": "Bullying or harassment",
    "Ngược đãi thể chất": "Physical abuse",
    "Có vẻ giống hành vi buôn người": "Human trafficking",
    "Tự tử hoặc tự gây thương tích": "Suicide or self-injury",
    "Chứng rối loạn ăn uống": "Eating disorder",
    "Mối đe dọa về an toàn có thể xảy ra": "Credible threat to safety",
    "Có vẻ giống hành vi khủng bố": "Terrorism",
    "Kêu gọi hành vi bạo lực": "Inciting violence",
    "Có vẻ giống tội phạm có tổ chức": "Organized crime",
    "Cổ xúy hành vi thù ghét": "Hate speech",
    "Thể hiện hành vi bạo lực, tử vong hoặc thương tích nghiêm trọng": "Violent or graphic content",
    "Ngược đãi động vật": "Animal abuse",
    "Chất cấm, chất gây nghiện": "Drugs",
    "Vũ khí": "Weapons",
    "Động vật": "Animals",
    "Có vẻ giống hành vi mại dâm": "Prostitution",
    "Hình ảnh khỏa thân của tôi đã bị chia sẻ": "My nude images were shared",
    "Ảnh khỏa thân hoặc hoạt động tình dục": "Nudity or sexual activity",
    "Gian lận hoặc lừa đảo": "Fraud or scam",
    "Chia sẻ thông tin sai sự thật": "False information",
    "Spam": "Spam",
    "Tôi": "Me",
    "Một người bạn": "A friend",
    "Một người nổi tiếng hoặc người của công chúng": "Celebrity or public figure",
    "Một doanh nghiệp": "A business",
    "Tài khoản này không phải là của người thật": "Not a real person"
}