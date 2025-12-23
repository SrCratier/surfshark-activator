from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Permitimos que cualquier web (tu frontend) hable con este backend
CORS(app)

# URL y Headers configurados con tus datos extraídos
TARGET_URL = "https://my.surfshark.com/account/p_api/v1/account/authorization/assign"

@app.route('/', methods=['GET'])
def home():
    return "El Bot de Surfshark está vivo y esperando órdenes."

@app.route('/activar', methods=['POST'])
def activar_dispositivo():
    data = request.json
    codigo_tv = data.get('code')

    if not codigo_tv:
        return jsonify({"success": False, "message": "Falta el código"}), 400

    # Obtenemos tus credenciales secretas desde las Variables de Entorno de Render
    # ESTO ES IMPORTANTE PARA NO PUBLICAR TU COOKIE EN GITHUB
    mis_cookies = os.environ.get('SURFSHARK_COOKIE')
    user_agent = os.environ.get('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')

    if not mis_cookies:
        return jsonify({"success": False, "message": "Error de configuración: Faltan las cookies en el servidor."}), 500

    headers = {
        "authority": "my.surfshark.com",
        "method": "POST",
        "path": "/account/p_api/v1/account/authorization/assign",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "es-ES,es;q=0.9",
        "content-type": "application/json",
        "origin": "https://my.surfshark.com",
        "referer": "https://my.surfshark.com/account/login-code",
        "user-agent": user_agent,
        "cookie": mis_cookies
    }

    payload = {"code": codigo_tv}

    try:
        print(f"Intentando activar código: {codigo_tv}...")
        response = requests.post(TARGET_URL, json=payload, headers=headers)
        
        print(f"Respuesta Surfshark: {response.status_code}")
        
        if response.status_code == 200:
            return jsonify({"success": True, "message": "¡Dispositivo activado con éxito!"})
        elif response.status_code == 404:
            return jsonify({"success": False, "message": "Código incorrecto o expirado."})
        elif response.status_code == 401 or response.status_code == 403:
            return jsonify({"success": False, "message": "Error de sesión (Cookie expirada o bloqueo de seguridad)."})
        else:
            return jsonify({"success": False, "message": f"Error desconocido: {response.status_code}"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)