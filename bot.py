from serp_scraper import obtener_fixture_independiente
from twilio.rest import Client
from datetime import datetime
import re
import os

# Traducción manual de días abreviados
dias_es = {
    "Lun": "Mon", "Mar": "Tue", "Mié": "Wed", "mié": "Wed",
    "Jue": "Thu", "Vie": "Fri", "Sáb": "Sat", "Dom": "Sun","mar": "Tue"
}

def normalizar_fecha(fecha_str):
    for esp, eng in dias_es.items():
        if fecha_str.startswith(esp):
            return fecha_str.replace(esp, eng)
    return fecha_str

def limpiar_hora(hora_raw):
    if not hora_raw:
        return "Por definirse"
    hora_limpia = re.sub(r"[^\x00-\x7F]+", "", hora_raw).strip()

    return hora_limpia

def enviar_recordatorio():
    print("📡 Consultando SerpAPI...")
    partidos = obtener_fixture_independiente()
    print(f"📦 Partidos encontrados: {len(partidos)}")

    if not partidos:
        return

    account_sid = account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_TOKEN"
    client = Client(account_sid, auth_token)

    remitente = "whatsapp:+14155238886"
    destinatario = os.getenv("TWILIO_TO")

    hoy = datetime.now().date()

    for partido in partidos:
        try:
            fecha_raw = partido["fecha"].split(",")[0].strip()
            fecha_str = normalizar_fecha(fecha_raw)
            hora = limpiar_hora(partido["hora"])

            fecha_obj = None
            for formato in ("%a, %d/%m", "%d/%m", "%a %d-%m", "%a %d/%m"):
                try:
                    fecha_obj = datetime.strptime(fecha_str, formato)
                    break
                except ValueError:
                    continue

            if fecha_obj is None:
                print(f"⚠️ Error procesando partido: {partido['fecha']}")
                continue

            fecha = fecha_obj.replace(year=hoy.year).date()
            dias = (fecha - hoy).days

            if dias in [2, 0]:
                if partido["es_local"]:
                    msg = (
                        f"📣 ¡Recordá que juega Independiente!\n"
                        f"🏟️ Partido de LOCAL 🆚 Rival: {partido['visitante']}\n"
                        f"📅 Fecha: {partido['fecha']} 🕒 Hora: {hora}\n"
                        f"🏆 Competencia: {partido['competencia']}"
                    )
                else:
                    msg = (
                        f"📣 ¡Juega Independiente de visitante!\n"
                        f"🚌 Partido de VISITANTE 🆚 Rival: {partido['local']}\n"
                        f"📅 Fecha: {partido['fecha']} 🕒 Hora: {hora}\n"
                        f"🏆 Competencia: {partido['competencia']}"
                    )

                client.messages.create(body=msg, from_=remitente, to=destinatario)
                print("✅ Mensaje enviado.")
        except Exception as e:
            print("⚠️ Error procesando partido:", e)
