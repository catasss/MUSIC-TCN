"""
grafo.py
Grafo NO dirigido y NO pesado, implementado a mano con LISTA DE ADYACENCIA
(sin librerías externas de grafos).

En MUSICTCN v6 se utiliza para explorar las relaciones entre artistas (vértice = artista;
arista = comparten al menos un género musical).

Complejidad (V = vértices, E = aristas):
    - BFS (Breadth-First Search): O(V + E)
    - DFS (Depth-First Search): O(V + E)
"""

from typing import Any, Dict, Hashable, List, Optional, Tuple, Set


class Grafo:
    """Grafo no dirigido y sin pesos, con lista de adyacencia."""

    def __init__(self):
        self._adyacencia: Dict[Hashable, List[Hashable]] = {}

    def agregar_vertice(self, vertice: Hashable):
        """Agrega un vértice (si ya estaba, no hace nada). O(1)."""
        self._adyacencia.setdefault(vertice, [])

    def agregar_arista(self, a: Hashable, b: Hashable):
        """Conecta a con b (crea los vértices si no existen). O(grado)."""
        if a == b:
            return
        self.agregar_vertice(a)
        self.agregar_vertice(b)
        if b not in self._adyacencia[a]:
            self._adyacencia[a].append(b)
            self._adyacencia[b].append(a)

    def _verificar(self, vertice: Hashable):
        if vertice not in self._adyacencia:
            raise KeyError(f"El vértice {vertice!r} no existe en el grafo")

    def tiene_vertice(self, vertice: Hashable) -> bool:
        return vertice in self._adyacencia

    def vecinos(self, vertice: Hashable) -> List[Hashable]:
        self._verificar(vertice)
        return list(self._adyacencia[vertice])

    def vertices(self) -> List[Hashable]:
        return list(self._adyacencia)

    # ------------------------------------------------------------------
    # Entregables TP 8: Recorridos BFS y DFS
    # ------------------------------------------------------------------

    def bfs(self, origen: Hashable) -> List[Hashable]:
        """
        Recorrido en ANCHURA (BFS).
        Explora nivel por nivel desde el origen (primero vecinos directos a salto 1, 
        luego a salto 2, etc.). Utiliza una COLA (FIFO).

        Uso real: Encontrar el artista más cercano o el camino con menor número de saltos.
        Complejidad: O(V + E) en tiempo, O(V) en memoria.
        """
        self._verificar(origen)
        visitados: Set[Hashable] = {origen}
        orden: List[Hashable] = []
        cola: List[Hashable] = [origen]
        i = 0  # Índice para pop(0) en O(1)

        while i < len(cola):
            actual = cola[i]
            i += 1
            orden.append(actual)

            for vecino in self._adyacencia[actual]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)

        return orden

    def dfs(self, origen: Hashable) -> List[Hashable]:
        """
        Recorrido en PROFUNDIDAD (DFS).
        Explora lo más profundo posible a lo largo de cada rama antes de retroceder (backtracking).
        Utiliza una PILA (LIFO) explícita.

        Uso real: Exploración exhaustiva de una comunidad/red de artistas completa.
        Complejidad: O(V + E) en tiempo, O(V) en memoria.
        """
        self._verificar(origen)
        visitados: Set[Hashable] = set()
        orden: List[Hashable] = []
        pila: List[Hashable] = [origen]

        while pila:
            actual = pila.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            orden.append(actual)

            # Invertimos la lista de vecinos para mantener un orden intuitivo de visita
            for vecino in reversed(self._adyacencia[actual]):
                if vecino not in visitados:
                    pila.append(vecino)

        return orden

    def camino_mas_corto(self, origen: Hashable, destino: Hashable) -> Optional[List[Hashable]]:
        """Devuelve el camino más corto en aristas usando BFS. O(V + E)."""
        self._verificar(origen)
        self._verificar(destino)
        if origen == destino:
            return [origen]

        padre = {origen: None}
        cola = [origen]
        i = 0

        while i < len(cola):
            actual = cola[i]
            i += 1
            for vecino in self._adyacencia[actual]:
                if vecino not in padre:
                    padre[vecino] = actual
                    if vecino == destino:
                        camino = [destino]
                        while padre[camino[-1]] is not None:
                            camino.append(padre[camino[-1]])
                        camino.reverse()
                        return camino
                    cola.append(vecino)
        return None
