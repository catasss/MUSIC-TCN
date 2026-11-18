"""Pruebas de Dijkstra y del grafo ponderado (Objetivo 9)."""
import random
import unittest

from grafo_ponderado import GrafoPonderado, construir_grafo_artistas, costo_por_popularidad


class TestGrafoPonderado(unittest.TestCase):
    def setUp(self):
        # A-C directo cuesta 5, pero A-B-C cuesta 2
        self.g = GrafoPonderado()
        self.g.agregar_arista("A", "B", 1)
        self.g.agregar_arista("B", "C", 1)
        self.g.agregar_arista("A", "C", 5)
        self.g.agregar_arista("C", "D", 2)
        self.g.agregar_vertice("Aislado")

    def test_camino_de_menor_costo_no_es_el_de_menos_saltos(self):
        camino, costo = self.g.camino_minimo("A", "C")
        self.assertEqual(camino, ["A", "B", "C"])
        self.assertEqual(costo, 2)
        # BFS (menos saltos) elegiría el directo, que cuesta más
        self.assertEqual(self.g.camino_mas_corto("A", "C"), ["A", "C"])
        self.assertGreater(self.g.costo_de(["A", "C"]), costo)

    def test_camino_largo(self):
        self.assertEqual(self.g.camino_minimo("A", "D"), (["A", "B", "C", "D"], 4))

    def test_origen_igual_destino(self):
        self.assertEqual(self.g.camino_minimo("A", "A"), (["A"], 0.0))

    def test_sin_camino(self):
        self.assertIsNone(self.g.camino_minimo("A", "Aislado"))

    def test_vertice_inexistente(self):
        with self.assertRaises(KeyError):
            self.g.camino_minimo("A", "Z")

    def test_costo_negativo_rechazado(self):
        with self.assertRaises(ValueError):
            self.g.agregar_arista("X", "Y", -1)

    def test_simetria_no_dirigido(self):
        self.assertEqual(self.g.camino_minimo("D", "A")[1], self.g.camino_minimo("A", "D")[1])

    def test_dijkstra_completo(self):
        dist, _ = self.g.dijkstra("A")
        self.assertEqual(dist, {"A": 0, "B": 1, "C": 2, "D": 4})

    def test_contra_floyd_warshall_en_grafos_aleatorios(self):
        random.seed(7)
        for _ in range(30):
            n = random.randint(2, 9)
            g = GrafoPonderado()
            inf = float("inf")
            m = [[0 if i == j else inf for j in range(n)] for i in range(n)]
            for v in range(n):
                g.agregar_vertice(v)
            for _ in range(random.randint(0, n * 2)):
                a, b = random.randrange(n), random.randrange(n)
                if a != b:
                    w = random.randint(0, 9)
                    g.agregar_arista(a, b, w)
                    w = g.peso(a, b)
                    m[a][b] = m[b][a] = w
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        m[i][j] = min(m[i][j], m[i][k] + m[k][j])
            for i in range(n):
                dist, _ = g.dijkstra(i)
                for j in range(n):
                    self.assertEqual(dist.get(j, inf), m[i][j])


class TestGrafoArtistas(unittest.TestCase):
    def test_costo_base_y_penalizacion(self):
        self.assertEqual(costo_por_popularidad(80, 80), 1)
        self.assertEqual(costo_por_popularidad(90, 70), 5)

    def test_escalonado_gana_al_salto_grande(self):
        generos = {"Top": ["pop"], "Medio": ["pop"], "Chico": ["pop"]}
        pop = {"Top": 90, "Medio": 70, "Chico": 50}
        g = construir_grafo_artistas(generos, pop)
        camino, costo = g.camino_minimo("Top", "Chico")
        self.assertEqual(camino, ["Top", "Medio", "Chico"])   # costo 10 < 17 directo
        self.assertEqual(costo, 10)

    def test_generos_distintos_sin_conexion(self):
        g = construir_grafo_artistas({"A": ["rock"], "B": ["rap"]}, {"A": 50, "B": 50})
        self.assertIsNone(g.camino_minimo("A", "B"))


if __name__ == "__main__":
    unittest.main()
