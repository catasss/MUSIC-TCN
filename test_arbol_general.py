"""
test_arbol_general.py
Pruebas del árbol general de categorías (arbol_general.py) y de su
integración con CatalogoMusical.

Ejecutar con:
    python3 -m unittest test_arbol_general.py -v
"""

import os
import unittest

from arbol_general import ArbolCategorias, NodoCategoria
from gestor_musica_v3 import CatalogoMusical

CARPETA = os.path.dirname(os.path.abspath(__file__))

# Árbol de referencia (el de la consigna):
#   Películas
#   ├── Ciencia ficción
#   │   ├── Cyberpunk
#   │   ├── Viajes temporales
#   │   └── Inteligencia artificial
#   ├── Acción
#   └── Comedia
DATOS = {
    "nombre": "Películas",
    "hijos": [
        {"nombre": "Ciencia ficción", "hijos": [
            {"nombre": "Cyberpunk"},
            {"nombre": "Viajes temporales"},
            {"nombre": "Inteligencia artificial"},
        ]},
        {"nombre": "Acción"},
        {"nombre": "Comedia"},
    ],
}


def nombres(nodos):
    return [n.nombre for n in nodos]


class TestEstructura(unittest.TestCase):

    def setUp(self):
        self.arbol = ArbolCategorias.desde_dict(DATOS)

    def test_cantidad_altura_y_hojas(self):
        self.assertEqual(self.arbol.cantidad(), 7)
        self.assertEqual(self.arbol.altura(), 3)
        self.assertEqual(nombres(self.arbol.hojas()),
                         ["Cyberpunk", "Viajes temporales", "Inteligencia artificial",
                          "Acción", "Comedia"])

    def test_un_nodo_puede_tener_muchos_hijos(self):
        ciencia = self.arbol.buscar("Ciencia ficción")
        self.assertEqual(len(ciencia.hijos), 3)

    def test_padre_de_cada_nodo(self):
        self.assertIsNone(self.arbol.raiz.padre)
        cyber = self.arbol.buscar("Cyberpunk")
        self.assertEqual(cyber.padre.nombre, "Ciencia ficción")

    def test_arbol_de_un_solo_nodo(self):
        arbol = ArbolCategorias(NodoCategoria("Solo"))
        self.assertEqual(arbol.cantidad(), 1)
        self.assertEqual(arbol.altura(), 1)
        self.assertEqual(nombres(arbol.por_niveles()[0]), ["Solo"])

    def test_agregar_a_un_padre_existente(self):
        self.arbol.agregar("Acción", NodoCategoria("Artes marciales"))
        self.assertEqual(self.arbol.cantidad(), 8)
        self.assertEqual(self.arbol.altura(), 3)
        self.assertEqual(self.arbol.buscar("Artes marciales").padre.nombre, "Acción")

    def test_agregar_a_un_padre_inexistente_falla(self):
        with self.assertRaises(ValueError):
            self.arbol.agregar("No existe", NodoCategoria("X"))

    def test_la_lista_de_hijos_no_se_expone_para_modificar(self):
        copia = self.arbol.raiz.hijos
        copia.clear()
        self.assertEqual(len(self.arbol.raiz.hijos), 3)


class TestBusquedas(unittest.TestCase):

    def setUp(self):
        self.arbol = ArbolCategorias.desde_dict(DATOS)

    def test_buscar_exacto_ignora_mayusculas(self):
        self.assertEqual(self.arbol.buscar("cyberPUNK").nombre, "Cyberpunk")

    def test_buscar_inexistente(self):
        self.assertIsNone(self.arbol.buscar("Terror"))

    def test_buscar_parcial(self):
        # "ci" aparece en tres nombres (también en "Acción"), en orden de preorden
        self.assertEqual(nombres(self.arbol.buscar_parcial("ci")),
                         ["Ciencia ficción", "Inteligencia artificial", "Acción"])
        self.assertEqual(nombres(self.arbol.buscar_parcial("artif")),
                         ["Inteligencia artificial"])

    def test_ruta_desde_la_raiz(self):
        nodo = self.arbol.buscar("Viajes temporales")
        self.assertEqual(self.arbol.ruta(nodo),
                         ["Películas", "Ciencia ficción", "Viajes temporales"])
        self.assertEqual(self.arbol.ruta(self.arbol.raiz), ["Películas"])


class TestRecorridos(unittest.TestCase):

    def setUp(self):
        self.arbol = ArbolCategorias.desde_dict(DATOS)

    def test_preorden_padre_antes_que_hijos(self):
        self.assertEqual(nombres(self.arbol.preorden()), [
            "Películas", "Ciencia ficción", "Cyberpunk", "Viajes temporales",
            "Inteligencia artificial", "Acción", "Comedia"])

    def test_postorden_hijos_antes_que_padre(self):
        self.assertEqual(nombres(self.arbol.postorden()), [
            "Cyberpunk", "Viajes temporales", "Inteligencia artificial",
            "Ciencia ficción", "Acción", "Comedia", "Películas"])

    def test_por_niveles(self):
        niveles = [nombres(n) for n in self.arbol.por_niveles()]
        self.assertEqual(niveles, [
            ["Películas"],
            ["Ciencia ficción", "Acción", "Comedia"],
            ["Cyberpunk", "Viajes temporales", "Inteligencia artificial"],
        ])

    def test_recorrido_desde_un_subarbol(self):
        ciencia = self.arbol.buscar("Ciencia ficción")
        self.assertEqual(nombres(self.arbol.preorden(ciencia)),
                         ["Ciencia ficción", "Cyberpunk", "Viajes temporales",
                          "Inteligencia artificial"])

    def test_todos_los_recorridos_visitan_los_mismos_nodos(self):
        pre = sorted(nombres(self.arbol.preorden()))
        post = sorted(nombres(self.arbol.postorden()))
        niv = sorted(n.nombre for nivel in self.arbol.por_niveles() for n in nivel)
        self.assertEqual(pre, post)
        self.assertEqual(pre, niv)

    def test_dibujo_coincide_con_la_consigna(self):
        esperado = "\n".join([
            "Películas",
            "├── Ciencia ficción",
            "│   ├── Cyberpunk",
            "│   ├── Viajes temporales",
            "│   └── Inteligencia artificial",
            "├── Acción",
            "└── Comedia",
        ])
        self.assertEqual(self.arbol.dibujar(), esperado)


class TestIntegracionConCatalogo(unittest.TestCase):

    def setUp(self):
        self.cat = CatalogoMusical()
        self.cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
        self.cat.cargar_categorias_desde_json(os.path.join(CARPETA, "datos", "categorias.json"))
        self.arbol = self.cat.categorias

    def test_la_raiz_cubre_todo_el_catalogo(self):
        self.assertEqual(len(self.cat.canciones_de_categoria(self.arbol.raiz)), len(self.cat))

    def test_cada_cancion_cae_en_una_sola_familia(self):
        total = sum(len(self.cat.canciones_de_categoria(f)) for f in self.arbol.raiz.hijos)
        self.assertEqual(total, len(self.cat))

    def test_familia_agrupa_sus_generos(self):
        pop = self.arbol.buscar("Pop y derivados")
        generos = {c.genero for c in self.cat.canciones_de_categoria(pop)}
        self.assertEqual(generos, {"pop", "k-pop"})
        self.assertEqual(len(self.cat.canciones_de_categoria(pop)), 7)

    def test_nodo_de_artista_solo_trae_sus_canciones(self):
        bts = self.arbol.buscar("BTS")
        canciones = self.cat.canciones_de_categoria(bts)
        self.assertEqual(len(canciones), 2)
        self.assertTrue(all(c.artista == "BTS" for c in canciones))

    def test_los_artistas_salen_del_catalogo_real(self):
        artistas_catalogo = set(self.cat.artistas_disponibles())
        artistas_arbol = {n.artista for n in self.arbol.preorden() if n.artista}
        self.assertEqual(artistas_arbol, artistas_catalogo)

    def test_ruta_de_una_cancion(self):
        dynamite = self.cat.buscar_titulo_exacto("Dynamite")
        self.assertEqual(self.cat.ruta_categoria_de(dynamite),
                         "Música > Pop y derivados > K-pop > BTS")

    def test_buscar_categoria_parcial(self):
        nombres_enc = [n.nombre for n in self.cat.buscar_categoria("pop")]
        self.assertIn("Pop y derivados", nombres_enc)
        self.assertIn("K-pop", nombres_enc)

    def test_genero_desconocido_va_a_otros(self):
        from modelos import Cancion
        extra = Cancion(99, "Cumbia Test", "Los Test", "cumbia", 2000, 50)
        self.cat.cargar_desde_lista(self.cat.listar() + [extra])
        otros = self.cat.categorias.buscar("Otros")
        self.assertIsNotNone(otros)
        self.assertEqual(len(self.cat.canciones_de_categoria(otros)), 1)
        self.assertEqual(self.cat.ruta_categoria_de(extra),
                         "Música > Otros > Cumbia > Los Test")


if __name__ == "__main__":
    unittest.main()
