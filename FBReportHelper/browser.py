# browser.py
import time
import random
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

class BrowserManager:
    def __init__(self):
        self.driver = None

    # --- Phần Proxy & Tìm Chrome (Giữ nguyên như cũ) ---
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
            if path: return path
        if platform.system() == "Windows":
            possible = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
            for p in possible:
                if os.path.exists(p): return p
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
                auth, host_port = p_str.split('@')
                user, password = auth.split(':')
                host, port = host_port.split(':')
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
        if not self.driver: return False, "Chưa khởi động trình duyệt"
        try:
            self.driver.get("https://www.facebook.com/")
            cookies = []
            raw_cookie_str = raw_cookie_str.replace('Cookie:', '').strip()
            pairs = raw_cookie_str.split(';')
            for pair in pairs:
                if '=' in pair:
                    name, value = pair.strip().split('=', 1)
                    cookies.append({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com', 'path': '/'})
            for c in cookies:
                try: self.driver.add_cookie(c)
                except: pass
            self.driver.refresh()
            time.sleep(3)
            if "login" not in self.driver.current_url: return True, "Đã Inject Cookie & Login OK"
            else: return False, "Inject xong nhưng chưa Login được"
        except Exception as e: return False, f"Lỗi Inject Cookie: {str(e)}"

    # --- PHẦN QUAN TRỌNG: AUTOMATION REPORT ---

    def auto_report_process(self, category_text):
        """
        Hàm thực hiện chuỗi hành động báo cáo tự động
        category_text: Nội dung lấy từ ComboBox UI (ví dụ: "Spam", "Bạo lực"...)
        """
        try:
            wait = WebDriverWait(self.driver, 5)

            # BƯỚC 1: Click 3 chấm
            print("Đang tìm nút 3 chấm...")
            xpath_3dots = "//div[@aria-label='Hành động với bài viết này' or @aria-label='Actions for this post' or @aria-label='More' or @aria-label='Xem thêm tùy chọn']"
            try:
                btn_3dots = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_3dots)))
                btn_3dots.click()
            except:
                return False, "Không thấy nút 3 chấm (có thể do mạng hoặc layout khác)"
            
            time.sleep(2) # Chờ menu xổ ra

            # BƯỚC 2: Click dòng "Báo cáo" / "Tìm hỗ trợ"
            print("Đang tìm nút Báo cáo trong menu...")
            xpath_report = "//span[contains(text(), 'Báo cáo') or contains(text(), 'Report') or contains(text(), 'Find support') or contains(text(), 'Tìm hỗ trợ')]"
            try:
                btn_report = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_report)))
                btn_report.click()
            except:
                return False, "Không thấy nút Báo cáo trong menu"

            time.sleep(3) # Chờ popup hiện ra

            # BƯỚC 3: Chọn Lý do từ Popup
            # Mapping từ UI Category sang text keyword trên Facebook
            # FB text có thể là: "Spam", "Bạo lực", "Hàng giả", "Bán hàng cấm"...
            # Ta sẽ dùng thuật toán tìm text gần đúng (contains)
            
            print(f"Đang tìm lý do: {category_text}")
            
            # Xử lý mapping từ text UI sang keyword tìm kiếm trên FB
            search_keyword = category_text
            if "người lớn" in category_text.lower(): search_keyword = "khỏa thân" # FB thường dùng từ "Khỏa thân" hoặc "Ảnh khỏa thân"
            elif "lừa đảo" in category_text.lower(): search_keyword = "Lừa đảo"
            elif "bạo lực" in category_text.lower(): search_keyword = "Bạo lực"
            elif "bắt nạt" in category_text.lower(): search_keyword = "Bắt nạt"
            elif "thông tin sai" in category_text.lower(): search_keyword = "Thông tin sai"
            elif "bán hàng" in category_text.lower(): search_keyword = "Bán hàng"

            # Tìm thẻ chứa text lý do (thường là span hoặc div trong role='button' hoặc listitem)
            xpath_reason = f"//span[contains(text(), '{search_keyword}')]"
            
            try:
                btn_reason = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_reason)))
                btn_reason.click()
            except:
                return False, f"Không tìm thấy lý do '{search_keyword}' trong popup FB. Hãy chọn tay."

            time.sleep(1)

            # BƯỚC 4: Bấm nút "Gửi" (Submit) hoặc "Tiếp" (Next)
            print("Đang tìm nút Gửi...")
            # Nút submit thường có aria-label="Gửi" hoặc text là Gửi
            xpath_submit = "//div[@aria-label='Gửi' or @aria-label='Submit' or text()='Gửi' or text()='Submit' or @aria-label='Tiếp' or text()='Tiếp']"
            
            try:
                # Đôi khi phải scroll xuống nút submit nếu popup dài
                btn_submit = wait.until(EC.presence_of_element_located((By.XPATH, xpath_submit)))
                self.driver.execute_script("arguments[0].click();", btn_submit) # Click bằng JS cho chắc
                return True, f"Đã chọn '{category_text}' và bấm Gửi thành công!"
            except:
                return True, "Đã chọn lý do, nhưng không bấm được nút Gửi (hãy bấm tay bước cuối)."

        except Exception as e:
            return False, f"Lỗi Auto Report: {str(e)}"

    def navigate_to(self, url, category_ui_text, is_random=False):
        """
        Nhận thêm tham số category_ui_text để biết người dùng muốn report thể loại gì
        """
        if not self.driver: return False, "Browser chưa chạy"
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            target_url = url
            
            if is_random:
                self.driver.execute_script("window.scrollTo(0, 1000);")
                time.sleep(2)
                links = self.driver.find_elements(By.TAG_NAME, "a")
                valid_links = []
                for link in links:
                    href = link.get_attribute('href')
                    if href and any(x in href for x in ['/posts/', '/videos/', '/photos/', 'fbid=']):
                        valid_links.append(href)
                
                if valid_links:
                    target_url = random.choice(valid_links)
                    self.driver.get(target_url)
                    time.sleep(3)

            # BẮT ĐẦU QUY TRÌNH REPORT TỰ ĐỘNG
            status, msg = self.auto_report_process(category_ui_text)
            
            if is_random:
                return status, f"Random bài {target_url} -> {msg}"
            else:
                return status, f"Link {target_url} -> {msg}"
            
        except Exception as e:
            return False, f"Lỗi điều hướng: {str(e)}"

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            if os.path.exists('proxy_auth_plugin.zip'):
                try: os.remove('proxy_auth_plugin.zip')
                except: pass