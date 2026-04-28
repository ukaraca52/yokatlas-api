from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx, urllib3, json
urllib3.disable_warnings()

app = Flask(__name__)
CORS(app)

API = "https://yokatlas.yok.gov.tr/api"
H = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://yokatlas.yok.gov.tr/",
    "Origin": "https://yokatlas.yok.gov.tr",
}

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/iller")
def iller():
    r = httpx.get(API + "/tercih-kilavuz/universite-iller", headers=H, verify=False, timeout=15)
    return jsonify(r.json())

@app.route("/api/universiteler")
def universiteler():
    r = httpx.get(API + "/tercih-kilavuz/universiteler", headers=H, verify=False, timeout=15)
    return jsonify(r.json())

@app.route("/api/programlar")
def programlar():
    r = httpx.get(API + "/tercih-kilavuz/universite-programlar", headers=H, verify=False, timeout=15)
    return jsonify(r.json())

@app.route("/api/search")
def search():
    """Lisans ve onlisans arama - sayfalama ile tam veri"""
    puan_turu  = request.args.get("puanTuru", "SAY").upper()
    birim_turu = int(request.args.get("birimTuruId", 46))
    page       = int(request.args.get("page", 0))
    size       = int(request.args.get("size", 100))

    body = {
        "filters": {
            "puanTuru":   puan_turu,
            "birimTuruId": birim_turu,
        },
        "page": page,
        "size": size,
        "sortBy": "basariSirasi",
        "direction": "ASC"
    }

    r = httpx.post(API + "/tercih-kilavuz/search", json=body, headers=H, verify=False, timeout=30)
    if r.status_code == 200:
        return jsonify(r.json())
    return jsonify({"error": f"HTTP {r.status_code}", "body": r.text[:200]}), 502

@app.route("/test")
def test():
    body = {"filters": {"puanTuru": "SAY", "birimTuruId": 46}, "page": 0, "size": 3, "sortBy": "basariSirasi", "direction": "ASC"}
    r = httpx.post(API + "/tercih-kilavuz/search", json=body, headers=H, verify=False, timeout=30)
    return jsonify({"status": r.status_code, "data": r.json() if r.status_code == 200 else r.text[:300]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
