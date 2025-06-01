import csv
import re
import os
from datetime import timedelta

def ms_to_hms(ms):
    return str(timedelta(milliseconds=int(ms)))

def cargar_datos(nombre_archivo="music.csv"):
    with open(nombre_archivo, encoding='utf-8') as f:
        lector = csv.DictReader(f)
        return list(lector)

def buscar_titulo_o_artista(datos):
    texto = input("Ingrese parte del título o artista: ").strip()
    patron = re.compile(re.escape(texto), re.IGNORECASE)
    resultados = [d for d in datos if patron.search(d['artista']) or patron.search(d['track'])]
    resultados_ordenados = sorted(resultados, key=lambda x: int(x.get('reproducciones', 0)), reverse=True)
    print("\nResultados:")
    for r in resultados_ordenados:
        print(f"{r['artista']} - {r['track']} - {ms_to_hms(r['duracion_ms'])}")

def top10_artista(datos):
    artista = input("Ingrese el nombre del artista: ").strip()
    patron = re.compile(re.escape(artista), re.IGNORECASE)
    canciones = [d for d in datos if patron.search(d['artista'])]
    canciones_ordenadas = sorted(canciones, key=lambda x: int(x.get('reproducciones', 0)), reverse=True)[:10]
    for c in canciones_ordenadas:
        rep_millones = int(c.get('reproducciones', 0)) / 1_000_000
        print(f"{c['artista']} - {c['track']} - {ms_to_hms(c['duracion_ms'])} - {rep_millones:.2f}M reproducciones")

def validar_y_crear_registro(row):
    regex_uri = re.compile(r'^spotify:track:[a-zA-Z0-9]{22}$')
    regex_url = re.compile(r'^https?://[^\s]+$')
    if not (regex_uri.match(row['uri_spotify']) and regex_url.match(row['url_spotify']) and regex_url.match(row['url_youtube'])):
        print("Error en los formatos de URI o URL")
        return None
    if int(row['likes']) > int(row['views']):
        print("Likes no puede ser mayor a Views")
        return None
    return row

def insertar_registro():
    opcion = input("¿Desea insertar desde archivo CSV (A) o manualmente (M)? ").upper()
    if opcion == 'A':
        archivo = input("Nombre del archivo CSV: ")
        if not os.path.exists(archivo):
            print("Archivo no encontrado.")
            return
        with open(archivo, encoding='utf-8') as f:
            lector = csv.DictReader(f)
            nuevos = [validar_y_crear_registro(row) for row in lector if validar_y_crear_registro(row)]
        with open('music.csv', 'a', newline='', encoding='utf-8') as f:
            escritor = csv.DictWriter(f, fieldnames=nuevos[0].keys())
            for row in nuevos:
                escritor.writerow(row)
        print(f"{len(nuevos)} registros insertados.")
    elif opcion == 'M':
        campos = ['artista', 'track', 'album', 'uri_spotify', 'duracion_ms', 'url_spotify', 'url_youtube', 'likes', 'views', 'reproducciones']
        entrada = {campo: input(f"{campo}: ").strip() for campo in campos}
        if validar_y_crear_registro(entrada):
            with open('music.csv', 'a', newline='', encoding='utf-8') as f:
                escritor = csv.DictWriter(f, fieldnames=entrada.keys())
                escritor.writerow(entrada)
            print("Registro insertado.")

def mostrar_albums(datos):
    artista = input("Nombre del artista: ").strip()
    patron = re.compile(re.escape(artista), re.IGNORECASE)
    albums = {}
    for d in datos:
        if patron.search(d['artista']):
            alb = d['album']
            dur = int(d['duracion_ms'])
            albums.setdefault(alb, {'canciones': 0, 'duracion': 0})
            albums[alb]['canciones'] += 1
            albums[alb]['duracion'] += dur
    print(f"El artista tiene {len(albums)} álbumes.")
    for alb, info in albums.items():
        print(f"Álbum: {alb} - Canciones: {info['canciones']} - Duración total: {ms_to_hms(info['duracion'])}")

def menu():
    while True:
        datos = cargar_datos()
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