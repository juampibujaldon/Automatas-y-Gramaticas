import csv
import re
import os
from datetime import timedelta

COLUMNAS_CSV = ['Index', 'Artist', 'Url_spotify', 'Track', 'Album', 'Album_type', 'Uri', 'Danceability', 'Energy', 'Key', 'Loudness', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 'Duration_ms', 'Url_youtube', 'Title', 'Channel', 'Views', 'Likes', 'Comments', 'Licensed', 'official_video', 'Stream']

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

def ms_to_hms(ms):
    return str(timedelta(milliseconds=int(float(ms))))

def cargar_datos(nombre_archivo="spotify_and_youtube.csv"):
    with open(nombre_archivo, encoding='utf-8') as f:
        lector = csv.DictReader(f)
        next(lector)
        return list(lector)

def buscar_titulo_o_artista(datos):
    texto = input("Ingrese parte del título o artista: ").strip()
    patron = re.compile(re.escape(texto), re.IGNORECASE)
    resultados = [d for d in datos if patron.search(d['Artist']) or patron.search(d['Track'])]
    # resultados_ordenados = sorted(resultados, key=lambda x: float(x.get('Stream', 0)), reverse=True)
    print("\nResultados:")
    for r in resultados:
        print(f"{r['Artist']} - {r['Track']} - {ms_to_hms(r['Duration_ms'])}")

def top10_artista(datos):
    artista = input("Ingrese el nombre del artista: ").strip()
    patron = re.compile(re.escape(artista), re.IGNORECASE)
    canciones = [d for d in datos if patron.search(d['Artist'])]
    canciones_ordenadas = sorted(canciones, key=lambda x: float(x.get('Stream', 0)), reverse=True)[:10]
    for c in canciones_ordenadas:
        rep_millones = float(c.get('Stream', 0)) / 1_000_000
        print(f"{c['Artist']} - {c['Track']} - {ms_to_hms(c['Duration_ms'])} - {rep_millones:.2f}M reproducciones")

def insertar_registro():
    campos_personalizados = ['Artist', 'Track', 'Album', 'Uri', 'Duration_ms', 'Url_spotify', 'Url_youtube', 'Likes', 'Views', 'Stream']
    entrada = {col: "" for col in COLUMNAS_CSV}

    regex_uri = re.compile(r"^spotify:track:[\w]{22}$")
    regex_url_spotify = re.compile(r"^https?://open\.spotify\.com/(track|artist)/[\w]{22}$")
    regex_url_youtube = re.compile(r"^https?://(?:www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}$")

    for campo in campos_personalizados:
        while True:
            if campo == 'Duration_ms':
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
                        entrada['Duration_ms'] = str(ms)
                        break
                    except ValueError:
                        print("Formato de duración inválido. Intente nuevamente.")
                else:
                    entrada['Duration_ms'] = duracion_input
                    break
            else:
                valor = input(f"{campo}: ").strip()

                if campo == 'Uri' and not regex_uri.match(valor):
                    print("URI de Spotify inválida.")
                    continue
                elif campo == 'Url_spotify':
                    valor = limpiar_url_spotify(valor)
                    if not regex_url_spotify.match(valor):
                        print("URL de Spotify inválida.")
                        continue
                elif campo == 'Url_youtube':
                    valor = limpiar_url_youtube(valor)
                    if not regex_url_youtube.match(valor):
                        print("URL de YouTube inválida.")
                        continue

                entrada[campo] = valor
                break

    try:
        if int(entrada['Likes']) > int(entrada['Views']):
            print("\u274c Error: Likes no puede ser mayor que Views.")
            return
    except ValueError:
        print("\u274c Error: Likes y Views deben ser números.")
        return

    with open("spotify_and_youtube.csv", 'a', newline='', encoding='utf-8') as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
        if os.stat('spotify_and_youtube.csv').st_size == 0:
            escritor.writeheader()
        escritor.writerow(entrada)
    print("Registro insertado correctamente.")


def insertar_desde_archivo():
    archivo = input("Ingrese el nombre del archivo CSV: ").strip()
    if not os.path.exists(archivo):
        print("Archivo no encontrado.")
        return

    with open(archivo, encoding='utf-8') as f:
        lector = csv.DictReader(f)
        nuevos = []
        for row in lector:
            # Normalizar URLs
            row['Url_spotify'] = limpiar_url_spotify(row.get('Url_spotify', ''))
            row['Url_youtube'] = limpiar_url_youtube(row.get('Url_youtube', ''))

            # Validaciones
            try:
                if int(row.get('Likes', 0)) > int(row.get('Views', 0)):
                    print("Likes no puede ser mayor que Views.")
                    continue
            except ValueError:
                print("Likes y Views deben ser números.")
                continue

            regex_uri = re.compile(r"^spotify:track:[\w]{22}$")
            regex_url_spotify = re.compile(r"^https?://open\.spotify\.com/track/[\w]{22}/?$")
            regex_url_youtube = re.compile(r"^https?://(?:www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}$")

            if row.get("Uri") and not regex_uri.match(row["Uri"]):
                print("URI inválida.")
                continue
            if row.get("Url_spotify") and not regex_url_spotify.match(row["Url_spotify"]):
                print("URL de Spotify inválida.")
                continue
            if row.get("Url_youtube") and not regex_url_youtube.match(row["Url_youtube"]):
                print("URL de YouTube inválida.")
                continue

            nuevos.append({col: row.get(col, "") for col in COLUMNAS_CSV})

    if nuevos:
        with open('spotify_and_youtube.csv', 'a', newline='', encoding='utf-8') as f:
            escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
            if os.stat('spotify_and_youtube.csv').st_size == 0:
                escritor.writeheader()
            escritor.writerows(nuevos)
        print(f"{len(nuevos)} registros insertados correctamente.")


def mostrar_albums(datos):
    artista = input("Nombre del artista: ").strip()
    patron = re.compile(re.escape(artista), re.IGNORECASE)
    albums = {}
    for d in datos:
        if patron.search(d['Artist']):
            alb = d['Album']
            dur = float(d['Duration_ms'])
            albums.setdefault(alb, {'canciones': 0, 'duracion': 0})
            albums[alb]['canciones'] += 1
            albums[alb]['duracion'] += dur
    print(f"El artista tiene {len(albums)} álbumes.")
    for alb, info in albums.items():
        print(f"Álbum: {alb} - Canciones: {info['canciones']} - Duración total: {ms_to_hms(info['duracion'])}")

def menu():
    while True:
        datos_raw = cargar_datos()
        print("\n--- MENÚ ---")
        print("1. Buscar por título o artista")
        print("2. Top 10 canciones de un artista")
        print("3. Insertar un registro")
        print("4. Insertar registros desde archivo CSV")
        print("5. Mostrar álbumes de un artista")
        print("6. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            buscar_titulo_o_artista(datos_raw)
        elif opcion == '2':
            top10_artista(datos_raw)
        elif opcion == '3':
            insertar_registro()
        elif opcion == '4':
            insertar_desde_archivo()
        elif opcion == '5':
            mostrar_albums(datos_raw)
        elif opcion == '6':
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()

#revisar linea 34 a 36
#pedir que la uri sea un obligatoria