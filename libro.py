import os
from pathlib import Path
from string import punctuation
import nltk
from nltk.corpus import stopwords as nltk_stopwords
nltk.download('stopwords', quiet=True)


class Libro:
    """
    Representa un libro de texto y permite preprocesar su contenido.

    Parameters
    ----------
    name : str
        Nombre del libro.
    filename : str
        Ruta al archivo de texto.

    Attributes
    ----------
    CARACTERES_ESPECIALES : str or None
        Caracteres que se eliminan durante la limpieza. Por defecto None.
    STOPWORDS : list of str or None
        Palabras vacías que se eliminan durante la tokenización. Por defecto None.
    """

    def __init__(self, name, filename) -> None:
        self.name = name
        self.filename = filename
        self.CARACTERES_ESPECIALES: str | None = None
        self.STOPWORDS: list[str] | None = None

    @property
    def name(self):
        """str: Nombre del libro."""
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("El nombre debe ser un string")
        self._name = value

    @property
    def filename(self):
        """str: Ruta al archivo de texto."""
        return self._filename

    @filename.setter
    def filename(self, value):
        if not isinstance(value, str):
            raise TypeError("El nombre del archivo debe ser un string")
        if not os.path.exists(value):
            raise FileNotFoundError("No se ha encontrado el archivo en la ruta indicada")
        self._filename = value

    def _limpiar_linea(self, linea):
        """
        Elimina los caracteres especiales de una línea.

        Parameters
        ----------
        linea : str
            Línea de texto a limpiar.

        Returns
        -------
        str
            Línea sin los caracteres especiales, o la línea original si
            ``CARACTERES_ESPECIALES`` es None.
        """
        if not self.CARACTERES_ESPECIALES:
            return linea
        caracteres_limpios = [char for char in linea if char not in self.CARACTERES_ESPECIALES]
        return "".join(caracteres_limpios)

    def _limpiar_tokens(self, tokens):
        """
        Elimina las stopwords de una lista de tokens.

        Parameters
        ----------
        tokens : list of str
            Lista de tokens a filtrar.

        Returns
        -------
        list of str
            Lista sin las stopwords, o la lista original si ``STOPWORDS`` es None.
        """
        if not self.STOPWORDS:
            return tokens
        for word in tokens.copy():
            if word in self.STOPWORDS:
                tokens.remove(word)
        return tokens

    def _preprocesar_linea(self, linea) -> list[str]:
        """
        Normaliza y tokeniza una línea de texto.

        Aplica strip, lowercase, limpieza de caracteres especiales y
        eliminación de stopwords.

        Parameters
        ----------
        linea : str
            Línea de texto cruda.

        Returns
        -------
        list of str
            Tokens limpios de la línea.
        """
        linea = linea.strip()
        linea = linea.lower()
        linea = self._limpiar_linea(linea)
        tokens = linea.split()
        tokens = self._limpiar_tokens(tokens)
        return tokens

    def leer_libro(self) -> list[str]:
        """
        Lee el archivo y devuelve las líneas no vacías.

        Returns
        -------
        list of str
            Líneas del archivo que contienen texto.
        """
        lineas = []
        with open(self.filename, encoding='utf-8') as f:
            for linea in f:
                if linea.strip():          
                    lineas.append(linea)
        return lineas

    def preprocesar_libro(self) -> dict[str, int]:
        """
        Calcula la frecuencia de cada token en el libro.

        Returns
        -------
        dict of {str: int}
            Diccionario con tokens como claves y su frecuencia como valores.
        """
        frecuencias = {}
        for linea in self.leer_libro():
            tokens = self._preprocesar_linea(linea)
            for token in tokens:
                if token in frecuencias:
                    frecuencias[token] += 1
                else:
                    frecuencias[token] = 1
        return frecuencias

    def __str__(self) -> str:
        return f"Libro: '{self.name}' | Archivo: {self.filename}"

    def __repr__(self) -> str:
        return f"Libro(name={self.name!r}, filename={self.filename!r})"


class LibroGutenberg(Libro):
    """
    Libro proveniente del Proyecto Gutenberg.

    Extiende ``Libro`` para ignorar el encabezado y pie de página que
    Project Gutenberg añade a sus archivos, leyendo solo el contenido
    entre las marcas ``*** START`` y ``*** END``.
    """

    def leer_libro(self) -> list[str]:
        """
        Lee solo el contenido del libro, omitiendo el encabezado y pie de Gutenberg.

        Returns
        -------
        list of str
            Líneas no vacías entre las marcas de inicio y fin del texto.
        """
        lineas = []
        dentro = False
        with open(self.filename, encoding='utf-8') as f:
            for linea in f:
                if linea.startswith('*** START'):
                    dentro = True
                    continue              
                if linea.startswith('*** END'):
                    break                
                if dentro and linea.strip():
                    lineas.append(linea)
        return lineas


class LibroEnglish(LibroGutenberg):
    """
    Libro de Gutenberg en inglés.

    Carga automáticamente las stopwords en inglés de NLTK.

    Parameters
    ----------
    name : str
        Nombre del libro.
    filename : str
        Ruta al archivo de texto.
    """

    def __init__(self, name, filename) -> None:
        super().__init__(name, filename)
        self.STOPWORDS = set(nltk_stopwords.words('english'))


class LibroSpanish(LibroGutenberg):
    """
    Libro de Gutenberg en español.

    Carga automáticamente las stopwords en español de NLTK.

    Parameters
    ----------
    name : str
        Nombre del libro.
    filename : str
        Ruta al archivo de texto.
    """

    def __init__(self, name, filename) -> None:
        super().__init__(name, filename)
        self.STOPWORDS = set(nltk_stopwords.words('spanish'))


class LibroFrench(LibroGutenberg):
    """
    Libro de Gutenberg en francés.

    Carga automáticamente las stopwords en francés de NLTK.

    Parameters
    ----------
    name : str
        Nombre del libro.
    filename : str
        Ruta al archivo de texto.
    """

    def __init__(self, name, filename) -> None:
        super().__init__(name, filename)
        self.STOPWORDS = set(nltk_stopwords.words('french'))


def crear_lista_libros_ingles(directory: str, caract_especiales=punctuation):
    """
    Crea una lista de ``LibroEnglish`` a partir de los archivos .txt de un directorio.

    Parameters
    ----------
    directory : str
        Ruta al directorio que contiene los archivos .txt.
    caract_especiales : str, optional
        Caracteres a eliminar durante el preprocesamiento.
        Por defecto usa ``string.punctuation``.

    Returns
    -------
    list of LibroEnglish
        Un objeto ``LibroEnglish`` por cada archivo .txt encontrado.
    """
    libros = []
    path = Path(directory)
    for file in path.glob('*.txt'):
        filename = str(file.relative_to(path.parent))
        libro = LibroEnglish(file.name, filename)
        libro.CARACTERES_ESPECIALES = caract_especiales
        libros.append(libro)
    return libros
