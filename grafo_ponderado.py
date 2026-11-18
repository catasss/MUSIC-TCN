"""
grafo_ponderado.py  (Objetivo 9: Optimización - camino mínimo)

GrafoPonderado extiende el Grafo de grafo.py (no dirigido, lista de adyacencia)
agregándole un COSTO a cada arista, y suma el algoritmo de Dijkstra.

Costo en MUSICTCN
-----------------
Vértice = artista. Arista = dos artistas comparten género (igual que en v5).
Costo de la arista = 1 + ((pop_A - pop_B) / 10) ** 2, donde pop es la
popularidad media del artista (0-100).
  * El "1" es el costo base de dar un paso.
  * El término cuadrático penaliza los saltos grandes de popularidad:
    pasar de un artista masivo a uno casi desconocido "cuesta" más que ir
    escalonado por artistas intermedios. Por eso el camino de menor costo
    NO siempre es el de menos saltos (que sería el BFS).
  * Nunca es negativo (mínimo 1), condición necesaria para Dijkstra.

Por qué Dijkstra
----------------
  * Hay pesos, así que BFS (que cuenta aristas) ya no sirve.
  * Todos los pesos son >= 0, así que Dijkstra es correcto.
    (Bellman-Ford solo haría falta con pesos negativos.)
  * El grafo es ralo (pocas aristas respecto de V^2), así que conviene lista
    de adyacencia + heap en vez de matriz y búsqueda lineal.

Complejidad (V vértices, E aristas)
    construir el grafo         O(V + suma de k^2 por género)
    dijkstra (con heap)        O((V + E) log V)
    camino_minimo              O((V + E) log V)
    Con un arreglo en lugar del heap sería O(V^2).
"""

from typing import Callable, Dict, Hashable, Iterable, List, Optional, Tuple

from grafo import Grafo
from heap_prioridad import ColaPrioridad


class GrafoPonderado(Grafo):
    """Grafo no dirigido con costos no negativos en las aristas."""

    def __init__(self):
        super().__init__()
        self._pesos: Dict[frozenset, float] = {}

    def agregar_arista(self, a: Hashable, b: Hashable, peso: float = 1.0):
        """Conecta a con b con el costo dado (>= 0). O(g)."""
        if peso < 0:
            raise ValueError("Dijkstra no admite costos negativos")
        if a == b:
            return
        super().agregar_arista(a, b)
        self._pesos[frozenset((a, b))] = peso

    def peso(self, a: Hashable, b: Hashable) -> float:
        """Costo de la arista a-b. O(1)."""
        clave = frozenset((a, b))
        if clave not in self._pesos:
            raise KeyError(f"No existe la arista {a!r} - {b!r}")
        return self._pesos[clave]

    def dijkstra(self, origen: Hashable, destino: Optional[Hashable] = None
                 ) -> Tuple[Dict[Hashable, float], Dict[Hashable, Optional[Hashable]]]:
        """Costo mínimo desde el origen hacia los demás vértices.

        Devuelve (distancia, padre). Si se da destino, corta apenas queda
        fijado su costo. O((V + E) log V).

        La ColaPrioridad del proyecto es un heap MÁXIMO; para obtener el de
        MENOR costo se guarda la prioridad negada (-costo).
        Los costos viejos que quedan en el heap se descartan al sacarlos
        ("eliminación perezosa"): si el vértice ya está definitivo, se saltea.
        """
        self._verificar(origen)
        distancia = {origen: 0.0}
        padre = {origen: None}
        definitivos = set()
        cola = ColaPrioridad()
        cola.insertar(origen, 0.0)
        while not cola.esta_vacia:
            actual, _ = cola.extraer_maximo()
            if actual in definitivos:
                continue
            definitivos.add(actual)
            if destino is not None and actual == destino:
                break
            for vecino in self._adyacencia[actual]:
                if vecino in definitivos:
                    continue
                nuevo = distancia[actual] + self._pesos[frozenset((actual, vecino))]
                if vecino not in distancia or nuevo < distancia[vecino]:
                    distancia[vecino] = nuevo
                    padre[vecino] = actual
                    cola.insertar(vecino, -nuevo)
        return distancia, padre

    def camino_minimo(self, origen: Hashable, destino: Hashable
                      ) -> Optional[Tuple[List[Hashable], float]]:
        """Camino de menor costo como ([origen, ..., destino], costo_total);
        None si no hay camino. O((V + E) log V)."""
        self._verificar(origen)
        self._verificar(destino)
        distancia, padre = self.dijkstra(origen, destino)
        if destino not in distancia:
            return None
        camino = [destino]
        while padre[camino[-1]] is not None:
            camino.append(padre[camino[-1]])
        camino.reverse()
        return camino, distancia[destino]

    def costo_de(self, camino: List[Hashable]) -> float:
        """Suma de los costos de un camino dado (para comparar con BFS)."""
        return sum(self.peso(a, b) for a, b in zip(camino, camino[1:]))


def costo_por_popularidad(pop_a: float, pop_b: float) -> float:
    """Costo de pasar de un artista a otro: 1 + (diferencia de popularidad / 10)^2."""
    return 1 + ((pop_a - pop_b) / 10) ** 2


def construir_grafo_artistas(generos_por_artista: Dict[str, Iterable[str]],
                             popularidad_por_artista: Dict[str, float],
                             costo: Callable[[float, float], float] = costo_por_popularidad
                             ) -> GrafoPonderado:
    """Arma el grafo ponderado de artistas: dos artistas se conectan si
    comparten al menos un género; el costo sale de su popularidad media."""
    grafo = GrafoPonderado()
    por_genero: Dict[str, List[str]] = {}
    for artista, generos in generos_por_artista.items():
        grafo.agregar_vertice(artista)
        for genero in generos:
            por_genero.setdefault(genero, []).append(artista)
    for artistas in por_genero.values():
        for i in range(len(artistas)):
            for j in range(i + 1, len(artistas)):
                a, b = artistas[i], artistas[j]
                grafo.agregar_arista(a, b, costo(popularidad_por_artista[a],
                                                 popularidad_por_artista[b]))
    return grafo
