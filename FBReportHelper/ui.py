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
        # Layout chính
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # === KHUNG CẤU HÌNH (TRÁI) ===
        left_frame = ttk.LabelFrame(main_frame, text="1. Kết nối & Tài khoản", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)

        # Nút Start/Stop
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        self.btn_start = ttk.Button(btn_frame, text="KHỞI ĐỘNG BROWSER", command=self.start_thread)
        self.btn_start.pack(side='left', expand=True, fill='x')
        self.btn_stop = ttk.Button(btn_frame, text="DỪNG", command=self.stop_browser, state='disabled')
        self.btn_stop.pack(side='right', expand=True, fill='x')

        ttk.Label(left_frame, text="Proxy (IP:Port hoặc User:Pass@IP:Port):").pack(anchor='w', pady=(10,0))
        self.entry_proxy = ttk.Entry(left_frame)
        self.entry_proxy.pack(fill='x')

        ttk.Label(left_frame, text="Cookie Facebook (Raw):").pack(anchor='w', pady=(10,0))
        self.txt_cookie = tk.Text(left_frame, height=10)
        self.txt_cookie.pack(fill='x')
        
        # === KHUNG THAO TÁC (PHẢI) ===
        right_frame = ttk.LabelFrame(main_frame, text="2. Thiết lập Báo cáo", padding=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)

        ttk.Label(right_frame, text="Link cần báo cáo (Trang hoặc Bài viết):").pack(anchor='w')
        self.entry_url = ttk.Entry(right_frame)
        self.entry_url.pack(fill='x', pady=5)

        # Combobox Hạng mục (Cấp 1)
        ttk.Label(right_frame, text="Chọn Hạng mục chính:").pack(anchor='w', pady=(10,0))
        self.combo_category = ttk.Combobox(right_frame, values=config.CATEGORIES, state="readonly")
        self.combo_category.pack(fill='x', pady=5)
        self.combo_category.bind("<<ComboboxSelected>>", self.on_category_change)

        # Combobox Chi tiết (Cấp 2)
        ttk.Label(right_frame, text="Chọn Chi tiết hành vi:").pack(anchor='w', pady=(10,0))
        self.combo_detail = ttk.Combobox(right_frame, state="readonly")
        self.combo_detail.pack(fill='x', pady=5)

        # Nút Hành động
        ttk.Label(right_frame, text="Hành động:").pack(anchor='w', pady=(20,0))
        self.btn_run = ttk.Button(right_frame, text=">>> CHẠY AUTO REPORT <<<", command=self.run_report_thread, state='disabled')
        self.btn_run.pack(fill='x', ipady=10)

        # Status Bar
        self.lbl_status = ttk.Label(self.root, text="Trạng thái: Chờ khởi động...", relief="sunken", anchor="w")
        self.lbl_status.pack(side='bottom', fill='x')
        
        # Init default values
        if config.CATEGORIES:
            self.combo_category.current(0)
            self.on_category_change()

    # --- EVENT HANDLERS ---
    def on_category_change(self, event=None):
        """Khi chọn Hạng mục -> Cập nhật danh sách Chi tiết tương ứng"""
        cat = self.combo_category.get()
        details = config.REPORT_DATA.get(cat, [])
        self.combo_detail.config(values=details)
        if details:
            self.combo_detail.current(0)
        else:
            self.combo_detail.set("")

    def update_status(self, msg):
        self.lbl_status.config(text=f"Trạng thái: {msg}")

    def start_thread(self):
        t = threading.Thread(target=self.start_browser_process)
        t.daemon = True; t.start()

    def start_browser_process(self):
        self.btn_start.config(state='disabled')
        self.update_status("Đang mở trình duyệt...")
        
        proxy = self.entry_proxy.get().strip()
        cookie = self.txt_cookie.get("1.0", "end-1c").strip()
        
        ok, msg = self.browser_manager.start_browser(proxy)
        if ok:
            if cookie:
                self.update_status("Injecting Cookie...")
                self.browser_manager.inject_cookies(cookie)
            self.update_status("Trình duyệt sẵn sàng.")
            self.btn_stop.config(state='normal')
            self.btn_run.config(state='normal')
        else:
            self.update_status(f"Lỗi: {msg}")
            self.btn_start.config(state='normal')

    def run_report_thread(self):
        t = threading.Thread(target=self.process_report)
        t.daemon = True; t.start()

    def process_report(self):
        url = self.entry_url.get().strip()
        cat = self.combo_category.get()
        detail = self.combo_detail.get()

        if not url:
            messagebox.showwarning("Thiếu Link", "Vui lòng nhập URL cần báo cáo.")
            return

        self.update_status(f"Đang chạy auto: {cat}...")
        ok, msg = self.browser_manager.navigate_and_report(url, cat, detail)
        self.update_status(msg)
        
        # Ghi log
        log_report(url, cat, detail, msg)
        if ok:
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Thất bại", msg)

    def stop_browser(self):
        self.browser_manager.close()
        self.update_status("Đã đóng trình duyệt.")
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.btn_run.config(state='disabled')