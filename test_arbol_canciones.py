"""
test_arbol_canciones.py
Pruebas unitarias de ArbolCanciones: inserción, búsqueda, autocompletado
y los tres recorridos (inorder, preorder, postorder).

Ejecutar con:
    python3 -m unittest test_arbol_canciones.py -v
"""

import random
import unittest

from modelos import Cancion
from arbol_canciones import ArbolCanciones


def _cancion(titulo, id_=0):
    return Cancion(id_cancion=id_, titulo=titulo, artista="Artista X",
                    genero="pop", anio=2020, popularidad=50)


class TestInsercionYBusqueda(unittest.TestCase):

    def test_arbol_vacio_no_encuentra_nada(self):
        arbol = ArbolCanciones()
        self.assertIsNone(arbol.buscar("Cualquiera"))
        self.assertEqual(len(arbol), 0)

    def test_insertar_y_buscar_un_elemento(self):
        arbol = ArbolCanciones()
        c = _cancion("Matrix")
        arbol.insertar(c)
        self.assertEqual(len(arbol), 1)
        encontrada = arbol.buscar("Matrix")
        self.assertIsNotNone(encontrada)
        self.assertEqual(encontrada.titulo, "Matrix")

    def test_buscar_titulo_inexistente_devuelve_none(self):
        arbol = ArbolCanciones()
        arbol.insertar(_cancion("Matrix"))
        self.assertIsNone(arbol.buscar("Titanic"))

    def test_insertar_varios_y_buscar_cada_uno(self):
        titulos = ["Matrix", "Inception", "Titanic", "Avatar", "Gladiator", "Up"]
        arbol = ArbolCanciones()
        for t in titulos:
            arbol.insertar(_cancion(t))
        self.assertEqual(len(arbol), len(titulos))
        for t in titulos:
            encontrada = arbol.buscar(t)
            self.assertIsNotNone(encontrada, f"no encontró '{t}'")
            self.assertEqual(encontrada.titulo, t)
        self.assertIsNone(arbol.buscar("No Existe"))

    def test_titulo_duplicado_reemplaza_sin_duplicar_nodo(self):
        arbol = ArbolCanciones()
        arbol.insertar(_cancion("Matrix", id_=1))
        arbol.insertar(_cancion("Matrix", id_=2))  # mismo título, otra canción
        self.assertEqual(len(arbol), 1)
        self.assertEqual(arbol.buscar("Matrix").id, 2)


class TestRecorridos(unittest.TestCase):
    """Árbol de referencia (el mismo de la consigna):
              Matrix
              /    \\
        Inception  Titanic
    """

    def setUp(self):
        self.arbol = ArbolCanciones()
        # se insertan en este orden para que el árbol quede EXACTAMENTE
        # con esta forma (Matrix como raíz)
        for t in ["Matrix", "Inception", "Titanic"]:
            self.arbol.insertar(_cancion(t))

    def test_inorder_da_orden_alfabetico(self):
        titulos = [c.titulo for c in self.arbol.recorrido_inorder()]
        self.assertEqual(titulos, ["Inception", "Matrix", "Titanic"])

    def test_preorder_es_raiz_izquierda_derecha(self):
        titulos = [c.titulo for c in self.arbol.recorrido_preorder()]
        self.assertEqual(titulos, ["Matrix", "Inception", "Titanic"])

    def test_postorder_es_izquierda_derecha_raiz(self):
        titulos = [c.titulo for c in self.arbol.recorrido_postorder()]
        self.assertEqual(titulos, ["Inception", "Titanic", "Matrix"])

    def test_inorder_sobre_arbol_grande_es_siempre_orden_alfabetico(self):
        titulos_originales = [f"Cancion {i:04d}" for i in range(500)]
        arbol = ArbolCanciones.construir_balanceado(
            [_cancion(t, id_=i) for i, t in enumerate(titulos_originales)]
        )
        titulos_inorder = [c.titulo for c in arbol.recorrido_inorder()]
        self.assertEqual(titulos_inorder, sorted(titulos_originales))


class TestBusquedaPorPrefijo(unittest.TestCase):

    def setUp(self):
        titulos = ["Dynamite", "Dynasty", "Boy With Luv", "Blinding Lights",
                   "Bohemian Rhapsody", "Dance Monkey", "Sicko Mode"]
        self.arbol = ArbolCanciones.construir_balanceado(
            [_cancion(t, id_=i) for i, t in enumerate(titulos)]
        )
        self.titulos = titulos

    def test_prefijo_devuelve_solo_coincidencias_y_ordenadas(self):
        resultados = [c.titulo for c in self.arbol.buscar_por_prefijo("Dy")]
        self.assertEqual(resultados, ["Dynamite", "Dynasty"])

    def test_prefijo_que_no_matchea_nada(self):
        resultados = self.arbol.buscar_por_prefijo("Zzz")
        self.assertEqual(resultados, [])

    def test_prefijo_respeta_max_resultados(self):
        resultados = self.arbol.buscar_por_prefijo("B", max_resultados=1)
        self.assertEqual(len(resultados), 1)

    def test_prefijo_vacio_devuelve_todo_ordenado(self):
        resultados = [c.titulo for c in self.arbol.buscar_por_prefijo("", max_resultados=100)]
        self.assertEqual(resultados, sorted(self.titulos))

    def test_prefijo_coincide_con_busqueda_por_fuerza_bruta(self):
        # verificación cruzada: comparamos contra un filtro lineal simple,
        # sobre un árbol más grande y con varios prefijos al azar
        titulos = [f"Cancion {i:05d}" for i in range(300)]
        canciones = [_cancion(t, id_=i) for i, t in enumerate(titulos)]
        arbol = ArbolCanciones.construir_balanceado(canciones)

        for prefijo in ["Cancion 001", "Cancion 00012", "Cancion 2", "Cancion 99999"]:
            esperado = sorted(t for t in titulos if t.startswith(prefijo))
            obtenido = [c.titulo for c in arbol.buscar_por_prefijo(prefijo, max_resultados=1000)]
            self.assertEqual(obtenido, esperado, f"falló con prefijo {prefijo!r}")


if __name__ == "__main__":
    unittest.main()
