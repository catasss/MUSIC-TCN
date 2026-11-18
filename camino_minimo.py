"""
camino_minimo.py  (TP09 - Optimización, versión 7)

Camino mínimo ponderado con DIJKSTRA sobre el grafo de artistas.

Se extiende Grafo (no se toca grafo.py): GrafoPonderado guarda además un
peso por arista. El peso representa la "distancia" entre dos artistas
(menor peso = más parecidos). La cola de prioridad es un min-heap escrito
a mano, igual que en el resto del proyecto (sin heapq).

Complejidad: O((V + E) log V) con heap binario.
"""
from typing import Callable, Dict, Hashable, List, Optional, Tuple

from grafo import Grafo


class _MinHeap:
    """Min-heap binario a mano sobre una lista de (prioridad, desempate, valor)."""

    def __init__(self):
        self._d: List[Tuple[float, int, Hashable]] = []
        self._n = 0  # desempate: evita comparar vértices entre sí

    def __len__(self):
        return len(self._d)

    def push(self, prioridad: float, valor: Hashable):
        self._d.append((prioridad, self._n, valor))
        self._n += 1
        i = len(self._d) - 1
        while i > 0:                       # subir
            p = (i - 1) // 2
            if self._d[i][:2] >= self._d[p][:2]:
                break
            self._d[i], self._d[p] = self._d[p], self._d[i]
            i = p

    def pop(self) -> Tuple[float, Hashable]:
        d = self._d
        d[0], d[-1] = d[-1], d[0]
        prioridad, _, valor = d.pop()
        i = 0
        while True:                        # bajar
            h, m = 2 * i + 1, i
            if h < len(d) and d[h][:2] < d[m][:2]:
                m = h
            if h + 1 < len(d) and d[h + 1][:2] < d[m][:2]:
                m = h + 1
            if m == i:
                break
            d[i], d[m] = d[m], d[i]
            i = m
        return prioridad, valor


class GrafoPonderado(Grafo):
    """Grafo no dirigido con peso positivo en cada arista."""

    def __init__(self):
        super().__init__()
        self._pesos: Dict[frozenset, float] = {}

    def agregar_arista(self, a: Hashable, b: Hashable, peso: float = 1.0):
        if peso < 0:
            raise ValueError("Dijkstra no admite pesos negativos")
        super().agregar_arista(a, b)
        if a != b:
            self._pesos[frozenset((a, b))] = peso

    def peso(self, a: Hashable, b: Hashable) -> float:
        return self._pesos[frozenset((a, b))]

    @classmethod
    def desde_grafo(cls, grafo: Grafo,
                    funcion_peso: Callable[[Hashable, Hashable], float] = lambda a, b: 1.0
                    ) -> "GrafoPonderado":
        """Copia un Grafo existente asignando peso = funcion_peso(a, b)."""
        g = cls()
        for v in grafo.vertices():
            g.agregar_vertice(v)
        for a, b in grafo.aristas():
            g.agregar_arista(a, b, funcion_peso(a, b))
        return g

    def dijkstra(self, origen: Hashable) -> Tuple[Dict[Hashable, float], Dict[Hashable, Optional[Hashable]]]:
        """Distancia mínima del origen a cada vértice alcanzable y el padre
        de cada uno en el árbol de caminos mínimos. O((V + E) log V)."""
        self._verificar(origen)
        dist = {origen: 0.0}
        padre: Dict[Hashable, Optional[Hashable]] = {origen: None}
        hecho = set()
        cola = _MinHeap()
        cola.push(0.0, origen)
        while len(cola):
            d, actual = cola.pop()
            if actual in hecho:            # entrada vieja del heap
                continue
            hecho.add(actual)
            for vecino in self._adyacencia[actual]:
                nueva = d + self.peso(actual, vecino)
                if vecino not in dist or nueva < dist[vecino]:
                    dist[vecino] = nueva
                    padre[vecino] = actual
                    cola.push(nueva, vecino)
        return dist, padre

    def camino_minimo(self, origen: Hashable, destino: Hashable
                      ) -> Optional[Tuple[List[Hashable], float]]:
        """([origen, ..., destino], costo total) o None si no hay camino."""
        self._verificar(destino)
        dist, padre = self.dijkstra(origen)
        if destino not in dist:
            return None
        camino = [destino]
        while padre[camino[-1]] is not None:
            camino.append(padre[camino[-1]])
        camino.reverse()
        return camino, dist[destino]


if __name__ == "__main__":
    # Prueba rápida: el camino directo A-D cuesta 10, pero A-B-C-D cuesta 4.
    g = GrafoPonderado()
    g.agregar_arista("A", "B", 1)
    g.agregar_arista("B", "C", 1)
    g.agregar_arista("C", "D", 2)
    g.agregar_arista("A", "D", 10)
    g.agregar_vertice("Aislado")
    print(g.camino_minimo("A", "D"))          # (['A','B','C','D'], 4.0)
    print(g.camino_minimo("A", "Aislado"))    # None
    # Con pesos 1 coincide con BFS:
    h = GrafoPonderado.desde_grafo(g)
    print(h.camino_minimo("A", "D"))          # (['A','D'], 1.0)
    print(g.camino_mas_corto("A", "D"))       # ['A','D']  (BFS, en saltos)
