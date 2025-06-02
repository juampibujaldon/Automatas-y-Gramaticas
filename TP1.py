import re as re
from collections import Counter
import csv

# EJERCICIO N° 1 

def validate_string(string):
    alphanumeric = bool(re.search(r'\w', string))
    letter = bool(re.search(r'[a-zA-Z]', string))
    uppercase = bool(re.search(r'[A-Z]', string))
    lowercase = bool(re.search(r'[a-z]', string))
    digit = bool(re.search(r'\d', string))
    length = len(string) >= 8
    
    return alphanumeric, letter, uppercase, lowercase, digit, length

input_string = input("Ingrese una cadena de texto: ")
output = validate_string(input_string)
print("Dado el string:", input_string, "el output esperado es:", output)

# EJERCICIO N° 2
def solve(expression: str) -> int:
    terms = expression.split('+')
    total = 0
    for term in terms:
        factors = term.strip().split('*')
        product = 1
        for factor in factors:
            product *= int(factor.strip())
        total += product
    return total

# EJERCICIO N° 3

# a) Analizador de Emails
EMAIL_DOMAINS = ['gmail', 'yahoo', 'hotmail', 'outlook', 'protonmail']
EMAIL_COUNTRIES = ['com', 'ar', 'es', 'net', 'org']

def analizar_emails(archivo):
    patron = re.compile(
        r'^[a-zA-Z][\w\.-]*@(?:' + '|'.join(EMAIL_DOMAINS) + r')\.(?:' + '|'.join(EMAIL_COUNTRIES) + r')$'
    )
    with open(archivo, 'r') as f:
        for linea in f:
            email = linea.strip()
            print(f"{email}: {'Válido' if patron.match(email) else 'Inválido'}")


# b) Analizador de URLs
def analizar_urls(archivo):
    patron = re.compile(
        r'^(https?:\/\/)?(www\.)?[\w\-]+(\.[a-z]{2,})(\/)?(\?.+)?$'
    )
    with open(archivo, 'r') as f:
        for linea in f:
            url = linea.strip()
            print(f"{url}: {'Válida' if patron.match(url) else 'Inválida'}")


# c) Analizador de IPs IPv4
def es_ip_valida(ip):
    partes = ip.strip().split('.')
    if len(partes) != 4:
        return False
    for parte in partes:
        if not parte.isdigit():
            return False
        num = int(parte)
        if num < 0 or num > 255:
            return False
    return True

def analizar_ips(archivo):
    with open(archivo, 'r') as f:
        for linea in f:
            ip = linea.strip()
            print(f"{ip}: {'Válida' if es_ip_valida(ip) else 'Inválida'}")


# d) Contar palabras y encontrar la más repetida
def analizar_texto(archivo):
    with open(archivo, 'r') as f:
        texto = f.read().lower()
        palabras = re.findall(r'\b\w+\b', texto)
        conteo = Counter(palabras)
        mas_comun = conteo.most_common(1)[0]
        print(f"Total de palabras: {len(palabras)}")
        print(f"Palabra más repetida: '{mas_comun[0]}' con {mas_comun[1]} apariciones.")


if __name__ == "__main__":
    print("\n--- Emails ---")
    analizar_emails("emails.txt")
    
    print("\n--- URLs ---")
    analizar_urls("urls.txt")
    
    print("\n--- IPs ---")
    analizar_ips("ips.txt")
    
    print("\n--- Análisis de Texto ---")
    analizar_texto("texto.txt")

