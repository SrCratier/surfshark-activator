from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests
import os
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

TARGET_URL = "https://my.surfshark.com/account/p_api/v1/account/authorization/assign"

VALID_TOKENS = [
"GAMSGO-S10PA",
"GAMSGO-9DAO1",
"GAMSGO-CPSA0",
"GAMSGO-MIS81",
"GAMSGO-0DSA8",
"GAMSGO-48392",
"GAMSGO-75014",
"GAMSGO-19607",
"GAMSGO-86420",
"GAMSGO-03178",
"GAMSGO-59241",
"GAMSGO-40736",
"GAMSGO-91805",
"GAMSGO-26094",
"GAMSGO-77563",
"GAMSGO-14890",
"GAMSGO-63927",
"GAMSGO-80451",
"GAMSGO-39206",
"GAMSGO-57018"

]

@app.route('/', methods=['GET'])
def home():
    return "System Online"

@app.route('/activar', methods=['POST'])
def activar_dispositivo():
    data = request.json
    surfshark_code = data.get('code')
    access_token = data.get('token')
    user_country = data.get('country', 'Unknown')

    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    tz_peru = pytz.timezone('America/Lima')
    current_time = datetime.now(tz_peru).strftime('%Y-%m-%d %H:%M:%S')

    if access_token not in VALID_TOKENS:
        print(f"[ACCESO DENEGADO] {current_time} | IP: {ip_address} | País: {user_country} | Token Inválido: {access_token}")
        return jsonify({"success": False, "message": "Access Token Invalid / Código de Acceso Inválido"}), 403

    if not surfshark_code:
        return jsonify({"success": False, "message": "Missing Surfshark Code"}), 400

    mis_cookies = os.environ.get('SURFSHARK_COOKIE')

    if not mis_cookies:
        return jsonify({"success": False, "message": "Server Config Error"}), 500

    headers = {
        "authority": "my.surfshark.com",
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://my.surfshark.com",
        "referer": "https://my.surfshark.com/account/login-code",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "cookie": mis_cookies
    }

    payload = {"code": surfshark_code}

    try:
        print(f"[INTENTO ACTIVACIÓN] {current_time} | IP: {ip_address} | País: {user_country} | Token: {access_token} | Code: {surfshark_code} | Device: {user_agent}")
        
        response = cffi_requests.post(
            TARGET_URL, 
            json=payload, 
            headers=headers, 
            impersonate="chrome110",
            timeout=20
        )
        
        if response.status_code == 200:
            print(f"[ÉXITO] Activación completada para el token {access_token}")
            return jsonify({"success": True, "message": "OK"})
        elif response.status_code == 404:
            print(f"[FALLO] Código Surfshark incorrecto/expirado")
            return jsonify({"success": False, "message": "Code Invalid/Expired"})
        elif response.status_code in [401, 403]:
            print(f"[CRITICAL] Bloqueo de sesión Surfshark")
            return jsonify({"success": False, "message": "Session Error (Server Side)"})
        else:
            return jsonify({"success": False, "message": f"Error: {response.status_code}"})

    except Exception as e:
        print(f"[ERROR INTERNO] {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
