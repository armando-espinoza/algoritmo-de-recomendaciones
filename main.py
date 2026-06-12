import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from libro import LibroEnglish, LibroSpanish, LibroFrench, crear_lista_libros_ingles
from recomendador import Recomendador

BOOKS_DIR = os.getenv("BOOKS_DIR", "Libros")
BOOKS_LANG = os.getenv("BOOKS_LANG", "english")

app = FastAPI(title="Recomendador de Libros")

rec: Recomendador | None = None

IDIOMA_CLASE = {
    "english": LibroEnglish,
    "spanish": LibroSpanish,
    "french": LibroFrench
}


def load_books() -> bool:
    """
    Carga los libros del directorio configurado y calcula sus pesos TF-IDF.

    Lee la variable global ``BOOKS_DIR`` para localizar los archivos y
    ``BOOKS_LANG`` para determinar el idioma. Inicializa el ``Recomendador``
    global ``rec``.

    Returns
    -------
    bool
        True si los libros se cargaron correctamente, False en caso contrario.
    """
    global rec
    
    try:
        if BOOKS_LANG == "english":
            libros = crear_lista_libros_ingles(BOOKS_DIR)
        else:
            print(f"[startup] Idioma '{BOOKS_LANG}' no soportado.")
            return False
    except (ValueError, FileNotFoundError) as exc:
        print(f"[startup] Error al cargar libros: {exc}")
        return False
    if not libros:
        print(f"[startup] No se encontraron archivos .txt en '{BOOKS_DIR}'.")
        return False
    rec = Recomendador(libros)
    rec.set_pesos()
    print(f"[startup] {len(libros)} libro(s) cargados en idioma '{BOOKS_LANG}'.")
    return True


@app.on_event("startup")
async def startup() -> None:
    """Evento de arranque de FastAPI: carga los libros al iniciar el servidor."""
    load_books()


@app.get("/api/libros", summary="Lista todos los libros disponibles")
def get_libros():
    """
    Devuelve la lista de libros cargados con su índice y nombre.

    Returns
    -------
    list of dict
        Lista de objetos ``{"index": int, "name": str}``.

    Raises
    ------
    HTTPException
        503 si no hay libros cargados.
    """
    if not rec:
        raise HTTPException(status_code=503, detail="No hay libros cargados")
    return [{"index": i, "name": l.name} for i, l in enumerate(rec.libros)]


class ResumenRequest(BaseModel):
    """
    Cuerpo de la petición para el endpoint de resumen.

    Attributes
    ----------
    idx : int
        Índice del libro en la lista cargada.
    num_palabras : int, optional
        Cantidad de palabras a devolver. Por defecto 15.
    """
    idx: int
    num_palabras: int = 15


@app.post("/api/resumen", summary="Top palabras TF-IDF de un libro")
def get_resumen(req: ResumenRequest):
    """
    Devuelve las palabras con mayor peso TF-IDF de un libro.

    Parameters
    ----------
    req : ResumenRequest
        Índice del libro y número de palabras deseadas.

    Returns
    -------
    dict
        ``{"libro": str, "palabras": list of str}``

    Raises
    ------
    HTTPException
        503 si no hay libros cargados.
        400 si el índice está fuera de rango.
    """
    if not rec:
        raise HTTPException(status_code=503, detail="No hay libros cargados")
    if not (0 <= req.idx < len(rec.libros)):
        raise HTTPException(status_code=400, detail="Índice fuera de rango")
    palabras = rec.resumen(req.idx, req.num_palabras)
    return {"libro": rec.libros[req.idx].name, "palabras": palabras}


class RecomendacionRequest(BaseModel):
    """
    Cuerpo de la petición para el endpoint de recomendaciones.

    Attributes
    ----------
    idx : int
        Índice del libro de referencia.
    num_libros : int, optional
        Cantidad de libros similares a devolver. Por defecto 5.
    """
    idx: int
    num_libros: int = 5


@app.post("/api/recomendaciones", summary="Libros similares a uno dado")
def get_recomendaciones(req: RecomendacionRequest):
    """
    Devuelve los libros más similares al libro indicado.

    Parameters
    ----------
    req : RecomendacionRequest
        Índice del libro de referencia y número de recomendaciones deseadas.

    Returns
    -------
    dict
        ``{"libro": str, "recomendaciones": list of {"index": int, "name": str}}``

    Raises
    ------
    HTTPException
        503 si no hay libros cargados.
        400 si el índice está fuera de rango.
    """
    if not rec:
        raise HTTPException(status_code=503, detail="No hay libros cargados")
    if not (0 <= req.idx < len(rec.libros)):
        raise HTTPException(status_code=400, detail="Índice fuera de rango")
    nombres = rec.libros_similares(req.idx, req.num_libros)   # list[str]
    resultado = []
    for nombre in nombres:
        for i, libro in enumerate(rec.libros):
            if libro.name == nombre:
                resultado.append({"index": i, "name": libro.name})
                break
    return {"libro": rec.libros[req.idx].name, "recomendaciones": resultado}


@app.get("/api/idiomas", summary="Idiomas soportados para el análisis")
def get_idiomas():
    """
    Devuelve los idiomas soportados y el idioma activo.

    Returns
    -------
    dict
        ``{"idiomas": list of str, "activo": str}``
    """
    return {"idiomas": list(IDIOMA_CLASE.keys()), "activo": BOOKS_LANG}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    """Sirve la página principal de la aplicación."""
    return FileResponse("static/index.html")
