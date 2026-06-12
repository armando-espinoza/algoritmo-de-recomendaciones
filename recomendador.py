import math


class Recomendador:
    """
    Recomienda libros similares usando pesos TF-IDF y similitud coseno.

    Parameters
    ----------
    libros : list of Libro
        Lista de libros a comparar. Cada libro debe implementar
        ``preprocesar_libro()``.

    Attributes
    ----------
    _pesos : list of dict or None
        Pesos TF-IDF de cada libro. Se inicializa con ``set_pesos()``.
    """

    def __init__(self, libros) -> None:
        self.libros = libros
        self._pesos = None

    def set_pesos(self) -> None:
        """
        Calcula los pesos TF-IDF de cada libro y los guarda en ``_pesos``.

        ``_pesos`` queda como una lista de diccionarios, donde cada
        diccionario corresponde a un libro y contiene
        ``{palabra: peso_tfidf}``.
        """
        N = len(self.libros)
        frecuencias = [libro.preprocesar_libro() for libro in self.libros]
        df = {}
        for freq in frecuencias:
            for palabra in freq:
                df[palabra] = df.get(palabra, 0) + 1
        #   Calcular TF-IDF para cada libro
        self._pesos = []
        for freq in frecuencias:
            total_palabras = sum(freq.values())
            pesos_libro = {}
            for palabra, conteo in freq.items():
                tf = conteo / total_palabras
                idf = math.log(N / df[palabra])
                pesos_libro[palabra] = tf * idf
            self._pesos.append(pesos_libro)

    def get_pesos(self):
        """
        Devuelve los pesos TF-IDF calculados.

        Returns
        -------
        list of dict or None
            Lista de diccionarios ``{palabra: peso_tfidf}`` por libro,
            o None si ``set_pesos()`` no ha sido llamado.
        """
        return self._pesos

    def _producto_punto(self, idx_1: int, idx_2: int) -> float:
        """
        Calcula el producto punto entre los vectores TF-IDF de dos libros.

        Parameters
        ----------
        idx_1 : int
            Índice del primer libro en ``self.libros``.
        idx_2 : int
            Índice del segundo libro en ``self.libros``.

        Returns
        -------
        float
            Producto punto de los dos vectores.
        """
        pesos_1 = self._pesos[idx_1]
        pesos_2 = self._pesos[idx_2]
        # Iterar solo sobre el vocabulario del libro más pequeño
        if len(pesos_1) > len(pesos_2):
            pesos_1, pesos_2 = pesos_2, pesos_1
        return sum(
            peso * pesos_2.get(palabra, 0.0)
            for palabra, peso in pesos_1.items()
        )

    def _similitud(self, idx_1, idx_2) -> float:
        """
        Calcula la similitud coseno entre dos libros.

        Parameters
        ----------
        idx_1 : int
            Índice del primer libro en ``self.libros``.
        idx_2 : int
            Índice del segundo libro en ``self.libros``.

        Returns
        -------
        float
            Similitud coseno entre 0 y 1. Devuelve 0 si alguna norma es cero.
        """
        dot = self._producto_punto(idx_1, idx_2)
        norma_1 = math.sqrt(self._producto_punto(idx_1, idx_1))
        norma_2 = math.sqrt(self._producto_punto(idx_2, idx_2))
        if norma_1 == 0 or norma_2 == 0:
            return 0.0
        return dot / (norma_1 * norma_2)

    def mostrar_libros(self):
        """
        Imprime el índice y nombre de cada libro disponible.
        """
        print("\n Libros disponibles:")
        print("-" * 40)
        for i, libro in enumerate(self.libros):
            print(f"  [{i}] {libro.name}")
        print("-" * 40)

    def resumen(self, idx_libro, num_palabras) -> list[str]:
        """
        Devuelve las palabras más representativas de un libro según TF-IDF.

        Parameters
        ----------
        idx_libro : int
            Índice del libro en ``self.libros``.
        num_palabras : int
            Cantidad de palabras a devolver.

        Returns
        -------
        list of str
            Las ``num_palabras`` palabras con mayor peso TF-IDF.
        """
        pesos_libro = self._pesos[idx_libro]
        palabras_ordenadas = sorted(pesos_libro, key=pesos_libro.get, reverse=True)
        return palabras_ordenadas[:num_palabras]

    def libros_similares(self, idx_libro, num_libros) -> list[str]:
        """
        Devuelve los libros más similares a uno dado.

        Parameters
        ----------
        idx_libro : int
            Índice del libro de referencia en ``self.libros``.
        num_libros : int
            Cantidad de libros similares a devolver.

        Returns
        -------
        list of str
            Nombres de los ``num_libros`` libros más similares, ordenados
            de mayor a menor similitud.
        """
        similitudes = []
        for i in range(len(self.libros)):
            if i != idx_libro:
                sim = self._similitud(idx_libro, i)
                similitudes.append((sim, i))
        similitudes.sort(reverse=True)
        return [self.libros[i].name for _, i in similitudes[:num_libros]]
