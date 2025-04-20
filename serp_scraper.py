import requests

def obtener_fixture_independiente():
    api_key = "b542e28fb1213be0b91911964158008785c373486679ac7b2a4994e686eaa8ba"
    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": "Independiente próximos partidos",
        "hl": "es",
        "gl": "ar",
        "api_key": api_key,
    }

    response = requests.get(url, params=params)
    data = response.json()

    partidos = []
    sports = data.get("sports_results", {})

    def procesar_partido(p):
        try:
            equipos = p.get("teams", [])
            if len(equipos) < 2:
                return None
            local = equipos[0]["name"]
            visitante = equipos[1]["name"]
            competencia = p.get("league", "Desconocida")
            estadio = p.get("stadium", "")
            hora = p.get("time", "Por definirse")
            fecha_str = p.get("date", "")

            es_local = "Independiente" in local
            es_visitante = "Independiente" in visitante

            if not (es_local or es_visitante):
                return None

            return {
                "local": local,
                "visitante": visitante,
                "fecha": fecha_str,
                "hora": hora,
                "competencia": competencia,
                "estadio": estadio,
                "es_local": es_local,
            }
        except Exception as e:
            print("❌ Error extrayendo partido:", e)
            return None

    if "game_spotlight" in sports:
        partido_destacado = procesar_partido(sports["game_spotlight"])
        if partido_destacado:
            partidos.append(partido_destacado)

    for partido_raw in sports.get("games", []):
        partido = procesar_partido(partido_raw)
        if partido:
            partidos.append(partido)

    return partidos