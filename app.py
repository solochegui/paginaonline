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

# Enlaces y Datos Clave
ENLACES = {
    "coinbase": "https://coinbase.com/join/QHMF3XN?src=android-share",
    "robinhood": "https://join.robinhood.com/josea8104",
    "gumroad": GUMROAD_LINK
}

BORICOIN_DATA = {
    "symbol": "BRCN",
    "price": "0.0400 USD",
    "change": "+0.33%",
    "supply": "999,998,297 BRCN",
    "status": "Autoridades revocadas (Mint/Freeze/Metadata) - 100% Descentralizado"
}

TOKENS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "AVAX": "avalanche-2"
}

ESTILOS = [
    "entusiasta e influencer crypto",
    "analista técnico y cuantitativo",
    "educador Web3 y recomendador de bots",
    "host de podcast en vivo"
]

TEMAS_ESPECIALES = ["BORICOIN", "REFERIDOS", "MERCADO", "BORIFIGHT"]

def obtener_noticia():
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("Data"):
            item = random.choice(res["Data"][:5])
            return item.get("title", "Mercado crypto con alta actividad")
    except Exception:
        pass
    return "Consolidación generalizada y flujo de volumen en altcoins."

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
    return f"{symbol}: Analizando volumen y liquidez actual."

def generar_transmision_qwen():
    print("🤖 BoriBot Influencer 24/7 iniciado (Modo Ampliado con Boricoin y Referidos)...")
    
    while True:
        try:
            tema = random.choice(TEMAS_ESPECIALES)
            estilo = random.choice(ESTILOS)
            link_promovido = GUMROAD_LINK
            
            if tema == "BORICOIN":
                contexto_prompt = f"""
                TEMA: Presentación y Análisis de Boricoin (BRCN).
                - Datos actuales: Precio {BORICOIN_DATA['price']} ({BORICOIN_DATA['change']}), Suministro Total: {BORICOIN_DATA['supply']}.
                - Seguridad: Mint, Freeze y Metadata Authority están completamente REVOCADOS.
                - Recomendación de IA: Boricoin demuestra una estructura totalmente transparente en DexLab sin riesgo de emisión adicional. Excelente para sostener en el ecosistema.
                """
                link_promovido = "https://app.dexlab.space"

            elif tema == "REFERIDOS":
                opcion = random.choice(["Coinbase", "Robinhood", "Cryptohopper"])
                if opcion == "Coinbase":
                    contexto_prompt = f"RECOMENDACIÓN IA: Regístrate en Coinbase con mi enlace ({ENLACES['coinbase']}) y ambos ganaremos $20 en Bitcoin gratis."
                    link_promovido = ENLACES["coinbase"]
                elif opcion == "Robinhood":
                    contexto_prompt = f"RECOMENDACIÓN IA: Únete a Robinhood usando mi link ({ENLACES['robinhood']}) y ambos obtendremos una acción de regalo gratis para nuestro portafolio."
                    link_promovido = ENLACES["robinhood"]
                else:
                    contexto_prompt = "RECOMENDACIÓN IA: Optimiza tus operaciones creando tu bot en Cryptohopper. Al invitar amigos ganas hasta un 15% de comisión en cada suscripción."
                    link_promovido = GUMROAD_LINK

            elif tema == "BORIFIGHT":
                contexto_prompt = """
                TEMA: Comunidad BoriFight 🥊.
                - Invita a los oyentes a unirse al grupo de Telegram BoriFight donde se debate trading, bots automatizados y estrategias crypto en tiempo real.
                """

            else: # MERCADO CRIPTO EN VIVO
                symbol = random.choice(list(TOKENS.keys()))
                coin_id = TOKENS[symbol]
                analisis = analizar_token(symbol, coin_id)
                noticia = obtener_noticia()
                contexto_prompt = f"""
                TEMA: Análisis del mercado crypto en vivo.
                - Análisis del token: {analisis}
                - Noticia del momento: {noticia}
                - Recomendación de IA: Automatizar estas señales de mercado con BoriSystem en Gumroad.
                """
                link_promovido = GUMROAD_LINK

            prompt = f"""
            Eres BoriBot, el host e influencer 24/7 oficial.
            Tono: {estilo}.
            
            INFORMACIÓN PARA ESTE BLOQUE DEL PODCAST:
            {contexto_prompt}
            
            INSTRUCCIONES:
            - Habla en español como un host dinámico frente al micrófono.
            - Escribe entre 3 y 4 oraciones fluidas listas para ser leídas por la voz en el HTML.
            - Incluye siempre una recomendación clara de la Inteligencia Artificial para los oyentes.
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
                "link": link_promovido
            })
            
            if len(STREAM_HISTORY) > 20:
                STREAM_HISTORY.pop(0)

            print(f"[{timestamp}] [{tema}] Qwen: {mensaje_ia}\n")

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
