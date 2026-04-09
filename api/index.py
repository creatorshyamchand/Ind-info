from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# আপনার কাস্টম ক্রেডিট
CREDIT_TEXT = "Developed by CREATOR SHYAMCHAND | @nexxonhackers"

def safe_first(lst, key=None):
    if lst and isinstance(lst, list) and len(lst) > 0:
        return lst[0].get(key) if key else lst[0]
    return None

def fetch_truecaller(number):
    # আপনার দেওয়া টোকেন (এটি মেয়াদোত্তীর্ণ হলে পরিবর্তন করতে হবে)
    TOKEN = "a2i0a--xGEup3VdVkAZ5pEdGVr36IAiYoER_c8qIN5GftDqpn5ENRfvJ17vDX70U"
    
    # ইন্ডিয়ান নাম্বারের জন্য 'countryCode=IN' সেট করা আছে
    url = f"https://search5-noneu.truecaller.com/v2/search?q={number}&countryCode=IN&type=4&encoding=json"
    
    headers = {
        "User-Agent": "Truecaller/15.32.6 (Android;14)",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=12)
        res.raise_for_status()
        data = res.json()
        
        if not data.get("data"):
            return {"status": "error", "message": "No information found for this number."}

        info = data.get("data", [{}])[0]

        return {
            "status": "success",
            "name": info.get("name"),
            "phone": safe_first(info.get("phones"), "e164Format"),
            "carrier": safe_first(info.get("phones"), "carrier"),
            "email": safe_first(info.get("internetAddresses"), "id"),
            "gender": info.get("gender"),
            "city": safe_first(info.get("addresses"), "city"),
            "country": safe_first(info.get("addresses"), "countryCode"),
            "image": info.get("image"),
            "isFraud": info.get("isFraud", False),
            "credits": CREDIT_TEXT
        }
    except requests.exceptions.HTTPError as e:
        if res.status_code == 401:
            return {"error": "Unauthorized: Token might be expired."}
        return {"error": f"HTTP Error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Indian Number Info API is Live",
        "usage": "/truecaller?number=91XXXXXXXXXX",
        "developer": "CREATOR SHYAMCHAND"
    })

@app.route("/truecaller", methods=["GET"])
def truecaller_api():
    number = request.args.get("number")
    
    if not number:
        return jsonify({"error": "Missing number parameter (e.g. ?number=91XXXXXXXXXX)"}), 400
    
    # নাম্বার থেকে যদি '+' বা স্পেস থাকে তা রিমুভ করা
    clean_number = number.replace("+", "").replace(" ", "")
    
    result = fetch_truecaller(clean_number)
    return jsonify(result)

# Vercel-এর জন্য হ্যান্ডলার
app_handler = app
                   
