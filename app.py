import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import requests
import ta
import ollama

app = Flask(__name__)
CORS(app)

GUMROAD_LINK = "https://nonfungiblemetaverse.gumroad.com/l/borisystem"
STREAM_HISTORY = []

TOKENS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "1INCH": "1inch",
    "ATOM": "cosmos",
    "ADA": "cardano",
    "POL": "polygon-ecosystem-token",
    "AVAX": "avalanche-2",
    "DOT": "polkadot"
}

def obtener_noticia():
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("Data"):
            item = res["Data"][0]
            return item.get("title", "Mercado con alta actividad")
    except Exception:
        pass
    return "Consolidación generalizada en los mercados de altcoins."

def analizar_token(symbol, coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            prices = [p[1] for p in res.json()["prices"]]
            df = pd.DataFrame(prices, columns=["close"])
            df["rsi"] = ta.momentum.rsi(df["close"], window=14)
            
            rsi_val = round(df["rsi"].iloc[-1], 1)
            precio = round(df["close"].iloc[-1], 2)
            
            if rsi_val < 35:
                accion = "OPORTUNIDAD DE COMPRA (Sobrevendido)"
            elif rsi_val > 65:
                accion = "TOMAR GANANCIAS (Sobrecomprado)"
            else:
                accion = "HOLD / ACUMULACIÓN"
                
            return f"{symbol}: ${precio} (RSI: {rsi_val}) -> {accion}"
    except Exception:
        pass
    return None

def generar_transmision_qwen():
    print("🤖 Agente Influencer 24/7 iniciado con Qwen...")
    while True:
        try:
            noticia = obtener_noticia()
            analisis = analizar_token("BTC", TOKENS["BTC"])
            
            prompt = f"""
            Eres BoriBot, un influencer apasionado de criptomonedas, tecnología y host de podcast en vivo 24/7.
            
            DATOS ACTUALES DEL MERCADO:
            - Noticia reciente: {noticia}
            - Análisis técnico: {analisis}
            - Producto promocional: BoriSystem en Gumroad ({GUMROAD_LINK})
            
            TAREA:
            Genera un mensaje dinámico estilo transmisión de radio/podcast (máximo 4 oraciones).
            1. Da un comentario entusiasta sobre la noticia o el mercado técnico.
            2. Da una breve recomendación o análisis.
            3. Haz un llamado a la acción (CTA) invitando a los oyentes a automatizar sus estrategias con tu sistema BoriSystem en Gumroad.
            Habla directamente al público, sé directo y profesional.
            """

            response = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{"role": "user", "content": prompt}]
            )
            
            mensaje_ia = response['message']['content']
            timestamp = time.strftime("%H:%M:%S")

            STREAM_HISTORY.append({
                "time": timestamp,
                "text": mensaje_ia,
                "link": GUMROAD_LINK
            })
            
            if len(STREAM_HISTORY) > 15:
                STREAM_HISTORY.pop(0)

            print(f"[{timestamp}] Qwen Influencer: {mensaje_ia}\n")

        except Exception as e:
            print(f"Error generando transmisión con Qwen: {e}")

        time.sleep(60)

@app.route('/api/podcast-live', methods=['GET'])
def get_podcast_live():
    return jsonify(STREAM_HISTORY)

if __name__ == '__main__':
    thread = threading.Thread(target=generar_transmision_qwen, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
