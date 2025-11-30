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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import uuid
import config

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

    def start_browser(self, proxy_string=None, headless=False, language="vi"):
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
        options.add_argument("--blink-settings=imagesEnabled=false") # Disable images
        
        # Extra optimizations for speed and stability
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-device-discovery-notifications")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--password-store=basic")
        options.add_argument("--allow-running-insecure-content")
        
        # options.add_argument("--disable-extensions") # Moved down to avoid conflict with proxy extension
        options.add_argument("--ignore-certificate-errors") # Allow proxies with self-signed certs
        options.add_argument(f"--lang={language}") # Force language
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        # Block heavy content (Images, CSS, Fonts, JS if possible but we need JS)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 1,
            "profile.managed_default_content_settings.fonts": 1,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
        }
        options.add_experimental_option("prefs", prefs)

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080") # Desktop size
        else:
            options.add_argument("--window-size=1920,1080")

        binary_path = self.find_chrome_executable()
        if binary_path:
            options.binary_location = binary_path

        has_proxy_extension = False
        if proxy_string and proxy_string.strip():
            p_str = proxy_string.strip()
            # Remove protocol if present for parsing logic
            if "://" in p_str:
                p_str = p_str.split("://")[-1]

            user = password = host = port = None
            
            # Try parsing different formats
            if '@' in p_str:
                # Format: user:pass@host:port
                try:
                    auth, host_port = p_str.split('@', 1)
                    if ':' in auth and ':' in host_port:
                        user, password = auth.split(':', 1)
                        host, port = host_port.split(':', 1)
                except:
                    pass
            elif p_str.count(':') == 3:
                # Format: host:port:user:pass
                try:
                    parts = p_str.split(':')
                    host = parts[0]
                    port = parts[1]
                    user = parts[2]
                    password = parts[3]
                except:
                    pass
            
            if user and password and host and port:
                plugin_file = self.create_proxy_auth_extension(host, port, user, password)
                options.add_extension(plugin_file)
                has_proxy_extension = True
            else:
                # Format: host:port or invalid auth format -> try direct
                options.add_argument(f'--proxy-server={proxy_string.strip()}')

        if not has_proxy_extension:
            options.add_argument("--disable-extensions")

        try:
            # Cache driver path to avoid repeated checks
            if not globals().get('CACHED_DRIVER_PATH'):
                globals()['CACHED_DRIVER_PATH'] = ChromeDriverManager().install()
            
            service = Service(globals()['CACHED_DRIVER_PATH'])
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Enable CDP to block resources aggressively
            try:
                self.driver.execute_cdp_cmd('Network.enable', {})
                self.driver.execute_cdp_cmd('Network.setBlockedURLs', {
                    "urls": [
                        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.ico", 
                        "*.mp4", "*.avi", "*.webm",
                        "*google-analytics*", "*doubleclick*", "*facebook.com/tr/*"
                    ]
                })
            except:
                pass

            # Set timeouts to prevent hanging on slow/dead proxies
            self.driver.set_page_load_timeout(20)
            self.driver.set_script_timeout(10)
            
            return True, "Khởi tạo trình duyệt thành công"
        except Exception as e:
            return False, f"Lỗi khởi tạo Browser: {str(e)}"

    def reset_session(self):
        if self.driver:
            try:
                self.driver.delete_all_cookies()
                self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            except:
                pass

    def inject_cookies(self, raw_cookie_str):
        if not self.driver:
            return False, "Chưa khởi động trình duyệt"
        try:
            # 1. Ensure we are on facebook.com domain to set cookies
            # If we are already on a facebook page (from previous run), we don't need to reload.
            # If not, load a lightweight page to set domain context.
            current_url = self.driver.current_url
            if "facebook.com" not in current_url:
                try:
                    self.driver.get("https://www.facebook.com/robots.txt")
                except:
                    # If robots.txt fails, try root but stop quickly
                    self.driver.get("https://www.facebook.com/")
            
            # 2. Parse and add cookies
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
                    pass
            
            # 3. NO REFRESH, NO CHECK. Trust the cookie.
            # We will validate login status when we navigate to the target URL.
            return True, "Đã Inject Cookie"
            
        except Exception as e:
            return False, f"Lỗi Inject Cookie: {str(e)}"

    # ------------------ Helpers ------------------
    def smart_click(self, xpath, timeout=5):
        """Chờ element clickable rồi click bằng JS để ổn định hơn."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Try clickable first
            try:
                elem = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            except:
                # Fallback to presence + visibility if clickable fails
                elem = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            
            self.driver.execute_script("arguments[0].click();", elem)
            return True
        except Exception:
            return False

    def click_button_by_text(self, texts, timeout=3):
        """Thử click phần tử chứa một trong các texts."""
        # 1. Priority: Exact match on aria-label or role=button with text
        for t in texts:
            xpath_high_priority = (
                f"//div[@role='button'][@aria-label='{t}'] | "
                f"//div[@role='button'][.//span[normalize-space(.)='{t}']] | "
                f"//button[normalize-space(.)='{t}']"
            )
            if self.smart_click(xpath_high_priority, timeout=1):
                return True

        # 2. Fallback: Contains text, generic spans
        for t in texts:
            xpath_generic = (
                f"//span[contains(normalize-space(.), '{t}')] | "
                f"//div[@aria-label='{t}'] | "
                f"//button[.//span[contains(normalize-space(.), '{t}')]] | "
                f"//div[@role='button'][.//span[contains(normalize-space(.), '{t}')]] | "
                f"//div[@role='button'][contains(normalize-space(.), '{t}')]"
            )
            if self.smart_click(xpath_generic, timeout=timeout):
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

        # 0) PRIORITY: Try specific aria-label from user request (Profile settings 3-dots)
        # This fixes the issue where it clicks the first post's 3-dots instead of the Page's 3-dots.
        try:
            # "Xem thêm tùy chọn trong phần cài đặt trang cá nhân"
            specific_aria_vi = "Xem thêm tùy chọn trong phần cài đặt trang cá nhân"
            specific_aria_en = "See more options in profile settings" # Approximate English
            # User provided HTML shows it's a div with role='button'
            # Also added "Profile settings see more options" based on user snippet
            xpath_specific = f"//div[(@aria-label='{specific_aria_vi}' or @aria-label='{specific_aria_en}' or @aria-label='Profile settings see more options') and @role='button']"
            if self.smart_click(xpath_specific, timeout=2):
                return True, "Đã click nút 3 chấm (Profile Settings)"
        except Exception:
            pass

        # 0.5) Try finding the "More" tab/button specifically (common in English UI)
        try:
            # Based on user snippet: <div role="tab" ...> ... <span>More</span> ... </div>
            # Updated to include role='button' and exact text match for robustness
            # Also added direct aria-label check for role=tab
            xpath_more_tab = (
                "//div[@role='tab' or @role='button'][.//span[normalize-space(.)='More']] | "
                "//div[@role='tab'][@aria-label='More']"
            )
            if self.smart_click(xpath_more_tab, timeout=1):
                 return True, "Đã click nút More (Tab/Button)"
        except Exception:
            pass

        # 1) Try common aria-label/text variants (fast)
        variants = [
            "Hành động với bài viết này",
            "Actions for this post",
            "Xem thêm",
            "See more",
            "More",
            "Xem thêm tùy chọn",
            "More options",
            "Options",
            "Tùy chọn",
            "Thêm",
            "Khác",
            "See options"
        ]
        for v in variants:
            try:
                # match aria-label exactly or span text contains
                # Added role='tab' support
                xpath = f"//div[@aria-label='{v}'] | //button[@aria-label='{v}'] | //div[@role='tab'][@aria-label='{v}'] | //span[contains(normalize-space(.), '{v}')]"
                if self.smart_click(xpath, timeout=1):
                    return True, f"Đã click nút 3 chấm (variant='{v}')"
            except Exception:
                pass

        # 1.5) Try specific Profile/Page 3-dots (often just an icon in a div with role button)
        # Look for the button next to "Nhắn tin" (Message) or "Theo dõi" (Follow)
        try:
            # Find 'Nhắn tin' or 'Message' button, then look for the button next to it
            ref_xpath = "//div[@aria-label='Nhắn tin' or @aria-label='Message' or .//span[text()='Nhắn tin'] or .//span[text()='Message']]"
            ref_btn = self.driver.find_elements(By.XPATH, ref_xpath)
            if ref_btn:
                # Try to find a sibling button that contains an SVG (the 3 dots)
                # This is heuristic: usually the 3-dots is in the same container or a sibling container
                # We look for a nearby div/button with an SVG
                nearby_xpath = "(//div[@aria-label='Nhắn tin' or @aria-label='Message']/following::div[@role='button'][.//svg])[1]"
                if self.smart_click(nearby_xpath, timeout=1):
                     return True, "Đã click nút 3 chấm (cạnh nút Nhắn tin)"
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
    def execute_report_flow(self, category, detail, target_info=None, sub_detail=None):
        """
        Example flow:
         - find/click 3-dots
         - click 'Báo cáo' / 'Report'
         - choose category (category)
         - click Next
         - choose detail (detail)
         - click Next
         - (Optional) choose sub_detail (Level 3) -> click Next
         - (Optional) Input target info (Name/URL) -> Select -> Next
         - Submit
        """
        if not self.driver:
            return False, "Browser chưa chạy"

        try:
            ok, msg = self.find_and_click_three_dots()
            if not ok:
                return False, msg

            time.sleep(0.5)

            # click report button
            if not self.click_button_by_text(["Báo cáo trang", "Report Page", "Báo cáo", "Report", "Tìm hỗ trợ", "Find support", "Tìm hỗ trợ hoặc báo cáo", "Find support or report"]):
                return False, "Không click được nút Báo cáo sau khi mở menu"

            # wait a bit for popup
            # time.sleep(1.5)
            # Wait for dialog header or next option
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog'] | //div[@aria-label='Đóng' or @aria-label='Close']"))
                )
            except:
                pass

            # If popup asks "Bạn muốn báo cáo điều gì?" (Page-specific), try choose "Thông tin về trang này" or "Bài viết cụ thể"
            # We'll try to click "Thông tin về trang này" if present first (safe), user can choose correct category/detail in UI
            self.click_button_by_text(["Thông tin về trang này", "Something about this page", "Information about this Page", "Bài viết cụ thể", "A specific post", "Trang cá nhân", "Profile"])

            # Choose category (level 1)
            if category:
                cats = [category]
                if hasattr(config, 'TRANSLATIONS') and category in config.TRANSLATIONS:
                    cats.append(config.TRANSLATIONS[category])

                if not self.click_button_by_text(cats):
                    # try a normalized match (lowercase contains)
                    if not self.click_button_by_text([category.split()[0]]):
                        return False, f"Không tìm thấy hạng mục '{category}'"
            # time.sleep(0.5) # Removed sleep
            # Next
            self.click_next_action()
            # time.sleep(0.5) # Removed sleep

            # Choose detail (level 2)
            if detail:
                details = [detail]
                if hasattr(config, 'TRANSLATIONS') and detail in config.TRANSLATIONS:
                    details.append(config.TRANSLATIONS[detail])

                if not self.click_button_by_text(details, timeout=4):
                    # fallback: try partial words
                    parts = detail.split()
                    if len(parts) >= 2:
                        short = " ".join(parts[:2])
                        self.click_button_by_text([short], timeout=2)
            # time.sleep(0.4) # Removed sleep
            # Next
            self.click_next_action()
            
            # Choose sub_detail (level 3)
            if sub_detail:
                # Wait a bit for next screen
                time.sleep(0.5)
                subs = [sub_detail]
                if hasattr(config, 'TRANSLATIONS') and sub_detail in config.TRANSLATIONS:
                    subs.append(config.TRANSLATIONS[sub_detail])
                
                if not self.click_button_by_text(subs, timeout=4):
                     # fallback
                    parts = sub_detail.split()
                    if len(parts) >= 2:
                        short = " ".join(parts[:2])
                        self.click_button_by_text([short], timeout=2)
                
                time.sleep(0.5)
                self.click_next_action()

            # Handle Target Info Input (for Fake Page -> Friend/Celebrity/Business)
            if target_info:
                try:
                    wait = WebDriverWait(self.driver, 5)
                    # More specific XPaths based on user provided HTML
                    input_xpaths = [
                        "//input[@aria-label='Tên']",
                        "//input[@aria-label='Name']",
                        "//input[@aria-label='URL hoặc tên Trang Facebook']",
                        "//input[@aria-label='URL or Facebook Page name']",
                        "//input[@role='combobox'][@type='search']"
                    ]
                    
                    inp = None
                    for xp in input_xpaths:
                        try:
                            inp = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                            if inp: break
                        except:
                            continue
                    
                    if inp:
                        # Click to focus
                        try:
                            inp.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", inp)
                        
                        time.sleep(0.5)
                        
                        # Clear and Type
                        # React inputs sometimes need robust clearing
                        inp.send_keys(Keys.CONTROL + "a")
                        inp.send_keys(Keys.DELETE)
                        time.sleep(0.2)
                        inp.send_keys(target_info)
                        
                        # Wait for suggestions to load
                        time.sleep(2.5)
                        
                        # Try to select the first suggestion
                        # Method 1: Arrow Down + Enter
                        inp.send_keys(Keys.ARROW_DOWN)
                        time.sleep(0.5)
                        inp.send_keys(Keys.ENTER)
                        
                        # Method 2: If listbox appears, click the first item
                        # Facebook suggestions usually have role="option" or are in a listbox
                        try:
                            suggestion_xpath = "//ul[@role='listbox']//li | //div[@role='listbox']//div[@role='option'] | //div[contains(@class, 'x1n2onr6')][@role='button']" 
                            # This is a guess for the suggestion item. 
                            # Let's stick to Arrow Down + Enter as primary, but maybe do it twice if needed?
                            # Or check if aria-expanded becomes true?
                            pass
                        except:
                            pass

                        time.sleep(1)
                        
                        # Click Next after selecting
                        self.click_next_action()
                except Exception as e:
                    print(f"Error entering target info: {e}")
                    pass

            # Final Submit / Finish
            # Wait for the Submit button to appear clearly
            time.sleep(2.0) 
            
            # Try clicking Submit/Next/Done multiple times to ensure completion
            submit_clicked = False
            submit_texts = ["Gửi", "Submit", "Gửi báo cáo", "Submit Report"]
            
            for _ in range(5):
                # 1. Try clicking Submit
                if self.click_button_by_text(submit_texts, timeout=3):
                    submit_clicked = True
                    time.sleep(3) # Wait for submission to process
                
                # 2. If not found, maybe it's "Next" (Tiếp) leading to Submit?
                elif self.click_button_by_text(["Tiếp", "Next"], timeout=2):
                    time.sleep(1)
                    
                # 3. Check for "Done" (Xong) - means success
                elif self.click_button_by_text(["Xong", "Done", "Đóng", "Close"], timeout=2):
                    submit_clicked = True # Considered success
                    break
            
            if not submit_clicked:
                 # Last ditch effort: try to find any blue button in dialog?
                 # For now, just try one last time with longer timeout
                 if self.click_button_by_text(submit_texts, timeout=5):
                     submit_clicked = True
                 else:
                     # Try clicking the last button in the dialog (usually Submit/Confirm)
                     try:
                         last_btn_xpath = "(//div[@role='dialog']//div[@role='button'])[last()]"
                         if self.smart_click(last_btn_xpath, timeout=2):
                             submit_clicked = True
                     except:
                         pass
            
            if not submit_clicked:
                return False, "Không tìm thấy hoặc không click được nút Gửi (Submit)."

            return True, "Quy trình báo cáo đã được thực hiện (kiểm tra UI để xác nhận)."

        except Exception as e:
            return False, f"Lỗi trong execute_report_flow: {str(e)}"

    def navigate_and_report(self, url, category, detail, target_info=None, sub_detail=None):
        if not self.driver:
            return False, "Browser chưa chạy"
        
        # Retry mechanism for loading page
        for attempt in range(2):
            try:
                self.driver.get(url)
                
                # FAST CHECK: Login or Checkpoint?
                # We check this immediately. If we are redirected to login, cookie is dead.
                current_url = self.driver.current_url
                if "login" in current_url or "checkpoint" in current_url:
                     return False, "Cookie die hoặc Checkpoint"

                # Wait for body to ensure basic layout is present
                try:
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except:
                    pass
                
                # Check if "Report" button is already visible (e.g. on some Pages/Groups)
                if self.click_button_by_text(["Báo cáo trang", "Report Page", "Báo cáo", "Report", "Tìm hỗ trợ hoặc báo cáo"], timeout=3):
                     # If clicked directly, skip 3-dots
                     pass
                else:
                     ok, msg = self.execute_report_flow(category, detail, target_info, sub_detail)
                     if not ok:
                         if attempt < 1: # If first attempt failed, refresh and try again
                             continue
                         return ok, msg
                     return True, msg
                
                # If we clicked "Report" directly above, continue flow
                # time.sleep(0.5) # Removed sleep
                self.click_button_by_text(["Thông tin về trang này", "Something about this page", "Information about this Page", "Bài viết cụ thể", "A specific post", "Trang cá nhân", "Profile"])
                
                # Choose category (level 1)
                if category:
                    cats = [category]
                    if hasattr(config, 'TRANSLATIONS') and category in config.TRANSLATIONS:
                        cats.append(config.TRANSLATIONS[category])

                    if not self.click_button_by_text(cats):
                        if not self.click_button_by_text([category.split()[0]]):
                            return False, f"Không tìm thấy hạng mục '{category}'"
                # time.sleep(0.2) # Removed sleep
                self.click_next_action()
                # time.sleep(0.2) # Removed sleep

                # Choose detail (level 2)
                if detail:
                    details = [detail]
                    if hasattr(config, 'TRANSLATIONS') and detail in config.TRANSLATIONS:
                        details.append(config.TRANSLATIONS[detail])

                    if not self.click_button_by_text(details, timeout=2):
                        parts = detail.split()
                        if len(parts) >= 2:
                            short = " ".join(parts[:2])
                            self.click_button_by_text([short], timeout=1)
                # time.sleep(0.2) # Removed sleep
                self.click_next_action()

                # Choose sub_detail (level 3)
                if sub_detail:
                    # Wait a bit for next screen
                    time.sleep(0.5)
                    subs = [sub_detail]
                    if hasattr(config, 'TRANSLATIONS') and sub_detail in config.TRANSLATIONS:
                        subs.append(config.TRANSLATIONS[sub_detail])
                    
                    if not self.click_button_by_text(subs, timeout=4):
                        # fallback
                        parts = sub_detail.split()
                        if len(parts) >= 2:
                            short = " ".join(parts[:2])
                            self.click_button_by_text([short], timeout=2)
                    
                    time.sleep(0.5)
                    self.click_next_action()
                
                # Handle Target Info Input (for Fake Page -> Friend/Celebrity/Business)
                if target_info:
                    try:
                        wait = WebDriverWait(self.driver, 5)
                        # More specific XPaths based on user provided HTML
                        input_xpaths = [
                            "//input[@aria-label='Tên']",
                            "//input[@aria-label='URL hoặc tên Trang Facebook']",
                            "//input[@role='combobox'][@type='search']"
                        ]
                        
                        inp = None
                        for xp in input_xpaths:
                            try:
                                inp = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                                if inp: break
                            except:
                                continue
                        
                        if inp:
                            # Click to focus
                            try:
                                inp.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", inp)
                            
                            time.sleep(0.5)
                            
                            # Clear and Type
                            # React inputs sometimes need robust clearing
                            inp.send_keys(Keys.CONTROL + "a")
                            inp.send_keys(Keys.DELETE)
                            time.sleep(0.2)
                            inp.send_keys(target_info)
                            
                            # Wait for suggestions to load
                            time.sleep(2.5)
                            
                            # Try to select the first suggestion
                            # Method 1: Arrow Down + Enter
                            inp.send_keys(Keys.ARROW_DOWN)
                            time.sleep(0.5)
                            inp.send_keys(Keys.ENTER)
                            
                            time.sleep(1)
                            
                            # Click Next after selecting
                            self.click_next_action()
                    except Exception as e:
                        print(f"Error entering target info: {e}")
                        pass

                # Final Submit / Finish
                # Wait for the Submit button to appear clearly
                time.sleep(2.0) 
                
                # Try clicking Submit/Next/Done multiple times to ensure completion
                submit_clicked = False
                submit_texts = ["Gửi", "Submit", "Gửi báo cáo", "Submit Report"]
                
                for _ in range(5):
                    # 1. Try clicking Submit
                    if self.click_button_by_text(submit_texts, timeout=3):
                        submit_clicked = True
                        time.sleep(3) # Wait for submission to process
                    
                    # 2. If not found, maybe it's "Next" (Tiếp) leading to Submit?
                    elif self.click_button_by_text(["Tiếp", "Next"], timeout=2):
                        time.sleep(1)
                        
                    # 3. Check for "Done" (Xong) - means success
                    elif self.click_button_by_text(["Xong", "Done", "Đóng", "Close"], timeout=2):
                        submit_clicked = True # Considered success
                        break
                
                if not submit_clicked:
                     # Last ditch effort
                     if self.click_button_by_text(submit_texts, timeout=5):
                         submit_clicked = True
                     else:
                         # Try clicking the last button in the dialog (usually Submit/Confirm)
                         try:
                             last_btn_xpath = "(//div[@role='dialog']//div[@role='button'])[last()]"
                             if self.smart_click(last_btn_xpath, timeout=2):
                                 submit_clicked = True
                         except:
                             pass
                
                if not submit_clicked:
                    return False, "Không tìm thấy hoặc không click được nút Gửi (Submit)."

                return True, "Quy trình báo cáo đã được thực hiện (kiểm tra UI để xác nhận)."

            except Exception as e:
                if attempt < 1:
                    continue
                return False, f"Lỗi navigate_and_report: {str(e)}"
        
        return False, "Không thể tải trang hoặc tìm nút báo cáo sau 2 lần thử"

    def get_screenshot_base64(self):
        # This method is called from UI thread, but driver is in worker thread.
        # Selenium is not thread-safe.
        # However, if we just read a cached value, it's safe.
        # But we don't have a cached value yet.
        # For now, we will try to grab it, but suppress errors.
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