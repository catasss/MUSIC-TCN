"""
test_gestor_categorias.py
Pruebas de las operaciones de categorías agregadas al gestor en la v3
(conteo en postorden y casos borde). Los tests del árbol en sí están en
test_arbol_general.py.

Ejecutar con:
    python3 -m unittest test_gestor_categorias -v
"""

import os
import unittest

from gestor_musica_v3 import CatalogoMusical
from modelos import Cancion

CARPETA = os.path.dirname(os.path.abspath(__file__))


class TestConteoPorCategoria(unittest.TestCase):

    def setUp(self):
        self.cat = CatalogoMusical()
        self.cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
        self.cat.cargar_categorias_desde_json(os.path.join(CARPETA, "datos", "categorias.json"))
        self.arbol = self.cat.categorias
        self.conteo = self.cat.conteo_por_categoria()

    def test_la_raiz_suma_todo_el_catalogo(self):
        self.assertEqual(self.conteo[self.arbol.raiz], len(self.cat))

    def test_cada_padre_es_la_suma_de_sus_hijos(self):
        for nodo in self.arbol.preorden():
            if nodo.hijos:
                self.assertEqual(self.conteo[nodo], sum(self.conteo[h] for h in nodo.hijos))

    def test_conteos_conocidos(self):
        self.assertEqual(self.conteo[self.arbol.buscar("K-pop")], 4)
        self.assertEqual(self.conteo[self.arbol.buscar("Soda Stereo")], 2)

    def test_el_conteo_se_actualiza_al_cambiar_los_datos(self):
        extra = Cancion(99, "Otra de BTS", "BTS", "k-pop", 2021, 80)
        self.cat.cargar_desde_lista(self.cat.listar() + [extra])
        conteo = self.cat.conteo_por_categoria()
        self.assertEqual(conteo[self.cat.categorias.buscar("BTS")], 3)
        self.assertEqual(conteo[self.cat.categorias.raiz], 16)


class TestSinCategorias(unittest.TestCase):

    def test_sin_jerarquia_cargada_no_falla(self):
        cat = CatalogoMusical()
        cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
        self.assertIsNone(cat.categorias)
        self.assertEqual(cat.buscar_categoria("pop"), [])
        self.assertEqual(cat.conteo_por_categoria(), {})
        self.assertIsNone(cat.ruta_categoria_de(cat.listar()[0]))

    def test_cargar_la_jerarquia_antes_que_las_canciones(self):
        cat = CatalogoMusical()
        cat.cargar_categorias_desde_json(os.path.join(CARPETA, "datos", "categorias.json"))
        cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
        self.assertEqual(cat.conteo_por_categoria()[cat.categorias.raiz], 15)


if __name__ == "__main__":
    unittest.main()
