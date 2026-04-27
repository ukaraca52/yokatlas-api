from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

# yokatlas-py kütüphanesi
try:
    from yokatlas_py.lisanstercihsihirbazi import YOKATLASLisansTercihSihirbazi
    from yokatlas_py.onlisanstercihsihirbazi import YOKATLASOnlisansTercihSihirbazi
    from urllib.parse import urlencode
    import httpx, urllib3
    urllib3.disable_warnings()
    YOKATLAS_AVAILABLE = True
except ImportError:
    YOKATLAS_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # WordPress'ten istek gelebilsin

LISANS_URL   = 'https://yokatlas.yok.gov.tr/server_side/server_processing-atlas2016-TS-t4.php'
ONLISANS_URL = 'https://yokatlas.yok.gov.tr/server_side/server_processing-atlas2016-TS-t3.php'

HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
}

def yok_post(url, payload):
    r = httpx.post(url, data=payload, headers=HEADERS, verify=False, timeout=30)
    if r.status_code == 200:
        return r.json()
    return {'error': f'HTTP {r.status_code}'}

@app.route('/api/lisans', methods=['GET', 'POST'])
def lisans():
    f = request.values
    params = {
        'puan_turu':       f.get('puan_turu', 'say'),
        'length':          int(f.get('length', 25)),
        'start':           int(f.get('start', 0)),
    }
    if f.get('uni_adi'):        params['universite'] = f.get('uni_adi')
    if f.get('program_adi'):    params['program']    = f.get('program_adi')
    if f.get('sehir'):          params['sehir']      = f.get('sehir')
    if f.get('universite_turu'):params['universite_turu'] = f.get('universite_turu')
    if f.get('ogretim_turu'):   params['ogretim_turu']    = f.get('ogretim_turu')

    s       = YOKATLASLisansTercihSihirbazi(params)
    payload = urlencode(s.columns, safe='[]%')
    result  = yok_post(LISANS_URL, payload)
    return jsonify(result)

@app.route('/api/onlisans', methods=['GET', 'POST'])
def onlisans():
    f = request.values
    params = {
        'length': int(f.get('length', 25)),
        'start':  int(f.get('start', 0)),
    }
    if f.get('uni_adi'):        params['universite'] = f.get('uni_adi')
    if f.get('program_adi'):    params['program']    = f.get('program_adi')
    if f.get('sehir'):          params['sehir']      = f.get('sehir')

    s       = YOKATLASOnlisansTercihSihirbazi(params)
    payload = urlencode(s.columns, safe='[]%')
    result  = yok_post(ONLISANS_URL, payload)
    return jsonify(result)

@app.route('/api/detay/lisans/<program_id>', methods=['GET'])
def lisans_detay(program_id):
    base = 'https://yokatlas.yok.gov.tr'
    eps = {
        'genel':    f'/content/lisans-dynamic/1000_1_1.php?y={program_id}',
        'kontenjan':f'/content/lisans-dynamic/1000_2_1a.php?y={program_id}',
        'siralama': f'/content/lisans-dynamic/1000_3_1b.php?y={program_id}',
    }
    result = {}
    for key, path in eps.items():
        r = httpx.get(base + path, headers={'User-Agent': HEADERS['User-Agent'],
            'Referer': 'https://yokatlas.yok.gov.tr/', 'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'tr-TR,tr;q=0.9', 'X-Requested-With': 'XMLHttpRequest'},
            verify=False, timeout=15)
        try:    result[key] = r.json()
        except: result[key] = {}
    return jsonify(result)

@app.route('/api/detay/onlisans/<program_id>', methods=['GET'])
def onlisans_detay(program_id):
    base = 'https://yokatlas.yok.gov.tr'
    eps = {
        'genel':    f'/content/onlisans-dynamic/1100_1_1.php?y={program_id}',
        'kontenjan':f'/content/onlisans-dynamic/1100_2_1a.php?y={program_id}',
    }
    result = {}
    for key, path in eps.items():
        r = httpx.get(base + path, headers={'User-Agent': HEADERS['User-Agent'],
            'Referer': 'https://yokatlas.yok.gov.tr/', 'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'tr-TR,tr;q=0.9', 'X-Requested-With': 'XMLHttpRequest'},
            verify=False, timeout=15)
        try:    result[key] = r.json()
        except: result[key] = {}
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'yokatlas': YOKATLAS_AVAILABLE})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
