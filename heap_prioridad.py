"""
heap_prioridad.py
Cola de prioridad implementada con un HEAP BINARIO MÁXIMO, escrito a mano
sobre un arreglo (no se usa el módulo heapq de Python).

Representación: un heap binario es un árbol binario casi completo que se
guarda en una lista. Para el nodo en la posición i:
    padre:           (i - 1) // 2
    hijo izquierdo:  2 * i + 1
    hijo derecho:    2 * i + 2

Invariante (propiedad de heap máximo): la prioridad de cada nodo es mayor
o igual que la de sus hijos. Por eso la raíz (posición 0) es siempre el
elemento de mayor prioridad, y se lee en O(1).

Desempate: si dos elementos tienen la misma prioridad, sale primero el que
se insertó antes (cada entrada guarda su número de orden de llegada).

Complejidad (n = elementos en el heap, N = cantidad pedida):
    insertar            O(log n)
    ver_maximo          O(1)
    extraer_maximo      O(log n)
    desde_lista         O(n)          (construcción bottom-up de Floyd)
    mejores(N)          O(N log N)    (no depende de n, y no modifica el heap)
"""

from typing import Any, Iterable, List, Tuple


class ColaPrioridad:
    """Cola de prioridad máxima: siempre sale primero el de mayor prioridad."""

    def __init__(self):
        # cada entrada es una tupla (prioridad, orden_de_llegada, elemento)
        self._datos: List[Tuple[Any, int, Any]] = []
        self._orden = 0
        self._comparaciones = 0

    def __len__(self) -> int:
        return len(self._datos)

    @property
    def esta_vacia(self) -> bool:
        return not self._datos

    # ------------------------------------------------------------------
    # Conteo de comparaciones (para medir el costo sin depender de la
    # velocidad de la máquina ni del lenguaje)
    # ------------------------------------------------------------------
    @property
    def comparaciones(self) -> int:
        return self._comparaciones

    def reiniciar_comparaciones(self):
        self._comparaciones = 0

    # ------------------------------------------------------------------
    # Operaciones internas
    # ------------------------------------------------------------------
    def _antes(self, i: int, j: int) -> bool:
        """True si la entrada i debe salir antes que la j (tiene más
        prioridad, o igual prioridad y llegó antes)."""
        self._comparaciones += 1
        a, b = self._datos[i], self._datos[j]
        if a[0] != b[0]:
            return a[0] > b[0]
        return a[1] < b[1]

    def _intercambiar(self, i: int, j: int):
        self._datos[i], self._datos[j] = self._datos[j], self._datos[i]

    def _subir(self, i: int):
        """Sube la entrada i mientras tenga más prioridad que su padre."""
        while i > 0:
            padre = (i - 1) // 2
            if self._antes(i, padre):
                self._intercambiar(i, padre)
                i = padre
            else:
                break

    def _bajar(self, i: int):
        """Baja la entrada i mientras algún hijo tenga más prioridad."""
        n = len(self._datos)
        while True:
            izq = 2 * i + 1
            der = izq + 1
            mayor = i
            if izq < n and self._antes(izq, mayor):
                mayor = izq
            if der < n and self._antes(der, mayor):
                mayor = der
            if mayor == i:
                break
            self._intercambiar(i, mayor)
            i = mayor

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------
    def insertar(self, elemento: Any, prioridad: Any):
        """Agrega al final y lo sube hasta su lugar. O(log n)."""
        self._datos.append((prioridad, self._orden, elemento))
        self._orden += 1
        self._subir(len(self._datos) - 1)

    def ver_maximo(self) -> Tuple[Any, Any]:
        """Devuelve (elemento, prioridad) del mayor, sin sacarlo. O(1)."""
        if not self._datos:
            raise IndexError("La cola de prioridad está vacía")
        prioridad, _, elemento = self._datos[0]
        return elemento, prioridad

    def extraer_maximo(self) -> Tuple[Any, Any]:
        """Saca y devuelve (elemento, prioridad) del mayor. O(log n).

        Se lleva el último elemento a la raíz y se lo baja hasta su lugar.
        """
        if not self._datos:
            raise IndexError("La cola de prioridad está vacía")
        self._intercambiar(0, len(self._datos) - 1)
        prioridad, _, elemento = self._datos.pop()
        if self._datos:
            self._bajar(0)
        return elemento, prioridad

    @classmethod
    def desde_lista(cls, pares: Iterable[Tuple[Any, Any]]) -> "ColaPrioridad":
        """Construye el heap de una vez a partir de pares (elemento, prioridad).

        Usa la construcción bottom-up (Floyd): se baja cada nodo interno,
        desde el último padre hasta la raíz. Cuesta O(n), mejor que hacer
        n inserciones (O(n log n)): la mayoría de los nodos están cerca de
        las hojas y casi no tienen que bajar.
        """
        cola = cls()
        for elemento, prioridad in pares:
            cola._datos.append((prioridad, cola._orden, elemento))
            cola._orden += 1
        for i in range(len(cola._datos) // 2 - 1, -1, -1):
            cola._bajar(i)
        return cola

    def mejores(self, n: int) -> List[Tuple[Any, Any]]:
        """Los n de mayor prioridad, en orden, SIN modificar el heap.

        Truco: el siguiente mejor elemento siempre es hijo de alguno ya
        elegido. Se usa un heap auxiliar de "candidatos" (posiciones del
        heap principal): se arranca con la raíz y, cada vez que se elige
        un candidato, se agregan sus dos hijos. Solo se llega a tocar
        O(n) posiciones, no todo el heap: costo O(N log N), independiente
        del tamaño total n.
        """
        if n <= 0 or not self._datos:
            return []
        n = min(n, len(self._datos))

        candidatos = ColaPrioridad()
        prioridad, orden, _ = self._datos[0]
        candidatos.insertar(0, (prioridad, -orden))  # -orden: el que llegó antes gana

        resultado: List[Tuple[Any, Any]] = []
        while len(resultado) < n:
            posicion, _ = candidatos.extraer_maximo()
            prioridad, _, elemento = self._datos[posicion]
            resultado.append((elemento, prioridad))
            for hijo in (2 * posicion + 1, 2 * posicion + 2):
                if hijo < len(self._datos):
                    p_hijo, o_hijo, _ = self._datos[hijo]
                    candidatos.insertar(hijo, (p_hijo, -o_hijo))

        self._comparaciones_ultima_consulta = candidatos.comparaciones
        return resultado

    @property
    def comparaciones_ultima_consulta(self) -> int:
        """Comparaciones que hizo la última llamada a mejores()."""
        return getattr(self, "_comparaciones_ultima_consulta", 0)

    # ------------------------------------------------------------------
    # Verificación (útil para pruebas)
    # ------------------------------------------------------------------
    def cumple_invariante(self) -> bool:
        """Comprueba que ningún hijo tenga más prioridad que su padre."""
        for i in range(1, len(self._datos)):
            padre = (i - 1) // 2
            if self._datos[i][0] > self._datos[padre][0]:
                return False
        return True
