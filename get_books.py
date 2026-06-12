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
    """
    Obtiene las URLs y títulos de los libros más descargados de Project Gutenberg.

    Consulta la página ``https://www.gutenberg.org/browse/scores/top`` y extrae
    los enlaces a los archivos .txt de los libros seleccionados.

    Parameters
    ----------
    n : int or list of int, optional
        Número o lista de números (1-based) de los libros a obtener.
        Usa -1 (por defecto) para obtener todos.

    Returns
    -------
    links : list of str
        URLs directas a los archivos .txt en UTF-8.
    titles : list of str
        Nombres de archivo seguros derivados del título de cada libro.
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
    """
    Descarga un archivo desde una URL y lo guarda en el directorio indicado.

    Parameters
    ----------
    url : str
        URL del archivo a descargar.
    name : str
        Nombre con el que se guardará el archivo.
    directory : str
        Ruta del directorio donde se guardará el archivo.

    Returns
    -------
    bool
        True si la descarga fue exitosa, False en caso contrario.
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
    """
    Descarga y guarda una lista de archivos en el directorio indicado.

    Crea el directorio si no existe y llama a ``download_file`` por cada par
    URL-nombre.

    Parameters
    ----------
    links : list of str
        URLs de los archivos a descargar.
    names : list of str
        Nombres con los que se guardará cada archivo.
    directory : str, optional
        Ruta del directorio destino. Por defecto ``'./'``.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    for url, name in zip(links, names):
        download_file(url, name, directory)


def main(n=-1, directory='./'):
    """
    Punto de entrada principal: obtiene y descarga los libros seleccionados.

    Parameters
    ----------
    n : int or list of int, optional
        Número o lista de números (1-based) de los libros a descargar.
        Usa -1 (por defecto) para descargar todos.
    directory : str, optional
        Directorio donde se guardarán los archivos. Por defecto ``'./'``.
    """
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
