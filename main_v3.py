"""
main_v3.py
Interfaz de terminal de MUSICTCN (v3).

v3 agrega la opción 9, "Explorar categorías", que usa el árbol general
(arbol_general.py) integrado al catálogo (gestor_musica_v3.py):

    Música
    ├── Pop y derivados
    │   ├── Pop
    │   └── K-pop
    │       └── BTS
    └── ...

Desde ahí se puede ver el árbol completo, navegar entrando y saliendo de
las ramas, buscar categorías, ver los recorridos (preorden, postorden y
por niveles) y averiguar en qué rama del árbol está una canción.

Esta capa solo imprime y lee con input(); nunca arma el árbol por su
cuenta: todo pasa por CatalogoMusical.
"""

import os

from gestor_musica_v3 import CatalogoMusical

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_DATOS = os.path.join(CARPETA, "datos", "canciones.json")
RUTA_CATEGORIAS = os.path.join(CARPETA, "datos", "categorias.json")


# ----------------------------------------------------------------------
# Utilidades de entrada / salida
# ----------------------------------------------------------------------
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
    print("10. Explorar conexiones entre artistas (próximamente)")
    print("11. Obtener recomendaciones personalizadas (próximamente)")
    print("0. Salir")
    print("-" * 40)


def imprimir_canciones(canciones):
    if not canciones:
        print("No se encontraron resultados.")
        return
    for c in canciones:
        print(c)


def leer_entero(mensaje: str):
    """Pide un número entero. Devuelve None si se deja vacío o no es un número."""
    texto = input(mensaje).strip()
    if not texto:
        return None
    try:
        return int(texto)
    except ValueError:
        print(f"'{texto}' no es un número válido; se ignora ese dato.")
        return None


# ----------------------------------------------------------------------
# Opciones 1 a 8 (sin cambios respecto de la v2)
# ----------------------------------------------------------------------
def opcion_buscar(catalogo: CatalogoMusical):
    texto = input("Buscar (título o artista): ")
    imprimir_canciones(catalogo.buscar(texto))


def opcion_buscar_titulo_exacto(catalogo: CatalogoMusical):
    titulo = input("Título exacto: ")
    resultado = catalogo.buscar_titulo_exacto(titulo)
    if resultado is None:
        print("No se encontró ninguna canción con ese título exacto.")
    else:
        print(resultado)


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
    anio_min = leer_entero("Año mínimo (Enter para omitir): ")
    anio_max = leer_entero("Año máximo (Enter para omitir): ")
    pop_min = leer_entero("Popularidad mínima (Enter para omitir): ")
    imprimir_canciones(catalogo.filtrar(genero=genero, anio_min=anio_min,
                                        anio_max=anio_max, popularidad_min=pop_min))


# ----------------------------------------------------------------------
# Opción 9: Explorar categorías (árbol general)
# ----------------------------------------------------------------------
def mostrar_submenu_categorias():
    print("\n--- Explorar categorías ---")
    print("1. Ver el árbol completo (con cantidad de canciones)")
    print("2. Navegar por las categorías (entrar y salir de las ramas)")
    print("3. Buscar una categoría por nombre")
    print("4. Ver un recorrido del árbol (preorden, postorden, por niveles)")
    print("5. Ver en qué rama del árbol está una canción")
    print("0. Volver al menú principal")


def _etiqueta_con_conteo(conteo):
    return lambda nodo: f"{nodo.nombre} ({conteo[nodo]})"


def _pedir_categoria(arbol, mensaje: str):
    """Pide un nombre y devuelve el nodo (o None). Enter = raíz."""
    texto = input(mensaje).strip()
    if not texto:
        return arbol.raiz
    nodo = arbol.buscar(texto)
    if nodo is None:
        print(f"No existe la categoría '{texto}'.")
    return nodo


def ver_arbol_completo(catalogo: CatalogoMusical):
    arbol = catalogo.categorias
    conteo = catalogo.conteo_por_categoria()
    print()
    print(arbol.dibujar(etiqueta=_etiqueta_con_conteo(conteo)))
    print(f"\n{arbol.cantidad()} nodos, {arbol.altura()} niveles, "
          f"{len(arbol.hojas())} hojas.")


def navegar_categorias(catalogo: CatalogoMusical, inicio=None):
    """Recorrido interactivo: se entra a una subcategoría con su número,
    se sube con 'u' y se listan las canciones del nodo actual con 'c'."""
    arbol = catalogo.categorias
    conteo = catalogo.conteo_por_categoria()
    actual = inicio or arbol.raiz
    while True:
        print("\nEstás en: " + " > ".join(arbol.ruta(actual)))
        print(f"{conteo[actual]} canción(es) en esta categoría.")
        hijos = actual.hijos
        if hijos:
            print("Subcategorías:")
            for i, hijo in enumerate(hijos, start=1):
                print(f"  {i}. {hijo.nombre} ({conteo[hijo]})")
        else:
            print("(No tiene subcategorías.)")
            imprimir_canciones(catalogo.canciones_de_categoria(actual))

        acciones = []
        if hijos:
            acciones.append("número = entrar")
            acciones.append("c = ver sus canciones")
        if actual.padre is not None:
            acciones.append("u = subir")
        acciones.append("0 = salir")
        eleccion = input(f"[{' | '.join(acciones)}]: ").strip().lower()

        if eleccion == "0":
            return
        if eleccion == "u" and actual.padre is not None:
            actual = actual.padre
        elif eleccion == "c" and hijos:
            imprimir_canciones(catalogo.canciones_de_categoria(actual))
        elif eleccion.isdigit() and 1 <= int(eleccion) <= len(hijos):
            actual = hijos[int(eleccion) - 1]
        else:
            print("Opción inválida.")


def buscar_categoria(catalogo: CatalogoMusical):
    arbol = catalogo.categorias
    conteo = catalogo.conteo_por_categoria()
    texto = input("Nombre (o parte del nombre) de la categoría: ")
    encontrados = catalogo.buscar_categoria(texto) if texto.strip() else []
    if not encontrados:
        print("No se encontró ninguna categoría.")
        return
    print(f"Se encontraron {len(encontrados)} categoría(s):")
    for i, nodo in enumerate(encontrados, start=1):
        print(f"  {i}. {' > '.join(arbol.ruta(nodo))} ({conteo[nodo]} canciones)")
    eleccion = input("Número para explorarla (Enter para volver): ").strip()
    if eleccion.isdigit() and 1 <= int(eleccion) <= len(encontrados):
        navegar_categorias(catalogo, encontrados[int(eleccion) - 1])


def ver_recorrido(catalogo: CatalogoMusical):
    arbol = catalogo.categorias
    conteo = catalogo.conteo_por_categoria()
    print("Recorrido: 1) preorden  2) postorden  3) por niveles")
    tipo = input("Elegí una opción: ").strip()
    if tipo not in ("1", "2", "3"):
        print("Opción inválida.")
        return
    inicio = _pedir_categoria(arbol, "Desde qué categoría (Enter = Música): ")
    if inicio is None:
        return
    base = len(arbol.ruta(inicio))  # para indentar relativo al nodo de inicio

    def con_sangria(nodo):
        profundidad = len(arbol.ruta(nodo)) - base
        return f"{'    ' * profundidad}{nodo.nombre} ({conteo[nodo]})"

    if tipo == "1":
        print("\nPREORDEN (el padre antes que sus hijos; muestra la jerarquía de arriba hacia abajo):")
        for i, nodo in enumerate(arbol.preorden(inicio), start=1):
            print(f"{i:>3}. {con_sangria(nodo)}")
    elif tipo == "2":
        print("\nPOSTORDEN (los hijos antes que el padre; así se calcula la cantidad de canciones por categoría):")
        for i, nodo in enumerate(arbol.postorden(inicio), start=1):
            print(f"{i:>3}. {con_sangria(nodo)}")
    else:
        print("\nPOR NIVELES (de a un nivel a la vez, en anchura):")
        for nivel, nodos in enumerate(arbol.por_niveles(inicio)):
            print(f"  Nivel {nivel}: " + ", ".join(n.nombre for n in nodos))


def ver_ruta_de_cancion(catalogo: CatalogoMusical):
    titulo = input("Título de la canción: ").strip()
    cancion = catalogo.buscar_titulo_exacto(titulo)
    if cancion is None:
        print("No hay una canción con ese título exacto.")
        sugerencias = catalogo.autocompletar(titulo, max_resultados=5) if titulo else []
        if sugerencias:
            print("¿Quisiste decir alguna de estas?")
            imprimir_canciones(sugerencias)
        return
    print(cancion)
    print("Ruta en el árbol: " + catalogo.ruta_categoria_de(cancion))


def opcion_categorias(catalogo: CatalogoMusical):
    if catalogo.categorias is None:
        print("No hay una jerarquía de categorías cargada.")
        return
    acciones = {
        "1": ver_arbol_completo,
        "2": navegar_categorias,
        "3": buscar_categoria,
        "4": ver_recorrido,
        "5": ver_ruta_de_cancion,
    }
    while True:
        mostrar_submenu_categorias()
        op = input("Elegí una opción: ").strip()
        if op == "0":
            return
        if op in acciones:
            acciones[op](catalogo)
        else:
            print("Opción inválida, intentá de nuevo.")


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
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
        print(f"Aviso: no se encontró '{RUTA_CATEGORIAS}'; la opción 9 no estará disponible.")

    acciones = {
        "1": opcion_buscar,
        "2": opcion_buscar_titulo_exacto,
        "3": opcion_autocompletar,
        "4": opcion_generos,
        "5": opcion_top10,
        "6": opcion_listar,
        "7": opcion_listar_ordenado_arbol,
        "8": opcion_filtrar,
        "9": opcion_categorias,
    }

    while True:
        mostrar_menu()
        opcion = input("Elegí una opción: ").strip()

        if opcion == "0":
            print("¡Hasta la próxima!")
            break
        elif opcion in acciones:
            acciones[opcion](catalogo)
        elif opcion in ("10", "11"):
            print("Esta función todavía no está disponible en la v3.")
        else:
            print("Opción inválida, intentá de nuevo.")


if __name__ == "__main__":
    iniciar_programa()
