<div align="center">

# 🐉 Oculus Draco - Security OSINT & Audit Tool

![Version](https://img.shields.io/badge/Version-v2--Beast_Mode-blue.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success.svg?style=for-the-badge)
![Category](https://img.shields.io/badge/Category-OSINT%20%7C%20DAST-orange.svg?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)

```text
██████  ██████  ██  ██  ██      ██  ██  ██████ 
██  ██  ██      ██  ██  ██      ██  ██  ██     
██  ██  ██      ██  ██  ██      ██  ██  ██████ 
██  ██  ██      ██  ██  ██      ██  ██      ██ 
██████  ██████  ██████  ██████  ██████  ██████



Extended Description: The Ultimate OSINT & DAST Framework
Modern security auditing requires speed, precision, and the ability to correlate vast amounts of data in real-time. Oculus Draco v2 is an advanced, ultra-aggressive Open Source Intelligence (OSINT) and Dynamic Application Security Testing (DAST) framework built for Red Teamers, Bug Bounty hunters, and Security Researchers.

Unlike traditional sequential scanners, Oculus Draco operates on a highly optimized, multi-threaded concurrent engine. It deploys 25 tactical modules simultaneously to map target infrastructure, extract hidden endpoints, identify sensitive data leaks, and test for active vulnerabilities all within seconds.

Core Capabilities:

Deep OSINT Extraction: Aggressive DOM parsing to uncover hidden emails, internal endpoints, exposed API routes, and hardcoded secrets (AWS Keys, JWT tokens, API keys).

Vulnerability Assessment: Automated, heuristic payload injection to detect critical flaws such as SQL Injection (SQLi), Cross-Site Scripting (XSS), and Local File Inclusion (LFI).

Infrastructure Mapping: Comprehensive reconnaissance including BGP/ASN routing, DNS intelligence, WAF/CDN detection, and native TCP port scanning.

Zero-Dependency Fallback: Engineered to be resilient. If external binaries or modules are missing from the host system, the framework seamlessly pivots to native Python TCP/Socket probes to ensure the audit is never interrupted.

Oculus Draco eliminates the noise. It replaces convoluted outputs with a sleek, Rich-powered terminal dashboard that delivers actionable intelligence, severity scorings, and a fully structured JSON/Markdown forensic report upon completion.

Installation:

git clone [https://github.com/Shieldxpert/Oculus-Draco.git](https://github.com/Shieldxpert/Oculus-Draco.git)
cd Oculus-Draco

Install the required dependencies:

pip install -r requirements.txt

Or install manually: pip install requests beautifulsoup4 rich dnspython

Usage

Run the framework directly from your terminal:

python oculus_draco.py

⚠️ Disclaimer:

Oculus Draco is designed exclusively for educational purposes and for authorized security audits. The developer assumes no responsibility and shall not be held liable for any misuse or damage caused by this program. Always obtain explicit, mutual, and authorized consent before scanning a target. Operates within the framework of the GDPR, the NIS2 Directive, the CFAA, and the Safe Harbor principles.
