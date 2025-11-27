# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
import threading
import queue
import time
import csv
import os
import random
import shutil
import base64
from browser import BrowserManager
from logger import log_report, migrate_log_if_needed
import config

class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry("1200x750")
        
        # Migrate log file if needed
        migrate_log_if_needed()
        
        # State
        self.is_running = False
        self.stop_event = threading.Event()
        self.active_browsers = {} # {tree_item_id: browser_instance}
        self.account_data = {} # {tree_item_id: full_cookie}
        # self.final_screenshots = {} # REMOVED: Save to disk instead
        self.report_sets = [] # List of (category, detail) tuples
        self.lock = threading.Lock()
        
        # UI Queue for performance
        self.ui_queue = queue.Queue()
        
        # Temp folder for screenshots
        self.temp_dir = "temp_screenshots"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        self.setup_ui()
        
        # Start UI consumer
        self.process_ui_queue()

    def process_ui_queue(self):
        try:
            # Process up to 50 events at a time to keep UI responsive
            for _ in range(50):
                task = self.ui_queue.get_nowait()
                func, args = task
                try:
                    func(*args)
                except Exception:
                    pass
                self.ui_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(50, self.process_ui_queue)

    def setup_ui(self):

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # === LEFT PANEL: ACCOUNT LIST & SETTINGS ===
        left_frame = ttk.LabelFrame(main_frame, text="1. Quản lý Tài khoản (Cookies)", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Control Bar for List
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill='x', pady=5)
        
        # Cookie Input (c_user & xs)
        cookie_frame = ttk.Frame(control_frame)
        cookie_frame.pack(fill='x', pady=2)
        
        ttk.Label(cookie_frame, text="c_user:").pack(side='left')
        self.entry_c_user = ttk.Entry(cookie_frame, width=15)
        self.entry_c_user.pack(side='left', padx=5)
        
        ttk.Label(cookie_frame, text="xs:").pack(side='left')
        self.entry_xs = ttk.Entry(cookie_frame, width=15)
        self.entry_xs.pack(side='left', padx=5)
        
        ttk.Button(cookie_frame, text="Thêm Cookie", command=self.add_cookie).pack(side='left', padx=5)

        # File Actions
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill='x', pady=5)
        
        ttk.Button(file_frame, text="Nhập Excel (CSV)", command=self.import_cookies).pack(side='left')
        ttk.Button(file_frame, text="Nhập (.xlsx)", command=self.import_cookies_xlsx).pack(side='left', padx=5)
        
        ttk.Button(file_frame, text="Xuất Excel (CSV)", command=self.export_cookies).pack(side='left')
        ttk.Button(file_frame, text="Xuất (.xlsx)", command=self.export_cookies_xlsx).pack(side='left', padx=5)
        
        ttk.Button(file_frame, text="Xóa chọn", command=self.delete_selected).pack(side='left')

        # Treeview
        columns = ("stt", "cookie", "status", "result", "view")
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings', selectmode='extended')
        self.tree.heading("stt", text="#")
        self.tree.heading("cookie", text="Cookie (Ẩn)")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("result", text="Kết quả")
        self.tree.heading("view", text="Hành động")
        
        self.tree.column("stt", width=40, anchor='center')
        self.tree.column("cookie", width=150)
        self.tree.column("status", width=100)
        self.tree.column("result", width=200)
        self.tree.column("view", width=80, anchor='center')
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind click for View column
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Context Menu for View Browser
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Xem trình duyệt (Screenshot)", command=self.view_browser_snapshot)

        # Settings Frame (Bottom Left)
        settings_frame = ttk.Frame(left_frame)
        settings_frame.pack(fill='x', pady=10)
        
        ttk.Label(settings_frame, text="Số luồng (Threads):").pack(side='left')
        self.spin_threads = ttk.Spinbox(settings_frame, from_=1, to=50, width=5)
        self.spin_threads.set(2)
        self.spin_threads.pack(side='left', padx=5)
        
        self.var_headless = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Chạy ngầm (Headless)", variable=self.var_headless).pack(side='left', padx=10)

        ttk.Label(settings_frame, text="Proxy chung:").pack(side='left', padx=(10,0))
        self.entry_proxy = ttk.Entry(settings_frame, width=20)
        self.entry_proxy.pack(side='left', padx=5)

        # === RIGHT PANEL: REPORT CONFIG ===
        right_frame = ttk.LabelFrame(main_frame, text="2. Cấu hình Báo cáo", padding=10)
        right_frame.pack(side='right', fill='both', expand=False, padx=5, ipadx=10)
        
        ttk.Label(right_frame, text="Link cần báo cáo:").pack(anchor='w')
        self.entry_url = ttk.Entry(right_frame, width=40)
        self.entry_url.pack(fill='x', pady=5)

        ttk.Label(right_frame, text="Hạng mục chính:").pack(anchor='w', pady=(10,0))
        self.combo_category = ttk.Combobox(right_frame, values=config.CATEGORIES, state="readonly")
        self.combo_category.pack(fill='x', pady=5)
        self.combo_category.bind("<<ComboboxSelected>>", self.on_category_change)

        ttk.Label(right_frame, text="Chi tiết hành vi:").pack(anchor='w', pady=(10,0))
        self.combo_detail = ttk.Combobox(right_frame, state="readonly")
        self.combo_detail.pack(fill='x', pady=5)
        
        # Report Sets UI
        btn_set_frame = ttk.Frame(right_frame)
        btn_set_frame.pack(fill='x', pady=5)
        ttk.Button(btn_set_frame, text="Thêm vào bộ (Random)", command=self.add_report_set).pack(side='left', expand=True, fill='x')
        ttk.Button(btn_set_frame, text="Xóa bộ", command=self.clear_report_set).pack(side='left', padx=5)

        ttk.Label(right_frame, text="Danh sách bộ báo cáo:").pack(anchor='w')
        self.list_report_sets = tk.Listbox(right_frame, height=6)
        self.list_report_sets.pack(fill='x', pady=5)
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=20)
        
        self.btn_run = ttk.Button(right_frame, text="CHẠY HÀNG LOẠT", command=self.start_batch)
        self.btn_run.pack(fill='x', ipady=10)
        
        self.btn_stop = ttk.Button(right_frame, text="DỪNG TẤT CẢ", command=self.stop_batch, state='disabled')
        self.btn_stop.pack(fill='x', pady=5)
        
        self.btn_history = ttk.Button(right_frame, text="Xem Lịch sử", command=self.view_history)
        self.btn_history.pack(fill='x', pady=5)
        
        self.lbl_status = ttk.Label(right_frame, text="Sẵn sàng", relief="sunken", anchor="w")
        self.lbl_status.pack(side='bottom', fill='x', pady=10)

        # Init
        if config.CATEGORIES:
            self.combo_category.current(0)
            self.on_category_change()

    # --- EVENT HANDLERS ---
    def add_cookie(self):
        c_user = self.entry_c_user.get().strip()
        xs = self.entry_xs.get().strip()
        
        if c_user and xs:
            # Format: c_user=...;xs=...
            full_cookie = f"c_user={c_user};xs={xs}"
            
            # Mask cookie for display
            display_c = f"{c_user} | {xs[:5]}..."
            item_id = self.tree.insert("", "end", values=(len(self.tree.get_children())+1, display_c, "Chờ", "", "Xem"))
            self.account_data[item_id] = full_cookie
            
            self.entry_c_user.delete(0, 'end')
            self.entry_xs.delete(0, 'end')
        else:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập cả c_user và xs")

    def import_cookies(self):
        fp = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if fp:
            try:
                with open(fp, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    # Try to detect header
                    header = next(reader, None)
                    if not header: return
                    
                    # Check columns
                    try:
                        # Normalize headers
                        headers = [h.strip().lower() for h in header]
                        idx_c = headers.index('c_user')
                        idx_xs = headers.index('xs')
                    except ValueError:
                        messagebox.showerror("Lỗi Format", "File CSV cần có cột 'c_user' và 'xs'")
                        return
                        
                    count = 0
                    for row in reader:
                        if len(row) > max(idx_c, idx_xs):
                            c_user = row[idx_c].strip()
                            xs = row[idx_xs].strip()
                            if c_user and xs:
                                full_cookie = f"c_user={c_user};xs={xs}"
                                display_c = f"{c_user} | {xs[:5]}..."
                                item_id = self.tree.insert("", "end", values=(len(self.tree.get_children())+1, display_c, "Chờ", "", "Xem"))
                                self.account_data[item_id] = full_cookie
                                count += 1
                    messagebox.showinfo("Thành công", f"Đã nhập {count} tài khoản.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không đọc được file: {e}")

    def export_cookies(self):
        fp = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if fp:
            try:
                with open(fp, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["c_user", "xs"])
                    
                    for item_id, full_cookie in self.account_data.items():
                        # Parse back c_user and xs
                        try:
                            parts = full_cookie.split(';')
                            c_val = ""
                            xs_val = ""
                            for p in parts:
                                if 'c_user=' in p:
                                    c_val = p.split('=')[1]
                                if 'xs=' in p:
                                    xs_val = p.split('=')[1]
                            writer.writerow([c_val, xs_val])
                        except:
                            pass
                messagebox.showinfo("Thành công", "Đã xuất file CSV.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không ghi được file: {e}")

    def delete_selected(self):
        for item in self.tree.selection():
            self.tree.delete(item)
            if item in self.account_data:
                del self.account_data[item]
        # Re-index STT
        for i, item in enumerate(self.tree.get_children()):
            self.tree.set(item, "stt", i+1)

    def on_category_change(self, event=None):
        cat = self.combo_category.get()
        details = config.REPORT_DATA.get(cat, [])
        self.combo_detail.config(values=details)
        if details:
            self.combo_detail.current(0)
        else:
            self.combo_detail.set("")

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.tree.identify_column(event.x)
            if col == "#5": # Column 'view'
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    self.open_preview(item_id)

    def open_preview(self, item_id):
        status = self.tree.set(item_id, "status")
        
        top = Toplevel(self.root)
        top.title(f"Xem: {item_id} - {status}")
        top.geometry("800x600")
        
        lbl_img = tk.Label(top, text="Đang tải hình ảnh...", bg="black", fg="white")
        lbl_img.pack(fill='both', expand=True)
        
        # If running, update live. If finished, show final.
        if status in ["Chờ", "Lỗi Start"]:
             lbl_img.config(text="Trình duyệt chưa chạy hoặc lỗi khởi động.")
        elif status in ["Hoàn thành", "Lỗi"]:
            # Show final from disk
            b64 = self.get_screenshot_from_disk(item_id)
            if b64:
                self.show_image(lbl_img, b64)
            else:
                lbl_img.config(text="Không có ảnh (Đã đóng).")
        else:
            # Running
            self.update_live_preview(top, lbl_img, item_id)

    def update_live_preview(self, top, lbl_img, item_id):
        if not top.winfo_exists(): return
        
        with self.lock:
            bm = self.active_browsers.get(item_id)
            
        if bm:
            b64 = bm.get_screenshot_base64()
            if b64:
                self.show_image(lbl_img, b64)
            else:
                pass 
        else:
            # Browser might have just finished, check disk
            b64 = self.get_screenshot_from_disk(item_id)
            if b64:
                self.show_image(lbl_img, b64)
            return

        # Refresh every 1s
        top.after(1000, lambda: self.update_live_preview(top, lbl_img, item_id))

    def show_image(self, lbl, b64):
        try:
            img = tk.PhotoImage(data=b64)
            # Simple resize logic (subsample) if too large
            w = img.width()
            h = img.height()
            if w > 1000:
                scale = w // 800 + 1
                img = img.subsample(scale, scale)
            
            lbl.config(image=img, text="")
            lbl.image = img
        except Exception as e:
            lbl.config(text=f"Lỗi hiển thị ảnh: {e}")

    def view_browser_snapshot(self):
        sel = self.tree.selection()
        if not sel: return
        item_id = sel[0]
        self.open_preview(item_id)

    def view_history(self):
        if not os.path.exists(config.LOG_FILE):
             messagebox.showinfo("Info", "Chưa có lịch sử báo cáo.")
             return

        try:
            with open(config.LOG_FILE, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                data = list(reader)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được file log: {e}")
            return

        if not data:
            messagebox.showinfo("Info", "File lịch sử trống.")
            return

        header = data[0]
        self.history_header = header
        rows = data[1:]
        # Reverse to show newest first
        rows.reverse()
        
        self.history_rows = rows
        self.history_page = 0
        self.history_page_size = 20
        
        top = Toplevel(self.root)
        top.title("Lịch sử Báo cáo")
        top.geometry("1000x600")
        
        # Treeview Frame
        tree_frame = ttk.Frame(top)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.hist_tree = ttk.Treeview(tree_frame, columns=header, show='headings', 
                                      yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.hist_tree.yview)
        scrollbar_x.config(command=self.hist_tree.xview)
        
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        self.hist_tree.pack(side='left', fill='both', expand=True)
        
        for col in header:
            self.hist_tree.heading(col, text=col)
            self.hist_tree.column(col, width=150, minwidth=100)
            
        # Pagination Controls
        ctrl_frame = ttk.Frame(top, padding=10)
        ctrl_frame.pack(fill='x', side='bottom')
        
        ttk.Button(ctrl_frame, text="<< Trước", command=lambda: self.change_hist_page(-1)).pack(side='left')
        self.lbl_page_info = ttk.Label(ctrl_frame, text="Trang 1")
        self.lbl_page_info.pack(side='left', padx=20)
        ttk.Button(ctrl_frame, text="Sau >>", command=lambda: self.change_hist_page(1)).pack(side='left')
        
        ttk.Button(ctrl_frame, text="Xuất Excel (.xlsx)", command=self.export_history_xlsx).pack(side='right', padx=10)
        
        self.load_hist_page()

    def change_hist_page(self, delta):
        new_page = self.history_page + delta
        total_rows = len(self.history_rows)
        if total_rows == 0: return
        max_page = (total_rows - 1) // self.history_page_size
        
        if 0 <= new_page <= max_page:
            self.history_page = new_page
            self.load_hist_page()

    def load_hist_page(self):
        # Clear current items
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)
            
        start = self.history_page * self.history_page_size
        end = start + self.history_page_size
        page_data = self.history_rows[start:end]
        
        for row in page_data:
            self.hist_tree.insert("", "end", values=row)
            
        total_rows = len(self.history_rows)
        if total_rows == 0:
            max_page = 1
        else:
            max_page = (total_rows - 1) // self.history_page_size + 1
        self.lbl_page_info.config(text=f"Trang {self.history_page + 1} / {max_page} (Tổng: {total_rows} dòng)")

    def import_cookies_xlsx(self):
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt openpyxl: pip install openpyxl")
            return

        fp = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if fp:
            try:
                wb = openpyxl.load_workbook(fp)
                sheet = wb.active
                
                # Find headers
                headers = {}
                for cell in sheet[1]:
                    if cell.value:
                        headers[str(cell.value).strip().lower()] = cell.column - 1
                
                if 'c_user' not in headers or 'xs' not in headers:
                    messagebox.showerror("Lỗi Format", "File Excel cần có cột 'c_user' và 'xs' ở dòng đầu tiên.")
                    return
                
                idx_c = headers['c_user']
                idx_xs = headers['xs']
                
                count = 0
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if row[idx_c] and row[idx_xs]:
                        c_user = str(row[idx_c]).strip()
                        xs = str(row[idx_xs]).strip()
                        
                        full_cookie = f"c_user={c_user};xs={xs}"
                        display_c = f"{c_user} | {xs[:5]}..."
                        item_id = self.tree.insert("", "end", values=(len(self.tree.get_children())+1, display_c, "Chờ", "", "Xem"))
                        self.account_data[item_id] = full_cookie
                        count += 1
                messagebox.showinfo("Thành công", f"Đã nhập {count} tài khoản từ Excel.")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không đọc được file: {e}")

    def export_cookies_xlsx(self):
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt openpyxl: pip install openpyxl")
            return
            
        fp = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if fp:
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(["c_user", "xs"])
                
                for item_id, full_cookie in self.account_data.items():
                    try:
                        parts = full_cookie.split(';')
                        c_val = ""
                        xs_val = ""
                        for p in parts:
                            if 'c_user=' in p:
                                c_val = p.split('=')[1]
                            if 'xs=' in p:
                                xs_val = p.split('=')[1]
                        ws.append([c_val, xs_val])
                    except:
                        pass
                
                wb.save(fp)
                messagebox.showinfo("Thành công", "Đã xuất file Excel (.xlsx).")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không ghi được file: {e}")

    def export_history_xlsx(self):
        if not self.history_rows:
            return
            
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt openpyxl: pip install openpyxl")
            return

        fp = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if fp:
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                # Header
                if hasattr(self, 'history_header'):
                    ws.append(self.history_header)
                else:
                    ws.append(["Thời gian", "URL", "Hạng mục", "Chi tiết", "Kết quả", "Account"])
                # Rows
                for row in self.history_rows:
                    ws.append(row)
                wb.save(fp)
                messagebox.showinfo("Thành công", "Đã xuất lịch sử ra Excel.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không ghi được file: {e}")

    def add_report_set(self):
        cat = self.combo_category.get()
        detail = self.combo_detail.get()
        if cat and detail:
            self.report_sets.append((cat, detail))
            self.list_report_sets.insert('end', f"{cat} -> {detail}")
        else:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Hạng mục và Chi tiết trước khi thêm.")

    def clear_report_set(self):
        self.report_sets = []
        self.list_report_sets.delete(0, 'end')

    # --- BATCH LOGIC ---
    def start_batch(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Thiếu URL", "Vui lòng nhập URL.")
            return
            
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("Thiếu Account", "Danh sách tài khoản trống.")
            return

        self.is_running = True
        self.stop_event.clear()
        self.btn_run.config(state='disabled')
        self.btn_stop.config(state='normal')
        
        # Reset status
        for item in items:
            self.tree.set(item, "status", "Chờ")
            self.tree.set(item, "result", "")
            
        # Queue
        q = queue.Queue()
        for item in items:
            # Retrieve full cookie from dict
            cookie = self.account_data.get(item, "")
            q.put((item, cookie))
            
        # Threads
        try:
            num_threads = int(self.spin_threads.get())
        except:
            num_threads = 1
            
        # Prepare report sets
        current_sets = list(self.report_sets)
        # If empty, use the currently selected one
        if not current_sets:
            cat = self.combo_category.get()
            detail = self.combo_detail.get()
            if cat and detail:
                current_sets.append((cat, detail))
            else:
                messagebox.showwarning("Thiếu cấu hình", "Vui lòng chọn Hạng mục báo cáo hoặc thêm vào bộ báo cáo.")
                self.btn_run.config(state='normal')
                self.btn_stop.config(state='disabled')
                return

        threading.Thread(target=self.run_queue, args=(q, num_threads, url, current_sets)).start()

    def run_queue(self, q, num_threads, url, report_sets):
        proxy = self.entry_proxy.get().strip()
        headless = self.var_headless.get()
        
        def worker():
            while not self.stop_event.is_set():
                try:
                    item, cookie = q.get(timeout=1)
                except queue.Empty:
                    break
                
                # Pick random report config
                if report_sets:
                    r_cat, r_detail = random.choice(report_sets)
                    self.process_one_account(item, cookie, url, r_cat, r_detail, proxy, headless)
                
                q.task_done()

        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
            
        self.root.after(0, self.on_batch_finished)

    def process_one_account(self, item, cookie, url, cat, detail, proxy, headless):
        self.update_item(item, "status", "Đang chạy...")
        
        # Extract c_user for logging
        c_user = ""
        try:
            if "c_user=" in cookie:
                c_user = cookie.split("c_user=")[1].split(";")[0]
        except:
            pass

        bm = BrowserManager()
        with self.lock:
            self.active_browsers[item] = bm
            
        try:
            ok, msg = bm.start_browser(proxy, headless=headless)
            if not ok:
                self.update_item(item, "status", "Lỗi Start")
                self.update_item(item, "result", msg)
                log_report(url, cat, detail, f"Start Failed: {msg}", c_user)
                return

            self.update_item(item, "status", "Inject Cookie...")
            bm.inject_cookies(cookie)
            
            self.update_item(item, "status", "Đang báo cáo...")
            ok_report, msg_report = bm.navigate_and_report(url, cat, detail)
            
            if ok_report:
                self.update_item(item, "status", "Hoàn thành")
                self.update_item(item, "result", msg_report)
                log_report(url, cat, detail, "Success", c_user)
            else:
                self.update_item(item, "status", "Lỗi")
                self.update_item(item, "result", msg_report)
                log_report(url, cat, detail, f"Failed: {msg_report}", c_user)
            
            # Final screenshot
            b64 = bm.get_screenshot_base64()
            self.save_screenshot_to_disk(item, b64)
            
        except Exception as e:
            self.update_item(item, "status", "Lỗi")
            self.update_item(item, "result", str(e))
            log_report(url, cat, detail, f"Exception: {str(e)}", c_user)
            
            # Error screenshot
            b64 = bm.get_screenshot_base64()
            self.save_screenshot_to_disk(item, b64)
        finally:
            bm.close()
            with self.lock:
                if item in self.active_browsers:
                    del self.active_browsers[item]

    def update_item(self, item, col, val):
        # Push to queue instead of direct update
        self.ui_queue.put((self.tree.set, (item, col, val)))

    def save_screenshot_to_disk(self, item_id, b64_data):
        if not b64_data: return
        try:
            path = os.path.join(self.temp_dir, f"{item_id}.png")
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64_data))
        except Exception:
            pass

    def get_screenshot_from_disk(self, item_id):
        path = os.path.join(self.temp_dir, f"{item_id}.png")
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode('utf-8')
            except:
                return None
        return None

    def stop_batch(self):
        self.stop_event.set()
        self.btn_stop.config(state='disabled')
        self.lbl_status.config(text="Đang dừng...")

    def on_batch_finished(self):
        self.is_running = False
        self.btn_run.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.lbl_status.config(text="Đã hoàn tất batch.")
        messagebox.showinfo("Xong", "Đã chạy xong danh sách.")