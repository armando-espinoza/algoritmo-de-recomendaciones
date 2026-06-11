from string import punctuation
from libro import crear_lista_libros_ingles
from recomendador import Recomendador

DIRECTORIO_LIBROS = "Libros"   


def pedir_entero(mensaje: str, minimo: int, maximo: int) -> int:
    """Pide un entero al usuario dentro de [minimo, maximo]."""
    while True:
        try:
            valor = int(input(mensaje))
            if minimo <= valor <= maximo:
                return valor
            print(f"   Ingresa un número entre {minimo} y {maximo}.")
        except ValueError:
            print("   Eso no es un número válido, intenta de nuevo.")


def menu_principal() -> str:
    print("\n¿Qué deseas hacer?")
    print("  [1] Ver un resumen de palabras clave de un libro")
    print("  [2] Obtener recomendaciones a partir de un libro que te gustó")
    print("  [0] Salir")
    while True:
        opcion = input("\nElige una opción: ").strip()
        if opcion in ("0", "1", "2"):
            return opcion
        print("   Opción no válida, elige 0, 1 o 2.")


def flujo_resumen(rec: Recomendador):
    rec.mostrar_libros()
    idx = pedir_entero(
        "Índice del libro que deseas resumir: ",
        0, len(rec.libros) - 1
    )
    num = pedir_entero("¿Cuántas palabras clave quieres ver? (1-50): ", 1, 50)

    palabras = rec.resumen(idx, num)
    nombre = rec.libros[idx].name

    print(f"\n Resumen de «{nombre}»")
    print("=" * 45)
    print(f"  Las {num} palabras más representativas son:\n")
    for pos, palabra in enumerate(palabras, start=1):
        print(f"    {pos:>2}. {palabra}")
    print("=" * 45)


def flujo_recomendaciones(rec: Recomendador):
    rec.mostrar_libros()
    idx = pedir_entero(
        "Índice del libro que te gustó: ",
        0, len(rec.libros) - 1
    )
    max_rec = len(rec.libros) - 1
    num = pedir_entero(
        f"¿Cuántos libros quieres que te recomendemos? (1-{max_rec}): ",
        1, max_rec
    )

    similares = rec.libros_similares(idx, num)
    nombre_base = rec.libros[idx].name

    print(f"\n Porque te gustó «{nombre_base}», te recomendamos:")
    print("=" * 45)
    for pos, nombre in enumerate(similares, start=1):
        print(f"    {pos}. {nombre}")
    print("=" * 45)


def main():
    print("=" * 55)
    print("    Bienvenido al Recomendador de Libros ")
    print("=" * 55)
    print(
        "\nEste programa analiza una colección de libros y te permite:\n"
        "  • Ver las palabras más importantes de cualquier libro.\n"
        "  • Recibir recomendaciones basadas en un libro que ya leíste.\n"
        "\nUsamos el algoritmo TF-IDF para medir la relevancia de cada\n"
        "palabra y la similitud coseno para comparar los libros entre sí."
    )

    print("\n Cargando y procesando los libros, un momento...")
    libros = crear_lista_libros_ingles(DIRECTORIO_LIBROS, punctuation)

    if not libros:
        print(f"\n No se encontraron libros en '{DIRECTORIO_LIBROS}'. "
              "Verifica el directorio e intenta de nuevo.")
        return

    rec = Recomendador(libros)
    rec.set_pesos()
    print(f" {len(libros)} libro(s) cargado(s) correctamente.\n")

    while True:
        opcion = menu_principal()
        if opcion == "0":
            print("\n ¡Hasta luego!\n")
            break
        elif opcion == "1":
            flujo_resumen(rec)
        elif opcion == "2":
            flujo_recomendaciones(rec)


if __name__ == "__main__":
    main()
