"""
YOK Atlas Veri İndirici
-----------------------
Kullanım:
  pip install requests
  python yokatlas_indir.py

Render API'niz üzerinden tüm YOK Atlas verilerini çeker,
'yokatlas_data/' klasörüne JSON olarak kaydeder.
Bu JSON'ları WordPress eklentisinin 'data/' klasörüne koyun.
"""

import requests, json, time, os, sys

# ── AYARLAR ──────────────────────────────────────────────
RENDER_URL = "https://yokatlas-api.onrender.com"  # Render URL'niz
CIKTI_KLASOR = "yokatlas_data"
# ─────────────────────────────────────────────────────────

os.makedirs(CIKTI_KLASOR, exist_ok=True)

def kaydet(dosya, veri):
    path = os.path.join(CIKTI_KLASOR, dosya)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {dosya} kaydedildi ({len(veri) if isinstance(veri,list) else 'dict'} kayıt)")

def get(path):
    r = requests.get(RENDER_URL + path, timeout=30)
    r.raise_for_status()
    return r.json()

def search_tumunu(puan_turu, birim_turu, etiket):
    print(f"\n{etiket} indiriliyor...")
    tum = []
    page = 0
    while True:
        r = requests.get(RENDER_URL + "/api/search", params={
            "puanTuru": puan_turu,
            "birimTuruId": birim_turu,
            "page": page,
            "size": 100,
        }, timeout=60)
        r.raise_for_status()
        data = r.json()

        icerik = data.get("content", data) if isinstance(data, dict) else data
        toplam_sayfa = data.get("totalPages", 1) if isinstance(data, dict) else 1
        toplam = data.get("totalElements", len(icerik)) if isinstance(data, dict) else len(icerik)

        if not icerik:
            break

        tum.extend(icerik)
        print(f"  Sayfa {page+1}/{toplam_sayfa} — {len(tum)}/{toplam} kayıt", end="\r", flush=True)

        if page + 1 >= toplam_sayfa:
            break
        page += 1
        time.sleep(0.2)

    print(f"\n  Toplam: {len(tum)} kayıt")
    return tum

# ── 1. Statik veriler ──
print("=== Statik Veriler ===")
try:
    iller = get("/api/iller")
    kaydet("iller.json", iller)
except Exception as e:
    print(f"  ✗ iller: {e}")

try:
    universiteler = get("/api/universiteler")
    kaydet("universiteler.json", universiteler)
except Exception as e:
    print(f"  ✗ universiteler: {e}")

try:
    programlar = get("/api/programlar")
    kaydet("programlar.json", programlar)
except Exception as e:
    print(f"  ✗ programlar: {e}")

# ── 2. Lisans programları ──
print("\n=== Lisans Programları ===")
for pt in ["SAY", "EA", "SOZ", "DIL"]:
    try:
        veri = search_tumunu(pt, 46, f"Lisans {pt}")
        kaydet(f"lisans_{pt.lower()}.json", veri)
    except Exception as e:
        print(f"\n  ✗ Lisans {pt}: {e}")

# ── 3. Önlisans ──
print("\n=== Önlisans Programları ===")
try:
    veri = search_tumunu("TYT", 47, "Önlisans TYT")
    kaydet("onlisans_tyt.json", veri)
except Exception as e:
    print(f"\n  ✗ Önlisans: {e}")

# ── Özet ──
print("\n" + "="*50)
print("TAMAMLANDI!")
print(f"Dosyalar: {CIKTI_KLASOR}/")
for f in os.listdir(CIKTI_KLASOR):
    path = os.path.join(CIKTI_KLASOR, f)
    size = os.path.getsize(path)
    with open(path, encoding="utf-8") as fp:
        data = json.load(fp)
    print(f"  {f}: {len(data) if isinstance(data,list) else '?'} kayıt, {size//1024} KB")

print("\nSonraki adım:")
print("  'yokatlas_data/' içindeki JSON dosyalarını")
print("  WordPress eklentisinin 'wp-content/plugins/yok-atlas-wp/data/' klasörüne kopyalayın.")
