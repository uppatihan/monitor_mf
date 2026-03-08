import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

TARGET_URL = os.getenv("TARGET_URL")
SHEET_ID = os.getenv("SHEET_ID")

def parse_tickets(html_text):
    """
    ฟังก์ชันสำหรับดึงข้อมูลตารางใบงาน (GrdHist) จาก HTML
    """
    soup = BeautifulSoup(html_text, 'html.parser')
    table = soup.find('table', id='GrdHist')
    
    if not table:
        return []

    tickets = []
    # ข้ามแถวแรก (Header)
    rows = table.find_all('tr')[1:]
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 12:
            ticket = {
                "request_id": cols[0].text.strip(),
                "created_date": cols[1].text.strip(),
                "updated_date": cols[2].text.strip(),
                "customer": cols[3].text.strip(),
                "subject": cols[4].text.strip(),
                "car_number": cols[6].text.strip(),
                "province": cols[7].text.strip(),
                "assignee": cols[8].text.strip(),
                "status": cols[9].text.strip(),
                "department": cols[10].text.strip(),
                "dept_status": cols[11].text.strip()
            }
            tickets.append(ticket)
            
    return [t for t in tickets if t.get("dept_status") != "ปิด"]


def perform_login(username, password):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    })

    try:
        response = session.get(TARGET_URL, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        viewstate = soup.find('input', id='__VIEWSTATE').get('value', '')
        viewstategenerator = soup.find('input', id='__VIEWSTATEGENERATOR').get('value', '')
        eventvalidation = soup.find('input', id='__EVENTVALIDATION').get('value', '')

        payload = {
            '__EVENTTARGET': 'btnLogin',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'txtUsername': username,
            'txtPassword': password,
            'txtNewPassword': '',
            'txtConfirmPassword': '',
            'remember': '1',
            'hidIsGo': '',
            'hidChagePwd': ''
        }

        login_response = session.post(response.url, data=payload, timeout=15)
        
        soup_login = BeautifulSoup(login_response.text, 'html.parser')
        lbl_error = soup_login.find('span', id='lblError')
        error_text = lbl_error.text.strip() if lbl_error else ""
        
        final_response = session.get(TARGET_URL, timeout=15)
        
        if 'RequestListView' in final_response.url or error_text == "":
            if 'txtPassword' in final_response.text:
                 if error_text:
                     return False, f"ล็อกอินไม่สำเร็จ: {error_text}", []
                 else:
                     return False, "ล็อกอินไม่สำเร็จ: รหัสผ่านอาจไม่ถูกต้อง", []
            
            # ดึงข้อมูลจากตารางมาจัดรูปแบบ (หน้าแรก)
            tickets = parse_tickets(final_response.text)
            
            # ดึงข้อมูลยอดรวมจริงจาก API TicketCounter (เหมือนใน test_api.py)
            total_group_open = len(tickets) # Fallback
            try:
                api_url = "https://imindmflow.clogic.asia/imind/webServices/TicketCounterServices.asmx/GetTicketCounter"
                api_headers = {
                    'Content-Type': 'application/json; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                res = session.post(api_url, json={}, headers=api_headers, timeout=10)
                if res.status_code == 200:
                    api_data = res.json()
                    total_group_open = api_data.get('d', {}).get('Data', {}).get('TotalGroupOpen', str(len(tickets)))
                    # print(f"   📊 API TicketCounter -> TotalGroupOpen: {total_group_open}")
            except Exception as api_err:
                print(f"   ⚠️ ไม่สามารถดึงยอดจาก API ได้: {api_err}")

            return True, f"เข้าสู่ระบบสำเร็จ! (Group Open: {total_group_open})", tickets, total_group_open
        else:
             return False, "ล็อกอินไม่สำเร็จ ไม่สามารถเข้าสู่ระบบเป้าหมายได้", [], 0

    except Exception as e:
        return False, f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}", [], 0


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "กรุณาส่ง Username และ Password มาให้ครบถ้วน", "data": []}), 400
        
    # print(f"กำลังล็อกอิน: {username} ...")
    success, message, tickets, total_group_open = perform_login(username, password)
    return jsonify({
        "success": success,
        "message": message,
        "data": tickets,
        "total_group_open": total_group_open
    })

@app.route('/api/gsheet-counts', methods=['GET'])
def api_gsheet_counts():
    """
    ดึงข้อมูลจาก Google Sheet เฉพาะช่วง F5:H
    นับจำนวนแถวใน column F และ H พร้อมคำนวณส่วนต่าง
    """
    CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=IT&range=F5:H"

    try:
        import csv
        import io

        # print(f"📊 กำลังดึงข้อมูลจาก Google Sheet (IT!F5:H)...")
        response = requests.get(CSV_URL, timeout=15)
        response.raise_for_status()

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)

        # Column F = index 0, Column G = index 1, Column H = index 2 (ใน range F:H)
        count_f = 0
        count_h = 0
        for row in rows:
            if len(row) > 0 and row[0].strip():
                count_f += 1
            if len(row) > 2 and row[2].strip():
                count_h += 1

        # print(f"   ✅ F: {count_f} | H: {count_h}")
        # print(f"   ✅ diff: {count_f - count_h}")
        return jsonify({
            "success": True,
            "count_f": count_f,
            "count_h": count_h,
            "diff": count_f - count_h
        })

    except Exception as e:
        print(f"❌ Error fetching Google Sheet: {e}")
        return jsonify({
            "success": False, 
            "count_f": 0, 
            "count_h": 0, 
            "diff": 0,
            "error": str(e)
        })


if __name__ == '__main__':
    print("🚀 Start Server on port 5000 ...")
    app.run(port=5000, debug=True, use_reloader=False)
