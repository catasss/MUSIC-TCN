"""
main_v7.py  -  MUSICTCN v7 (Objetivo 9: Optimización + Demo Day)

Punto de entrada final. Ejecutar:  python3 main_v7.py

Opciones:
  1. Camino mínimo entre artistas (Dijkstra)   <- novedad de la v7
  2. Comparar Dijkstra vs BFS
  3. Ver el grafo de artistas con costos
  4. Abrir el catálogo completo (menú v6: árboles, heap, BFS/DFS)
  0. Salir

Los datos se leen de datos/canciones.json (el mismo archivo que usan las
versiones anteriores).
"""
import json
import os
import runpy
import sys

from grafo_ponderado import construir_grafo_artistas

RUTA_DATOS = os.path.join("datos", "canciones.json")


def _campo(cancion, *nombres):
    """Devuelve el primer campo que exista (tolera tildes y mayúsculas)."""
    for nombre in nombres:
        for clave in cancion:
            if clave.lower() == nombre:
                return cancion[clave]
    raise KeyError(f"La canción no tiene ninguno de los campos {nombres}: {list(cancion)}")


def cargar_artistas(ruta=RUTA_DATOS):
    """Lee el JSON y devuelve (generos_por_artista, popularidad_media)."""
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    if isinstance(datos, dict):  # por si el JSON viene como {"canciones": [...]}
        datos = next(v for v in datos.values() if isinstance(v, list))
    generos, sumas, cantidad = {}, {}, {}
    for c in datos:
        artista = _campo(c, "artista", "artist")
        genero = _campo(c, "genero", "género", "genre")
        pop = float(_campo(c, "popularidad", "popularity"))
        generos.setdefault(artista, set()).add(genero)
        sumas[artista] = sumas.get(artista, 0) + pop
        cantidad[artista] = cantidad.get(artista, 0) + 1
    popularidad = {a: sumas[a] / cantidad[a] for a in sumas}
    return generos, popularidad


def elegir_artista(grafo, mensaje):
    """Pide un artista por nombre (parcial, sin importar mayúsculas)."""
    while True:
        texto = input(mensaje).strip().lower()
        if not texto:
            return None
        coinciden = [a for a in grafo.vertices() if texto in a.lower()]
        exacto = [a for a in coinciden if a.lower() == texto]
        if len(exacto) == 1:
            return exacto[0]
        if len(coinciden) == 1:
            return coinciden[0]
        if not coinciden:
            print("  No encontré ese artista. Probá con otra parte del nombre.")
        else:
            print("  Varios coinciden:", ", ".join(sorted(coinciden)))


def listar_artistas(grafo, popularidad):
    print("\nArtistas disponibles (popularidad media):")
    for a in sorted(grafo.vertices(), key=str.lower):
        print(f"  - {a} ({popularidad[a]:.0f})")


def mostrar_camino(grafo, camino, titulo):
    print(f"\n{titulo}")
    print("  " + " -> ".join(camino))
    for a, b in zip(camino, camino[1:]):
        print(f"    {a} -> {b}: costo {grafo.peso(a, b):.2f}")
    print(f"  Saltos: {len(camino) - 1} | Costo total: {grafo.costo_de(camino):.2f}")


def opcion_camino_minimo(grafo, popularidad):
    listar_artistas(grafo, popularidad)
    origen = elegir_artista(grafo, "\nArtista de origen (Enter para volver): ")
    if origen is None:
        return
    destino = elegir_artista(grafo, "Artista de destino (Enter para volver): ")
    if destino is None:
        return
    resultado = grafo.camino_minimo(origen, destino)
    if resultado is None:
        print(f"\nNo hay camino entre {origen} y {destino} (no comparten ninguna cadena de géneros).")
        return
    mostrar_camino(grafo, resultado[0], "Camino de MENOR COSTO (Dijkstra):")


def opcion_comparar(grafo, popularidad):
    listar_artistas(grafo, popularidad)
    origen = elegir_artista(grafo, "\nArtista de origen (Enter para volver): ")
    if origen is None:
        return
    destino = elegir_artista(grafo, "Artista de destino (Enter para volver): ")
    if destino is None:
        return
    bfs = grafo.camino_mas_corto(origen, destino)
    if bfs is None:
        print("\nNo hay camino entre esos artistas.")
        return
    dij, _ = grafo.camino_minimo(origen, destino)
    mostrar_camino(grafo, bfs, "BFS (menos saltos, ignora el costo):")
    mostrar_camino(grafo, dij, "Dijkstra (menor costo):")
    if bfs == dij:
        print("\n  En este par coinciden: el camino directo ya es el más barato.")
    else:
        print("\n  Distinto camino: BFS minimiza saltos, Dijkstra minimiza costo.")


def opcion_ver_grafo(grafo):
    print(f"\n{grafo}  |  densidad {grafo.densidad():.2f}")
    for a, b in sorted(grafo.aristas(), key=lambda p: (p[0].lower(), p[1].lower())):
        print(f"  {a} -- {b}  (costo {grafo.peso(a, b):.2f})")
    print(f"\nGrupos conexos: {len(grafo.componentes_conexas())}")


def abrir_catalogo_v6():
    """Ejecuta el menú completo de la v6 (árboles, heap, grafo, BFS/DFS)."""
    if not os.path.exists("main_v6.py"):
        print("No encuentro main_v6.py en esta carpeta.")
        return
    runpy.run_path("main_v6.py", run_name="__main__")


def main():
    try:
        generos, popularidad = cargar_artistas()
    except (OSError, KeyError, StopIteration) as error:
        print(f"No pude leer {RUTA_DATOS}: {error}")
        sys.exit(1)
    grafo = construir_grafo_artistas(generos, popularidad)

    while True:
        print("\n" + "=" * 40)
        print(" MUSICTCN v7")
        print("=" * 40)
        print("1. Camino mínimo entre artistas (Dijkstra)")
        print("2. Comparar Dijkstra vs BFS")
        print("3. Ver grafo de artistas con costos")
        print("4. Abrir catálogo completo (menú v6)")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            opcion_camino_minimo(grafo, popularidad)
        elif opcion == "2":
            opcion_comparar(grafo, popularidad)
        elif opcion == "3":
            opcion_ver_grafo(grafo)
        elif opcion == "4":
            abrir_catalogo_v6()
        elif opcion == "0":
            print("¡Chau!")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
