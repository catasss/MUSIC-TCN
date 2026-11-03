"""
ejemplos_consultas_grafo.py
Ejemplos de consultas sobre el grafo de artistas de MUSICTCN (TP7 - Grafos),
usando el catálogo real de datos/.

Ejecutar con:
    python3 ejemplos_consultas_grafo.py
    python3 ejemplos_consultas_grafo.py > ejemplos_consultas_grafo.txt
"""

import os

from gestor_musica_v5 import CatalogoMusical
from modelos import Cancion

CARPETA = os.path.dirname(os.path.abspath(__file__))


def titulo(texto):
    print("\n" + "=" * 64)
    print(texto)
    print("=" * 64)


def main():
    cat = CatalogoMusical()
    cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
    g = cat.grafo

    titulo("1. El grafo (vértice = artista, arista = comparten género)")
    print(g.lista_de_adyacencia())

    titulo("2. Por qué lista de adyacencia: densidad del grafo")
    v, e = g.cantidad_vertices(), g.cantidad_aristas()
    print(f"Vértices: {v} | Aristas: {e} | Densidad: {g.densidad():.1%}")
    print(f"Matriz de adyacencia: {v} x {v} = {v * v} celdas, solo {2 * e} con una conexión "
          f"({2 * e / (v * v):.0%}); el resto guarda ceros.")
    print(f"Lista de adyacencia : {v} listas con {2 * e} entradas en total.")
    print("En un catálogo grande la densidad tiende a 1 / (cantidad de géneros):")
    print("con 20 géneros repartidos parejo, ronda el 5%. Una matriz de 10.000")
    print("artistas ocuparía 100 millones de celdas casi vacías.")

    titulo("3. Vecinos y grado")
    for artista in ("Drake", "BTS", "Mercedes Sosa"):
        vecinos = cat.artistas_relacionados(artista)
        print(f"{artista:<14} grado {g.grado(artista)}: {', '.join(vecinos) if vecinos else '(sin conexiones)'}")
    grado_maximo = max(g.grado(a) for a in g.vertices())
    lideres = [a for a in g.vertices() if g.grado(a) == grado_maximo]
    print(f"\nArtistas con más conexiones (grado {grado_maximo}): {', '.join(lideres)}")
    print(f"Artistas aislados: {[a for a in g.vertices() if g.grado(a) == 0]}")

    titulo("4. Recorridos desde Dua Lipa")
    print("BFS (anchura)     :", " -> ".join(g.bfs("Dua Lipa")))
    print("DFS (profundidad) :", " -> ".join(g.dfs("Dua Lipa")))

    titulo("5. Camino más corto (BFS)")
    for origen, destino in [("Drake", "Eminem"), ("Drake", "BTS"), ("Queen", "Soda Stereo")]:
        camino = cat.camino_entre_artistas(origen, destino)
        resultado = " -> ".join(camino) + f"  ({len(camino) - 1} salto)" if camino else "no hay camino (grupos separados)"
        print(f"{origen} a {destino}: {resultado}")

    titulo("6. Componentes conexas: los grupos separados")
    for i, grupo in enumerate(cat.grupos_de_artistas(), start=1):
        print(f"Grupo {i} ({len(grupo)}): {', '.join(grupo)}")
    print("\nCada género forma un grupo donde todos se conocen entre sí; entre")
    print("géneros distintos no hay camino... hasta que aparece un puente.")

    titulo("7. Un artista en dos géneros hace de puente")
    print("Se agrega 'Pray for Me' de The Weeknd, clasificada como rap.\n")
    cat.agregar_cancion(Cancion(cat.siguiente_id(), "Pray for Me", "The Weeknd", "rap", 2018, 80))
    g = cat.grafo
    print(f"The Weeknd ahora: {', '.join(cat.generos_de_artista('The Weeknd'))} | grado {g.grado('The Weeknd')}")
    camino = cat.camino_entre_artistas("Harry Styles", "Drake")
    print(f"Harry Styles a Drake: {' -> '.join(camino)}  ({len(camino) - 1} saltos)")
    print("\nArtistas a 2 saltos de Harry Styles:")
    for nombre, saltos in cat.artistas_a_n_saltos("Harry Styles", 2):
        print(f"  {saltos} salto(s): {nombre}")
    print(f"\nGrupos ahora: {[len(x) for x in cat.grupos_de_artistas()]} (antes: [4, 3, 2, 2, 1])")


if __name__ == "__main__":
    main()
