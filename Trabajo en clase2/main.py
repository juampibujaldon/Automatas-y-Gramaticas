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
    texto = input("Ingrese parte del título: ").lower()
    encontrados = [m for m in movies if texto in m['Title'].lower()]
    if encontrados:
        for m in encontrados:
            print(f"{m['Title']} ({m['platform']}, {m['category']}, Rating: {m['rating']})")
    else:
        print("No se encontraron películas.")

def buscar_por_plataforma_categoria(movies):
    print("Plataformas disponibles:", ', '.join(PLATFORMS))
    plataforma = input("Seleccione plataforma: ")
    if plataforma not in PLATFORMS:
        print("Plataforma inválida.")
        return
    print("Categorías disponibles:", ', '.join(CATEGORIES))
    categoria = input("Seleccione categoría: ")
    if categoria not in CATEGORIES:
        print("Categoría inválida.")
        return
    # Filtrar por plataforma (columna con valor '1') y categoría (columna 'Age')
    filtradas = [m for m in movies if m.get(plataforma, '0') == '1' and m.get('Age', '') == categoria]
    # Limpiar el rating para que sea solo el número antes del '/'
    def get_rating(m):
        return float(m['Rating'].split('/')[0]) if '/' in m['Rating'] else float(m['Rating'])
    filtradas.sort(key=get_rating, reverse=True)
    for m in filtradas[:10]:
        print(f"{m['Title']} (Rating: {m['Rating']})")
    if not filtradas:
        print("No se encontraron películas.")

def insertar_pelicula(movies, fieldnames):
    nueva = {}
    for campo in fieldnames:
        if campo == 'rating':
            valor = input(f"Ingrese {campo} (0-100): ")
            if valor not in RATINGS:
                print("Error: rating inválido. Debe ser un número entre 0 y 100.")
                return
        elif campo == 'platform':
            valor = input(f"Ingrese {campo} ({', '.join(PLATFORMS)}): ")
            if valor not in PLATFORMS:
                print("Error: plataforma inválida.")
                return
        elif campo == 'category':
            valor = input(f"Ingrese {campo} ({', '.join(CATEGORIES)}): ")
            if valor not in CATEGORIES:
                print("Error: categoría inválida.")
                return
        else:
            valor = input(f"Ingrese {campo}: ")
            if not valor:
                print(f"Error: {campo} no puede estar vacío.")
                return
        nueva[campo] = valor
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
