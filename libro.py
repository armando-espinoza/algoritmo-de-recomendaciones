import os
from pathlib import Path
from string import punctuation
import nltk
from nltk.corpus import stopwords as nltk_stopwords

nltk.download('stopwords', quiet=True)


class Libro:
    def __init__(self, name, filename) -> None:
        self.name = name
        self.filename = filename
        self.CARACTERES_ESPECIALES: str | None = None
        self.STOPWORDS: list[str] | None = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("El nombre debe ser un string")
        self._name = value

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        if not isinstance(value, str):
            raise TypeError("El nombre del archivo debe ser un string")
        if not os.path.exists(value):
            raise FileNotFoundError("No se ha encontrado el archivo en la ruta indicada")
        self._filename = value

    def _limpiar_linea(self, linea):
        if not self.CARACTERES_ESPECIALES:
            return linea
        caracteres_limpios = [char for char in linea if char not in self.CARACTERES_ESPECIALES]
        return "".join(caracteres_limpios)

    def _limpiar_tokens(self, tokens):
        if not self.STOPWORDS:
            return tokens
        for word in tokens.copy():
            if word in self.STOPWORDS:
                tokens.remove(word)
        return tokens

    def _preprocesar_linea(self, linea) -> list[str]:
        linea = linea.strip()
        linea = linea.lower()
        linea = self._limpiar_linea(linea)
        tokens = linea.split()
        tokens = self._limpiar_tokens(tokens)
        return tokens

    def leer_libro(self) -> list[str]:
        lineas = []
        with open(self.filename, encoding='utf-8') as f:
            for linea in f:
                if linea.strip():          
                    lineas.append(linea)
        return lineas

    def preprocesar_libro(self) -> dict[str, int]:
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
    def leer_libro(self) -> list[str]:
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
    def __init__(self, name, filename) -> None:
        super().__init__(name, filename)
        self.STOPWORDS = set(nltk_stopwords.words('english'))


class LibroSpanish(LibroGutenberg):
    def __init__(self, name, filename) -> None:
        super().__init__(name, filename)
        self.STOPWORDS = set(nltk_stopwords.words('spanish'))


class LibroFrench(LibroGutenberg):
    def __init__(self, name, filename) -> None:
        super().__init__(name, filename)
        self.STOPWORDS = set(nltk_stopwords.words('french'))


def crear_lista_libros_ingles(directory: str, caract_especiales=punctuation):
    libros = []
    path = Path(directory)
    for file in path.glob('*.txt'):
        filename = str(file.relative_to(path.parent))
        libro = LibroEnglish(file.name, filename)
        libro.CARACTERES_ESPECIALES = caract_especiales
        libros.append(libro)
    return libros
