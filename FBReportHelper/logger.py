# logger.py
import csv
import os
import threading
from datetime import datetime
from config import LOG_FILE

log_lock = threading.Lock()

def log_report(url, category, detail, note):
    with log_lock:
        file_exists = os.path.isfile(LOG_FILE)
        try:
            with open(LOG_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Thời gian", "URL", "Hạng mục", "Chi tiết", "Kết quả"])
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([current_time, url, category, detail, note])
                return True
        except:
            return False