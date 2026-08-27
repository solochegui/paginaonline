import time
import random
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

ESTILOS = [
    "entusiasta y analítico",
    "directo y enfocado en trading cuantitativo",
    "alerta de mercado urgente y dinámico",
    "educativo sobre indicadores técnicos",
    "estilo podcaster de tecnología y Web3"
]

def obtener_noticia():
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("Data"):
            items = res["Data"][:5]
            item = random.choice(items)
            return item.get("title", "Mercado con alta actividad")
    except Exception:
        pass
    return "Consolidación generalizada y volatilidad detectada en altcoins."

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
                accion = "HOLD / ACUMULACIÓN NEUTRA"
                
            return f"{symbol}: ${precio} (RSI: {rsi_val}) -> {accion}"
    except Exception:
        pass
    return f"{symbol}: Analizando flujo de ordenes y volatilidad actual."

def generar_transmision_qwen():
    print("🤖 BoriBot Influencer 24/7 iniciado (Modo dinámico)...")
    token_keys = list(TOKENS.keys())
    
    while True:
        try:
            symbol = random.choice(token_keys)
            coin_id = TOKENS[symbol]
            estilo = random.choice(ESTILOS)
            
            noticia = obtener_noticia()
            analisis = analizar_token(symbol, coin_id)
            
            prompt = f"""
            Eres BoriBot, el host e influencer 24/7 de criptomonedas, bots de trading y Web3.
            
            MERCADO EN TIEMPO REAL:
            - Token enfocado ahora: {symbol}
            - Análisis del token: {analisis}
            - Headline actual: {noticia}
            - Producto: BoriSystem en Gumroad ({GUMROAD_LINK})
            
            INSTRUCCIONES:
            - Adopta un tono {estilo}.
            - Genera un bloque para el podcast live (máximo 3 o 4 oraciones).
            - Habla explícitamente sobre los datos de {symbol} y la noticia.
            - Cierra invitando a automatizar sus entradas con BoriSystem en Gumroad.
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
            
            if len(STREAM_HISTORY) > 20:
                STREAM_HISTORY.pop(0)

            print(f"[{timestamp}] [{symbol}] Qwen Influencer: {mensaje_ia}\n")

        except Exception as e:
            print(f"Error en transmisión Qwen: {e}")

        time.sleep(45)

@app.route('/api/podcast-live', methods=['GET'])
def get_podcast_live():
    return jsonify(STREAM_HISTORY)

if __name__ == '__main__':
    thread = threading.Thread(target=generar_transmision_qwen, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
