from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests # Librería anti-detección
import os

app = Flask(__name__)
CORS(app)

TARGET_URL = "https://my.surfshark.com/account/p_api/v1/account/authorization/assign"

@app.route('/', methods=['GET'])
def home():
    return "Bot Surfshark Camuflado V2 - Online"

@app.route('/activar', methods=['POST'])
def activar_dispositivo():
    data = request.json
    codigo_tv = data.get('code')

    if not codigo_tv:
        return jsonify({"success": False, "message": "Falta el código"}), 400

    # Recuperamos la cookie desde las variables de Render
    mis_cookies = os.environ.get('SURFSHARK_COOKIE')

    if not mis_cookies:
        return jsonify({"success": False, "message": "Error: Falta la cookie en el servidor"}), 500

    # Configuración para engañar a Cloudflare
    headers = {
        "authority": "my.surfshark.com",
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://my.surfshark.com",
        "referer": "https://my.surfshark.com/account/login-code",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "cookie": mis_cookies
    }

    payload = {"code": codigo_tv}

    try:
        print(f"Intentando activar código {codigo_tv} simulando Chrome...")
        
        # Usamos impersonate='chrome110' para evitar el bloqueo TLS
        response = cffi_requests.post(
            TARGET_URL, 
            json=payload, 
            headers=headers, 
            impersonate="chrome110",
            timeout=20
        )
        
        print(f"Respuesta Surfshark: {response.status_code}")
        
        if response.status_code == 200:
            return jsonify({"success": True, "message": "¡Dispositivo activado con éxito!"})
        elif response.status_code == 404:
            return jsonify({"success": False, "message": "Código incorrecto o expirado."})
        elif response.status_code in [401, 403]:
            return jsonify({"success": False, "message": "Bloqueo de seguridad (IP/Cookie). Intenta el Plan B."})
        else:
            return jsonify({"success": False, "message": f"Error desconocido: {response.status_code}"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
