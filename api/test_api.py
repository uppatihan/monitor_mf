import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TARGET_URL = os.getenv("TARGET_URL")

def debug_login():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })

    print("Fetching login page...")
    response = session.get(TARGET_URL, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    viewstate = soup.find('input', id='__VIEWSTATE').get('value', '') if soup.find('input', id='__VIEWSTATE') else ''
    viewstategenerator = soup.find('input', id='__VIEWSTATEGENERATOR').get('value', '') if soup.find('input', id='__VIEWSTATEGENERATOR') else ''
    eventvalidation = soup.find('input', id='__EVENTVALIDATION').get('value', '') if soup.find('input', id='__EVENTVALIDATION') else ''

    payload = {
        '__EVENTTARGET': 'btnLogin',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__EVENTVALIDATION': eventvalidation,
        'txtUsername': 'Patihan.kha',
        'txtPassword': 'Patihan1212121',
        'txtNewPassword': '',
        'txtConfirmPassword': '',
        'remember': '1',
        'hidIsGo': '',
        'hidChagePwd': ''
    }

    print("Posting login...")
    login_response = session.post(response.url, data=payload, timeout=15)
    
    print("Fetching dashboard...")
    final = session.get(TARGET_URL, timeout=15)
    
    with open('debug_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(final.text)
        
    print(f"Saved dashboard HTML. Size: {len(final.text)} bytes")
    print("Does it contain GrdHist table?: ", "GrdHist" in final.text)
    
    # ลองยิง API TicketCounter
    try:
        api_url = "https://imindmflow.clogic.asia/imind/webServices/TicketCounterServices.asmx/GetTicketCounter"
        # เพิ่ม headers ของ Ajax 
        api_headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
        res = session.post(api_url, json={}, headers=api_headers)
        print("\nAPI Response TicketCounter:")
        print(json.dumps(res.json(), indent=2))
        
    except Exception as e:
        print("Failed to call API:", e)

if __name__ == '__main__':
    debug_login()
