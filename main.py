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
    """Carga los libros del directorio y calcula los pesos TF-IDF."""
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
    load_books()



@app.get("/api/libros", summary="Lista todos los libros disponibles")
def get_libros():
    if not rec:
        raise HTTPException(status_code=503, detail="No hay libros cargados")
    return [{"index": i, "name": l.name} for i, l in enumerate(rec.libros)]


class ResumenRequest(BaseModel):
    idx: int
    num_palabras: int = 15


@app.post("/api/resumen", summary="Top palabras TF-IDF de un libro")
def get_resumen(req: ResumenRequest):
    if not rec:
        raise HTTPException(status_code=503, detail="No hay libros cargados")
    if not (0 <= req.idx < len(rec.libros)):
        raise HTTPException(status_code=400, detail="Índice fuera de rango")
    palabras = rec.resumen(req.idx, req.num_palabras)
    return {"libro": rec.libros[req.idx].name, "palabras": palabras}


class RecomendacionRequest(BaseModel):
    idx: int
    num_libros: int = 5

@app.post("/api/recomendaciones", summary="Libros similares a uno dado")
def get_recomendaciones(req: RecomendacionRequest):
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
    return {"idiomas": list(IDIOMA_CLASE.keys()), "activo": BOOKS_LANG}



app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")
