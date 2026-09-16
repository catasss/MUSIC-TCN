"""
main.py
Interfaz de terminal de MUSICTCN (v1).

v1 implementa las operaciones mínimas requeridas: Buscar, Listar y Filtrar,
además de "Explorar géneros" y "Top 10" que reutilizan el mismo gestor.
Las opciones 5, 6 y 7 (conexiones entre artistas, caminos de colaboración
y recomendaciones personalizadas) quedan marcadas como pendientes para
una próxima versión, ya que requieren un modelo de grafo de colaboraciones
que todavía no forma parte del dominio de esta v1.
"""

from gestor_musica import CatalogoMusical

RUTA_DATOS = "datos/canciones.json"


def mostrar_menu():
    print("\n" + "=" * 40)
    print(" MUSICTCN")
    print("=" * 40)
    print("1. Buscar canción o artista")
    print("2. Explorar géneros (k-pop, rap, rock, pop, ...)")
    print("3. Ver top 10 de canciones populares")
    print("4. Listar todo el catálogo")
    print("5. Filtrar canciones")
    print("6. Explorar conexiones entre artistas (próximamente)")
    print("7. Obtener recomendaciones personalizadas (próximamente)")
    print("0. Salir")
    print("-" * 40)


def imprimir_canciones(canciones):
    if not canciones:
        print("No se encontraron resultados.")
        return
    for c in canciones:
        print(c)


def opcion_buscar(catalogo: CatalogoMusical):
    texto = input("Buscar (título o artista): ")
    resultados = catalogo.buscar(texto)
    imprimir_canciones(resultados)


def opcion_generos(catalogo: CatalogoMusical):
    generos = catalogo.generos_disponibles()
    print("Géneros disponibles:", ", ".join(generos))
    elegido = input("¿Qué género querés explorar? ")
    imprimir_canciones(catalogo.filtrar(genero=elegido))


def opcion_top10(catalogo: CatalogoMusical):
    imprimir_canciones(catalogo.top_n(10))


def opcion_listar(catalogo: CatalogoMusical):
    print("Ordenar por: 1) título 2) artista 3) año 4) popularidad 5) sin orden")
    op = input("Elegí una opción: ")
    campos = {"1": "titulo", "2": "artista", "3": "anio", "4": "popularidad"}
    campo = campos.get(op)
    imprimir_canciones(catalogo.listar(orden_por=campo, descendente=(campo == "popularidad")))


def opcion_filtrar(catalogo: CatalogoMusical):
    genero = input("Género (Enter para omitir): ").strip() or None
    anio_min = input("Año mínimo (Enter para omitir): ").strip()
    anio_max = input("Año máximo (Enter para omitir): ").strip()
    pop_min = input("Popularidad mínima (Enter para omitir): ").strip()

    resultados = catalogo.filtrar(
        genero=genero,
        anio_min=int(anio_min) if anio_min else None,
        anio_max=int(anio_max) if anio_max else None,
        popularidad_min=int(pop_min) if pop_min else None,
    )
    imprimir_canciones(resultados)


def iniciar_programa():
    catalogo = CatalogoMusical()
    try:
        catalogo.cargar_desde_json(RUTA_DATOS)
    except FileNotFoundError:
        print(f"No se encontró el archivo de datos en '{RUTA_DATOS}'.")
        return

    acciones = {
        "1": opcion_buscar,
        "2": opcion_generos,
        "3": opcion_top10,
        "4": opcion_listar,
        "5": opcion_filtrar,
    }

    while True:
        mostrar_menu()
        opcion = input("Elegí una opción: ").strip()

        if opcion == "0":
            print("¡Hasta la próxima!")
            break
        elif opcion in acciones:
            acciones[opcion](catalogo)
        elif opcion in ("6", "7"):
            print("Esta función todavía no está disponible en la v1.")
        else:
            print("Opción inválida, intentá de nuevo.")


if __name__ == "__main__":
    iniciar_programa()
