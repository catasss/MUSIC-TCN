"""
comparacion_arbol_vs_secuencial.py
Compara, sobre la MISMA operación (buscar una canción por título exacto),
dos estrategias:
    1) Búsqueda secuencial: recorrer la lista de canciones una por una
       (la misma idea que ya se usó en el TP2 para "filtrar_canciones").
    2) Búsqueda con ArbolCanciones (BST): descender por el árbol.

Uso:
    python3 comparacion_arbol_vs_secuencial.py
"""

import csv
import random
import time

from modelos import Cancion
from arbol_canciones import ArbolCanciones

TAMANOS = [100, 1_000, 10_000, 100_000]
BUSQUEDAS_POR_TAMANO = 200
PROPORCION_INEXISTENTES = 0.5  # la mitad de las búsquedas son de títulos que no están


def busqueda_secuencial(canciones, titulo):
    """La misma estrategia 'de línea base' usada en el TP2: recorrer todo
    hasta encontrar el título o llegar al final. O(n)."""
    for cancion in canciones:
        if cancion.titulo == titulo:
            return cancion
    return None


def generar_catalogo(n):
    canciones = []
    for i in range(n):
        canciones.append(Cancion(
            id_cancion=i,
            titulo=f"Cancion {i:07d}",
            artista=f"Artista {i % 500}",
            genero=random.choice(["k-pop", "rap", "rock", "pop", "folk"]),
            anio=random.randint(1960, 2026),
            popularidad=random.randint(1, 100),
        ))
    return canciones


def generar_titulos_a_buscar(canciones, cantidad, proporcion_inexistentes):
    n_inexistentes = int(cantidad * proporcion_inexistentes)
    n_existentes = cantidad - n_inexistentes
    existentes = [c.titulo for c in random.sample(canciones, min(n_existentes, len(canciones)))]
    inexistentes = [f"Titulo Inexistente {i}" for i in range(n_inexistentes)]
    titulos = existentes + inexistentes
    random.shuffle(titulos)
    return titulos


def medir(func, *args):
    inicio = time.perf_counter()
    func(*args)
    return time.perf_counter() - inicio


def correr():
    resultados = []
    for n in TAMANOS:
        print(f"Probando con n = {n} canciones...")
        canciones = generar_catalogo(n)
        titulos = generar_titulos_a_buscar(canciones, BUSQUEDAS_POR_TAMANO, PROPORCION_INEXISTENTES)

        # --- Estrategia 1: secuencial ---
        tiempos_seq = [medir(busqueda_secuencial, canciones, t) for t in titulos]
        prom_seq_ms = (sum(tiempos_seq) / len(tiempos_seq)) * 1000

        # --- Estrategia 2: árbol (construcción + búsquedas) ---
        inicio = time.perf_counter()
        arbol = ArbolCanciones.construir_balanceado(canciones)
        construccion_ms = (time.perf_counter() - inicio) * 1000

        tiempos_arbol = [medir(arbol.buscar, t) for t in titulos]
        prom_arbol_ms = (sum(tiempos_arbol) / len(tiempos_arbol)) * 1000

        resultados.append({
            "n_elementos": n,
            "secuencial_ms": round(prom_seq_ms, 4),
            "arbol_ms": round(prom_arbol_ms, 4),
            "construccion_arbol_ms": round(construccion_ms, 2),
            "speedup": round(prom_seq_ms / prom_arbol_ms, 1) if prom_arbol_ms > 0 else None,
        })
    return resultados


def guardar_csv(resultados, ruta="resultados_arbol_vs_secuencial.csv"):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
        writer.writeheader()
        writer.writerows(resultados)


def imprimir_tabla(resultados):
    print("\n" + "=" * 90)
    print(f"{'N':>10} | {'Secuencial (ms)':>16} | {'Árbol (ms)':>12} | {'Construcción (ms)':>18} | {'Speedup':>8}")
    print("-" * 90)
    for r in resultados:
        print(f"{r['n_elementos']:>10} | {r['secuencial_ms']:>16} | {r['arbol_ms']:>12} | "
              f"{r['construccion_arbol_ms']:>18} | {r['speedup']:>8}")
    print("=" * 90)


if __name__ == "__main__":
    random.seed(42)
    resultados = correr()
    imprimir_tabla(resultados)
    guardar_csv(resultados)
    print("\nResultados guardados en resultados_arbol_vs_secuencial.csv")
