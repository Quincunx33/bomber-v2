# Advanced SMS & Email Bomber (v2.1)

A high-performance, cross-platform bombing tool designed for iOS (a-Shell), Android (Termux), Windows, and Linux.

## New Features in v2.1
- **Smart Stop System**: Press **Enter** to stop bombing and return to the main menu without exiting the project.
- **Unlimited Mode**: Set limit to `0` for continuous bombing.
- **High Thread Support**: Supports up to **150 threads** for maximum speed.
- **Full Logging**: Real-time terminal logging without clearing history, plus detailed file logs.
- **Advanced Proxy System**: Auto-scrapes from multiple sources and tracks proxy success/fail rates.
- **Multi-Platform**: Optimized for mobile and PC terminal environments.
- **Smart Retry**: Automatically retries with different APIs on failure.

## Features
- **SMS Bombing**: Using high-quality Bangladesh-based APIs.
- **Email Bombing**: Using global and local email APIs.
- **Professional Stealth & Reliability**:
  - **Smart Retry System**: Automatically switches to a different API if one fails.
  - **Session Management**: Uses persistent sessions to handle cookies and headers.
  - **Detailed Logging**: Every attempt is logged with timestamps and status codes.
  - **Random User-Agents**: Rotates device signatures (iPhone, Android, Windows, Mac).
  - **Auto-Proxy Scraper**: Automatically finds and uses free proxies.
  - **Request Jittering**: Adds random delays to mimic human behavior.
- **Multi-threaded**: High-speed execution (up to 150 threads).
- **Cross-Platform**: 100% compatible with iOS, Android, Windows, and Linux.

## Installation & Usage

### 1. Android (Termux)
```bash
pkg update && pkg upgrade
pkg install python
pip install requests
python sms_bomber.py
```

### 2. iOS (a-Shell)
- Install **a-Shell** from the App Store.
- Open a-Shell and run:
```bash
pip install requests
python sms_bomber.py
```

### 3. Windows
- Install [Python](https://www.python.org/downloads/).
- Open CMD or PowerShell and run:
```bash
pip install requests
python sms_bomber.py
```

### 4. Linux
```bash
sudo apt update && sudo apt install python3 python3-pip
pip3 install requests
python3 sms_bomber.py
```

## Usage
1. Run the script: `python sms_bomber.py`
2. Select Mode (SMS or Email).
3. Enter Target (Phone number or Email).
4. Enter Limit (`0` for continuous).
5. Enter Thread Count (up to 150).
6. Select Proxy Mode.
7. **Press Enter** to stop bombing and return to the menu.
8. Select **E** in the main menu to exit the project.

## Disclaimer
This tool is for educational purposes only. The creator is not responsible for any misuse. Use it at your own risk.
