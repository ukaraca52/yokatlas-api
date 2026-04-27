from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx, urllib3
urllib3.disable_warnings()

app = Flask(__name__)
CORS(app)

LISANS_URL   = 'https://yokatlas.yok.gov.tr/server_side/server_processing-atlas2016-TS-t4.php'
ONLISANS_URL = 'https://yokatlas.yok.gov.tr/server_side/server_processing-atlas2016-TS-t3.php'
YOK_BASE     = 'https://yokatlas.yok.gov.tr'

L_COLS = 'draw=4&columns[0][data]=0&columns[0][searchable]=true&columns[0][orderable]=false&columns[0][search][regex]=false&columns[1][data]=1&columns[1][searchable]=true&columns[1][orderable]=false&columns[1][search][regex]=false&columns[2][data]=2&columns[2][searchable]=true&columns[2][orderable]=false&columns[2][search][regex]=false&columns[3][data]=3&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][regex]=false&columns[4][data]=4&columns[4][searchable]=true&columns[4][orderable]=false&columns[4][search][regex]=false&columns[5][data]=5&columns[5][searchable]=true&columns[5][orderable]=true&columns[5][search][regex]=false&columns[6][data]=6&columns[6][searchable]=true&columns[6][orderable]=false&columns[6][search][regex]=false&columns[7][data]=7&columns[7][searchable]=true&columns[7][orderable]=false&columns[7][search][regex]=false&columns[8][data]=8&columns[8][searchable]=true&columns[8][orderable]=false&columns[8][search][regex]=false&columns[9][data]=9&columns[9][searchable]=true&columns[9][orderable]=false&columns[9][search][regex]=false&columns[10][data]=10&columns[10][searchable]=true&columns[10][orderable]=false&columns[10][search][regex]=false&columns[11][data]=11&columns[11][searchable]=true&columns[11][orderable]=true&columns[11][search][regex]=false&columns[12][data]=12&columns[12][searchable]=true&columns[12][orderable]=true&columns[12][search][regex]=false&columns[13][data]=13&columns[13][searchable]=true&columns[13][orderable]=true&columns[13][search][regex]=false&columns[14][data]=14&columns[14][searchable]=true&columns[14][orderable]=false&columns[14][search][regex]=false&columns[15][data]=15&columns[15][searchable]=true&columns[15][orderable]=false&columns[15][search][regex]=false&columns[16][data]=16&columns[16][searchable]=true&columns[16][orderable]=true&columns[16][search][regex]=false&columns[17][data]=17&columns[17][searchable]=true&columns[17][orderable]=true&columns[17][search][regex]=false&columns[18][data]=18&columns[18][searchable]=true&columns[18][orderable]=true&columns[18][search][regex]=false&columns[19][data]=19&columns[19][searchable]=true&columns[19][orderable]=true&columns[19][search][regex]=false&columns[20][data]=20&columns[20][searchable]=true&columns[20][orderable]=true&columns[20][search][regex]=false&columns[21][data]=21&columns[21][searchable]=true&columns[21][orderable]=true&columns[21][search][regex]=false&columns[22][data]=22&columns[22][searchable]=true&columns[22][orderable]=true&columns[22][search][regex]=false&columns[23][data]=23&columns[23][searchable]=true&columns[23][orderable]=true&columns[23][search][regex]=false&columns[24][data]=24&columns[24][searchable]=true&columns[24][orderable]=true&columns[24][search][regex]=false&columns[25][data]=25&columns[25][searchable]=true&columns[25][orderable]=true&columns[25][search][regex]=false&columns[26][data]=26&columns[26][searchable]=true&columns[26][orderable]=true&columns[26][search][regex]=false&columns[27][data]=27&columns[27][searchable]=true&columns[27][orderable]=true&columns[27][search][regex]=false&columns[28][data]=28&columns[28][searchable]=true&columns[28][orderable]=true&columns[28][search][regex]=false&columns[29][data]=29&columns[29][searchable]=true&columns[29][orderable]=true&columns[29][search][regex]=false&columns[30][data]=30&columns[30][searchable]=true&columns[30][orderable]=true&columns[30][search][regex]=false&columns[31][data]=31&columns[31][searchable]=true&columns[31][orderable]=true&columns[31][search][regex]=false&columns[32][data]=32&columns[32][searchable]=true&columns[32][orderable]=true&columns[32][search][regex]=false&columns[33][data]=33&columns[33][searchable]=true&columns[33][orderable]=true&columns[33][search][regex]=false&columns[34][data]=34&columns[34][searchable]=true&columns[34][orderable]=true&columns[34][search][regex]=false&columns[35][data]=35&columns[35][searchable]=true&columns[35][orderable]=true&columns[35][search][regex]=false&columns[36][data]=36&columns[36][searchable]=true&columns[36][orderable]=true&columns[36][search][regex]=false&columns[37][data]=37&columns[37][searchable]=true&columns[37][orderable]=true&columns[37][search][regex]=false&columns[38][data]=38&columns[38][searchable]=true&columns[38][orderable]=true&columns[38][search][regex]=false&columns[39][data]=39&columns[39][searchable]=true&columns[39][orderable]=true&columns[39][search][regex]=false&columns[40][data]=40&columns[40][searchable]=true&columns[40][orderable]=true&columns[40][search][regex]=false&columns[41][data]=41&columns[41][searchable]=true&columns[41][orderable]=true&columns[41][search][regex]=false&columns[42][data]=42&columns[42][searchable]=true&columns[42][orderable]=true&columns[42][search][regex]=false&columns[43][data]=43&columns[43][searchable]=true&columns[43][orderable]=true&columns[43][search][regex]=false&columns[44][data]=44&columns[44][searchable]=true&columns[44][orderable]=true&columns[44][search][regex]=false'
O_COLS = 'draw=2&columns[0][data]=0&columns[0][searchable]=true&columns[0][orderable]=false&columns[0][search][regex]=false&columns[1][data]=1&columns[1][searchable]=true&columns[1][orderable]=false&columns[1][search][regex]=false&columns[2][data]=2&columns[2][searchable]=true&columns[2][orderable]=false&columns[2][search][regex]=false&columns[3][data]=3&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][regex]=false&columns[4][data]=4&columns[4][searchable]=true&columns[4][orderable]=false&columns[4][search][regex]=false&columns[5][data]=5&columns[5][searchable]=true&columns[5][orderable]=true&columns[5][search][regex]=false&columns[6][data]=6&columns[6][searchable]=true&columns[6][orderable]=false&columns[6][search][regex]=false&columns[7][data]=7&columns[7][searchable]=true&columns[7][orderable]=false&columns[7][search][regex]=false&columns[8][data]=8&columns[8][searchable]=true&columns[8][orderable]=false&columns[8][search][regex]=false&columns[9][data]=9&columns[9][searchable]=true&columns[9][orderable]=false&columns[9][search][regex]=false&columns[10][data]=10&columns[10][searchable]=true&columns[10][orderable]=false&columns[10][search][regex]=false&columns[11][data]=11&columns[11][searchable]=true&columns[11][orderable]=true&columns[11][search][regex]=false&columns[12][data]=12&columns[12][searchable]=true&columns[12][orderable]=true&columns[12][search][regex]=false&columns[13][data]=13&columns[13][searchable]=true&columns[13][orderable]=true&columns[13][search][regex]=false&columns[14][data]=14&columns[14][searchable]=true&columns[14][orderable]=false&columns[14][search][regex]=false&columns[15][data]=15&columns[15][searchable]=true&columns[15][orderable]=false&columns[15][search][regex]=false&columns[16][data]=16&columns[16][searchable]=true&columns[16][orderable]=true&columns[16][search][regex]=false&columns[17][data]=17&columns[17][searchable]=true&columns[17][orderable]=true&columns[17][search][regex]=false&columns[18][data]=18&columns[18][searchable]=true&columns[18][orderable]=true&columns[18][search][regex]=false&columns[19][data]=19&columns[19][searchable]=true&columns[19][orderable]=true&columns[19][search][regex]=false&columns[20][data]=20&columns[20][searchable]=true&columns[20][orderable]=true&columns[20][search][regex]=false&columns[21][data]=21&columns[21][searchable]=true&columns[21][orderable]=true&columns[21][search][regex]=false&columns[22][data]=22&columns[22][searchable]=true&columns[22][orderable]=true&columns[22][search][regex]=false&columns[23][data]=23&columns[23][searchable]=true&columns[23][orderable]=true&columns[23][search][regex]=false&columns[24][data]=24&columns[24][searchable]=true&columns[24][orderable]=true&columns[24][search][regex]=false&columns[25][data]=25&columns[25][searchable]=true&columns[25][orderable]=true&columns[25][search][regex]=false&columns[26][data]=26&columns[26][searchable]=true&columns[26][orderable]=true&columns[26][search][regex]=false&columns[27][data]=27&columns[27][searchable]=true&columns[27][orderable]=true&columns[27][search][regex]=false&columns[28][data]=28&columns[28][searchable]=true&columns[28][orderable]=true&columns[28][search][regex]=false&columns[29][data]=29&columns[29][searchable]=true&columns[29][orderable]=true&columns[29][search][regex]=false&columns[30][data]=30&columns[30][searchable]=true&columns[30][orderable]=true&columns[30][search][regex]=false&columns[31][data]=31&columns[31][searchable]=true&columns[31][orderable]=true&columns[31][search][regex]=false&columns[32][data]=32&columns[32][searchable]=true&columns[32][orderable]=true&columns[32][search][regex]=false&columns[33][data]=33&columns[33][searchable]=true&columns[33][orderable]=true&columns[33][search][regex]=false&columns[34][data]=34&columns[34][searchable]=true&columns[34][orderable]=true&columns[34][search][regex]=false&columns[35][data]=35&columns[35][searchable]=true&columns[35][orderable]=true&columns[35][search][regex]=false&columns[36][data]=36&columns[36][searchable]=true&columns[36][orderable]=true&columns[36][search][regex]=false&columns[37][data]=37&columns[37][searchable]=true&columns[37][orderable]=true&columns[37][search][regex]=false&columns[38][data]=38&columns[38][searchable]=true&columns[38][orderable]=true&columns[38][search][regex]=false&columns[39][data]=39&columns[39][searchable]=true&columns[39][orderable]=true&columns[39][search][regex]=false&columns[40][data]=40&columns[40][searchable]=true&columns[40][orderable]=true&columns[40][search][regex]=false&columns[41][data]=41&columns[41][searchable]=true&columns[41][orderable]=true&columns[41][search][regex]=false&columns[42][data]=42&columns[42][searchable]=true&columns[42][orderable]=true&columns[42][search][regex]=false&columns[43][data]=43&columns[43][searchable]=true&columns[43][orderable]=true&columns[43][search][regex]=false&columns[44][data]=44&columns[44][searchable]=true&columns[44][orderable]=true&columns[44][search][regex]=false'

HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'tr-TR,tr;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
    'Referer': 'https://yokatlas.yok.gov.tr/tercih-sihirbazi-t4.php',
    'Origin': 'https://yokatlas.yok.gov.tr',
}

GET_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
    'Referer': 'https://yokatlas.yok.gov.tr/',
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'tr-TR,tr;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
}

def arr(val):
    if not val: return '[]'
    import json
    return json.dumps([val], ensure_ascii=False)

def lisans_payload(f, start, length):
    from urllib.parse import quote
    p = L_COLS
    p += '&order[0][column]=34&order[0][dir]=desc'
    p += '&order[1][column]=41&order[1][dir]=asc'
    p += '&order[2][column]=42&order[2][dir]=asc'
    p += f'&start={int(start)}&length={int(length)}'
    p += '&search[regex]=false'
    p += f'&puan_turu={quote(f.get("puan_turu","say"))}'
    p += '&yeniler=1'
    p += f'&universite={quote(arr(f.get("uni_adi","")))}'
    p += f'&program={quote(arr(f.get("program_adi","")))}'
    p += f'&sehir={quote(arr(f.get("sehir","")))}'
    p += f'&universite_turu={quote(arr(f.get("universite_turu","")))}'
    p += f'&ogretim_turu={quote(arr(f.get("ogretim_turu","")))}'
    p += '&doluluk=[]&search[value]='
    p += f'&ust_bs={quote(f.get("ust_bs",""))}'
    p += f'&alt_bs={quote(f.get("alt_bs",""))}'
    p += '&kilavuz_kodu='
    p += f'&ucret={quote(arr(f.get("burs","")))}'
    return p

def onlisans_payload(f, start, length):
    from urllib.parse import quote
    p = O_COLS
    p += '&order[0][column]=32&order[0][dir]=desc'
    p += '&order[1][column]=33&order[1][dir]=asc'
    p += '&order[2][column]=34&order[2][dir]=asc'
    p += f'&start={int(start)}&length={int(length)}'
    p += '&search[regex]=false&puan_turu=tyt&yeniler=1'
    p += f'&universite={quote(arr(f.get("uni_adi","")))}'
    p += f'&program={quote(arr(f.get("program_adi","")))}'
    p += f'&sehir={quote(arr(f.get("sehir","")))}'
    p += f'&universite_turu={quote(arr(f.get("universite_turu","")))}'
    p += f'&ogretim_turu={quote(arr(f.get("ogretim_turu","")))}'
    p += '&doluluk=[]&search[value]='
    p += f'&ust_puan={quote(f.get("ust_bs",""))}'
    p += f'&alt_puan={quote(f.get("alt_bs",""))}'
    p += '&tip=TYT&kilavuz_kodu=&ucret=[]'
    return p

@app.route('/api/lisans', methods=['GET','POST'])
def lisans():
    f = request.values
    body = lisans_payload(f, f.get('start',0), f.get('length',25))
    r = httpx.post(LISANS_URL, data=body, headers=HEADERS, verify=False, timeout=30)
    if r.status_code == 200:
        return jsonify(r.json())
    return jsonify({'error': f'HTTP {r.status_code}'}), 502

@app.route('/api/onlisans', methods=['GET','POST'])
def onlisans():
    f = request.values
    body = onlisans_payload(f, f.get('start',0), f.get('length',25))
    r = httpx.post(ONLISANS_URL, data=body, headers=HEADERS, verify=False, timeout=30)
    if r.status_code == 200:
        return jsonify(r.json())
    return jsonify({'error': f'HTTP {r.status_code}'}), 502

@app.route('/api/detay/lisans/<pid>', methods=['GET'])
def lisans_detay(pid):
    eps = {
        'genel':    f'/content/lisans-dynamic/1000_1_1.php?y={pid}',
        'kontenjan':f'/content/lisans-dynamic/1000_2_1a.php?y={pid}',
        'siralama': f'/content/lisans-dynamic/1000_3_1b.php?y={pid}',
    }
    result = {}
    for k, path in eps.items():
        try:
            r = httpx.get(YOK_BASE+path, headers=GET_HEADERS, verify=False, timeout=15)
            result[k] = r.json()
        except:
            result[k] = {}
    return jsonify(result)

@app.route('/api/detay/onlisans/<pid>', methods=['GET'])
def onlisans_detay(pid):
    eps = {
        'genel':    f'/content/onlisans-dynamic/1100_1_1.php?y={pid}',
        'kontenjan':f'/content/onlisans-dynamic/1100_2_1a.php?y={pid}',
    }
    result = {}
    for k, path in eps.items():
        try:
            r = httpx.get(YOK_BASE+path, headers=GET_HEADERS, verify=False, timeout=15)
            result[k] = r.json()
        except:
            result[k] = {}
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
