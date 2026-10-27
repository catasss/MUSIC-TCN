"""
comparacion_heap_vs_sort.py
Compara dos formas de obtener el Top-N de un ranking:

    A) ORDENAR TODO: calcular la prioridad de todas las canciones, ordenar
       la lista completa y quedarse con las primeras N. O(n log n) en cada
       consulta.
    B) HEAP: construir el heap (O(n)) y pedirle las N mejores
       (O(N log N)). Si el heap ya está construido y solo entran canciones
       nuevas, cada inserción cuesta O(log n).

Se miden dos escenarios:
    1) Consulta única: el catálogo recién cargado, un solo Top-N.
    2) Ranking dinámico: entra una canción nueva y se vuelve a pedir el
       Top-N, muchas veces seguidas (lo que pasa en la app con la opción
       "Agregar canción").

Además del tiempo se cuenta la cantidad de comparaciones, que mide el
costo del algoritmo sin depender de la velocidad de la máquina. OJO con
los tiempos: sorted() de Python está escrito en C y el heap de este
proyecto en Python puro, así que el tiempo favorece a sorted() más de lo
que lo haría con implementaciones equivalentes.

Uso:
    python3 comparacion_heap_vs_sort.py
"""

import csv
import random
import time
from functools import cmp_to_key

from heap_prioridad import ColaPrioridad
from modelos import Cancion
from prioridad import CriterioPrioridad

TAMANOS = [1_000, 10_000, 100_000]
TOP_N = 10
RONDAS_DINAMICAS = 50          # canciones nuevas + consulta, por tamaño
REPETICIONES_UNICA = 5          # se promedia la consulta única
CRITERIO = CriterioPrioridad.equilibrado()


def generar_catalogo(n, desde_id=0):
    return [Cancion(desde_id + i, f"Cancion {desde_id + i}", f"Artista {i % 500}",
                    random.choice(["k-pop", "rap", "rock", "pop", "folk"]),
                    random.randint(1960, 2026), random.randint(1, 100))
            for i in range(n)]


# ---------------------------------------------------------------------------
# Estrategia A: ordenar todo
# ---------------------------------------------------------------------------
def top_n_ordenando(canciones, n, criterio):
    return sorted(canciones, key=criterio.puntaje, reverse=True)[:n]


def comparaciones_al_ordenar(canciones, criterio):
    """Cuenta las comparaciones que hace sorted() sobre la lista completa."""
    contador = [0]
    puntajes = {c.id: criterio.puntaje(c) for c in canciones}

    def comparar(a, b):
        contador[0] += 1
        return puntajes[b.id] - puntajes[a.id]

    sorted(canciones, key=cmp_to_key(comparar))
    return contador[0]


# ---------------------------------------------------------------------------
# Estrategia B: heap
# ---------------------------------------------------------------------------
def construir_heap(canciones, criterio):
    return ColaPrioridad.desde_lista((c, criterio.puntaje(c)) for c in canciones)


def medir(funcion):
    inicio = time.perf_counter()
    resultado = funcion()
    return resultado, (time.perf_counter() - inicio) * 1000


def correr():
    filas = []
    for n in TAMANOS:
        print(f"Probando con n = {n} canciones...")
        random.seed(n)
        catalogo = generar_catalogo(n)

        # ---------------- Escenario 1: consulta única ----------------
        tiempos_sort = [medir(lambda: top_n_ordenando(catalogo, TOP_N, CRITERIO))[1]
                        for _ in range(REPETICIONES_UNICA)]
        t_sort = sum(tiempos_sort) / len(tiempos_sort)

        t_build, t_query = [], []
        for _ in range(REPETICIONES_UNICA):
            heap, tb = medir(lambda: construir_heap(catalogo, CRITERIO))
            _, tq = medir(lambda: heap.mejores(TOP_N))
            t_build.append(tb)
            t_query.append(tq)
        t_heap_build = sum(t_build) / len(t_build)
        t_heap_query = sum(t_query) / len(t_query)

        comps_sort = comparaciones_al_ordenar(catalogo, CRITERIO)
        heap = construir_heap(catalogo, CRITERIO)
        comps_build = heap.comparaciones
        heap.mejores(TOP_N)
        comps_query = heap.comparaciones_ultima_consulta

        # ---------------- Escenario 2: ranking dinámico ----------------
        nuevas = generar_catalogo(RONDAS_DINAMICAS, desde_id=n)

        lista = list(catalogo)
        inicio = time.perf_counter()
        for cancion in nuevas:
            lista.append(cancion)
            top_n_ordenando(lista, TOP_N, CRITERIO)
        t_dyn_sort = (time.perf_counter() - inicio) * 1000 / RONDAS_DINAMICAS

        heap = construir_heap(catalogo, CRITERIO)
        inicio = time.perf_counter()
        for cancion in nuevas:
            heap.insertar(cancion, CRITERIO.puntaje(cancion))
            heap.mejores(TOP_N)
        t_dyn_heap = (time.perf_counter() - inicio) * 1000 / RONDAS_DINAMICAS

        # verificación: las dos estrategias deben dar el mismo Top-N
        assert [c.id for c in top_n_ordenando(lista, TOP_N, CRITERIO)] == \
               [c.id for c, _ in heap.mejores(TOP_N)], "los Top-N no coinciden"

        filas.append({
            "n": n,
            "unica_sort_ms": round(t_sort, 2),
            "unica_heap_construccion_ms": round(t_heap_build, 2),
            "unica_heap_consulta_ms": round(t_heap_query, 4),
            "comparaciones_sort": comps_sort,
            "comparaciones_heap_construccion": comps_build,
            "comparaciones_heap_consulta": comps_query,
            "dinamico_sort_ms_por_ronda": round(t_dyn_sort, 2),
            "dinamico_heap_ms_por_ronda": round(t_dyn_heap, 4),
            "dinamico_speedup": round(t_dyn_sort / t_dyn_heap, 1),
        })
    return filas


def imprimir(filas):
    print("\n=== Escenario 1: consulta única (Top-%d) ===" % TOP_N)
    print(f"{'n':>8} | {'Ordenar (ms)':>13} | {'Heap: build (ms)':>17} | {'Heap: consulta (ms)':>20}")
    for f in filas:
        print(f"{f['n']:>8} | {f['unica_sort_ms']:>13} | {f['unica_heap_construccion_ms']:>17} | "
              f"{f['unica_heap_consulta_ms']:>20}")

    print("\n=== Comparaciones realizadas ===")
    print(f"{'n':>8} | {'Ordenar todo':>13} | {'Heap: build':>12} | {'Heap: Top-%d' % TOP_N:>12}")
    for f in filas:
        print(f"{f['n']:>8} | {f['comparaciones_sort']:>13} | "
              f"{f['comparaciones_heap_construccion']:>12} | {f['comparaciones_heap_consulta']:>12}")

    print("\n=== Escenario 2: ranking dinámico (canción nueva + Top-%d, por ronda) ===" % TOP_N)
    print(f"{'n':>8} | {'Ordenar (ms)':>13} | {'Heap (ms)':>10} | {'Speedup':>8}")
    for f in filas:
        print(f"{f['n']:>8} | {f['dinamico_sort_ms_por_ronda']:>13} | "
              f"{f['dinamico_heap_ms_por_ronda']:>10} | {f['dinamico_speedup']:>7}x")


if __name__ == "__main__":
    filas = correr()
    imprimir(filas)
    with open("resultados_heap_vs_sort.csv", "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)
    print("\nResultados guardados en resultados_heap_vs_sort.csv")
