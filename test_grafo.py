"""
test_grafo.py
Pruebas del grafo de artistas (v5): la estructura Grafo y su integración
con el catálogo.

Ejecutar con:
    python3 -m unittest test_grafo -v
"""

import os
import unittest

from grafo import Grafo
from gestor_musica_v5 import CatalogoMusical
from modelos import Cancion

CARPETA = os.path.dirname(os.path.abspath(__file__))


def grafo_de_ejemplo():
    """  A - B - C - D        E - F        G (aislado)
         |_____|                           """
    g = Grafo()
    for a, b in [("A", "B"), ("B", "C"), ("C", "D"), ("A", "C"), ("E", "F")]:
        g.agregar_arista(a, b)
    g.agregar_vertice("G")
    return g


class TestEstructura(unittest.TestCase):

    def test_grafo_vacio(self):
        g = Grafo()
        self.assertEqual(g.cantidad_vertices(), 0)
        self.assertEqual(g.cantidad_aristas(), 0)
        self.assertEqual(g.densidad(), 0.0)
        self.assertEqual(g.componentes_conexas(), [])

    def test_agregar_arista_crea_los_vertices(self):
        g = Grafo()
        g.agregar_arista("A", "B")
        self.assertTrue(g.tiene_vertice("A") and g.tiene_vertice("B"))

    def test_no_dirigido(self):
        g = Grafo()
        g.agregar_arista("A", "B")
        self.assertTrue(g.tiene_arista("A", "B"))
        self.assertTrue(g.tiene_arista("B", "A"))

    def test_aristas_repetidas_y_lazos_se_ignoran(self):
        g = Grafo()
        g.agregar_arista("A", "B")
        g.agregar_arista("B", "A")
        g.agregar_arista("A", "B")
        g.agregar_arista("A", "A")
        self.assertEqual(g.cantidad_aristas(), 1)
        self.assertEqual(g.grado("A"), 1)

    def test_conteos_y_grado(self):
        g = grafo_de_ejemplo()
        self.assertEqual(g.cantidad_vertices(), 7)
        self.assertEqual(g.cantidad_aristas(), 5)
        self.assertEqual(g.grado("C"), 3)
        self.assertEqual(g.grado("G"), 0)
        self.assertEqual(len(g.aristas()), 5)

    def test_densidad(self):
        g = Grafo()
        for a, b in [("A", "B"), ("A", "C"), ("B", "C")]:
            g.agregar_arista(a, b)
        self.assertEqual(g.densidad(), 1.0)           # triángulo: completo
        g.agregar_vertice("D")
        self.assertAlmostEqual(g.densidad(), 0.5)     # 3 de 6 posibles

    def test_vertice_inexistente(self):
        g = grafo_de_ejemplo()
        with self.assertRaises(KeyError):
            g.vecinos("Z")
        with self.assertRaises(KeyError):
            g.camino_mas_corto("A", "Z")

    def test_vecinos_devuelve_copia(self):
        g = grafo_de_ejemplo()
        g.vecinos("A").append("X")
        self.assertNotIn("X", g.vecinos("A"))


class TestRecorridosYConsultas(unittest.TestCase):

    def setUp(self):
        self.g = grafo_de_ejemplo()

    def test_bfs_visita_por_niveles(self):
        self.assertEqual(self.g.bfs("A"), ["A", "B", "C", "D"])

    def test_dfs_visita_todo_su_grupo(self):
        orden = self.g.dfs("A")
        self.assertEqual(orden[0], "A")
        self.assertEqual(sorted(orden), ["A", "B", "C", "D"])

    def test_distancias(self):
        self.assertEqual(self.g.distancias("A"), {"A": 0, "B": 1, "C": 1, "D": 2})

    def test_distancias_con_limite_de_saltos(self):
        self.assertEqual(self.g.distancias("A", max_saltos=1), {"A": 0, "B": 1, "C": 1})

    def test_camino_mas_corto_prefiere_el_atajo(self):
        self.assertEqual(self.g.camino_mas_corto("A", "D"), ["A", "C", "D"])

    def test_camino_a_si_mismo(self):
        self.assertEqual(self.g.camino_mas_corto("A", "A"), ["A"])

    def test_camino_inexistente_es_none(self):
        self.assertIsNone(self.g.camino_mas_corto("A", "E"))
        self.assertIsNone(self.g.camino_mas_corto("A", "G"))

    def test_componentes_conexas(self):
        grupos = self.g.componentes_conexas()
        self.assertEqual([len(x) for x in grupos], [4, 2, 1])
        self.assertEqual(sorted(sum(grupos, [])), sorted(self.g.vertices()))

    def test_esta_conectado(self):
        self.assertFalse(self.g.esta_conectado())
        chico = Grafo()
        chico.agregar_arista("A", "B")
        self.assertTrue(chico.esta_conectado())


class TestGrafoDeArtistas(unittest.TestCase):

    def setUp(self):
        self.cat = CatalogoMusical()
        self.cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
        self.grafo = self.cat.grafo

    def test_un_vertice_por_artista(self):
        artistas = {c.artista for c in self.cat.listar()}
        self.assertEqual(set(self.grafo.vertices()), artistas)
        self.assertEqual(self.grafo.cantidad_vertices(), 12)

    def test_aristas_entre_artistas_del_mismo_genero(self):
        self.assertTrue(self.grafo.tiene_arista("BTS", "BLACKPINK"))
        self.assertTrue(self.grafo.tiene_arista("Drake", "Eminem"))
        self.assertFalse(self.grafo.tiene_arista("Drake", "BTS"))
        self.assertEqual(self.grafo.cantidad_aristas(), 11)

    def test_grupos_iniciales_son_los_generos(self):
        self.assertEqual([len(g) for g in self.cat.grupos_de_artistas()], [4, 3, 2, 2, 1])

    def test_artistas_relacionados(self):
        self.assertEqual(self.cat.artistas_relacionados("BTS"), ["BLACKPINK"])
        self.assertEqual(self.cat.artistas_relacionados("Mercedes Sosa"), [])

    def test_sin_camino_entre_generos_distintos(self):
        self.assertIsNone(self.cat.camino_entre_artistas("Drake", "BTS"))

    def test_buscar_artista(self):
        self.assertEqual(self.cat.buscar_artista("drake"), "Drake")
        self.assertEqual(self.cat.buscar_artista("kendr"), "Kendrick Lamar")  # parcial único
        self.assertIsNone(self.cat.buscar_artista("zzz"))
        self.assertIsNone(self.cat.buscar_artista(""))

    def test_un_artista_con_dos_generos_une_dos_grupos(self):
        self.cat.agregar_cancion(
            Cancion(self.cat.siguiente_id(), "Pray for Me", "The Weeknd", "rap", 2018, 80))
        self.assertEqual(self.cat.camino_entre_artistas("Harry Styles", "Drake"),
                         ["Harry Styles", "The Weeknd", "Drake"])
        self.assertEqual([len(g) for g in self.cat.grupos_de_artistas()], [7, 2, 2, 1])

    def test_artista_nuevo_se_suma_al_grafo(self):
        self.cat.agregar_cancion(
            Cancion(self.cat.siguiente_id(), "Otra", "Artista Nuevo", "folk", 2020, 50))
        self.assertTrue(self.grafo is not self.cat.grafo)   # se reconstruyó
        self.assertEqual(self.cat.artistas_relacionados("Artista Nuevo"), ["Mercedes Sosa"])

    def test_artistas_a_n_saltos(self):
        self.assertEqual(self.cat.artistas_a_n_saltos("BTS", 3), [("BLACKPINK", 1)])
        self.assertEqual(len(self.cat.artistas_a_n_saltos("Drake", 1)), 3)

    def test_el_grafo_sobrevive_a_cargar_otros_datos(self):
        self.cat.cargar_desde_lista([Cancion(1, "X", "Solo", "pop", 2000, 10)])
        self.assertEqual(self.cat.grafo.cantidad_vertices(), 1)


if __name__ == "__main__":
    unittest.main()
