# browser.py
"""
Module quản lý trình duyệt và automation cho Facebook Report Tool.

Quy trình báo cáo Facebook:
=========================
1. Báo cáo BÀI VIẾT:
   - Click nút 3 chấm "..." ở góc trên bên phải post
   - Chọn "Tìm hỗ trợ hoặc báo cáo bài viết" / "Báo cáo bài viết"
   - Popup: "Tại sao bạn báo cáo bài viết này?"
   - Chọn hạng mục chính (Category)
   - Click "Tiếp" / "Next"
   - Chọn chi tiết hành vi (Detail)
   - Click "Gửi" / "Submit"

2. Báo cáo TRANG (Page):
   - Vào trang (Page) cần báo cáo
   - Click nút 3 chấm "..." cạnh nút "Tin nhắn", "Theo dõi"
   - Chọn "Báo cáo Trang"
   - Popup: "Bạn muốn báo cáo điều gì?"
     + "Thông tin về trang này" -> Chọn lý do báo cáo trang
     + "Bài viết cụ thể" -> Quay lại luồng báo cáo bài viết
   - Chọn hạng mục và chi tiết
   - Click "Tiếp" / "Gửi" để hoàn tất

Xử lý sau báo cáo:
=================
- Hệ thống tự động lọc (Machine Learning)
- Moderator người thật xem xét (nếu cần)
- Kết quả: Không làm gì / Gỡ bài / Hạn chế tính năng / Khóa tài khoản
- Thông báo trong Hộp thư hỗ trợ (Support Inbox)
"""

import time
import zipfile
import os
import shutil
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Import constants từ config
try:
    from config import THREE_DOTS_VARIANTS, REPORT_BUTTON_TEXTS, NEXT_BUTTON_TEXTS, PAGE_REPORT_OPTIONS
except ImportError:
    # Fallback nếu không import được
    THREE_DOTS_VARIANTS = [
        "Hành động với bài viết này", "Actions for this post", "More",
        "Xem thêm tùy chọn", "More options", "Options", "Tùy chọn", "Thêm"
    ]
    REPORT_BUTTON_TEXTS = ["Báo cáo", "Report", "Tìm hỗ trợ", "Find support"]
    NEXT_BUTTON_TEXTS = ["Tiếp", "Next", "Gửi", "Submit", "Xong", "Done"]
    PAGE_REPORT_OPTIONS = ["Thông tin về trang này", "Information about this Page", 
                           "Bài viết cụ thể", "A specific post"]


class BrowserManager:
    def __init__(self):
        self.driver = None

    # ------------------ Setup & Proxy ------------------
    def create_proxy_auth_extension(self, proxy_host, proxy_port, proxy_user, proxy_pass, scheme='http'):
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"
            ],
            "background": { "scripts": ["background.js"] },
            "minimum_chrome_version":"22.0.0"
        }
        """
        background_js = f"""
        var config = {{
                mode: "fixed_servers",
                rules: {{
                singleProxy: {{ scheme: "{scheme}", host: "{proxy_host}", port: parseInt({proxy_port}) }},
                bypassList: ["localhost"]
                }}
            }};
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
        function callbackFn(details) {{
            return {{ authCredentials: {{ username: "{proxy_user}", password: "{proxy_pass}" }} }};
        }}
        chrome.webRequest.onAuthRequired.addListener(callbackFn, {{urls: ["<all_urls>"]}}, ['blocking']);
        """
        pluginfile = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return pluginfile

    def find_chrome_executable(self):
        candidates = ["chrome", "google-chrome", "chromium", "chromium-browser", "chrome.exe"]
        for name in candidates:
            path = shutil.which(name)
            if path:
                return path
        if platform.system() == "Windows":
            possible = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
            for p in possible:
                if os.path.exists(p):
                    return p
        return None

    def start_browser(self, proxy_string=None):
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")

        binary_path = self.find_chrome_executable()
        if binary_path:
            options.binary_location = binary_path

        if proxy_string and proxy_string.strip():
            p_str = proxy_string.strip()
            if '@' in p_str:
                auth, host_port = p_str.split('@', 1)
                user, password = auth.split(':', 1)
                host, port = host_port.split(':', 1)
                plugin_file = self.create_proxy_auth_extension(host, port, user, password)
                options.add_extension(plugin_file)
            else:
                options.add_argument(f'--proxy-server={p_str}')

        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            return True, "Khởi tạo trình duyệt thành công"
        except Exception as e:
            return False, f"Lỗi khởi tạo Browser: {str(e)}"

    def inject_cookies(self, raw_cookie_str):
        if not self.driver:
            return False, "Chưa khởi động trình duyệt"
        try:
            self.driver.get("https://www.facebook.com/")
            cookies = []
            raw = raw_cookie_str.replace('Cookie:', '').strip()
            pairs = [p.strip() for p in raw.split(';') if p.strip()]
            for pair in pairs:
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    cookies.append({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com', 'path': '/'})
            for c in cookies:
                try:
                    self.driver.add_cookie(c)
                except Exception:
                    # Một số cookie có thuộc tính không chấp nhận bởi Selenium -> bỏ qua
                    pass
            self.driver.refresh()
            time.sleep(2)
            if "login" not in self.driver.current_url:
                return True, "Đã Inject Cookie & Login OK"
            else:
                return False, "Inject xong nhưng chưa Login được (cookie có thể hết hạn hoặc checkpoint)"
        except Exception as e:
            return False, f"Lỗi Inject Cookie: {str(e)}"

    # ------------------ Helpers ------------------
    def smart_click(self, xpath, timeout=5):
        """Chờ element clickable rồi click bằng JS để ổn định hơn."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            elem = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].click();", elem)
            return True
        except Exception:
            return False

    def click_button_by_text(self, texts, timeout=3):
        """Thử click phần tử chứa một trong các texts."""
        for t in texts:
            xpath = f"//span[contains(normalize-space(.), '{t}')] | //div[@aria-label='{t}'] | //button[.//span[contains(normalize-space(.), '{t}')]]"
            if self.smart_click(xpath, timeout=timeout):
                return True
        return False

    def click_next_action(self):
        """Click nút Tiếp/Next/Gửi/Submit để chuyển sang bước tiếp theo."""
        return self.click_button_by_text(NEXT_BUTTON_TEXTS, timeout=2)

    # ------------------ Robust 3-dots finder ------------------
    def find_and_click_three_dots(self):
        """
        Robust method to find & click the three-dot menu:
        - Try aria-label / text variants
        - Try SVG detection: look for <svg> that contains 3 <circle> elements and click it (or its clickable ancestor)
        - Fallback tries: any clickable element with title/aria-label containing 'More' / 'Tùy' / 'Hành động'
        
        Quy trình:
        1. Tìm nút 3 chấm trên bài viết hoặc Trang
        2. Click để mở menu dropdown
        3. Menu sẽ hiển thị các tùy chọn như "Báo cáo", "Ẩn bài viết", v.v.
        """
        if not self.driver:
            return False, "Browser chưa chạy"

        wait = WebDriverWait(self.driver, 4)

        # 1) Try common aria-label/text variants (fast) - sử dụng constants từ config
        for v in THREE_DOTS_VARIANTS:
            try:
                # match aria-label exactly or span text contains
                xpath = f"//div[@aria-label='{v}'] | //button[@aria-label='{v}'] | //span[contains(normalize-space(.), '{v}')]"
                if self.smart_click(xpath, timeout=1):
                    return True, f"Đã click nút 3 chấm (variant='{v}')"
            except Exception:
                pass

        # 2) Try to detect svg with three circles: //svg[count(.//circle)=3] or //svg[count(circle)=3]
        try:
            # Wait presence of such svg (short timeout)
            svg_xpath_candidates = [
                "//svg[count(.//circle)=3]",
                "//svg[count(circle)=3]",
                "//svg[.//circle and string-length(normalize-space(.))>0]"  # fallback
            ]
            for sx in svg_xpath_candidates:
                try:
                    svg = wait.until(EC.presence_of_element_located((By.XPATH, sx)))
                    # Click the svg or nearest clickable ancestor
                    try:
                        # Try click the svg itself
                        self.driver.execute_script("arguments[0].click();", svg)
                        return True, "Đã click nút 3 chấm (bằng SVG 3 circle)"
                    except Exception:
                        # Fallback: click ancestor with role='button' or clickable div
                        try:
                            ancestor = svg.find_element(By.XPATH, "./ancestor::div[@role='button' or @role='menuitem'][1]")
                            self.driver.execute_script("arguments[0].click();", ancestor)
                            return True, "Đã click nút 3 chấm (ancestor)"
                        except Exception:
                            # try a more generic ancestor
                            try:
                                ancestor2 = svg.find_element(By.XPATH, "./ancestor::div[1]")
                                self.driver.execute_script("arguments[0].click();", ancestor2)
                                return True, "Đã click nút 3 chấm (ancestor2)"
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass

        # 3) Fallback: search for any element with role='button' that contains an svg with circles (scan few)
        try:
            candidate_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' or button or @role='menuitem']")
            for el in candidate_buttons:
                try:
                    svgs = el.find_elements(By.TAG_NAME, "svg")
                    for svg in svgs:
                        circles = svg.find_elements(By.TAG_NAME, "circle")
                        if len(circles) >= 3:
                            try:
                                self.driver.execute_script("arguments[0].click();", el)
                                return True, "Đã click nút 3 chấm (scan buttons/svg circles)"
                            except Exception:
                                pass
                except Exception:
                    continue
        except Exception:
            pass

        return False, "Không tìm thấy nút 3 chấm"

    # ------------------ Report flow (simplified usage) ------------------
    def execute_report_flow(self, category, detail):
        """
        Thực hiện quy trình báo cáo tự động.
        
        Luồng báo cáo bài viết:
        =======================
        1. Click nút 3 chấm "..." -> Mở menu tùy chọn
        2. Click "Báo cáo" / "Report" -> Mở popup báo cáo
        3. Popup: "Tại sao bạn báo cáo bài viết này?"
        4. Chọn Category (hạng mục chính): VD "Bạo lực, thù ghét..."
        5. Click "Tiếp" / "Next"
        6. Chọn Detail (chi tiết): VD "Ngôn từ thù ghét"
        7. Click "Gửi" / "Submit" -> Hoàn tất
        
        Luồng báo cáo Trang:
        ====================
        1. Click nút 3 chấm "..." -> Mở menu
        2. Click "Báo cáo Trang" -> Popup: "Bạn muốn báo cáo điều gì?"
        3. Chọn "Thông tin về trang này" hoặc "Bài viết cụ thể"
        4. Tiếp tục chọn Category và Detail như báo cáo bài viết
        5. Click "Gửi" -> Hoàn tất
        
        Parameters:
            category (str): Hạng mục chính (cấp 1)
            detail (str): Chi tiết hành vi (cấp 2)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.driver:
            return False, "Browser chưa chạy"

        try:
            # Bước 1: Tìm và click nút 3 chấm
            ok, msg = self.find_and_click_three_dots()
            if not ok:
                return False, msg

            time.sleep(0.5)

            # Bước 2: Click nút Báo cáo trong menu dropdown
            if not self.click_button_by_text(REPORT_BUTTON_TEXTS):
                return False, "Không click được nút Báo cáo sau khi mở menu"

            # Chờ popup báo cáo hiện ra
            time.sleep(0.8)

            # Bước 3: Nếu là Trang, popup sẽ hỏi "Bạn muốn báo cáo điều gì?"
            # Thử click "Thông tin về trang này" hoặc "Bài viết cụ thể"
            self.click_button_by_text(PAGE_REPORT_OPTIONS)

            # Bước 4: Chọn hạng mục chính (Category - Cấp 1)
            # VD: "Nội dung mang tính bạo lực, thù ghét hoặc gây phiền toái"
            if category:
                if not self.click_button_by_text([category]):
                    # Thử tìm với từ đầu tiên nếu không khớp chính xác
                    if not self.click_button_by_text([category.split()[0]]):
                        return False, f"Không tìm thấy hạng mục '{category}'"
            time.sleep(0.5)
            
            # Bước 5: Click "Tiếp" để chuyển sang bước chọn chi tiết
            self.click_next_action()
            time.sleep(0.5)

            # Bước 6: Chọn chi tiết hành vi (Detail - Cấp 2)
            # VD: "Ngôn từ thù ghét", "Kêu gọi bạo lực"
            if detail:
                if not self.click_button_by_text([detail], timeout=4):
                    # Fallback: thử với 2 từ đầu tiên
                    parts = detail.split()
                    if len(parts) >= 2:
                        short = " ".join(parts[:2])
                        self.click_button_by_text([short], timeout=2)
            time.sleep(0.4)
            
            # Bước 7: Click "Tiếp" / "Gửi" để hoàn tất
            self.click_next_action()
            time.sleep(0.6)
            
            # Thử click thêm một lần nữa (một số flow có 2 bước cuối)
            self.click_next_action()

            return True, "Quy trình báo cáo đã được thực hiện (kiểm tra UI để xác nhận)."

        except Exception as e:
            return False, f"Lỗi trong execute_report_flow: {str(e)}"

    def navigate_and_report(self, url, category, detail):
        """
        Điều hướng đến URL và thực hiện báo cáo.
        
        Parameters:
            url (str): Link bài viết hoặc Trang cần báo cáo
            category (str): Hạng mục chính
            detail (str): Chi tiết hành vi
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.driver:
            return False, "Browser chưa chạy"
        try:
            self.driver.get(url)
            # Chờ trang load
            time.sleep(1.2)
            ok, msg = self.execute_report_flow(category, detail)
            return ok, msg
        except Exception as e:
            return False, f"Lỗi navigate_and_report: {str(e)}"

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            if os.path.exists('proxy_auth_plugin.zip'):
                try:
                    os.remove('proxy_auth_plugin.zip')
                except Exception:
                    pass