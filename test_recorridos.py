"""
test_recorridos.py
Pruebas de los recorridos de grafos (TP8): BFS, DFS, dfs_arbol y bfs_buscar de
grafo.py, y las consultas de CatalogoMusical v6 que los usan.

Ejecutar con:
    python3 -m unittest test_recorridos.py -v
"""

import random
import unittest

from gestor_musica_v6 import CatalogoMusical
from grafo import Grafo
from modelos import Cancion

#   A --- B --- D --- E        F (aislado)
#   |           |
#   +---- C ----+
ARISTAS = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]


def grafo_de_referencia():
    g = Grafo()
    for a, b in ARISTAS:
        g.agregar_arista(a, b)
    g.agregar_vertice("F")
    return g


def dfs_recursivo(g, vertice, visitados, orden, padre=None, profundidad=0):
    """DFS clásico recursivo, como referencia para comparar con el iterativo."""
    visitados.add(vertice)
    orden.append((vertice, padre, profundidad))
    for vecino in g.vecinos(vertice):
        if vecino not in visitados:
            dfs_recursivo(g, vecino, visitados, orden, vertice, profundidad + 1)


def grafo_al_azar(semilla, n=40, m=60):
    azar = random.Random(semilla)
    g = Grafo()
    for v in range(n):
        g.agregar_vertice(v)
    for _ in range(m):
        g.agregar_arista(azar.randrange(n), azar.randrange(n))
    return g


class TestBFS(unittest.TestCase):
    def test_orden_por_niveles(self):
        self.assertEqual(grafo_de_referencia().bfs("A"), ["A", "B", "C", "D", "E"])

    def test_no_incluye_otros_grupos(self):
        self.assertNotIn("F", grafo_de_referencia().bfs("A"))

    def test_distancias(self):
        self.assertEqual(grafo_de_referencia().distancias("A"),
                         {"A": 0, "B": 1, "C": 1, "D": 2, "E": 3})

    def test_origen_inexistente(self):
        with self.assertRaises(KeyError):
            grafo_de_referencia().bfs("Z")

    def test_vertice_aislado(self):
        self.assertEqual(grafo_de_referencia().bfs("F"), ["F"])


class TestDFS(unittest.TestCase):
    def test_orden_en_profundidad(self):
        # A -> B -> D -> C (se mete hasta el fondo) y recién después E
        self.assertEqual(grafo_de_referencia().dfs("A"), ["A", "B", "D", "C", "E"])

    def test_dfs_arbol_padres_y_profundidad(self):
        self.assertEqual(
            grafo_de_referencia().dfs_arbol("A"),
            [("A", None, 0), ("B", "A", 1), ("D", "B", 2), ("C", "D", 3), ("E", "D", 3)])

    def test_profundidad_no_es_distancia(self):
        g = grafo_de_referencia()
        profundidad_c = {v: p for v, _, p in g.dfs_arbol("A")}["C"]
        self.assertEqual(profundidad_c, 3)
        self.assertEqual(g.distancias("A")["C"], 1)

    def test_coincide_con_dfs_recursivo_en_grafos_al_azar(self):
        for semilla in range(25):
            g = grafo_al_azar(semilla)
            esperado = []
            dfs_recursivo(g, 0, set(), esperado)
            self.assertEqual(g.dfs_arbol(0), esperado, f"semilla {semilla}")

    def test_dfs_y_bfs_visitan_los_mismos_vertices(self):
        for semilla in range(25):
            g = grafo_al_azar(semilla)
            self.assertEqual(set(g.dfs(0)), set(g.bfs(0)))
            self.assertEqual(len(g.dfs(0)), len(set(g.dfs(0))))  # sin repetidos

    def test_cadena_larga_no_desborda_la_pila(self):
        g = Grafo()
        for v in range(1, 5000):  # más que el límite de recursión de Python
            g.agregar_arista(v - 1, v)
        self.assertEqual(len(g.dfs(0)), 5000)

    def test_origen_inexistente(self):
        with self.assertRaises(KeyError):
            grafo_de_referencia().dfs("Z")


class TestBFSBuscar(unittest.TestCase):
    def test_encuentra_el_mas_cercano(self):
        g = grafo_de_referencia()
        self.assertEqual(g.bfs_buscar("A", lambda v: v in ("D", "E")), ["A", "B", "D"])

    def test_no_cuenta_al_origen(self):
        g = grafo_de_referencia()
        self.assertEqual(g.bfs_buscar("A", lambda v: v == "A"), None)
        self.assertEqual(g.bfs_buscar("A", lambda v: v in ("A", "B")), ["A", "B"])

    def test_ninguno_cumple_o_no_alcanzable(self):
        g = grafo_de_referencia()
        self.assertIsNone(g.bfs_buscar("A", lambda v: False))
        self.assertIsNone(g.bfs_buscar("A", lambda v: v == "F"))

    def test_camino_mas_corto_sigue_funcionando(self):
        g = grafo_de_referencia()
        self.assertEqual(g.camino_mas_corto("A", "E"), ["A", "B", "D", "E"])
        self.assertEqual(g.camino_mas_corto("A", "A"), ["A"])
        self.assertIsNone(g.camino_mas_corto("A", "F"))

    def test_camino_es_minimo_en_grafos_al_azar(self):
        for semilla in range(25):
            g = grafo_al_azar(semilla)
            distancias = g.distancias(0)
            for destino in range(1, 40):
                camino = g.camino_mas_corto(0, destino)
                if destino in distancias:
                    self.assertEqual(len(camino) - 1, distancias[destino])
                else:
                    self.assertIsNone(camino)


def catalogo_de_prueba():
    c = CatalogoMusical()
    c.cargar_desde_lista([
        Cancion(1, "a1", "Eminem", "rap", 2002, 90),
        Cancion(2, "a2", "Drake", "rap", 2018, 90),
        Cancion(3, "a3", "Weeknd", "pop", 2020, 90),
        Cancion(4, "a4", "BTS", "k-pop", 2020, 90),
        Cancion(5, "a5", "Mercedes Sosa", "folk", 1965, 80),
    ])
    return c


class TestConsultasDelCatalogo(unittest.TestCase):
    def setUp(self):
        self.cat = catalogo_de_prueba()

    def test_mas_cercano_de_su_mismo_genero(self):
        self.assertEqual(self.cat.artista_mas_cercano_de_genero("Eminem", "rap"),
                         ["Eminem", "Drake"])

    def test_sin_puente_no_hay_camino(self):
        self.assertIsNone(self.cat.artista_mas_cercano_de_genero("Eminem", "k-pop"))

    def test_genero_inexistente(self):
        self.assertIsNone(self.cat.artista_mas_cercano_de_genero("Eminem", "jazz"))

    def test_genero_sin_importar_mayusculas(self):
        self.cat.agregar_cancion(Cancion(6, "a6", "Drake", "pop", 2016, 80))
        camino = self.cat.artista_mas_cercano_de_genero("Eminem", " POP ")
        self.assertEqual(camino, ["Eminem", "Drake"])  # Drake ya canta pop

    def test_agregar_cancion_crea_el_puente(self):
        # Drake pasa a cantar pop y The Weeknd k-pop: Eminem ya llega a k-pop
        self.cat.agregar_cancion(Cancion(6, "a6", "Drake", "pop", 2016, 80))
        self.cat.agregar_cancion(Cancion(7, "a7", "Weeknd", "k-pop", 2021, 80))
        self.assertEqual(self.cat.artista_mas_cercano_de_genero("Eminem", "k-pop"),
                         ["Eminem", "Drake", "Weeknd"])

    def test_artista_inexistente(self):
        with self.assertRaises(KeyError):
            self.cat.artista_mas_cercano_de_genero("Nadie", "rap")

    def test_explorar_en_profundidad_y_anchura(self):
        self.assertEqual(self.cat.explorar_en_profundidad("Eminem"),
                         [("Eminem", None, 0), ("Drake", "Eminem", 1)])
        self.assertEqual(self.cat.explorar_en_anchura("Eminem"),
                         [("Eminem", 0), ("Drake", 1)])

    def test_artista_aislado(self):
        self.assertEqual(self.cat.explorar_en_profundidad("Mercedes Sosa"),
                         [("Mercedes Sosa", None, 0)])


if __name__ == "__main__":
    unittest.main()
