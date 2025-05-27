import csv
import os

# with open('movies.csv', newline='', encoding='utf-8') as csvfile:
#     reader = csv.reader(csvfile)
#     # for row in reader:
#     #     print(row)


CSV_FILE = 'movies.csv'
PLATFORMS = ['Netflix', 'Hulu', 'Prime Video', 'Disney+']
CATEGORIES = ['7+', '13+', '16+', '18+', 'all']  
RATINGS = [str(i) for i in range(0, 101)]

def load_movies():
    with open(CSV_FILE, encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_movies(movies, fieldnames):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(movies)

def buscar_por_titulo(movies):
    texto = input("Ingrese parte del título: ").upper()
    encontrados = [m for m in movies if texto in m['Title'].upper()]
    if encontrados:
        for m in encontrados:
            plataformas = [p for p in PLATFORMS if m.get(p, '0') == '1']
            print(f"{m['Title']} ({', '.join(plataformas)}, {m['Age']}, Rating: {m['Rating']})")
    else:
        print("No se encontraron películas.")


def buscar_por_plataforma_categoria(movies):
    print("Plataformas disponibles:", ', '.join(PLATFORMS))

    # hago el mapeo para soportar entrada flexible (ej: 'netflix', 'NETFLIX', 'Netflix')
    plataformas_mapeadas = {p.lower(): p for p in PLATFORMS}

    plataforma_input = input("Seleccione plataforma: ").strip().lower()

    if plataforma_input not in plataformas_mapeadas:
        print("Plataforma inválida.")
        return

    plataforma = plataformas_mapeadas[plataforma_input]

    print("Categorías disponibles:", ', '.join(CATEGORIES))
    categoria = input("Seleccione categoría: ").strip()
    if categoria not in CATEGORIES:
        print("Categoría inválida.")
        return

    filtradas = [m for m in movies if m.get(plataforma, '0') == '1' and m.get('Age', '') == categoria]

    def get_rating(m):
        try:
            return float(m['Rating'].split('/')[0]) if '/' in m['Rating'] else float(m['Rating'])
        except:
            return 0

    filtradas.sort(key=get_rating, reverse=True)

    if filtradas:
        for m in filtradas[:10]:
            print(f"{m['Title']} (Rating: {m['Rating']})")
    else:
        print("No se encontraron películas.")


def insertar_pelicula(movies, fieldnames):
    nueva = {}

    title = input("Ingrese título de la película: ").strip()
    if not title:
        print("Error: el título no puede estar vacío.")
        return
    nueva['Title'] = title

    print("Indique si la película está disponible en cada plataforma:")
    for plataforma in PLATFORMS:
        while True:
            resp = input(f"¿Está en {plataforma}? (s/n): ").strip().lower()
            if resp in ['s', 'si', 'sí']:
                nueva[plataforma] = '1'
                break
            elif resp in ['n', 'no']:
                nueva[plataforma] = '0'
                break
            else:
                print("Respuesta inválida. Ingrese 's' para sí o 'n' para no.")

    print("Categorías disponibles:", ', '.join(CATEGORIES))
    categoria = input("Ingrese categoría: ").strip()
    if categoria not in CATEGORIES:
        print("Error: categoría inválida.")
        return
    nueva['Age'] = categoria

    while True:
        year = input("Ingrese el año de la película (ej: 2020): ").strip()
        if year.isdigit() and 1800 <= int(year) <= 2100:
            nueva['Year'] = year
            break
        else:
            print("Error: ingrese un año válido entre 1800 y 2100.")

    while True:
        rating = input("Ingrese rating (0-100): ").strip()
        if rating.isdigit() and 0 <= int(rating) <= 100:
            nueva['Rating'] = f"{rating}/100"
            break
        else:
            print("Error: rating inválido. Debe ser un número entre 0 y 100.")

    movies.append(nueva)
    save_movies(movies, fieldnames)
    print("Película agregada correctamente.")


def main():
    if not os.path.exists(CSV_FILE):
        print(f"No se encontró el archivo {CSV_FILE}")
        return
    movies = load_movies()
    fieldnames = movies[0].keys() if movies else ['Title', 'platform', 'category', 'rating']
    while True:
        print("\nMenú:")
        print("1 - Buscar por título")
        print("2 - Buscar por plataforma y categoría")
        print("3 - Insertar una nueva película")
        print("0 - Salir")
        op = input("Seleccione opción: ")
        if op == '1':
            buscar_por_titulo(movies)
        elif op == '2':
            buscar_por_plataforma_categoria(movies)
        elif op == '3':
            insertar_pelicula(movies, fieldnames)
            movies = load_movies() 
        elif op == '0':
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
