"""
main.py
Interfaz de terminal de MUSICTCN (v4).

v2 incorporó un árbol binario de búsqueda (búsqueda exacta, autocompletado
y listado ordenado por título).

v3 agrega un árbol general (n-ario) con la jerarquía natural del dominio:
Música > familia > género > artista. Se usa desde tres opciones del menú:
"Explorar categorías" (navegar por la jerarquía), "Ver jerarquía completa"
(con los recorridos) y "Buscar categoría".

v4 agrega un ranking dinámico de recomendaciones con una cola de prioridad
(heap binario): "Ranking de recomendaciones" muestra el Top-N según un
criterio ajustable (popularidad, novedad y género preferido), y "Agregar
canción" la inserta en el heap, así el ranking se actualiza sin reordenar
todo el catálogo. Las canciones agregadas viven solo en memoria.

Las opciones 14 y 15 (conexiones entre artistas, caminos de colaboración
y recomendaciones personalizadas por perfil de usuario) quedan marcadas
como pendientes: requieren un grafo de colaboraciones y una clase Usuario
que todavía no forman parte del dominio.
"""

from gestor_musica import CatalogoMusical
from modelos import Cancion
from prioridad import CriterioPrioridad

RUTA_DATOS = "datos/canciones.json"
RUTA_CATEGORIAS = "datos/categorias.json"


def mostrar_menu():
    print("\n" + "=" * 40)
    print(" MUSICTCN")
    print("=" * 40)
    print("1. Buscar canción o artista (texto parcial)")
    print("2. Buscar canción por título exacto (árbol)")
    print("3. Autocompletar título (árbol)")
    print("4. Explorar géneros (k-pop, rap, rock, pop, ...)")
    print("5. Ver top 10 de canciones populares")
    print("6. Listar todo el catálogo")
    print("7. Listar ordenado alfabéticamente (árbol - inorder)")
    print("8. Filtrar canciones")
    print("9. Explorar categorías (árbol general)")
    print("10. Ver jerarquía completa de categorías (recorridos)")
    print("11. Buscar categoría por nombre")
    print("12. Ranking de recomendaciones (heap)")
    print("13. Agregar canción (el ranking se actualiza)")
    print("14. Explorar conexiones entre artistas (próximamente)")
    print("15. Recomendaciones personalizadas por perfil (próximamente)")
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


def opcion_buscar_titulo_exacto(catalogo: CatalogoMusical):
    titulo = input("Título exacto: ")
    resultado = catalogo.buscar_titulo_exacto(titulo)
    if resultado is None:
        print("No se encontró ninguna canción con ese título exacto.")
    else:
        print(resultado)
        ruta_cat = catalogo.ruta_categoria_de(resultado)
        if ruta_cat:
            print(f"   Categoría: {ruta_cat}")


def opcion_autocompletar(catalogo: CatalogoMusical):
    prefijo = input("Empezá a escribir el título: ")
    sugerencias = catalogo.autocompletar(prefijo, max_resultados=10)
    if not sugerencias:
        print("Sin sugerencias.")
    else:
        print(f"Sugerencias ({len(sugerencias)}):")
        imprimir_canciones(sugerencias)


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


def opcion_listar_ordenado_arbol(catalogo: CatalogoMusical):
    imprimir_canciones(catalogo.listar_ordenado_por_titulo())


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


def _nombre_con_conteo(catalogo: CatalogoMusical, nodo):
    return f"{nodo.nombre} ({len(catalogo.canciones_de_categoria(nodo))})"


def opcion_explorar_categorias(catalogo: CatalogoMusical):
    """Navegación interactiva por el árbol general: se baja eligiendo una
    subcategoría y se sube con 0."""
    arbol = catalogo.categorias
    if arbol is None:
        print("No hay categorías cargadas.")
        return

    nodo = arbol.raiz
    while True:
        print("\n" + " > ".join(arbol.ruta(nodo)))
        hijos = nodo.hijos
        canciones = catalogo.canciones_de_categoria(nodo)

        if hijos:
            print("Subcategorías:")
            for i, h in enumerate(hijos, start=1):
                print(f"  {i}. {_nombre_con_conteo(catalogo, h)}")
        else:
            print("(no tiene subcategorías)")

        if nodo is not arbol.raiz:
            print(f"Canciones en '{nodo.nombre}' ({len(canciones)}):")
            imprimir_canciones(canciones)

        volver = "0 para salir" if nodo is arbol.raiz else "0 para subir un nivel"
        eleccion = input(f"Elegí una subcategoría ({volver}): ").strip()

        if eleccion == "0":
            if nodo.padre is None:
                break
            nodo = nodo.padre
        elif eleccion.isdigit() and 1 <= int(eleccion) <= len(hijos):
            nodo = hijos[int(eleccion) - 1]
        else:
            print("Opción inválida.")


def opcion_jerarquia_completa(catalogo: CatalogoMusical):
    arbol = catalogo.categorias
    if arbol is None:
        print("No hay categorías cargadas.")
        return

    print("Recorrido: 1) árbol dibujado  2) preorden  3) postorden  4) por niveles")
    op = input("Elegí una opción: ").strip()

    if op == "1":
        print(catalogo.dibujar_categorias())
    elif op == "2":
        print("Preorden (padre antes que hijos):")
        print("  " + " -> ".join(n.nombre for n in arbol.preorden()))
    elif op == "3":
        print("Postorden (hijos antes que padre):")
        print("  " + " -> ".join(n.nombre for n in arbol.postorden()))
    elif op == "4":
        print("Por niveles:")
        for i, nivel in enumerate(arbol.por_niveles()):
            print(f"  Nivel {i}: " + ", ".join(n.nombre for n in nivel))
    else:
        print("Opción inválida.")
        return
    print(f"\nNodos: {arbol.cantidad()} | Niveles: {arbol.altura()} | Hojas: {len(arbol.hojas())}")


def opcion_buscar_categoria(catalogo: CatalogoMusical):
    texto = input("Nombre de la categoría (género, familia o artista): ")
    encontrados = catalogo.buscar_categoria(texto)
    if not encontrados:
        print("No se encontró ninguna categoría con ese nombre.")
        return
    for nodo in encontrados:
        canciones = catalogo.canciones_de_categoria(nodo)
        print(f"\n{' > '.join(catalogo.categorias.ruta(nodo))}  ({len(canciones)} canciones)")
        imprimir_canciones(canciones)


def _pedir_entero(mensaje: str, minimo: int, maximo: int):
    """Pide un entero en [minimo, maximo]; devuelve None si no es válido."""
    texto = input(mensaje).strip()
    try:
        valor = int(texto)
    except ValueError:
        return None
    return valor if minimo <= valor <= maximo else None


def opcion_ranking(catalogo: CatalogoMusical):
    print("Criterio del ranking:")
    print("  1) Popularidad")
    print("  2) Equilibrado (70% popularidad, 30% novedad)")
    print("  3) Novedades (30% popularidad, 70% novedad)")
    eleccion = input("Elegí un criterio (Enter = 1): ").strip() or "1"
    if eleccion not in ("1", "2", "3"):
        print("Opción inválida.")
        return

    genero = input("Género preferido, recibe +10 puntos (Enter para omitir): ").strip().lower() or None
    if genero and genero not in [g.lower() for g in catalogo.generos_disponibles()]:
        print(f"No hay canciones de '{genero}'; se ignora el género preferido.")
        genero = None

    n_texto = input("¿Cuántas canciones querés ver? (Enter = 5): ").strip()
    n = int(n_texto) if n_texto.isdigit() and int(n_texto) > 0 else 5

    criterio = {"1": CriterioPrioridad.popularidad,
                "2": CriterioPrioridad.equilibrado,
                "3": CriterioPrioridad.novedades}[eleccion](genero)

    resultados = catalogo.ranking(n, criterio)
    if not resultados:
        print("No hay canciones para rankear.")
        return
    print(f"\nTOP {len(resultados)}  ({criterio.descripcion()})")
    for puesto, (cancion, puntaje) in enumerate(resultados, start=1):
        detalle = f"{cancion.titulo} - {cancion.artista}"
        print(f"{puesto:>2}. {detalle:<42} {puntaje:6.1f}")


def opcion_agregar_cancion(catalogo: CatalogoMusical):
    titulo = input("Título: ").strip()
    artista = input("Artista: ").strip()
    genero = input("Género (ej: pop, rock, rap, k-pop, folk): ").strip().lower()
    if not titulo or not artista or not genero:
        print("Título, artista y género son obligatorios.")
        return
    anio = _pedir_entero("Año (1900-2100): ", 1900, 2100)
    popularidad = _pedir_entero("Popularidad (0-100): ", 0, 100)
    if anio is None or popularidad is None:
        print("Año o popularidad inválidos; no se agregó la canción.")
        return

    cancion = Cancion(catalogo.siguiente_id(), titulo, artista, genero, anio, popularidad)
    try:
        catalogo.agregar_cancion(cancion)
    except ValueError as error:
        print(f"No se pudo agregar: {error}")
        return
    print(f"Canción agregada con id {cancion.id}. El ranking ya la tiene en cuenta.")


def iniciar_programa():
    catalogo = CatalogoMusical()
    try:
        catalogo.cargar_desde_json(RUTA_DATOS)
    except FileNotFoundError:
        print(f"No se encontró el archivo de datos en '{RUTA_DATOS}'.")
        return
    try:
        catalogo.cargar_categorias_desde_json(RUTA_CATEGORIAS)
    except FileNotFoundError:
        print(f"Aviso: no se encontró '{RUTA_CATEGORIAS}'; las opciones de categorías no estarán disponibles.")

    acciones = {
        "1": opcion_buscar,
        "2": opcion_buscar_titulo_exacto,
        "3": opcion_autocompletar,
        "4": opcion_generos,
        "5": opcion_top10,
        "6": opcion_listar,
        "7": opcion_listar_ordenado_arbol,
        "8": opcion_filtrar,
        "9": opcion_explorar_categorias,
        "10": opcion_jerarquia_completa,
        "11": opcion_buscar_categoria,
        "12": opcion_ranking,
        "13": opcion_agregar_cancion,
    }

    while True:
        mostrar_menu()
        opcion = input("Elegí una opción: ").strip()

        if opcion == "0":
            print("¡Hasta la próxima!")
            break
        elif opcion in acciones:
            acciones[opcion](catalogo)
        elif opcion in ("14", "15"):
            print("Esta función todavía no está disponible en la v4.")
        else:
            print("Opción inválida, intentá de nuevo.")


if __name__ == "__main__":
    iniciar_programa()

