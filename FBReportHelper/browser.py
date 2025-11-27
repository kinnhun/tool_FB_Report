# browser.py
import time
import zipfile
import os
import shutil
import platform
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import uuid

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.plugin_file = None

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
        
        # Use tempfile to avoid file conflicts and IO lag in current dir
        t = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        self.plugin_file = t.name
        t.close()
        
        with zipfile.ZipFile(self.plugin_file, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return self.plugin_file

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

    def start_browser(self, proxy_string=None, headless=False):
        global CACHED_DRIVER_PATH
        
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        
        # Performance Optimizations - Aggressive
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-extensions") # Disable all extensions by default (except proxy if added)
        
        # Block heavy content (Images, CSS, Fonts, JS if possible but we need JS)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_settings.popups": 0,
        }
        options.add_experimental_option("prefs", prefs)

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=800,600") # Minimal size

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
            # Cache driver path to avoid repeated checks
            if not globals().get('CACHED_DRIVER_PATH'):
                globals()['CACHED_DRIVER_PATH'] = ChromeDriverManager().install()
            
            service = Service(globals()['CACHED_DRIVER_PATH'])
            self.driver = webdriver.Chrome(service=service, options=options)
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
        keywords = ["Tiếp", "Next", "Gửi", "Submit", "Xong", "Done"]
        return self.click_button_by_text(keywords, timeout=2)

    # ------------------ Robust 3-dots finder ------------------
    def find_and_click_three_dots(self):
        """
        Robust method to find & click the three-dot menu:
        - Try aria-label / text variants
        - Try SVG detection: look for <svg> that contains 3 <circle> elements and click it (or its clickable ancestor)
        - Fallback tries: any clickable element with title/aria-label containing 'More' / 'Tùy' / 'Hành động'
        """
        if not self.driver:
            return False, "Browser chưa chạy"

        wait = WebDriverWait(self.driver, 4)

        # 1) Try common aria-label/text variants (fast)
        variants = [
            "Hành động với bài viết này",
            "Actions for this post",
            "More",
            "Xem thêm tùy chọn",
            "More options",
            "Options",
            "Tùy chọn",
            "Thêm"
        ]
        for v in variants:
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
        Example flow:
         - find/click 3-dots
         - click 'Báo cáo' / 'Report'
         - choose category (category)
         - click Next
         - choose detail (detail)
         - click Next / Submit
        """
        if not self.driver:
            return False, "Browser chưa chạy"

        try:
            ok, msg = self.find_and_click_three_dots()
            if not ok:
                return False, msg

            time.sleep(0.5)

            # click report button
            if not self.click_button_by_text(["Báo cáo", "Report", "Tìm hỗ trợ", "Find support"]):
                return False, "Không click được nút Báo cáo sau khi mở menu"

            # wait a bit for popup
            time.sleep(0.8)

            # If popup asks "Bạn muốn báo cáo điều gì?" (Page-specific), try choose "Thông tin về trang này" or "Bài viết cụ thể"
            # We'll try to click "Thông tin về trang này" if present first (safe), user can choose correct category/detail in UI
            self.click_button_by_text(["Thông tin về trang này", "Information about this Page", "Bài viết cụ thể", "A specific post"])

            # Choose category (level 1)
            if category:
                if not self.click_button_by_text([category]):
                    # try a normalized match (lowercase contains)
                    if not self.click_button_by_text([category.split()[0]]):
                        return False, f"Không tìm thấy hạng mục '{category}'"
            time.sleep(0.5)
            # Next
            self.click_next_action()
            time.sleep(0.5)

            # Choose detail (level 2)
            if detail:
                if not self.click_button_by_text([detail], timeout=4):
                    # fallback: try partial words
                    parts = detail.split()
                    if len(parts) >= 2:
                        short = " ".join(parts[:2])
                        self.click_button_by_text([short], timeout=2)
            time.sleep(0.4)
            # Next / Submit
            self.click_next_action()
            time.sleep(0.6)
            # Final try
            self.click_next_action()

            return True, "Quy trình báo cáo đã được thực hiện (kiểm tra UI để xác nhận)."

        except Exception as e:
            return False, f"Lỗi trong execute_report_flow: {str(e)}"

    def navigate_and_report(self, url, category, detail):
        if not self.driver:
            return False, "Browser chưa chạy"
        try:
            self.driver.get(url)
            # short wait for page render; heavier waits occur in smart_click
            time.sleep(1.2)
            ok, msg = self.execute_report_flow(category, detail)
            return ok, msg
        except Exception as e:
            return False, f"Lỗi navigate_and_report: {str(e)}"

    def get_screenshot_base64(self):
        if self.driver:
            try:
                return self.driver.get_screenshot_as_base64()
            except:
                return None
        return None

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        
        if self.plugin_file and os.path.exists(self.plugin_file):
            try:
                os.remove(self.plugin_file)
            except Exception:
                pass
            self.plugin_file = None