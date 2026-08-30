import os
import random
import threading
import time
import xml.etree.ElementTree as ET
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import requests
import ta
import ollama

app = Flask(__name__)
CORS(app)

# Variables de configuración global
GUMROAD_LINK = os.getenv("GUMROAD_LINK", "https://nonfungiblemetaverse.gumroad.com/l/borisystem")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
STREAM_HISTORY = []
MAX_HISTORY_SIZE = 20

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
    """Obtiene titulares recientes desde el RSS público de Cointelegraph."""
    url = "https://cointelegraph.com/rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        root = ET.fromstring(res.content)
        items = root.findall("./channel/item")
        if items:
            item = random.choice(items[:5])
            title = item.find("title")
            if title is not None and title.text:
                return title.text
    except Exception as e:
        print(f"[WARN] Error consultando noticias RSS: {e}")
    return "Consolidación generalizada y volatilidad detectada en altcoins."

def analizar_token(symbol, coin_id):
    """Calcula el precio actual y RSI a 14 días para el token seleccionado."""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
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
    except requests.exceptions.RequestException as e:
        print(f"[WARN] Error analizando token {symbol}: {e}")
    return f"{symbol}: Analizando flujo de ordenes y volatilidad actual."

def generar_transmision_qwen():
    """Hilo en segundo plano que consulta Ollama y mantiene el buffer del podcast."""
    print(f"🤖 BoriBot Influencer 24/7 iniciado activando modelo {MODEL_NAME}...")
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
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )

            mensaje_ia = response['message']['content']
            timestamp = time.strftime("%H:%M:%S")

            STREAM_HISTORY.append({
                "time": timestamp,
                "text": mensaje_ia,
                "link": GUMROAD_LINK
            })

            if len(STREAM_HISTORY) > MAX_HISTORY_SIZE:
                STREAM_HISTORY.pop(0)

            print(f"[{timestamp}] [{symbol}] Influencer Live: {mensaje_ia}\n")

        except Exception as e:
            print(f"[ERROR] En transmisión de IA: {e}")

        time.sleep(45)

@app.route('/api/podcast-live', methods=['GET'])
def get_podcast_live():
    """Endpoint API JSON para consumir el historial del podcast."""
    return jsonify(STREAM_HISTORY)

if __name__ == '__main__':
    thread = threading.Thread(target=generar_transmision_qwen, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
