from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# Historial de publicaciones del Informante
publicaciones = [
    {
        "id": 1,
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "text": "Sistema Informante iniciado correctamente. Esperando actualizaciones...",
        "link": "https://t.me/boost/bori_channel"
    }
]

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/feed')
def get_feed():
    return jsonify(publicaciones)

@app.route('/api/publicar', methods=['POST'])
def publicar():
    data = request.get_json()
    if data and 'text' in data:
        nuevo_item = {
            "id": len(publicaciones) + 1,
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "text": data['text'],
            "link": data.get('link', 'https://t.me/boost/bori_channel')
        }
        publicaciones.append(nuevo_item)
        if len(publicaciones) > 30:
            publicaciones.pop(0)
        return jsonify({"status": "ok", "item": nuevo_item}), 200
    return jsonify({"status": "error", "message": "Falta el campo 'text'"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
