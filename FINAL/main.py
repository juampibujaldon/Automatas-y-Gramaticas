import csv
import re
import os
from datetime import timedelta

# Limpieza de URLs

def limpiar_url_spotify(url):
    url = url.split('?')[0]
    return url.replace("open.spotify.com/intl-es/", "open.spotify.com/")

def limpiar_url_youtube(url):
    if "watch?v=" in url:
        id_video = url.split("watch?v=")[1][:11]
        return "https://www.youtube.com/watch?v=" + id_video
    elif "youtu.be/" in url:
        id_video = url.split("youtu.be/")[1][:11]
        return "https://youtu.be/" + id_video
    return url

# Conversión de milisegundos a HH:MM:SS

def ms_to_hms(ms):
    return str(timedelta(milliseconds=int(float(ms))))

# Carga de datos

def cargar_datos(nombre_archivo="spotify_and_youtube.csv"):
    with open(nombre_archivo, encoding='utf-8') as f:
        lector = csv.DictReader(f)
        return list(lector)

def normalizar_columnas(datos):
    return [
        {
            'artista': d['Artist'],
            'track': d['Track'],
            'album': d['Album'],
            'uri_spotify': d['Uri'],
            'duracion_ms': d['Duration_ms'],
            'url_spotify': d['Url_spotify'],
            'url_youtube': d['Url_youtube'],
            'likes': d['Likes'],
            'views': d['Views'],
            'reproducciones': d['Stream']
        }
        for d in datos
    ]

# Validación de registro

def validar_y_crear_registro(row):
    row['url_spotify'] = limpiar_url_spotify(row['url_spotify'])
    row['url_youtube'] = limpiar_url_youtube(row['url_youtube'])

    regex_uri = re.compile(r"^spotify:track:[\w]{22}$")
    regex_url_spotify = re.compile(r"^https?://open\.spotify\.com/track/[\w]{22}$")
    regex_url_youtube = re.compile(r"^https?://(?:www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}$")

    if not (
        regex_uri.match(row['uri_spotify']) and
        regex_url_spotify.match(row['url_spotify']) and
        regex_url_youtube.match(row['url_youtube'])
    ):
        print("\u274c Error: URI o URLs no válidas.")
        return None

    try:
        likes = int(row['likes'])
        views = int(row['views'])
        if likes > views:
            print("\u274c Error: Likes no puede ser mayor que Views.")
            return None
    except ValueError:
        print("\u274c Error: Likes y Views deben ser números.")
        return None

    return row

# Funcionalidades principales

def buscar_titulo_o_artista(datos):
    texto = input("Ingrese parte del título o artista: ").strip()
    patron = re.compile(re.escape(texto), re.IGNORECASE)
    resultados = [d for d in datos if patron.search(d['artista']) or patron.search(d['track'])]
    resultados_ordenados = sorted(resultados, key=lambda x: float(x.get('reproducciones', 0)), reverse=True)
    print("\nResultados:")
    for r in resultados_ordenados:
        print(f"{r['artista']} - {r['track']} - {ms_to_hms(r['duracion_ms'])}")

def top10_artista(datos):
    artista = input("Ingrese el nombre del artista: ").strip()
    patron = re.compile(re.escape(artista), re.IGNORECASE)
    canciones = [d for d in datos if patron.search(d['artista'])]
    canciones_ordenadas = sorted(canciones, key=lambda x: float(x.get('reproducciones', 0)), reverse=True)[:10]
    for c in canciones_ordenadas:
        rep_millones = float(c.get('reproducciones', 0)) / 1_000_000
        print(f"{c['artista']} - {c['track']} - {ms_to_hms(c['duracion_ms'])} - {rep_millones:.2f}M reproducciones")

def insertar_registro():
    campos = ['artista', 'track', 'album', 'uri_spotify', 'duracion_ms', 'url_spotify', 'url_youtube', 'likes', 'views', 'reproducciones']
    opcion = input("¿Desea insertar desde archivo CSV (A) o manualmente (M)? ").upper()

    if opcion == 'A':
        archivo = input("Nombre del archivo CSV: ")
        if not os.path.exists(archivo):
            print("Archivo no encontrado.")
            return
        with open(archivo, encoding='utf-8') as f:
            lector = csv.DictReader(f)
            nuevos = [validar_y_crear_registro(row) for row in lector if validar_y_crear_registro(row)]
        if nuevos:
            with open('spotify_and_youtube.csv', 'a', newline='', encoding='utf-8') as f:
                escritor = csv.DictWriter(f, fieldnames=nuevos[0].keys())
                for row in nuevos:
                    escritor.writerow(row)
            print(f"{len(nuevos)} registros insertados.")

    elif opcion == 'M':
        entrada = {}
        regex_uri = re.compile(r"^spotify:track:[\w]{22}$")
        regex_url_spotify = re.compile(r"^https?://open\.spotify\.com/(track|album|artist|playlist)/[\w]{22}(\?.*)?$")
        regex_url_youtube = re.compile(r"^https?://(?:www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}([&?].*)?$")

        for campo in campos:
            while True:
                if campo == 'duracion_ms':
                    duracion_input = input(f"{campo} (en milisegundos o HH:MM:SS o MM:SS): ").strip()
                    if ':' in duracion_input:
                        partes = duracion_input.split(':')
                        try:
                            if len(partes) == 2:
                                minutos, segundos = map(int, partes)
                                ms = (minutos * 60 + segundos) * 1000
                            elif len(partes) == 3:
                                horas, minutos, segundos = map(int, partes)
                                ms = (horas * 3600 + minutos * 60 + segundos) * 1000
                            else:
                                raise ValueError
                            entrada[campo] = str(ms)
                            break
                        except ValueError:
                            print("❌ Formato de duración inválido. Intente nuevamente.")
                    else:
                        entrada[campo] = duracion_input
                        break
                else:
                    valor = input(f"{campo}: ").strip()

                    if campo == 'uri_spotify' and not regex_uri.match(valor):
                        print("❌ URI de Spotify inválida.")
                        continue
                    elif campo == 'url_spotify':
                        valor = limpiar_url_spotify(valor)
                        if not regex_url_spotify.match(valor):
                            print("❌ URL de Spotify inválida.")
                            continue
                    elif campo == 'url_youtube':
                        valor = limpiar_url_youtube(valor)
                        if not regex_url_youtube.match(valor):
                            print("❌ URL de YouTube inválida.")
                            continue

                    entrada[campo] = valor
                    break

        if validar_y_crear_registro(entrada):
            with open('spotify_and_youtube.csv', 'a', newline='', encoding='utf-8') as f:
                escritor = csv.DictWriter(f, fieldnames=entrada.keys())
                escritor.writerow(entrada)
            print("✅ Registro insertado.")

def mostrar_albums(datos):
    artista = input("Nombre del artista: ").strip()
    patron = re.compile(re.escape(artista), re.IGNORECASE)
    albums = {}
    for d in datos:
        if patron.search(d['artista']):
            alb = d['album']
            dur = float(d['duracion_ms'])
            albums.setdefault(alb, {'canciones': 0, 'duracion': 0})
            albums[alb]['canciones'] += 1
            albums[alb]['duracion'] += dur
    print(f"El artista tiene {len(albums)} álbumes.")
    for alb, info in albums.items():
        print(f"Álbum: {alb} - Canciones: {info['canciones']} - Duración total: {ms_to_hms(info['duracion'])}")

def menu():
    while True:
        datos_raw = cargar_datos()
        datos = normalizar_columnas(datos_raw)
        print("\n--- MENÚ ---")
        print("1. Buscar por título o artista")
        print("2. Top 10 canciones de un artista")
        print("3. Insertar un registro")
        print("4. Mostrar álbumes de un artista")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            buscar_titulo_o_artista(datos)
        elif opcion == '2':
            top10_artista(datos)
        elif opcion == '3':
            insertar_registro()
        elif opcion == '4':
            mostrar_albums(datos)
        elif opcion == '5':
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()


#!!!!   Justificación de herramientas:

    # # csv: para manipular archivos .csv de forma estructurada.

    # # re (expresiones regulares): para búsquedas parciales e insensibles a mayúsculas/minúsculas, y validación de entradas.

    # # datetime.timedelta: para convertir duración en milisegundos a formato HH:MM:SS.

    # # os.path.exists: para validar la existencia de archivos al insertar registros desde un archivo externo.