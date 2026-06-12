# Sistema de recomendaciones de libros

Sistema que descarga libros del Proyecto Gutenberg, los preprocesa con TF-IDF y expone una API REST para consultar recomendaciones por similitud entre libros.

## ¿Cómo funciona?

Cada libro se tokeniza y se le calculan pesos TF-IDF. A partir de esos pesos se construye un vector por libro, y la similitud entre dos libros se calcula con similitud coseno. El resultado es una API que, dado un libro, devuelve los más parecidos según su contenido.

## Estructura del proyecto

```
sistema_recomendaciones/
├── get_books.py        # Descarga libros de Project Gutenberg
├── libro.py            # Clases para representar y preprocesar libros
├── recomendador.py     # Lógica TF-IDF y similitud coseno
├── main.py             # API REST con FastAPI
└── static/             # Frontend (index.html)
```

## Instalación

Clona el repositorio e instala las dependencias:

```bash
git clone https://github.com/armando-espinoza/sistema_recomendaciones.git
cd sistema_recomendaciones
pip install -r requirements.txt
```

Las dependencias principales son `fastapi`, `uvicorn`, `nltk`, `beautifulsoup4` y `requests`.

## Uso

### 1. Descargar libros

Antes de correr la API necesitas tener libros en local. El script `get_books.py` los descarga directo de Gutenberg:

```python
# Dentro de get_books.py, ajusta estas variables:
directory = 'Books/'
n = range(1, 51)   # los primeros 50 libros más descargados
```

```bash
python get_books.py
```

Los archivos `.txt` quedarán en la carpeta que hayas configurado.

### 2. Correr la API

```bash
uvicorn main:app --reload
```

Por defecto la API busca libros en el directorio `Libros/` en inglés. Para pruebas puedes usar `BookTest_2/`. Puedes cambiar esto con variables de entorno:

```bash
BOOKS_DIR=BookTest_2 BOOKS_LANG=english uvicorn main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/libros` | Lista todos los libros cargados |
| POST | `/api/resumen` | Top palabras TF-IDF de un libro |
| POST | `/api/recomendaciones` | Libros similares a uno dado |
| GET | `/api/idiomas` | Idiomas soportados y el activo |
| GET | `/` | Frontend |

### Ejemplos

**Obtener recomendaciones:**
```bash
curl -X POST http://localhost:8000/api/recomendaciones \
  -H "Content-Type: application/json" \
  -d '{"idx": 0, "num_libros": 5}'
```

**Ver resumen de un libro:**
```bash
curl -X POST http://localhost:8000/api/resumen \
  -H "Content-Type: application/json" \
  -d '{"idx": 0, "num_palabras": 10}'
```

## Idiomas soportados

Por ahora el sistema soporta inglés, español y francés usando las stopwords de NLTK. El idioma activo se configura con la variable de entorno `BOOKS_LANG`.
