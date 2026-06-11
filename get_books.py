import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def get_links(n: int | list[int] = -1) -> tuple[list[str], list[str]]:
    """Obtiene los urls y los nombres de los libros del proyecto de Gutenberg
    deseados.
    Los libros se encuentran en formato txt bajo la sección descargados
    frecuentemente en:
        https://www.gutenberg.org/browse/scores/top.
    Los números `n` deben corresponder a los números en esta lista (empezando
    con uno).

    Parameters
    ----------
    n : int | list[int], optional
        Un entero o lista de enteros con los números de libros deseados.
        Escoge -1 (default) si se desean todos los libros.

    Returns
    -------
    links : list[str]
        Ligas a los archivos txt de los libros.
    titles : list[str]
        Títulos de los libros (usados como nombre de archivo .txt).
    """
    url = "https://www.gutenberg.org/browse/scores/top"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        parser = BeautifulSoup(response.text, 'html.parser')

        # La sección "Top 100 EBooks yesterday" es el primer <ol> de la página.
        # Cada <li> contiene un <a href="/ebooks/{id}"> con el título del libro.
        first_ol = parser.find('ol')
        if not first_ol:
            print("No se encontró la lista de libros en la página.")
            return [], []

        all_links = first_ol.find_all('a', href=True)

        # Filtrar solo los que apuntan a /ebooks/{número}
        book_entries = [
            a for a in all_links
            if re.match(r'^/ebooks/\d+$', a['href'])
        ]

        # Seleccionar los índices pedidos (n es 1-based)
        if n == -1:
            selected = book_entries
        else:
            indices = [n] if isinstance(n, int) else list(n)
            selected = [
                book_entries[i - 1]
                for i in indices
                if 1 <= i <= len(book_entries)
            ]

        links  = []
        titles = []
        for a in selected:
            ebook_id = a['href'].split('/')[-1]

            # URL directa al .txt en UTF-8
            txt_url = f"https://www.gutenberg.org/ebooks/{ebook_id}.txt.utf-8"

            # Título limpio → nombre de archivo seguro
            raw_title  = a.get_text(strip=True)
            clean_title = re.sub(r'\s*\(\d+\)\s*$', '', raw_title)   # quita "(1234)"
            safe_title  = re.sub(r'[\\/*?:"<>|]', '_', clean_title) + '.txt'

            links.append(txt_url)
            titles.append(safe_title)

        return links, titles

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Gutenberg: {e}")
        return [], []


def download_file(url: str, name: str, directory: str) -> bool:
    """Guarda un archivo que se encuentra en un `url` bajo el nombre que demos
    en `name` en el directorio deseado.

    Returns True si la descarga fue exitosa, False en caso contrario.
    """
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        response.raise_for_status()

        filepath = Path(directory) / name
        with open(filepath, mode='wb') as file:
            for chunk in response.iter_content(chunk_size=10 * 1024):
                file.write(chunk)

        print(f"  ✓ Descargado: {filepath}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error descargando {name}: {e}")
        return False


def store_files(links: list[str], names: list[str], directory: str = './') -> None:
    """Guarda cada liga de la lista de ligas `links` en la computadora
    utilizando el directorio deseado y cada uno de los nombres en names.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    for url, name in zip(links, names):
        download_file(url, name, directory)


def main(n=-1, directory='./'):
    print(" Obteniendo lista de libros de Project Gutenberg…")
    links, titles = get_links(n)

    if not links:
        print("No se encontraron libros. Verifica tu conexión o los índices pedidos.")
        return

    print(f" Descargando {len(links)} libro(s) en '{directory}'…\n")
    store_files(links, titles, directory)
    print("\n Hecho")


if __name__ == '__main__':
    directory = 'Books/'
    n = range(1, 51)   
    main(n, directory)
