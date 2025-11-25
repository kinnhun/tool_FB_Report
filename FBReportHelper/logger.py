# logger.py
import csv
import os
from datetime import datetime
from config import LOG_FILE

def log_report(report_link, category, behavior, related_link, note):
    """
    Ghi một dòng log vào file CSV.
    """
    file_exists = os.path.isfile(LOG_FILE)
    
    try:
        # Mở file mode 'a' (append), encoding utf-8-sig để Excel đọc được tiếng Việt
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # Nếu file chưa tồn tại, ghi header trước
            if not file_exists:
                writer.writerow(["Thời gian", "Link Report", "Hạng mục", "Hành vi", "Link liên quan", "Ghi chú"])
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([current_time, report_link, category, behavior, related_link, note])
            return True, "Ghi log thành công"
    except Exception as e:
        return False, f"Lỗi ghi log: {str(e)}"