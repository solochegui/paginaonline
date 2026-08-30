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
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Cargar variables de entorno desde .env
load_dotenv()

# Enlaces de afiliados, música y productos
GUMROAD_LINK = os.getenv("GUMROAD_LINK", "https://nonfungiblemetaverse.gumroad.com/l/borisystem")
CRYPTOHOPPER_LINK = "https://www.cryptohopper.com/?atid=40719"
COINBASE_LINK = "https://coinbase.com/join/QHMF3XN?src=android-share"
SOUNDCLOUD_CHEGUI = "https://on.soundcloud.com/e61T4nkt0xF3OzPn9m"
SOUNDCLOUD_DOBLEF = "https://on.soundcloud.com/QUUYz1hJYSPHnHceUG"

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
STREAM_HISTORY = []
MAX_HISTORY_SIZE = 50  # Aumentado para almacenar más bloques del podcast

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
    "entusiasta, detallado y analítico estilo analista de Wall Street",
    "cuantitativo, técnico y enfocado en bots de alta frecuencia",
    "alerta de mercado urgente, informativo y dinámico",
    "educativo, técnico e instruccional sobre indicadores de volumen y RSI",
    "estilo podcaster de tecnología Web3, filosófico y de largo plazo"
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
        app.logger.error(f"[WARN] Error consultando noticias RSS: {e}")
    return "Consolidación generalizada y volatilidad detectada en altcoins."

def analizar_token(symbol, coin_id):
    """Calcula el precio actual, soporte, resistencia y RSI a 14 días para el token."""
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
            max_precio = round(df["close"].max(), 2)
            min_precio = round(df["close"].min(), 2)

            if rsi_val < 35:
                accion = "OPORTUNIDAD DE COMPRA INTENSIVA (Sobrevendido)"
                sugerencia_promo = f"Aprovecha este precio bajo en {symbol} comprando en Coinbase y llévate $20 en BTC gratis ({COINBASE_LINK}) o automatiza tus recompras con BoriSystem en Gumroad ({GUMROAD_LINK})."
            elif rsi_val > 65:
                accion = "TOMAR GANANCIAS / ZONA DE DISTRIBUCIÓN (Sobrecomprado)"
                sugerencia_promo = f"Con la alta volatilidad de {symbol}, automatiza la toma de ganancias mediante CryptoHopper ({CRYPTOHOPPER_LINK}) o relájate mientras el mercado decide escuchando la música de Chegüi ({SOUNDCLOUD_CHEGUI}) y Doble F ({SOUNDCLOUD_DOBLEF})."
            else:
                accion = "HOLD Y ACUMULACIÓN EN RANGO LATERAL"
                sugerencia_promo = f"Mientras {symbol} consolida en rango, explora los ritmos urbanos y Web3 de Chegüi ({SOUNDCLOUD_CHEGUI}) y Doble F ({SOUNDCLOUD_DOBLEF}) en SoundCloud, o configura tu bot en CryptoHopper ({CRYPTOHOPPER_LINK})."

            return {
                "resumen": f"{symbol}: ${precio} (RSI 14d: {rsi_val}) | Máx 30d: ${max_precio} | Mín 30d: ${min_precio} -> {accion}",
                "sugerencia_promo": sugerencia_promo
            }
    except requests.exceptions.RequestException as e:
        app.logger.error(f"[WARN] Error analizando token {symbol}: {e}")
    return {
        "resumen": f"{symbol}: Analizando flujo de ordenes y volatilidad actual.",
        "sugerencia_promo": f"Conéctate a Coinbase ({COINBASE_LINK}) para comprar {symbol} o adquiere BoriSystem en Gumroad ({GUMROAD_LINK})."
    }

def generar_transmision_qwen():
    """Hilo en segundo plano que genera monólogos extensos para el podcast 24/7."""
    app.logger.info(f"🤖 BoriBot Influencer 24/7 iniciado activando modelo {MODEL_NAME}...")
    token_keys = list(TOKENS.keys())

    while True:
        try:
            symbol = random.choice(token_keys)
            coin_id = TOKENS[symbol]
            estilo = random.choice(ESTILOS)

            noticia = obtener_noticia()
            datos_analisis = analizar_token(symbol, coin_id)

            prompt = f"""
            Eres BoriBot, el locutor e influencer principal de un podcast de criptomonedas y trading transmitido 24 horas en vivo.
            
            ESTADO DEL MERCADO EN TIEMPO REAL:
            - Criptomoneda a analizar: {symbol}
            - Datos técnicos exhaustivos: {datos_analisis['resumen']}
            - Última noticia relevante: {noticia}
            - Contexto promocional adaptado: {datos_analisis['sugerencia_promo']}

            MALLA Y LISTA COMPLETA DE ENLACES OBLIGATORIOS A MENCIONAR ORGANICAMENTE EN EL DISCURSO:
            1. BoriSystem en Gumroad: {GUMROAD_LINK} (Herramienta principal de trading)
            2. CryptoHopper: {CRYPTOHOPPER_LINK} (Plataforma de bots automatizados)
            3. Coinbase: {COINBASE_LINK} (Regístrate y gana $20 en Bitcoin gratis)
            4. SoundCloud Chegüi: {SOUNDCLOUD_CHEGUI} (Música oficial para traders)
            5. SoundCloud Doble F: {SOUNDCLOUD_DOBLEF} (Tracks exclusivos en SoundCloud)

            INSTRUCCIONES DE NARRACIÓN (PODCAST EXTENSO):
            - Adopta un estilo {estilo}.
            - Desarrolla una locución SUMAMENTE EXTENSA y detallada (al menos 4 párrafos completos) dividida en:
              1. INTRODUCCIÓN Y CONTEXTO MACRO: Presenta la sesión del podcast en vivo, menciona el headline actual ({noticia}) y cómo afecta el sentimiento general.
              2. ANÁLISIS TÉCNICO PROFUNDO DE {symbol}: Desglosa el precio, los niveles de soporte/resistencia de los últimos 30 días, el comportamiento del indicador RSI y la estrategia recomendada.
              3. INTEGRACIÓN COMERCIAL Y AFILIADOS: Integra de manera natural y persuasiva la invitación a usar Coinbase, automatizar las entradas en CryptoHopper o adquirir BoriSystem en Gumroad basándote estrictamente en si la moneda está sobrecomprada, sobrevendida o lateral.
              4. SECCIÓN CULTURAL Y CIERRE: Cierra el segmento invitando a la audiencia a relajarse y disfrutar de la música de Chegüi y Doble F en SoundCloud mientras monitorean sus operaciones.
            """

            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )

            mensaje_ia = response['message']['content']
            timestamp = time.strftime("%H:%M:%S")

            STREAM_HISTORY.append({
                "time": timestamp,
                "token": symbol,
                "text": mensaje_ia,
                "link": GUMROAD_LINK
            })

            if len(STREAM_HISTORY) > MAX_HISTORY_SIZE:
                STREAM_HISTORY.pop(0)

            app.logger.info(f"[{timestamp}] [{symbol}] Transmisión generada con éxito ({len(mensaje_ia)} caracteres).\n")

        except Exception as e:
            app.logger.error(f"[ERROR] En transmisión de IA: {e}")

        # Pausa de 30 segundos entre cada bloque extenso
        time.sleep(30)

@app.route('/api/podcast-live', methods=['GET'])
def get_podcast_live():
    """Endpoint API JSON para consumir el historial del podcast."""
    return jsonify(STREAM_HISTORY)

if __name__ == '__main__':
    thread = threading.Thread(target=generar_transmision_qwen, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
