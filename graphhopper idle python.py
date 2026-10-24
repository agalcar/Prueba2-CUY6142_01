
import requests

geocode_url = "https://graphhopper.com/api/1/geocode"
route_url = "https://graphhopper.com/api/1/route"

key = "GRAPHHOPPER_API_KEY"  # Reemplazar por tu clave de GraphHopper


def salir(texto):
    return texto.strip().lower() in ("s", "salir")


def geocoding(location):
    while location == "":
        location = input("Ingresa nuevamente la ubicación: ")

        if salir(location):
            return None

    if salir(location):
        return None

    try:
        respuesta = requests.get(
            geocode_url,
            params={"q": location, "limit": 1, "key": key},
            timeout=20
        )

        if respuesta.status_code != 200:
            print("Error al consultar la ubicación.")
            print("Código HTTP:", respuesta.status_code)
            return None

        datos = respuesta.json()
        resultados = datos.get("hits", [])

        if not resultados:
            print("No se encontró la ubicación:", location)
            return None

        lugar = resultados[0]
        lat = lugar["point"]["lat"]
        lng = lugar["point"]["lng"]

        nombre = lugar.get("name", location)
        estado = lugar.get("state", "")
        pais = lugar.get("country", "")

        ubicacion = ", ".join(
            parte for parte in (nombre, estado, pais) if parte
        )

        print("Ubicación encontrada:", ubicacion)
        print(f"Latitud: {lat:.2f} | Longitud: {lng:.2f}")

        return lat, lng, ubicacion

    except (requests.RequestException, ValueError, KeyError) as error:
        print("No se pudo consultar la ubicación:", error)
        return None


while True:
    print("\n==========================================")
    print("       PLANIFICADOR DE RUTAS")
    print("==========================================")
    print("Escribe 's' o 'salir' para terminar.")

    loc1 = input("\nUbicación de origen: ")

    if salir(loc1):
        print("Programa finalizado.")
        break

    origen = geocoding(loc1)

    if origen is None:
        if salir(loc1):
            break
        continue

    loc2 = input("\nUbicación de destino: ")

    if salir(loc2):
        print("Programa finalizado.")
        break

    destino = geocoding(loc2)

    if destino is None:
        continue

    try:
        parametros = [
            ("key", key),
            ("point", f"{origen[0]},{origen[1]}"),
            ("point", f"{destino[0]},{destino[1]}"),
            ("profile", "car"),
            ("locale", "es"),
            ("instructions", "true")
        ]

        respuesta = requests.get(
            route_url,
            params=parametros,
            timeout=30
        )

        print("\nCódigo HTTP de la ruta:", respuesta.status_code)

        if respuesta.status_code != 200:
            print("No fue posible calcular la ruta.")
            print("Respuesta de la API:", respuesta.text[:300])
            continue

        datos = respuesta.json()
        rutas = datos.get("paths", [])

        if not rutas:
            print("No se encontraron rutas disponibles.")
            continue

        ruta = rutas[0]

        kilometros = ruta["distance"] / 1000
        millas = kilometros / 1.609344
        segundos = int(ruta["time"] / 1000)

        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_restantes = segundos % 60

        print("\n==========================================")
        print("          INFORMACIÓN DEL VIAJE")
        print("==========================================")
        print("Origen:", origen[2])
        print("Destino:", destino[2])
        print(f"Distancia: {kilometros:.2f} km / {millas:.2f} millas")
        print(
            f"Duración: {horas:02d}:"
            f"{minutos:02d}:{segundos_restantes:02d}"
        )

        print("\n========== INDICACIONES DE RUTA ==========")

        instrucciones = ruta.get("instructions", [])

        if not instrucciones:
            print("No se recibieron instrucciones de navegación.")

        for numero, instruccion in enumerate(instrucciones, start=1):
            texto = instruccion.get("text", "Continuar")
            distancia = instruccion.get("distance", 0) / 1000

            print(f"{numero}. {texto} ({distancia:.2f} km)")

        print("==========================================")

    except (requests.RequestException, ValueError, KeyError) as error:
        print("Ocurrió un error al calcular la ruta:", error)
