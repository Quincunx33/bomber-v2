# Bomber-V2 🚀

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/Quincunx33/bomber-v2)](https://github.com/Quincunx33/bomber-v2/releases)

Bomber-V2 is an advanced, asynchronous, and highly configurable tool designed for security testing and educational purposes. It specializes in simulating SMS, Call, and Email bombing attacks, primarily targeting Bangladeshi numbers and email services. Built with `asyncio` and `aiohttp`, it ensures high-speed concurrent operations while incorporating intelligent mechanisms to bypass modern security systems and prevent IP bans.

## ✨ Features

*   **Asynchronous Engine**: Leverages Python's `asyncio` and `aiohttp` libraries to perform high-speed, concurrent requests, ensuring efficient and rapid execution of bombing tasks.
*   **Smart Cooldown System**: Features an intelligent cooldown mechanism that automatically detects and adapts to API rate limits. This system temporarily pauses requests to specific APIs upon encountering rate-limiting responses (e.g., HTTP 429), effectively preventing IP bans and ensuring sustained operation.
*   **Dynamic Stealth Headers**: Generates sophisticated and dynamic HTTP headers, including `User-Agent`, `Origin`, `Referer`, and advanced Client-Hints (`Sec-Ch-Ua`, `Sec-Ch-Ua-Mobile`, `Sec-Ch-Ua-Platform`). These headers mimic real user traffic from various platforms (Windows, Android, iOS, macOS, Linux) and browser versions, making it significantly harder for target systems to detect and block automated requests.
*   **Cross-Platform Compatibility**: Engineered to run seamlessly across multiple operating systems, including Windows, Linux (with Termux support), and iOS (via a-Shell), offering broad accessibility for users.
*   **Multi-Mode Operation**: Supports three distinct bombing modes: SMS, Call, and Email. It comes pre-integrated with over 180 APIs, providing a comprehensive suite for various testing scenarios.
*   **Smart Learning API Controller**: An innovative feature that learns the optimal data formats (e.g., `raw`, `880`, `+880`) for different APIs based on their success rates. This system intelligently explores various formats and prioritizes those that yield successful responses, enhancing the tool's effectiveness over time.
*   **Enhanced Logging System**: Provides a detailed and color-coded logging system that outputs real-time status updates to the console and records comprehensive logs to a file. This includes information on API name, status (SUCCESS/FAILED), status codes, and a snippet of the response text for failed attempts, aiding in debugging and analysis.
*   **External API Only Mode**: A new configuration option that allows users to disable all internal, pre-configured APIs and exclusively utilize custom external APIs. This provides greater flexibility and control for users who wish to integrate their own services or focus on specific testing targets.
*   **Professional Packaging**: The tool is designed for easy installation as a Python package via `pip`, simplifying deployment and management.

## 🚀 Installation & Usage

### From Source (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Quincunx33/bomber-v2.git
    cd bomber-v2
    ```

2.  **Install the package:**
    ```bash
    pip install .
    ```

3.  **Run the application:**
    After installation, the command `bomber-v2` will be available globally.
    ```bash
    bomber-v2
    ```

## ⚙️ Configuration

### External API Management

Bomber-V2 allows you to add and manage your own external APIs. This can be done through the interactive settings menu within the application.

1.  **Access Settings**: From the main menu, select `[5] Settings & AI Control`.
2.  **Manage External APIs**: Choose `[4] Manage External APIs`.
3.  **Add New API**: Select `[A] Add New API` and follow the prompts to enter the API Name, URL (use `{phone}` as a placeholder for the target number), Method (GET/POST), Mode (sms/call/email), and JSON Payload (for POST requests).
4.  **Toggle API Status**: You can connect/disconnect (enable/disable) existing external APIs using the `[T] Toggle Connect/Disconnect` option.

### External API Only Mode

To exclusively use external APIs and disable all built-in APIs:

1.  **Access Settings**: From the main menu, select `[5] Settings & AI Control`.
2.  **Toggle External API Only**: Select `[2] External API Only` to switch it `ON` or `OFF`.
    *   When `ON`, only your configured and enabled external APIs will be used.
    *   When `OFF`, both internal and external APIs will be utilized.

## 🛡 Disclaimer

This tool is created for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool. Use it at your own risk and only on targets you have explicit permission to test.

## 🤝 Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for details on how to get started.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
