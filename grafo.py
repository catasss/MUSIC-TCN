"""
grafo.py
Grafo NO dirigido y NO pesado, implementado a mano con LISTA DE ADYACENCIA
(sin librerías de grafos).

En MUSICTCN se usa para conectar artistas (vértice = artista; arista = dos
artistas comparten género), pero la clase es genérica: sirve con cualquier
valor hashable como vértice.

Representación: un diccionario {vértice: [vecinos]}. Cada arista A-B se
guarda dos veces (B en la lista de A y A en la lista de B), porque el grafo
no es dirigido.

Complejidad (V = vértices, E = aristas, g = grado del vértice):
    agregar_vertice            O(1)
    agregar_arista             O(g)     (revisa que no esté repetida)
    tiene_arista, vecinos      O(g)
    grado                      O(1)
    recorridos BFS / DFS       O(V + E)
    camino_mas_corto           O(V + E)
    componentes_conexas        O(V + E)
    memoria                    O(V + E)  (una matriz de adyacencia usaría O(V²))
"""

from typing import Any, Dict, Hashable, List, Optional, Tuple


class Grafo:
    """Grafo no dirigido y sin pesos, con lista de adyacencia."""

    def __init__(self):
        self._adyacencia: Dict[Hashable, List[Hashable]] = {}

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    def agregar_vertice(self, vertice: Hashable):
        """Agrega un vértice (si ya estaba, no hace nada). O(1)."""
        self._adyacencia.setdefault(vertice, [])

    def agregar_arista(self, a: Hashable, b: Hashable):
        """Conecta a con b (crea los vértices si no existen).

        Se ignoran los lazos (a con sí mismo) y las aristas repetidas.
        """
        if a == b:
            return
        self.agregar_vertice(a)
        self.agregar_vertice(b)
        if b not in self._adyacencia[a]:
            self._adyacencia[a].append(b)
            self._adyacencia[b].append(a)

    # ------------------------------------------------------------------
    # Consultas básicas
    # ------------------------------------------------------------------
    def _verificar(self, vertice: Hashable):
        if vertice not in self._adyacencia:
            raise KeyError(f"El vértice {vertice!r} no existe en el grafo")

    def tiene_vertice(self, vertice: Hashable) -> bool:
        return vertice in self._adyacencia

    def tiene_arista(self, a: Hashable, b: Hashable) -> bool:
        return a in self._adyacencia and b in self._adyacencia[a]

    def vecinos(self, vertice: Hashable) -> List[Hashable]:
        """Vértices conectados directamente con el dado (copia de la lista)."""
        self._verificar(vertice)
        return list(self._adyacencia[vertice])

    def grado(self, vertice: Hashable) -> int:
        """Cantidad de vecinos."""
        self._verificar(vertice)
        return len(self._adyacencia[vertice])

    def vertices(self) -> List[Hashable]:
        return list(self._adyacencia)

    def aristas(self) -> List[Tuple[Hashable, Hashable]]:
        """Cada arista una sola vez, como par (a, b)."""
        posicion = {v: i for i, v in enumerate(self._adyacencia)}
        return [(a, b) for a, vecinos in self._adyacencia.items()
                for b in vecinos if posicion[a] < posicion[b]]

    def cantidad_vertices(self) -> int:
        return len(self._adyacencia)

    def cantidad_aristas(self) -> int:
        return sum(len(v) for v in self._adyacencia.values()) // 2

    def densidad(self) -> float:
        """Aristas presentes / aristas posibles: 2E / (V·(V-1)). Va de 0 a 1."""
        v = self.cantidad_vertices()
        if v < 2:
            return 0.0
        return 2 * self.cantidad_aristas() / (v * (v - 1))

    def __len__(self) -> int:
        return len(self._adyacencia)

    def __contains__(self, vertice: Hashable) -> bool:
        return vertice in self._adyacencia

    # ------------------------------------------------------------------
    # Recorridos
    # ------------------------------------------------------------------
    def bfs(self, origen: Hashable) -> List[Hashable]:
        """Recorrido en ANCHURA: primero el origen, después sus vecinos,
        después los vecinos de los vecinos, etc. Devuelve el orden de visita.
        O(V + E)."""
        return list(self.distancias(origen))

    def dfs(self, origen: Hashable) -> List[Hashable]:
        """Recorrido en PROFUNDIDAD: se sigue un camino hasta el fondo antes
        de volver atrás. Devuelve el orden de visita. O(V + E)."""
        self._verificar(origen)
        visitados = set()
        orden = []
        pila = [origen]
        while pila:
            actual = pila.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            orden.append(actual)
            # se apilan al revés para visitar primero al primer vecino
            for vecino in reversed(self._adyacencia[actual]):
                if vecino not in visitados:
                    pila.append(vecino)
        return orden

    def distancias(self, origen: Hashable,
                   max_saltos: Optional[int] = None) -> Dict[Hashable, int]:
        """Cantidad mínima de aristas (saltos) desde el origen hasta cada
        vértice alcanzable, calculada con BFS. Si se da max_saltos, no se
        sigue más lejos. El origen figura con distancia 0. O(V + E)."""
        self._verificar(origen)
        distancia = {origen: 0}
        cola = [origen]
        i = 0  # índice de lectura: evita el O(n) de cola.pop(0)
        while i < len(cola):
            actual = cola[i]
            i += 1
            if max_saltos is not None and distancia[actual] >= max_saltos:
                continue
            for vecino in self._adyacencia[actual]:
                if vecino not in distancia:
                    distancia[vecino] = distancia[actual] + 1
                    cola.append(vecino)
        return distancia

    # ------------------------------------------------------------------
    # Consultas sobre la estructura
    # ------------------------------------------------------------------
    def camino_mas_corto(self, origen: Hashable,
                         destino: Hashable) -> Optional[List[Hashable]]:
        """Camino con menos aristas entre dos vértices, como lista
        [origen, ..., destino]; None si no hay camino. Usa BFS: como todas
        las aristas "cuestan" lo mismo, la primera vez que se llega al
        destino es por el camino más corto. O(V + E)."""
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
                if vecino in padre:
                    continue
                padre[vecino] = actual
                if vecino == destino:
                    camino = [destino]
                    while padre[camino[-1]] is not None:
                        camino.append(padre[camino[-1]])
                    camino.reverse()
                    return camino
                cola.append(vecino)
        return None

    def componentes_conexas(self) -> List[List[Hashable]]:
        """Grupos de vértices que se pueden alcanzar entre sí. Cada vértice
        está en exactamente un grupo. Del más grande al más chico. O(V + E)."""
        visitados = set()
        grupos = []
        for vertice in self._adyacencia:
            if vertice in visitados:
                continue
            grupo = self.bfs(vertice)
            visitados.update(grupo)
            grupos.append(grupo)
        grupos.sort(key=len, reverse=True)
        return grupos

    def esta_conectado(self) -> bool:
        """True si todo el grafo es un único grupo."""
        return len(self.componentes_conexas()) <= 1

    # ------------------------------------------------------------------
    # Presentación
    # ------------------------------------------------------------------
    def lista_de_adyacencia(self) -> str:
        """El grafo como texto, un vértice por línea:  A -> B, C"""
        lineas = []
        for vertice in sorted(self._adyacencia, key=lambda v: str(v).lower()):
            vecinos = sorted(self._adyacencia[vertice], key=lambda v: str(v).lower())
            lineas.append(f"{vertice} -> {', '.join(map(str, vecinos)) if vecinos else '(sin conexiones)'}")
        return "\n".join(lineas)

    def __repr__(self) -> str:
        return f"Grafo({self.cantidad_vertices()} vértices, {self.cantidad_aristas()} aristas)"
