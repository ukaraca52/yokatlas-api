"""
YOK Atlas Veri İndirici v2
Kullanım: pip install requests  →  python yokatlas_indir.py
"""
import requests, json, time, os

RENDER_URL   = "https://yokatlas-api.onrender.com"
CIKTI_KLASOR = "yokatlas_data"
os.makedirs(CIKTI_KLASOR, exist_ok=True)

def kaydet(dosya, veri):
    path = os.path.join(CIKTI_KLASOR, dosya)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    n = len(veri) if isinstance(veri, list) else len(veri.get("content", []))
    kb = os.path.getsize(path) // 1024
    print(f"  ✓ {dosya} → {n} kayıt, {kb} KB")

def get(path):
    r = requests.get(RENDER_URL + path, timeout=30)
    r.raise_for_status()
    return r.json()

def search_tumunu(puan_turu, birim_turu, etiket):
    print(f"\n{etiket} indiriliyor...")
    tum, page = [], 0
    while True:
        deneme = 0
        while deneme < 3:
            try:
                r = requests.get(RENDER_URL + "/api/search", params={
                    "puanTuru": puan_turu, "birimTuruId": birim_turu,
                    "page": page, "size": 100,
                }, timeout=60)
                r.raise_for_status()
                break
            except Exception as e:
                deneme += 1
                print(f"\n  ⚠ Sayfa {page} hata ({deneme}/3): {e} — yeniden deneniyor...")
                time.sleep(3)
        else:
            print(f"\n  ✗ Sayfa {page} 3 denemede başarısız, atlıyorum.")
            break

        data = r.json()
        icerik = data.get("content", data) if isinstance(data, dict) else data
        toplam_sayfa = data.get("totalPages", 1) if isinstance(data, dict) else 1
        toplam = data.get("totalElements", "?") if isinstance(data, dict) else "?"

        if not icerik:
            break

        tum.extend(icerik)
        print(f"  Sayfa {page+1}/{toplam_sayfa} — {len(tum)}/{toplam}   ", end="\r", flush=True)

        if page + 1 >= toplam_sayfa:
            break
        page += 1
        time.sleep(0.3)

    print(f"\n  Toplam: {len(tum)} kayıt")
    return tum

# ── 1. Statik veriler
print("=== Statik Veriler ===")
for dosya, path in [("iller.json","/api/iller"), ("universiteler.json","/api/universiteler"), ("programlar.json","/api/programlar")]:
    try:
        kaydet(dosya, get(path))
    except Exception as e:
        print(f"  ✗ {dosya}: {e}")

# ── 2. Lisans
print("\n=== Lisans ===")
for pt in ["SAY", "EA", "SOZ", "DIL"]:
    try:
        veri = search_tumunu(pt, 46, f"Lisans {pt}")
        kaydet(f"lisans_{pt.lower()}.json", veri)
    except Exception as e:
        print(f"\n  ✗ Lisans {pt}: {e}")

# ── 3. Önlisans
print("\n=== Önlisans ===")
try:
    veri = search_tumunu("TYT", 47, "Önlisans TYT")
    kaydet("onlisans_tyt.json", veri)
except Exception as e:
    print(f"\n  ✗ Önlisans: {e}")

# ── Özet
print("\n" + "="*50)
print("TAMAMLANDI! Dosyalar:")
toplam_kb = 0
for fn in sorted(os.listdir(CIKTI_KLASOR)):
    p = os.path.join(CIKTI_KLASOR, fn)
    kb = os.path.getsize(p) // 1024
    toplam_kb += kb
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    n = len(d) if isinstance(d, list) else "?"
    print(f"  {fn:<30} {n:>6} kayıt   {kb:>5} KB")
print(f"\n  Toplam: {toplam_kb} KB")
print(f"\nSonraki adım:")
print(f"  'yokatlas_data/' klasörünü WordPress'e FTP ile yükle:")
print(f"  wp-content/plugins/yok-atlas-wp/data/")
