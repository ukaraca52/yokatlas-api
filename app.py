from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx, urllib3, json
urllib3.disable_warnings()

app = Flask(__name__)
CORS(app)

API_BASE = "https://yokatlas.yok.gov.tr/api"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://yokatlas.yok.gov.tr/",
    "Origin": "https://yokatlas.yok.gov.tr",
}

def yok_post(path, body):
    r = httpx.post(API_BASE + path, json=body, headers=HEADERS, verify=False, timeout=30)
    return r

def yok_get(path):
    r = httpx.get(API_BASE + path, headers=HEADERS, verify=False, timeout=15)
    return r

@app.route("/api/search", methods=["GET", "POST"])
def search():
    f = request.values if request.method == "GET" else {**request.values, **(request.json or {})}
    if request.is_json and request.json:
        f = request.json

    puan_turu    = f.get("puanTuru") or f.get("puan_turu") or "SAY"
    page         = int(f.get("page", 0))
    size         = int(f.get("size") or f.get("length", 20))
    min_sira     = f.get("minBasariSirasi") or f.get("alt_bs") or None
    max_sira     = f.get("maxBasariSirasi") or f.get("ust_bs") or None
    uni_id       = f.get("universiteId")
    birim_id     = f.get("birimGrupId") or f.get("program_adi")
    il_kodu      = f.get("ilKodu") or f.get("sehir")
    birim_turu   = f.get("birimTuruId")
    uni_turu     = f.get("universiteTuru") or f.get("universite_turu")
    burs_id      = f.get("bursOraniId") or f.get("burs")
    ogrenim_turu = f.get("ogrenimTuruId") or f.get("ogretim_turu")
    kilavuz_kodu = f.get("kilavuzKodu")

    body = {
        "filters": {
            "puanTuru":        puan_turu.upper() if puan_turu else None,
            "universiteId":    [int(uni_id)] if uni_id and str(uni_id).isdigit() else None,
            "birimGrupId":     [int(birim_id)] if birim_id and str(birim_id).isdigit() else None,
            "ilKodu":          [int(il_kodu)] if il_kodu and str(il_kodu).isdigit() else None,
            "birimTuruId":     int(birim_turu) if birim_turu else None,
            "universiteTuru":  uni_turu if uni_turu else None,
            "bursOraniId":     int(burs_id) if burs_id and str(burs_id).isdigit() else None,
            "ogrenimTuruId":   int(ogrenim_turu) if ogrenim_turu and str(ogrenim_turu).isdigit() else None,
            "kilavuzKodu":     kilavuz_kodu,
            "minBasariSirasi": int(min_sira) if min_sira else None,
            "maxBasariSirasi": int(max_sira) if max_sira else None,
        },
        "page": page,
        "size": size,
        "sortBy": "basariSirasi",
        "direction": "ASC"
    }
    # None olan filtreleri temizle
    body["filters"] = {k: v for k, v in body["filters"].items() if v is not None}

    r = yok_post("/tercih-kilavuz/search", body)
    if r.status_code == 200:
        return jsonify(r.json())
    return jsonify({"error": f"HTTP {r.status_code}: {r.text[:200]}"}), 502

@app.route("/api/iller")
def iller():
    r = yok_get("/tercih-kilavuz/universite-iller")
    return jsonify(r.json()) if r.status_code == 200 else (jsonify({"error": r.status_code}), 502)

@app.route("/api/universiteler")
def universiteler():
    r = yok_get("/tercih-kilavuz/universiteler")
    return jsonify(r.json()) if r.status_code == 200 else (jsonify({"error": r.status_code}), 502)

@app.route("/api/programlar")
def programlar():
    r = yok_get("/tercih-kilavuz/universite-programlar")
    return jsonify(r.json()) if r.status_code == 200 else (jsonify({"error": r.status_code}), 502)

@app.route("/health")
def health():
    try:
        r = yok_get("/tercih-kilavuz/universite-iller")
        return jsonify({"status": "ok", "yokatlas": r.status_code == 200})
    except Exception as e:
        return jsonify({"status": "ok", "yokatlas": False, "error": str(e)})

@app.route("/test")
def test():
    body = {"filters": {"puanTuru": "SAY", "birimTuruId": 46}, "page": 0, "size": 3, "sortBy": "basariSirasi", "direction": "ASC"}
    r = yok_post("/tercih-kilavuz/search", body)
    return jsonify({"status": r.status_code, "body": r.json() if r.status_code == 200 else r.text[:300]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
