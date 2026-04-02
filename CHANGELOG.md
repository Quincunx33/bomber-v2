# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-04-02

### Added
- Professional Python package structure (`src/` layout).
- Modern packaging with `pyproject.toml`.
- Automated release workflow using GitHub Actions.
- Global console script `bomber-v2`.
- Enhanced HTTP headers (Origin, Referer, Sec-Ch-Ua) for all APIs.
- Staggered request delays to avoid detection.
- Functional cooldown system for failed APIs.

### Changed
- Renamed `sms_bomber_updated.py` to `src/bomber_v2/main.py`.
- Updated `README.md` with professional installation instructions.

### Fixed
- Cooldown system not populating failed APIs.
- Missing Referer and Origin headers in API requests.

## [2.0.0] - 2024-01-01

### Added
- Initial release of Bomber-V2 with SMS, Call, and Email support.
- Asynchronous engine using `aiohttp`.
- Basic jitter and retry logic.
