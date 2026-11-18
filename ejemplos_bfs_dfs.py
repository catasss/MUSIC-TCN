"""
ejemplos_bfs_dfs.py
Ejemplos de los dos recorridos de grafos de MUSICTCN (TP8 - BFS y DFS) sobre
el grafo de artistas, usando el catálogo real de datos/.

Ejecutar con:
    python3 ejemplos_bfs_dfs.py
    python3 ejemplos_bfs_dfs.py > ejemplos_bfs_dfs.txt
"""

import os
import random
import sys
import time

from gestor_musica_v6 import CatalogoMusical
from grafo import Grafo
from modelos import Cancion

CARPETA = os.path.dirname(os.path.abspath(__file__))


def titulo(texto):
    print("\n" + "=" * 64)
    print(texto)
    print("=" * 64)


def con_generos(cat, artista):
    return f"{artista} ({', '.join(cat.generos_de_artista(artista))})"


def camino_por_dfs(grafo, origen, destino):
    """Camino hasta `destino` siguiendo el árbol de exploración del DFS
    (el que tomó el DFS, no necesariamente el más corto)."""
    padre = {v: p for v, p, _ in grafo.dfs_arbol(origen)}
    if destino not in padre:
        return None
    camino = [destino]
    while padre[camino[-1]] is not None:
        camino.append(padre[camino[-1]])
    return camino[::-1]


def main():
    cat = CatalogoMusical()
    cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
    g = cat.grafo

    titulo("1. El grafo del catálogo real (vértice = artista, arista = mismo género)")
    print(g.lista_de_adyacencia())
    grupos = cat.grupos_de_artistas()
    print(f"\n{g.cantidad_vertices()} artistas, {g.cantidad_aristas()} aristas, "
          f"{len(grupos)} grupos sin conexión entre sí:")
    for i, grupo in enumerate(grupos, start=1):
        print(f"  Grupo {i}: {', '.join(grupo)}")
    print("Con estos datos no hay artistas puente (ninguno canta en dos géneros),")
    print("así que cada recorrido se queda dentro de un solo género.")

    titulo("2. BFS vs DFS desde Eminem (grupo de rap: 4 artistas todos conectados entre sí)")
    print("BFS (anchura)     :", " -> ".join(f"{n} [{d}]" for n, d in cat.explorar_en_anchura("Eminem")))
    print("DFS (profundidad) :", " -> ".join(f"{n} [{p}]" for n, _, p in cat.explorar_en_profundidad("Eminem")))
    print("\nEntre corchetes: en BFS, saltos desde Eminem (distancia mínima); en DFS,")
    print("profundidad del camino que siguió. Los cuatro están a 1 salto de Eminem,")
    print("pero el DFS se mete por Travis Scott -> Drake -> Kendrick y llega a")
    print("profundidad 3: el número del DFS NO es la distancia.")

    titulo("3. Agregamos canciones que hacen de puente entre géneros (solo en memoria)")
    puentes = [
        ("One Dance", "Drake", "pop", 2016, 90),
        ("Ice Cream", "BLACKPINK", "pop", 2020, 85),
        ("Kiwi", "Harry Styles", "rock", 2017, 70),
    ]
    for titulo_cancion, artista, genero, anio, popularidad in puentes:
        cat.agregar_cancion(Cancion(cat.siguiente_id(), titulo_cancion, artista, genero, anio, popularidad))
        print(f"  + {titulo_cancion} - {artista} ({genero})")
    g = cat.grafo
    grupos = cat.grupos_de_artistas()
    print(f"\nAhora hay {len(grupos)} grupos:")
    for i, grupo in enumerate(grupos, start=1):
        print(f"  Grupo {i} ({len(grupo)}): {', '.join(grupo)}")
    print("Drake (rap y pop), BLACKPINK (k-pop y pop) y Harry Styles (pop y rock) conectan los géneros.")

    titulo("4. CASO DE USO BFS: ¿cuál es el artista de otro género más cercano?")
    print("Pregunta: 'me gusta X y quiero descubrir el género G; ¿por quién empiezo?'")
    print("Por qué BFS: explora por cantidad de saltos y corta en el primero que cumple,")
    print("así que el artista encontrado es de los más cercanos y la cadena es corta.\n")
    for origen, genero in [("Eminem", "k-pop"), ("Soda Stereo", "k-pop"),
                           ("Queen", "rap"), ("Eminem", "rock"), ("Mercedes Sosa", "rap")]:
        camino = cat.artista_mas_cercano_de_genero(origen, genero)
        if camino is None:
            print(f"{origen} -> {genero}: ninguno alcanzable (grupos separados)")
            continue
        print(f"{origen} -> {genero}: {camino[-1]}, a {len(camino) - 1} salto(s)")
        print("    " + " -> ".join(camino))

    print("\nNiveles del BFS desde Eminem (de ahí sale la respuesta):")
    por_nivel = {}
    for nombre, saltos in cat.explorar_en_anchura("Eminem"):
        por_nivel.setdefault(saltos, []).append(nombre)
    for saltos, nombres in por_nivel.items():
        print(f"  {saltos} salto(s): {', '.join(con_generos(cat, n) for n in nombres)}")

    titulo("5. CASO DE USO DFS: explorar toda la red de un artista en profundidad")
    print("Pregunta: 'mostrame todo lo que se puede descubrir a partir de Queen,")
    print("siguiendo una cadena de artistas hasta el fondo antes de volver'.")
    print("Por qué DFS: no busca lo más cercano sino recorrer TODO lo alcanzable;")
    print("va hasta el final de cada cadena y recién ahí retrocede.\n")
    visitas = cat.explorar_en_profundidad("Queen")
    for nombre, _, profundidad in visitas:
        print("  " * profundidad + con_generos(cat, nombre))
    print(f"\nSe visitaron {len(visitas)} artistas; cadena más larga: "
          f"{max(p for _, _, p in visitas)} pasos.")
    fuera = sorted(set(cat.artistas()) - {n for n, _, _ in visitas})
    print(f"No se alcanzan (otro grupo): {', '.join(fuera) if fuera else '(ninguno)'}")

    titulo("6. Mismo destino, distinto camino: BFS (mínimo) vs DFS (el primero que encuentra)")
    for origen, destino in [("Eminem", "BTS"), ("Soda Stereo", "Kendrick Lamar")]:
        corto = g.camino_mas_corto(origen, destino)
        profundo = camino_por_dfs(g, origen, destino)
        print(f"{origen} a {destino}")
        print(f"  BFS: {' -> '.join(corto)}  ({len(corto) - 1} salto(s))")
        print(f"  DFS: {' -> '.join(profundo)}  ({len(profundo) - 1} salto(s))")

    titulo("7. Costo: cuánto trabajan en total (todo el recorrido, grafos al azar)")
    print("Cada vértice se visita una vez y cada arista se mira dos veces (una")
    print("desde cada extremo): trabajo proporcional a V + E. Si el tiempo por")
    print("(V + E) se mantiene parecido al duplicar el tamaño, el costo es lineal.\n")
    print(f"{'V':>7} {'E':>8} {'BFS ms':>9} {'DFS ms':>9} {'BFS ns/(V+E)':>14} {'DFS ns/(V+E)':>14}")
    azar = random.Random(8)
    for n in (2000, 4000, 8000, 16000, 32000):
        grafo = Grafo()
        for v in range(n):
            grafo.agregar_vertice(v)
        # un camino que conecta todo + aristas al azar: en total unas 3 por vértice
        for v in range(1, n):
            grafo.agregar_arista(v - 1, v)
        for _ in range(2 * n):
            grafo.agregar_arista(azar.randrange(n), azar.randrange(n))
        total = grafo.cantidad_vertices() + grafo.cantidad_aristas()
        tiempos = {}
        for nombre, recorrido in (("bfs", grafo.bfs), ("dfs", grafo.dfs)):
            mejor = float("inf")
            for _ in range(5):
                inicio = time.perf_counter()
                visitados = recorrido(0)
                mejor = min(mejor, time.perf_counter() - inicio)
            assert len(visitados) == n
            tiempos[nombre] = mejor
        print(f"{n:>7} {grafo.cantidad_aristas():>8} {tiempos['bfs'] * 1000:>9.2f} "
              f"{tiempos['dfs'] * 1000:>9.2f} {tiempos['bfs'] / total * 1e9:>14.0f} "
              f"{tiempos['dfs'] / total * 1e9:>14.0f}")

    titulo("8. Por qué el DFS es iterativo (pila explícita) y no recursivo")
    cadena = Grafo()
    for v in range(1, 5000):
        cadena.agregar_arista(v - 1, v)
    print(f"Cadena de {cadena.cantidad_vertices()} vértices (cada uno conectado al siguiente).")
    print(f"dfs() iterativo visitó {len(cadena.dfs(0))} vértices sin problema.")

    def dfs_recursivo(grafo, vertice, visitados):
        visitados.add(vertice)
        for vecino in grafo.vecinos(vertice):
            if vecino not in visitados:
                dfs_recursivo(grafo, vecino, visitados)

    try:
        dfs_recursivo(cadena, 0, set())
        print("DFS recursivo: terminó.")
    except RecursionError:
        print(f"DFS recursivo: RecursionError (el límite de Python es {sys.getrecursionlimit()} llamadas anidadas).")


if __name__ == "__main__":
    main()
