import os
import sys
import json
import time
import re
import socket
import ssl
import base64
import hashlib
import argparse
import subprocess
import threading
import random
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

MISSING_LIBS = []
try:
    import requests
except ImportError:
    MISSING_LIBS.append("requests")

try:
    from bs4 import BeautifulSoup
except ImportError:
    MISSING_LIBS.append("beautifulsoup4")

try:
    from rich.console import Console
    from rich.text import Text
except ImportError:
    MISSING_LIBS.append("rich")

try:
    import dns.resolver as dns_res
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False

if MISSING_LIBS:
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n\033[91m[!] ERROR CRITICO: FALTAN LIBRERIAS PARA EL MOTOR OCULUS DRACON\033[0m")
    print(f"\033[93mFaltan: {', '.join(MISSING_LIBS)}\033[0m\n")
    print("\033[97mInstala las dependencias con:\033[0m")
    print("\033[1m\033[92m    pip install requests beautifulsoup4 rich dnspython\033[0m\n")
    input("\033[96mPresiona ENTER para salir...\033[0m")
    sys.exit(1)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()

C_CYAN    = "\033[96m"
C_ORANGE  = "\033[38;5;208m"
C_END     = "\033[0m"

D_PROV_B64 = "aGFja2VydGFyZ2V0LmNvbQ=="

MODULE_NAMES = {
    "m01": "Network Infra", "m02": "Service Banners", "m03": "DNS Intel",
    "m04": "WAF Security", "m05": "OS Fingerprint", "m06": "Path Fuzzing",
    "m07": "Endpoints", "m08": "Emails & Users", "m09": "SQL Injection",
    "m10": "XSS Audit", "m11": "LFI Traversal", "m12": "API Routes",
    "m13": "Malware Scan", "m14": "SSL Audit", "m15": "Headers",
    "m16": "Mail Security", "m17": "JS Secrets", "m18": "WHOIS Data",
    "m19": "Auth Surface", "m20": "CORS & Redirects", "m21": "Metadata",
    "m22": "Stack Profiling", "m23": "Port Scanner", "m24": "Form Extractor",
    "m25": "Protocol Enum"
}

def silent_setup():
    try:
        if platform.system() == "Windows":
            os.system('cls')
            os.system('') 
        else:
            os.system('clear')
    except:
        pass

def get_beast_ascii():
    return r"""
┌──────────────────────────────────────────────────────────────────────────────┐
│                 O C U L U S   D R A C O N  SHIELDXPERT                  │
│                                                                              │
│  $$$$$$\   $$$$$$\  $$\   $$\ $$\       $$\   $$\  $$$$$$\                 │
│ $$  __$$\ $$  __$$\ $$ |  $$ |$$ |      $$ |  $$ |$$  __$$\                │
│ $$ /  $$ |$$ /  \__|$$ |  $$ |$$ |      $$ |  $$ |$$ /  \__|               │
│ $$ |  $$ |$$ |      $$ |  $$ |$$ |      $$ |  $$ |\$$$$$$\                 │
│ $$ |  $$ |$$ |      $$ |  $$ |$$ |      $$ |  $$ | \____$$\                │
│ $$ |  $$ |$$ |  $$\ $$ |  $$ |$$ |      $$ |  $$ |$$\   $$ |               │
│  $$$$$$  |\$$$$$$  |\$$$$$$  |$$$$$$$$\ \$$$$$$  |\$$$$$$  |               │
│  \______/  \______/  \______/ \________| \______/  \______/                │
│                                                                              │
│  $$$$$$$\  $$$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\  $$\   $$\               │
│ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$$\  $$ |               │
│ $$ |  $$ |$$ |  $$ |$$ /  $$ |$$ /  \__|$$ /  $$ |$$$$\ $$ |               │
│ $$ |  $$ |$$$$$$$  |$$$$$$$$ |$$ |      $$ |  $$ |$$ $$\$$ |               │
│ $$ |  $$ |$$  __$$< $$  __$$ |$$ |      $$ |  $$ |$$ \$$$$ |               │
│ $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$\ $$ |  $$ |$$ |\$$$ |               │
│ $$$$$$$  |$$ |  $$ |$$ |  $$ |\$$$$$$  | $$$$$$  |$$ | \$$ |               │
│ \_______/ \__|  \__|\__|  \__| \______/  \______/ \__|  \__|               │
│                                                                            │
│  OCULUS DRACON ᴬ ᵠᵘⁱᵉᵗ ˡⁱⁿᵏ ʸᵒᵘ ᵇᵃʳᵉˡʸ ˢᵉᵉ, ʰⁱᵈᵉˢ ᵗʰᵉ ᵍʳᵉᵃᵗᵉˢᵗ ᵐʸˢᵗᵉʳʸ·    │
└──────────────────────────────────────────────────────────────────────────────┘
"""

def print_menu():
    console.print("\n[cyan]Choose feature set (public-only, legal):[/]")
    for i in range(1, 26):
        mid = f"m{i:02d}"
        console.print(f"[cyan]{i}) {MODULE_NAMES[mid]}[/]")
    console.print("[cyan]A) Run All Modules (Beast Mode)[/]")
    console.print("[cyan]0) Exit[/]\n")

class OculusEngine:
    def __init__(self, target, threads=25, output=None):
        self.target = target.replace("http://", "").replace("https://", "").split("/")[0]
        self.base_url = f"https://{self.target}"
        self.threads = threads
        self.output_file = output or f"DRACON_FULL_{self.target}.json"
        self.results = {}
        self.lock = threading.Lock()
        self.print_lock = threading.Lock()
        self.ip = None
        self.html = ""
        self.headers = {}
        self.malware_exts = [".exe", ".msi", ".bat", ".cmd", ".ps1", ".vbs", ".scr", ".zip", ".rar", ".apk", ".doc", ".pdf", ".sql", ".tar.gz", ".bak", ".swp", ".old", ".log"]
        self.sub_list = ["www", "dev", "api", "admin", "mail", "vpn", "test", "staging", "git", "portal", "cloud", "m", "blog", "shop", "secure", "ftp", "cdn", "beta", "web", "smtp", "pop", "ns1", "ns2", "host", "cpanel", "webmail", "remote", "gw", "exchange", "autodiscover", "app", "docs", "support"]
        self.fuzz_list = ["admin", "login", ".env", ".git/config", "backup", "db", "api", "robots.txt", "wp-admin", "cpanel", "server-status", ".DS_Store", "phpinfo.php", "setup.php", "config.php", "sitemap.xml", "wp-config.php", "swagger", "graphql", "admin.php", "login.php", "backup.sql", "database.sql", "test.php", ".ssh/id_rsa", "docker-compose.yml", "package.json", "composer.json"]
        self.flagged_count = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Oculus-Dracon/v24.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

    def fetch_base(self):
        if not self.html:
            try:
                r = self.session.get(self.base_url, timeout=8, verify=False)
                self.html = r.text
                self.headers = dict(r.headers)
            except:
                try:
                    r = self.session.get(f"http://{self.target}", timeout=8)
                    self.html = r.text
                    self.headers = dict(r.headers)
                except: pass

    def log_res(self, mid, data):
        with self.lock:
            self.results[mid] = data

    def print_finding(self, name, main_text, severity, detail):
        if severity == "HIGH":
            bar = "[bold white]██████████[/][bold red] 99% [/]"
        elif severity == "MEDIUM":
            bar = "[bold white]██████[/][grey50]░░░░[/][bold orange3] 60% [/]"
        elif severity == "LOW":
            bar = "[bold white]███[/][grey50]░░░░░░░[/][bold yellow] 30% [/]"
        else:
            bar = "[bold white]██████████[/][bold cyan] OK  [/]"

        with self.print_lock:
            console.print(f"[bold green][+][/] {name:<18} [white]{str(main_text)[:75]}[/]")
            console.print(f"    [bold deep_sky_blue1]severity :[/] [{bar}]  [bold orange3]({detail})[/]")

    def mod_01(self):
        try:
            self.ip = socket.gethostbyname(self.target)
            d_prov = base64.b64decode(D_PROV_B64).decode()
            try:
                data = self.session.get(f"https://ipwho.is/{self.ip}", timeout=4).json()
                asn = data.get('connection', {}).get('asn', 'ASN Unknown')
                isp = data.get('connection', {}).get('isp', 'ISP Unknown')
                city = data.get('city', 'Unknown City')
            except:
                asn = "Direct Routing"
                isp = "Unidentified Provider"
                city = "Global"
            return {"ip": self.ip, "asn": asn, "isp": isp, "city": city}
        except: return {"status": "Unresolved Domain"}

    def mod_02(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            if s.connect_ex((self.ip, 80)) == 0:
                s.send(b"HEAD / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                banner = s.recv(1024).decode(errors='ignore').split('\r\n')[0]
                s.close()
                if banner: return banner
            return "HTTP 200 OK (Inferred)"
        except: return "Connection Refused / Filtered"

    def mod_03(self):
        found = []
        if HAS_DNSPYTHON:
            try:
                for qtype in ['A', 'MX', 'NS']:
                    try:
                        answers = dns_res.resolve(self.target, qtype)
                        for rdata in answers:
                            found.append(f"{rdata}")
                    except: pass
            except: pass
        
        def check(s):
            try:
                sub = f"{s}.{self.target}"
                socket.gethostbyname(sub)
                return sub
            except: return None
            
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futs = [ex.submit(check, s) for s in self.sub_list]
            for f in as_completed(futs):
                if f.result() and f.result() not in found: found.append(f.result())
        
        if not found: found.append(f"www.{self.target}")
        return found

    def mod_04(self):
        h = str(self.headers).lower()
        wafs = {'cloudflare': 'Cloudflare', 'akamai': 'Akamai', 'sucuri': 'Sucuri', 'incap': 'Imperva', 'f5': 'F5 Big-IP', 'awselb': 'AWS CloudFront', 'x-powered-by': 'Custom Proxy'}
        for sig, name in wafs.items():
            if sig in h: return name
        return "Direct Routing (No WAF Detected)"

    def mod_05(self):
        srv = self.headers.get('Server', 'Unknown HTTP Server')
        os_est = "Windows" if any(x in srv.lower() for x in ["iis", "microsoft"]) else "Linux/Unix" if srv != "Unknown HTTP Server" else "Hardened OS"
        return {"srv": srv, "os": os_est}

    def mod_06(self):
        found = []
        for p in self.fuzz_list:
            try:
                r = self.session.head(f"{self.base_url}/{p}", timeout=2, verify=False, allow_redirects=False)
                if r.status_code in [200, 301, 302, 401, 403]: found.append(f"/{p}")
            except: pass
        if not found: found.append("Strict access control (paths hidden)")
        return found

    def mod_07(self):
        links = set()
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
            for tag in soup.find_all(['a', 'link', 'script', 'img', 'iframe', 'form', 'source']):
                url = tag.get('href') or tag.get('src') or tag.get('action') or tag.get('data-url')
                if url and len(url) > 1: links.add(url)
        except:
            links = set(re.findall(r'href=["\']([^"\'>]+)["\']', self.html))
        
        if not links: links.add(self.base_url)
        return list(links)

    def mod_08(self):
        emails = set()
        if self.html:
            try:
                soup = BeautifulSoup(self.html, 'html.parser')
                found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', soup.get_text())
                for e in found: emails.add(e.lower())
                for a in soup.find_all('a', href=True):
                    if 'mailto:' in a['href']:
                        emails.add(a['href'].replace('mailto:', '').split('?')[0].lower())
            except: pass
        
        if not emails:
            emails.update([f"admin@{self.target}", f"info@{self.target}", f"support@{self.target}", f"contact@{self.target}"])
            return {"status": "inferred", "list": list(emails)}
        
        users = [e.split('@')[0] for e in emails]
        if users:
            try:
                with open(f"users_{self.target}.txt", "w") as f: f.write("\n".join(set(users)))
            except: pass
        return {"status": "extracted", "list": list(emails)}

    def mod_09(self):
        try:
            payloads = ["' OR 1=1--", "' UNION SELECT 1,2,3--", "\" OR \"a\"=\"a", "1; DROP TABLE users"]
            for pay in payloads:
                u = f"{self.base_url}/?id={parse.quote(pay)}"
                r = self.session.get(u, timeout=3, verify=False).text.lower()
                if any(x in r for x in ["sql syntax", "mysql_fetch", "mariadb", "sqlite", "postgres", "ora-", "unclosed quotation"]): return "VULNERABLE"
        except: pass
        return "SECURED"

    def mod_10(self):
        try:
            pay = "<svg/onload=alert(1)>"
            u = f"{self.base_url}/?search={parse.quote(pay)}"
            if pay in self.session.get(u, timeout=3, verify=False).text: return "VULNERABLE"
        except: pass
        return "SECURED"

    def mod_11(self):
        paths = ["../../../../etc/passwd", "..\\..\\..\\..\\windows\\win.ini", "php://filter/resource=index.php"]
        for p in paths:
            try:
                r = self.session.get(f"{self.base_url}/?file={p}", timeout=3, verify=False).text
                if "root:x:" in r or "[extensions]" in r.lower() or "<?php" in r: return f"VULNERABLE ({p})"
            except: pass
        return "SECURED"

    def mod_12(self):
        routes = []
        for p in ["/api", "/v1", "/wp-json", "/graphql", "/swagger", "/api/users", "/server-status", "/.well-known/core"]:
            try:
                if self.session.get(f"{self.base_url}{p}", timeout=2, verify=False).status_code in [200, 401, 403]: routes.append(p)
            except: pass
        if not routes: routes.append("No common APIs exposed")
        return routes

    def mod_13(self):
        found = []
        pats = [r'href=["\'](.*?(' + '|'.join([re.escape(x) for x in self.malware_exts]) + r'))["\']']
        for p in pats:
            m = re.findall(p, self.html, re.I)
            for fm in m: found.append(fm[0].split('/')[-1])
        if not found: found.append("Clean DOM (No suspicious extensions)")
        return list(set(found))

    def mod_14(self):
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((self.target, 443), 4) as s:
                with ctx.wrap_socket(s, server_hostname=self.target) as ss:
                    cert = ss.getpeercert()
                    start = cert.get('notBefore', 'N/A')
                    end = cert.get('notAfter', 'N/A')
                    issuer = dict(x[0] for x in cert.get('issuer', [])).get('organizationName', 'Unknown')
                    return {"status": "VALID", "valid_from": start, "valid_to": end, "issuer": issuer}
        except ssl.SSLCertVerificationError:
            return {"status": "INVALID_CERT_OR_EXPIRED", "valid_from": "N/A", "valid_to": "N/A", "issuer": "N/A"}
        except:
            return {"status": "NO_SSL_OR_ERROR", "valid_from": "N/A", "valid_to": "N/A", "issuer": "N/A"}

    def mod_15(self):
        expected = ['Content-Security-Policy', 'X-Frame-Options', 'Strict-Transport-Security', 'X-XSS-Protection', 'X-Content-Type-Options', 'Referrer-Policy']
        miss = [h for h in expected if h.lower() not in [k.lower() for k in self.headers.keys()]]
        if not miss: return ["Fully Hardened Headers"]
        return miss

    def mod_16(self):
        try:
            if HAS_DNSPYTHON:
                answers = dns_res.resolve(self.target, 'TXT')
                for rdata in answers:
                    if 'v=spf1' in str(rdata): return "PROTECTED (SPF Active)"
            return "VULNERABLE (Missing SPF)"
        except: return "VULNERABLE (Missing SPF)"

    def mod_17(self):
        try:
            secrets = re.findall(r'(?i)(?:key|api|token|secret|pwd|pass)[a-z0-9_]*\s*[:=]\s*[\'"]([a-zA-Z0-9\-_]{16,})[\'"]', self.html)
            aws = re.findall(r'AKIA[0-9A-Z]{16}', self.html)
            tokens = re.findall(r'ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', self.html)
            
            found = []
            if secrets: found.append("Generic Keys")
            if aws: found.append("AWS Access Keys")
            if tokens: found.append("JWT Tokens")
            
            if found: return f"IDENTIFIED: {', '.join(found)}"
        except: pass
        return "CLEAN (No patterns matched)"

    def mod_18(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect(("whois.verisign-grs.com", 43))
            s.send(f"{self.target}\r\n".encode())
            response = b""
            while True:
                data = s.recv(4096)
                if not data: break
                response += data
            s.close()
            text = response.decode('utf-8', errors='ignore').lower()
            reg = re.search(r'registrar:\s*(.*)', text)
            return reg.group(1).strip().title() if reg else "Private Registry"
        except: return "Registry Query Blocked"

    def mod_19(self):
        auth_forms = []
        if "type=\"password\"" in self.html.lower(): auth_forms.append("Password Input")
        if "login" in self.html.lower(): auth_forms.append("Login Keyword")
        if "signin" in self.html.lower(): auth_forms.append("Signin Keyword")
        if "bearer" in str(self.headers).lower(): auth_forms.append("Bearer Auth")
        
        if auth_forms: return f"DETECTED ({', '.join(auth_forms)})"
        return "NO OBVIOUS AUTH SURFACE"

    def mod_20(self):
        cors = self.headers.get('Access-Control-Allow-Origin', '')
        if not cors: cors = self.headers.get('access-control-allow-origin', 'Restricted')
        reds = re.findall(r'(\?|&)(url|redirect|next|dest|return|go)=', self.html, re.I)
        return {"cors": cors, "redirect_params": len(reds)}

    def mod_21(self):
        t = re.search(r'<title>(.*?)</title>', self.html, re.I)
        d = re.search(r'name=["\']description["\']\s+content=["\'](.*?)["\']', self.html, re.I)
        title = t.group(1) if t else "No Title Tag"
        desc = d.group(1) if d else "No Meta Description"
        return {"title": title, "description": desc}

    def mod_22(self):
        sigs = {"React": "__react", "Angular": "ng-version", "Vue": "data-v-", "Next.js": "_next/static", "WordPress": "wp-content", "Joomla": "Joomla", "Laravel": "laravel", "Express": "X-Powered-By: Express"}
        det = [n for n, s in sigs.items() if s.lower() in self.html.lower() or s.lower() in str(self.headers).lower()]
        if not det: det.append("Static HTML / Custom Stack")
        return det

    def mod_23(self):
        ports = [21, 22, 25, 53, 80, 110, 143, 443, 3306, 8080, 8443]
        open_ports = []
        def scan(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                r = s.connect_ex((self.ip, p))
                s.close()
                if r == 0: open_ports.append(str(p))
            except: pass
        with ThreadPoolExecutor(max_workers=len(ports)) as ex:
            ex.map(scan, ports)
        if not open_ports: open_ports.append("All standard ports filtered")
        return open_ports

    def mod_24(self):
        forms = []
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
            for f in soup.find_all('form'):
                action = f.get('action', 'Self')
                method = f.get('method', 'GET').upper()
                inputs = len(f.find_all('input'))
                forms.append(f"[{method}] {action} ({inputs} inputs)")
        except: pass
        if not forms: forms.append("No active forms detected in DOM")
        return forms

    def mod_25(self):
        target_ports = [135, 139, 445, 3389]
        vuln = []
        for p in target_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                if s.connect_ex((self.ip, p)) == 0: vuln.append(f"Port {p} Open")
                s.close()
            except: pass
        if not vuln: vuln.append("SMB/RPC Protocols Secured")
        return vuln

    def parse_and_print(self, mid, res):
        name = MODULE_NAMES.get(mid, mid)
        main = "N/A"
        sev = "INFO"
        det = "Scanned successfully"

        if mid == "m01":
            main = f"IP: {res.get('ip', 'N/A')}"
            det = f"{res.get('isp', 'N/A')} - {res.get('asn', 'N/A')}"
        elif mid == "m02":
            main = str(res)[:60]
            det = "HTTP Header Check"
        elif mid == "m03":
            main = ", ".join(res)[:60] + ("..." if len(", ".join(res)) > 60 else "")
            sev = "MEDIUM" if len(res) > 1 else "INFO"
        elif mid == "m04":
            main = res
            sev = "MEDIUM" if "Direct" not in res else "INFO"
            det = "Perimeter Shield Check"
        elif mid == "m05":
            main = f"{res.get('os')} ({res.get('srv')})"
            det = "Heuristic Profiling"
        elif mid == "m06":
            main = ", ".join(res)[:60] + ("..." if len(", ".join(res)) > 60 else "")
            sev = "MEDIUM" if "Strict" not in main else "INFO"
        elif mid == "m07":
            main = ", ".join(res)[:60] + ("..." if len(", ".join(res)) > 60 else "")
            sev = "MEDIUM" if len(res) > 50 else "INFO"
            det = f"Total links: {len(res)}"
        elif mid == "m08":
            e_list = res.get("list", []) if isinstance(res, dict) else res
            status = res.get("status", "extracted") if isinstance(res, dict) else "extracted"
            main = ", ".join(e_list)[:60] + ("..." if len(", ".join(e_list)) > 60 else "")
            sev = "MEDIUM" if status == "extracted" else "INFO"
            det = f"Source: {status}"
        elif mid == "m09":
            main = res
            sev = "HIGH" if res == "VULNERABLE" else "LOW"
            det = "SQLi payload injection test"
        elif mid == "m10":
            main = res
            sev = "HIGH" if res == "VULNERABLE" else "LOW"
            det = "XSS reflection test"
        elif mid == "m11":
            main = res
            sev = "HIGH" if "VULNERABLE" in res else "LOW"
            det = "Path Traversal test"
        elif mid == "m12":
            main = ", ".join(res)[:60] if isinstance(res, list) else res
            sev = "MEDIUM" if "No common" not in main else "LOW"
            det = "API Endpoint recognition"
        elif mid == "m13":
            main = ", ".join(res)[:60]
            sev = "HIGH" if "Clean" not in main else "LOW"
            det = "Payload scan extension check"
        elif mid == "m14":
            if isinstance(res, dict) and res.get("status") == "VALID":
                main = f"From {res.get('valid_from')} To {res.get('valid_to')}"
                sev = "INFO"
                det = f"Issuer: {res.get('issuer')}"
            else:
                main = res.get("status", "N/A") if isinstance(res, dict) else res
                sev = "MEDIUM" if "INVALID" in main else "LOW"
                det = "Certificate Validation Failed"
        elif mid == "m15":
            main = ", ".join(res)[:60] + ("..." if len(", ".join(res)) > 60 else "")
            sev = "LOW" if "Hardened" not in main else "INFO"
        elif mid == "m16":
            main = res
            sev = "MEDIUM" if "VULNERABLE" in res else "INFO"
        elif mid == "m17":
            main = res
            sev = "HIGH" if "IDENTIFIED" in res else "LOW"
            det = "Regex mining across DOM"
        elif mid == "m18":
            main = res[:60]
            det = "Socket TCP/43 Lookup"
        elif mid == "m19":
            main = res
            sev = "MEDIUM" if "DETECTED" in res else "INFO"
        elif mid == "m20":
            main = f"CORS: {res.get('cors', 'Restricted')}"
            det = f"Redirect Params: {res.get('redirect_params', 0)}"
        elif mid == "m21":
            main = res.get('title', 'N/A')[:60]
            det = "DOM Text extraction"
        elif mid == "m22":
            main = ", ".join(res)[:60]
            det = "Stack signatures identified"
        elif mid == "m23":
            main = f"Ports: {', '.join(res)[:50]}"
            sev = "MEDIUM" if "filtered" not in main else "INFO"
            det = "Native TCP Port Scan"
        elif mid == "m24":
            main = ", ".join(res)[:60]
            det = "HTML Form/Input Extractor"
        elif mid == "m25":
            main = ", ".join(res)[:60]
            sev = "HIGH" if "Open" in main else "INFO"
            det = "Native SMB/RPC Probe"

        if sev in ["HIGH", "MEDIUM"]:
            self.flagged_count += 1
        
        self.print_finding(name, main, sev, det)

    def print_full_summary(self):
        console.print("\n[bold cyan]" + "█"*75 + "[/]")
        console.print("[bold white]                      FULL EXTRACTED DATA REPORT                     [/]")
        console.print("[bold cyan]" + "█"*75 + "[/]\n")
        
        for mid in sorted(self.results.keys()):
            name = MODULE_NAMES.get(mid, mid)
            res = self.results[mid]
            
            console.print(f"[bold deep_sky_blue1]>> {name} ({mid.upper()})[/]")
            
            if isinstance(res, dict):
                for k, v in res.items():
                    console.print(f"   [bold white]{str(k).capitalize()}:[/] {v}")
            elif isinstance(res, list):
                for item in res:
                    console.print(f"   [white]- {item}[/]")
            else:
                console.print(f"   [white]{res}[/]")
            
            console.print("\n")

    def run_all(self):
        console.print(f"\n[*] Searching: [bold white]{self.target}[/] across 25 modules\n")
        self.fetch_base()
        
        tasks = {
            "m01": self.mod_01, "m02": self.mod_02, "m03": self.mod_03, "m04": self.mod_04,
            "m05": self.mod_05, "m06": self.mod_06, "m07": self.mod_07, "m08": self.mod_08,
            "m09": self.mod_09, "m10": self.mod_10, "m11": self.mod_11, "m12": self.mod_12,
            "m13": self.mod_13, "m14": self.mod_14, "m15": self.mod_15, "m16": self.mod_16,
            "m17": self.mod_17, "m18": self.mod_18, "m19": self.mod_19, "m20": self.mod_20,
            "m21": self.mod_21, "m22": self.mod_22, "m23": self.mod_23, "m24": self.mod_24,
            "m25": self.mod_25
        }

        start = time.time()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(func): mid for mid, func in tasks.items()}
            for future in as_completed(futures):
                mid = futures[future]
                try:
                    res = future.result()
                    self.log_res(mid, res)
                    self.parse_and_print(mid, res)
                except Exception:
                    self.log_res(mid, "Error")
                    self.parse_and_print(mid, "Runtime Exception")

        duration = time.time() - start

        console.print(f"\n[*] Target    : [bold white]{self.target}[/]")
        console.print(f"[*] Found     : [bold white]{self.flagged_count} / 25 sites flagged[/]")
        console.print(f"[*] Duration  : [bold white]{duration:.3f}s[/]\n")
        
        self.print_full_summary()
        
        with open(self.output_file, "w") as f: json.dump(self.results, f, indent=4)

    def run_single(self, mid_int):
        self.fetch_base()
        mid = f"m{mid_int:02d}"
        
        tasks = {
            "m01": self.mod_01, "m02": self.mod_02, "m03": self.mod_03, "m04": self.mod_04,
            "m05": self.mod_05, "m06": self.mod_06, "m07": self.mod_07, "m08": self.mod_08,
            "m09": self.mod_09, "m10": self.mod_10, "m11": self.mod_11, "m12": self.mod_12,
            "m13": self.mod_13, "m14": self.mod_14, "m15": self.mod_15, "m16": self.mod_16,
            "m17": self.mod_17, "m18": self.mod_18, "m19": self.mod_19, "m20": self.mod_20,
            "m21": self.mod_21, "m22": self.mod_22, "m23": self.mod_23, "m24": self.mod_24,
            "m25": self.mod_25
        }
        
        func = tasks.get(mid)
        if func:
            try:
                res = func()
                self.log_res(mid, res)
                self.parse_and_print(mid, res)
            except Exception:
                self.log_res(mid, "Error")
                self.parse_and_print(mid, "Runtime Exception")
        else:
            console.print("[red]Invalid module ID.[/]")

if __name__ == "__main__":
    silent_setup()
    console.print(get_beast_ascii(), style="bold deep_sky_blue1")
    
    while True:
        print_menu()
        choice = input(f"\033[38;5;208mChoice > \033[0m").strip().upper()
        
        if choice == '0' or choice == 'EXIT':
            break
            
        target_in = input(f"\033[38;5;208mTarget URL / IP > \033[0m").strip()
        if not target_in:
            continue
            
        engine = OculusEngine(target_in)
        
        if choice == 'A':
            engine.run_all()
        elif choice.isdigit() and 1 <= int(choice) <= 25:
            engine.run_single(int(choice))
        else:
            console.print("[red]Invalid choice. Try again.[/]")
            
        console.print(f"\n[yellow]Press ENTER to return to menu...[/]")
        input()