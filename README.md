# 🚀 Ultimate SMS & Email Bomber v2.1 (Dual Engine Edition)

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20iOS%20%7C%20PC-green.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

A high-performance, interactive, and cross-platform bombing tool designed for **Termux (Android)**, **a-Shell (iOS)**, and **PC (Windows/Linux)**. This repository now offers two distinct versions: a classic threading-based version (v1) and a modern `asyncio`/`aiohttp`-based version (v2) for enhanced performance.

---

## 🌟 Key Features

### Version 1: Threading-based (sms_bomber_v1.py)

- **🔄 Interactive Mode**: Seamlessly switch between SMS and Email bombing.
- **♾️ Unlimited Mode**: Set limit to `0` for continuous bombing until manually stopped.
- **⚡ High Performance**: Supports up to **150 threads** for concurrent operations.
- **🛑 Smart Stop**: Press **Enter** to stop bombing and return to the main menu without exiting the script.
- **🕵️ Stealth & Security**:
  - **Auto-Proxy Scraper**: Automatically finds and uses free proxies.
  - **Proxy Tracker**: Real-time success/fail tracking for proxies.
  - **Random User-Agents**: Rotates device signatures to avoid detection.
  - **Smart Retry**: Automatically switches APIs on failure.
- **📊 Detailed Logging**: Live terminal logs and persistent file-based logging.

### Version 2: Asyncio & Aiohttp-based (sms_bomber_v2.py)

- **⚡ Extreme Performance (Asyncio & Aiohttp)**: Utilizes `asyncio` for highly efficient asynchronous operations and `aiohttp` for non-blocking HTTP requests, enabling superior concurrency and speed.
- **🔄 Interactive Mode**: Seamlessly switch between SMS and Email bombing.
- **♾️ Unlimited Mode**: Set limit to `0` for continuous bombing until manually stopped.
- **🛑 Smart Stop**: Press **Enter** to stop bombing and return to the main menu without exiting the script.
- **🕵️ Enhanced Stealth & Security**:
  - **VPN Recommended**: Explicitly advises users to use a VPN for optimal performance and to avoid IP bans. (Proxy system removed for simplicity and user control).
  - **Random User-Agents**: Rotates device signatures to avoid detection.
  - **Smart Retry**: Automatically handles API failures.
- **📊 Detailed & Clear Logging**: Live terminal logs with clear success/failure indicators and persistent file-based logging for comprehensive tracking.

---

## ⚠️ Important VPN Notice (for sms_bomber_v2.py)

For optimal performance, to maintain anonymity, and to prevent IP bans when using `sms_bomber_v2.py`, it is **highly recommended** to use a **VPN service** before running this tool. Please ensure your VPN is connected to a stable location before proceeding.

---

## 🛠️ Installation

First, clone the repository:
```bash
git clone https://github.com/Quincunx33/bomber-v2.git
cd bomber-v2
```

### For Version 1 (sms_bomber_v1.py - Threading-based)

Install dependencies:
```bash
pip install requests
```

### For Version 2 (sms_bomber_v2.py - Asyncio & Aiohttp-based)

Install dependencies:
```bash
pip install aiohttp
```

---

## 🚀 Usage Guide

### Using Version 1 (sms_bomber_v1.py)

1. **Launch**: Run `python sms_bomber_v1.py`.
2. **Select Mode**: Choose between SMS or Email bombing.
3. **Target**: Enter the phone number (e.g., `017xxxxxxxx`) or email address.
4. **Threads**: Enter the number of threads (Max 150).
5. **Proxy**: Choose your preferred proxy mode (Custom, Auto-Scrape, or None).
6. **Stop**: Press **Enter** at any time to stop and return to the menu.

### Using Version 2 (sms_bomber_v2.py)

1. **Launch**: Run `python sms_bomber_v2.py`.
2. **Select Mode**: Choose between SMS or Email bombing.
3. **Target**: Enter the phone number (e.g., `017xxxxxxxx`) or email address.
4. **Concurrency Level**: Enter the number of concurrent tasks (e.g., `50`).
5. **Stop**: Press **Enter** at any time to stop and return to the menu.

---

## ⚠️ Disclaimer

This tool is developed for **educational purposes only**. The developer is not responsible for any misuse or damage caused by this tool. Use it responsibly and at your own risk.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Quincunx33/bomber-v2/issues).

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

### #SMSBomber #EmailBomber #Python #Asyncio #Aiohttp #Threading #CyberSecurity #Termux #aShell #Automation
