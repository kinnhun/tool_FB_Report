# ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from browser import BrowserManager
from logger import log_report
import config

class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        
        self.browser_manager = BrowserManager()
        
        self.setup_ui()

    def setup_ui(self):
        # Chia layout: 2 cột
        left_frame = ttk.LabelFrame(self.root, text="Cấu hình & Input", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        right_frame = ttk.LabelFrame(self.root, text="Thao tác & Log", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- CỘT TRÁI ---
        
        # Nút Start/Stop
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        self.btn_start = ttk.Button(btn_frame, text="START BROWSER", command=self.start_thread)
        self.btn_start.pack(side='left', expand=True, fill='x', padx=2)
        
        self.btn_stop = ttk.Button(btn_frame, text="STOP", command=self.stop_browser, state='disabled')
        self.btn_stop.pack(side='right', expand=True, fill='x', padx=2)

        # Proxy
        ttk.Label(left_frame, text="Proxy (host:port hoặc user:pass@host:port):").pack(anchor='w', pady=(10,0))
        self.entry_proxy = ttk.Entry(left_frame)
        self.entry_proxy.pack(fill='x', pady=2)

        # Cookie
        ttk.Label(left_frame, text="Cookie (Raw text):").pack(anchor='w', pady=(10,0))
        self.txt_cookie = tk.Text(left_frame, height=8)
        self.txt_cookie.pack(fill='x', pady=2)

        # Link Report Input
        ttk.Label(left_frame, text="Link Report (Trang/Bài viết):").pack(anchor='w', pady=(10,0))
        self.entry_link_report = ttk.Entry(left_frame)
        self.entry_link_report.pack(fill='x', pady=2)

        # --- CỘT PHẢI ---

        # Hạng mục
        ttk.Label(right_frame, text="Hạng mục báo cáo:").pack(anchor='w')
        self.combo_category = ttk.Combobox(right_frame, values=config.CATEGORIES, state="readonly")
        self.combo_category.pack(fill='x', pady=5)
        self.combo_category.current(0)

        # Hành vi
        ttk.Label(right_frame, text="Chi tiết hành vi:").pack(anchor='w')
        self.combo_behavior = ttk.Combobox(right_frame, values=config.BEHAVIORS, state="readonly")
        self.combo_behavior.pack(fill='x', pady=5)
        self.combo_behavior.current(0)

        # Link liên quan
        ttk.Label(right_frame, text="Link người liên quan (nếu có):").pack(anchor='w')
        self.entry_related = ttk.Entry(right_frame)
        self.entry_related.pack(fill='x', pady=5)

        # Checkbox Random
        self.var_random = tk.BooleanVar()
        self.chk_random = ttk.Checkbutton(right_frame, text="Báo cáo bài viết random (trên Page)", variable=self.var_random)
        self.chk_random.pack(anchor='w', pady=10)

        # Nút Mở bài viết
        self.btn_open = ttk.Button(right_frame, text="MỞ BÀI VIẾT ĐỂ XEM", command=self.open_link_thread, state='disabled')
        self.btn_open.pack(fill='x', pady=10, ipady=5)

        # Nút Lưu Log
        self.btn_log = ttk.Button(right_frame, text="LƯU LOG (ĐÃ XỬ LÝ)", command=self.save_log)
        self.btn_log.pack(fill='x', pady=5)

        # Status bar
        self.lbl_status = ttk.Label(self.root, text="Trạng thái: Sẵn sàng", relief="sunken", anchor="w")
        self.lbl_status.grid(row=1, column=0, columnspan=2, sticky="ew")

    # --- Logic Handling ---

    def update_status(self, msg):
        self.lbl_status.config(text=f"Trạng thái: {msg}")

    def start_thread(self):
        t = threading.Thread(target=self.start_browser_process)
        t.daemon = True
        t.start()

    def start_browser_process(self):
        self.btn_start.config(state='disabled')
        self.update_status("Đang khởi động trình duyệt...")
        
        proxy = self.entry_proxy.get()
        cookie = self.txt_cookie.get("1.0", "end-1c")
        
        success, msg = self.browser_manager.start_browser(proxy)
        if success:
            self.update_status("Browser đã mở. Đang inject cookie...")
            
            # Inject cookie
            if cookie.strip():
                ok, c_msg = self.browser_manager.inject_cookies(cookie)
                self.update_status(c_msg)
            else:
                self.update_status("Đã mở browser (không cookie)")

            self.btn_stop.config(state='normal')
            self.btn_open.config(state='normal')
        else:
            self.update_status(msg)
            self.btn_start.config(state='normal')

    def open_link_thread(self):
        t = threading.Thread(target=self.process_open_link)
        t.daemon = True
        t.start()

     # Trong ui.py

    def process_open_link(self):
        url = self.entry_link_report.get().strip()
        is_random = self.var_random.get()
        category_text = self.combo_category.get()  # <--- Lấy text hạng mục (ví dụ: Nội dung người lớn)
        
        if not url:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Link Report")
            return

        self.update_status(f"Đang điều hướng và auto-report: {category_text}...")
        
        # Truyền category_text vào hàm navigate_to
        success, msg = self.browser_manager.navigate_to(url, category_text, is_random)
        self.update_status(msg)
        
    def save_log(self):
        url = self.entry_link_report.get().strip()
        cat = self.combo_category.get()
        beh = self.combo_behavior.get()
        rel = self.entry_related.get()
        
        if not url:
            messagebox.showerror("Lỗi", "Không có link report để ghi log")
            return

        note = "Đã mở xem"
        if self.var_random.get():
            note += " (Random post)"
        
        success, msg = log_report(url, cat, beh, rel, note)
        if success:
            messagebox.showinfo("Thành công", "Đã lưu log vào file CSV")
        else:
            messagebox.showerror("Lỗi", msg)

    def stop_browser(self):
        self.browser_manager.close()
        self.update_status("Đã dừng trình duyệt")
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.btn_open.config(state='disabled')