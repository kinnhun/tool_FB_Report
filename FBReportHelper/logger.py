# logger.py
import csv
import os
import threading
from datetime import datetime
from config import LOG_FILE

log_lock = threading.Lock()

def migrate_log_if_needed():
    with log_lock:
        if not os.path.exists(LOG_FILE): return
        try:
            with open(LOG_FILE, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)
                except StopIteration:
                    return # Empty file

                if "Account" not in header:
                    # Need migration
                    rows = list(reader)
                    # Append Account column to header and rows
                    new_header = header + ["Account"]
                    new_rows = [r + [""] for r in rows]
                    
                    with open(LOG_FILE, 'w', newline='', encoding='utf-8-sig') as f_out:
                        writer = csv.writer(f_out)
                        writer.writerow(new_header)
                        writer.writerows(new_rows)
        except Exception as e:
            print(f"Migration failed: {e}")

def log_report(url, category, detail, note, c_user=""):
    with log_lock:
        file_exists = os.path.isfile(LOG_FILE)
        has_link_lien_quan = False
        
        if file_exists:
            try:
                with open(LOG_FILE, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    try:
                        header = next(reader)
                        # Check for "Link liên quan" column which causes the shift
                        if "Link liên quan" in header:
                            has_link_lien_quan = True
                    except StopIteration:
                        pass
            except:
                pass

        try:
            with open(LOG_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if not file_exists:
                    # Create new file with standard 7 columns to match legacy format if preferred, 
                    # or just use the 6 columns. 
                    # Since user seems to have the 7-column format, let's stick to it for consistency if we recreate.
                    # But to avoid confusion, let's use the 6-column format for NEW files unless user provides a template.
                    # Actually, let's use 7 columns to be safe with the user's expectation of "Link liên quan"
                    writer.writerow(["Thời gian", "URL", "Hạng mục", "Chi tiết", "Link liên quan", "Kết quả", "Account"])
                    writer.writerow([current_time, url, category, detail, "", note, c_user])
                else:
                    if has_link_lien_quan:
                        # Insert empty string for "Link liên quan"
                        writer.writerow([current_time, url, category, detail, "", note, c_user])
                    else:
                        # Standard 6 columns
                        writer.writerow([current_time, url, category, detail, note, c_user])
                return True
        except:
            return False