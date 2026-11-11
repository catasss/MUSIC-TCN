"""
test_heap_prioridad.py
Pruebas de la cola de prioridad (heap), de la función de prioridad y de su
integración con CatalogoMusical.

Ejecutar con:
    python3 -m unittest test_heap_prioridad.py -v
"""

import os
import random
import unittest

from heap_prioridad import ColaPrioridad
from prioridad import CriterioPrioridad
from modelos import Cancion
from gestor_musica import CatalogoMusical

CARPETA = os.path.dirname(os.path.abspath(__file__))


class TestHeapBasico(unittest.TestCase):

    def test_heap_vacio(self):
        cola = ColaPrioridad()
        self.assertEqual(len(cola), 0)
        self.assertTrue(cola.esta_vacia)
        with self.assertRaises(IndexError):
            cola.ver_maximo()
        with self.assertRaises(IndexError):
            cola.extraer_maximo()
        self.assertEqual(cola.mejores(5), [])

    def test_un_elemento(self):
        cola = ColaPrioridad()
        cola.insertar("Matrix", 9.8)
        self.assertEqual(cola.ver_maximo(), ("Matrix", 9.8))
        self.assertEqual(cola.extraer_maximo(), ("Matrix", 9.8))
        self.assertTrue(cola.esta_vacia)

    def test_el_ranking_de_la_consigna(self):
        peliculas = [("Ex Machina", 9.0), ("Matrix", 9.8), ("Blade Runner", 9.2),
                     ("Inception", 9.6), ("Interstellar", 9.5), ("Cars", 7.1)]
        cola = ColaPrioridad()
        for nombre, rating in peliculas:
            cola.insertar(nombre, rating)
        top5 = [nombre for nombre, _ in cola.mejores(5)]
        self.assertEqual(top5, ["Matrix", "Inception", "Interstellar", "Blade Runner", "Ex Machina"])

    def test_extraer_devuelve_de_mayor_a_menor(self):
        cola = ColaPrioridad()
        for valor in [5, 1, 9, 3, 7, 2, 8]:
            cola.insertar(f"x{valor}", valor)
        salida = [cola.extraer_maximo()[1] for _ in range(7)]
        self.assertEqual(salida, [9, 8, 7, 5, 3, 2, 1])

    def test_ver_maximo_no_modifica(self):
        cola = ColaPrioridad()
        for valor in [3, 8, 5]:
            cola.insertar(valor, valor)
        self.assertEqual(cola.ver_maximo(), (8, 8))
        self.assertEqual(len(cola), 3)

    def test_empate_sale_primero_el_que_llego_antes(self):
        cola = ColaPrioridad()
        for nombre in ["a", "b", "c", "d"]:
            cola.insertar(nombre, 10)
        self.assertEqual([cola.extraer_maximo()[0] for _ in range(4)], ["a", "b", "c", "d"])

    def test_el_invariante_se_mantiene_en_cada_paso(self):
        random.seed(1)
        cola = ColaPrioridad()
        for _ in range(300):
            cola.insertar(None, random.randint(1, 100))
            self.assertTrue(cola.cumple_invariante())
        for _ in range(300):
            cola.extraer_maximo()
            self.assertTrue(cola.cumple_invariante())

    def test_el_invariante_detecta_un_heap_roto(self):
        cola = ColaPrioridad()
        for valor in [9, 5, 7]:
            cola.insertar(valor, valor)
        cola._datos[1] = (100, 99, "roto")  # un hijo mayor que la raíz
        self.assertFalse(cola.cumple_invariante())


class TestConstruccionYTopN(unittest.TestCase):

    def test_desde_lista_cumple_invariante_y_ordena(self):
        random.seed(2)
        pares = [(i, random.randint(1, 1000)) for i in range(500)]
        cola = ColaPrioridad.desde_lista(pares)
        self.assertTrue(cola.cumple_invariante())
        self.assertEqual(len(cola), 500)
        salida = [cola.extraer_maximo()[1] for _ in range(500)]
        self.assertEqual(salida, sorted((p for _, p in pares), reverse=True))

    def test_desde_lista_vacia_y_de_uno(self):
        self.assertEqual(len(ColaPrioridad.desde_lista([])), 0)
        cola = ColaPrioridad.desde_lista([("solo", 4)])
        self.assertEqual(cola.extraer_maximo(), ("solo", 4))

    def test_heapify_hace_menos_comparaciones_que_n_inserciones(self):
        random.seed(3)
        pares = [(i, random.random()) for i in range(5000)]
        por_floyd = ColaPrioridad.desde_lista(pares)
        por_inserciones = ColaPrioridad()
        for elem, prio in pares:
            por_inserciones.insertar(elem, prio)
        self.assertLess(por_floyd.comparaciones, por_inserciones.comparaciones)
        # Floyd cuesta menos de ~2n comparaciones por nivel; con n = 5000 sobra margen
        self.assertLess(por_floyd.comparaciones, 2 * 5000 * 2)

    def test_mejores_coincide_con_ordenar_todo(self):
        random.seed(4)
        for _ in range(40):
            n = random.randint(1, 200)
            pares = [(i, random.randint(1, 50)) for i in range(n)]  # muchos empates
            cola = ColaPrioridad.desde_lista(pares)
            esperado = sorted(pares, key=lambda p: p[1], reverse=True)  # orden estable
            for k in (1, 3, 10, n, n + 5):
                self.assertEqual(cola.mejores(k), esperado[:k], f"falló con n={n}, k={k}")

    def test_mejores_no_modifica_el_heap(self):
        cola = ColaPrioridad.desde_lista([(i, i) for i in range(100)])
        antes = list(cola._datos)
        primera = cola.mejores(10)
        segunda = cola.mejores(10)
        self.assertEqual(primera, segunda)
        self.assertEqual(cola._datos, antes)
        self.assertEqual(len(cola), 100)

    def test_mejores_con_n_cero_o_negativo(self):
        cola = ColaPrioridad.desde_lista([(i, i) for i in range(10)])
        self.assertEqual(cola.mejores(0), [])
        self.assertEqual(cola.mejores(-3), [])

    def test_mejores_hace_pocas_comparaciones_aunque_el_heap_sea_enorme(self):
        random.seed(5)
        chico = ColaPrioridad.desde_lista([(i, random.random()) for i in range(1_000)])
        grande = ColaPrioridad.desde_lista([(i, random.random()) for i in range(100_000)])
        chico.mejores(10)
        grande.mejores(10)
        # el costo es O(N log N): no crece con el tamaño del heap
        self.assertLess(grande.comparaciones_ultima_consulta, 200)
        self.assertLess(chico.comparaciones_ultima_consulta, 200)

    def test_insertar_despues_de_construir_mantiene_el_orden(self):
        cola = ColaPrioridad.desde_lista([(i, i) for i in range(50)])
        cola.insertar("nuevo", 1000)
        self.assertEqual(cola.mejores(1), [("nuevo", 1000)])
        self.assertTrue(cola.cumple_invariante())


def _cancion(id_, titulo="T", artista="A", genero="pop", anio=2020, pop=50):
    return Cancion(id_, f"{titulo}{id_}", artista, genero, anio, pop)


class TestCriterioPrioridad(unittest.TestCase):

    def test_popularidad_pura(self):
        c = CriterioPrioridad.popularidad()
        self.assertEqual(c.puntaje(_cancion(1, pop=87, anio=1970)), 87)

    def test_novedad_en_los_extremos(self):
        self.assertEqual(CriterioPrioridad.novedad(1960), 0)
        self.assertEqual(CriterioPrioridad.novedad(2026), 100)
        self.assertEqual(CriterioPrioridad.novedad(1900), 0)    # se recorta
        self.assertEqual(CriterioPrioridad.novedad(2100), 100)  # se recorta

    def test_equilibrado_combina_los_dos_factores(self):
        c = CriterioPrioridad.equilibrado()
        cancion = _cancion(1, pop=80, anio=2026)  # novedad 100
        self.assertAlmostEqual(c.puntaje(cancion), 0.7 * 80 + 0.3 * 100)

    def test_el_criterio_cambia_el_orden(self):
        vieja_popular = _cancion(1, pop=99, anio=1975)
        nueva_menos_popular = _cancion(2, pop=85, anio=2025)
        pop = CriterioPrioridad.popularidad()
        nov = CriterioPrioridad.novedades()
        self.assertGreater(pop(vieja_popular), pop(nueva_menos_popular))
        self.assertGreater(nov(nueva_menos_popular), nov(vieja_popular))

    def test_bono_de_genero_preferido(self):
        c = CriterioPrioridad.popularidad(genero_preferido="K-Pop")
        kpop = _cancion(1, genero="k-pop", pop=80)
        rock = _cancion(2, genero="rock", pop=80)
        self.assertEqual(c.puntaje(kpop), 90)
        self.assertEqual(c.puntaje(rock), 80)

    def test_los_pesos_no_necesitan_sumar_uno(self):
        a = CriterioPrioridad(7, 3)
        b = CriterioPrioridad(0.7, 0.3)
        cancion = _cancion(1, pop=60, anio=2000)
        self.assertAlmostEqual(a.puntaje(cancion), b.puntaje(cancion))

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            CriterioPrioridad(-1, 1)
        with self.assertRaises(ValueError):
            CriterioPrioridad(0, 0)
        with self.assertRaises(ValueError):
            CriterioPrioridad(1, 1, bono_genero=-5)

    def test_igualdad_y_hash(self):
        self.assertEqual(CriterioPrioridad.equilibrado("pop"), CriterioPrioridad(0.7, 0.3, "POP"))
        self.assertNotEqual(CriterioPrioridad.equilibrado(), CriterioPrioridad.novedades())
        self.assertEqual(len({CriterioPrioridad.popularidad(), CriterioPrioridad.popularidad()}), 1)


class TestIntegracionConCatalogo(unittest.TestCase):

    def setUp(self):
        self.cat = CatalogoMusical()
        self.cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
        self.cat.cargar_categorias_desde_json(os.path.join(CARPETA, "datos", "categorias.json"))

    def _esperado(self, criterio, n):
        # referencia: ordenar todo el catálogo (lo que el heap evita hacer)
        orden = sorted(self.cat.listar(), key=criterio.puntaje, reverse=True)
        return orden[:n]

    def test_top_n_coincide_con_ordenar_todo(self):
        esperado = sorted(self.cat.listar(), key=lambda c: c.popularidad, reverse=True)[:10]
        self.assertEqual(self.cat.top_n(10), esperado)

    def test_ranking_coincide_con_ordenar_todo_para_cada_criterio(self):
        criterios = [CriterioPrioridad.popularidad(), CriterioPrioridad.equilibrado(),
                     CriterioPrioridad.novedades(), CriterioPrioridad.equilibrado("k-pop")]
        for crit in criterios:
            for n in (1, 5, 15, 40):
                obtenido = [c for c, _ in self.cat.ranking(n, crit)]
                self.assertEqual(obtenido, self._esperado(crit, n), f"{crit} n={n}")

    def test_ranking_devuelve_el_puntaje(self):
        crit = CriterioPrioridad.equilibrado()
        for cancion, puntaje in self.cat.ranking(5, crit):
            self.assertAlmostEqual(puntaje, crit.puntaje(cancion))

    def test_el_genero_preferido_mueve_el_ranking(self):
        sin_bono = [c.genero for c, _ in self.cat.ranking(5, CriterioPrioridad.popularidad())]
        con_bono = [c.genero for c, _ in self.cat.ranking(5, CriterioPrioridad(1, 0, "folk", bono_genero=30))]
        self.assertNotIn("folk", sin_bono)
        self.assertIn("folk", con_bono)

    def test_agregar_cancion_actualiza_el_ranking(self):
        self.cat.ranking(5)  # construye y guarda el heap del criterio por defecto
        nueva = Cancion(self.cat.siguiente_id(), "Nueva Cumbre", "Artista Nuevo", "pop", 2026, 100)
        self.cat.agregar_cancion(nueva)
        self.assertEqual(self.cat.ranking(1)[0][0].titulo, "Nueva Cumbre")
        self.assertEqual(len(self.cat), 16)

    def test_agregar_cancion_actualiza_todos_los_heaps_guardados(self):
        crit_a, crit_b = CriterioPrioridad.popularidad(), CriterioPrioridad.novedades()
        self.cat.ranking(3, crit_a)
        self.cat.ranking(3, crit_b)
        nueva = Cancion(self.cat.siguiente_id(), "Nueva Cumbre", "Artista Nuevo", "pop", 2026, 100)
        self.cat.agregar_cancion(nueva)
        for crit in (crit_a, crit_b):
            obtenido = [c for c, _ in self.cat.ranking(15, crit)]
            self.assertEqual(obtenido, self._esperado(crit, 15))

    def test_agregar_cancion_tambien_actualiza_arbol_y_categorias(self):
        nueva = Cancion(self.cat.siguiente_id(), "Nueva Cumbre", "Artista Nuevo", "pop", 2026, 100)
        self.cat.agregar_cancion(nueva)
        self.assertIsNotNone(self.cat.buscar_titulo_exacto("Nueva Cumbre"))
        self.assertEqual(self.cat.ruta_categoria_de(nueva),
                         "Música > Pop y derivados > Pop > Artista Nuevo")

    def test_agregar_cancion_rechaza_id_o_titulo_repetidos(self):
        with self.assertRaises(ValueError):
            self.cat.agregar_cancion(Cancion(1, "Otro Titulo", "X", "pop", 2020, 50))
        with self.assertRaises(ValueError):
            self.cat.agregar_cancion(Cancion(99, "Dynamite", "X", "pop", 2020, 50))
        self.assertEqual(len(self.cat), 15)

    def test_recargar_datos_descarta_los_heaps_viejos(self):
        self.cat.ranking(5)
        self.cat.cargar_desde_lista([_cancion(1, pop=10), _cancion(2, pop=20)])
        self.assertEqual([c.id for c, _ in self.cat.ranking(5)], [2, 1])

    def test_ranking_de_catalogo_vacio(self):
        vacio = CatalogoMusical()
        vacio.cargar_desde_lista([])
        self.assertEqual(vacio.ranking(5), [])
        self.assertEqual(vacio.top_n(10), [])


if __name__ == "__main__":
    unittest.main()
