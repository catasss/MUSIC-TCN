"""
test_recorridos.py
Pruebas unitarias para verificar el correcto funcionamiento de BFS y DFS
en la clase Grafo de MUSICTCN (TP8 - Recorridos de Grafos).

Ejecutar con:
    python3 -m unittest test_recorridos.py -v
"""

import unittest
from grafo import Grafo


class TestRecorridosGrafo(unittest.TestCase):

    def setUp(self):
        """
        Grafo de prueba para las consultas de recorridos:
            Queen --- David Bowie --- Iggy Pop
              |
            Elton John
        """
        self.g = Grafo()
        self.g.agregar_arista("Queen", "David Bowie")
        self.g.agregar_arista("David Bowie", "Iggy Pop")
        self.g.agregar_arista("Queen", "Elton John")

    def test_bfs_orden_visitados(self):
        """Verifica que BFS recorra primero los vecinos a salto 1 antes que a salto 2."""
        recorrido = self.g.bfs("Queen")
        
        # El primer elemento siempre es el origen
        self.assertEqual(recorrido[0], "Queen")
        
        # A 1 salto están David Bowie y Elton John (posiciones 1 y 2)
        self.assertIn(recorrido[1], ["David Bowie", "Elton John"])
        self.assertIn(recorrido[2], ["David Bowie", "Elton John"])
        
        # A 2 saltos está Iggy Pop (posicion 3)
        self.assertEqual(recorrido[3], "Iggy Pop")

    def test_dfs_orden_visitados(self):
        """Verifica que DFS visite todos los nodos de la componente conexa."""
        recorrido = self.g.dfs("Queen")
        
        self.assertEqual(recorrido[0], "Queen")
        self.assertEqual(len(recorrido), 4)
        self.assertCountEqual(recorrido, ["Queen", "David Bowie", "Iggy Pop", "Elton John"])

    def test_caso_real_bfs_artista_mas_cercano(self):
        """Caso real TP8: El artista más cercano a Iggy Pop es David Bowie (distancia = 1 arista)."""
        recorrido = self.g.bfs("Iggy Pop")
        self.assertEqual(recorrido[1], "David Bowie")

    def test_recorridos_vertice_inexistente(self):
        """Verifica que se lance KeyError al intentar hacer BFS/DFS sobre un vértice que no existe."""
        with self.assertRaises(KeyError):
            self.g.bfs("Artista Inexistente")
        with self.assertRaises(KeyError):
            self.g.dfs("Artista Inexistente")


if __name__ == "__main__":
    unittest.main()