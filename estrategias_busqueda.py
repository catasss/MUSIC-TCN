"""
estrategias_busqueda.py
Dos estrategias distintas para resolver la misma necesidad:
"buscar una canción por título exacto" dentro del catálogo.

1) busqueda_secuencial: recorre la lista de canciones una por una.
2) ArbolBusquedaCanciones: arma un árbol binario de búsqueda (BST) indexado
   por título y busca descendiendo por el árbol.

Ambas reciben/operan sobre objetos Cancion (ver modelos.py).
"""

import random
from typing import List, Optional

from modelos import Cancion


# ----------------------------------------------------------------------
# Estrategia 1: Búsqueda secuencial
# ----------------------------------------------------------------------
def busqueda_secuencial(canciones: List[Cancion], titulo: str) -> Optional[Cancion]:
    """Recorre la lista de principio a fin comparando título por título.

    Complejidad temporal: O(n) en el peor caso y en el caso promedio
    (hay que revisar, en promedio, la mitad de la lista; en el peor
    caso -no está o está al final- se revisa toda).
    Complejidad espacial: O(1) adicional (no usa estructuras extra).
    """
    for cancion in canciones:
        if cancion.titulo == titulo:
            return cancion
    return None


# ----------------------------------------------------------------------
# Estrategia 2: Búsqueda en árbol binario de búsqueda (BST)
# ----------------------------------------------------------------------
class _NodoArbol:
    __slots__ = ("cancion", "izquierda", "derecha")

    def __init__(self, cancion: Cancion):
        self.cancion = cancion
        self.izquierda: Optional["_NodoArbol"] = None
        self.derecha: Optional["_NodoArbol"] = None


class ArbolBusquedaCanciones:
    """Árbol binario de búsqueda (BST) ordenado por título de canción.

    Complejidad temporal de la búsqueda:
        - Caso promedio (árbol razonablemente balanceado): O(log n)
        - Peor caso (árbol degenerado, ej. insertar títulos ya
          ordenados alfabéticamente sin balancear): O(n)
    Complejidad espacial: O(n) para guardar el árbol.

    Nota: esta implementación NO se autobalancea (no es un AVL ni un
    Rojo-Negro). Para que el caso promedio sea realmente O(log n) hay
    que insertar las canciones en un orden razonablemente aleatorio,
    tal como se hace en el experimento de este objetivo.
    """

    def __init__(self):
        self._raiz: Optional[_NodoArbol] = None

    def insertar(self, cancion: Cancion):
        if self._raiz is None:
            self._raiz = _NodoArbol(cancion)
            return
        actual = self._raiz
        while True:
            if cancion.titulo < actual.cancion.titulo:
                if actual.izquierda is None:
                    actual.izquierda = _NodoArbol(cancion)
                    return
                actual = actual.izquierda
            else:
                if actual.derecha is None:
                    actual.derecha = _NodoArbol(cancion)
                    return
                actual = actual.derecha

    def buscar(self, titulo: str) -> Optional[Cancion]:
        actual = self._raiz
        while actual is not None:
            if titulo == actual.cancion.titulo:
                return actual.cancion
            elif titulo < actual.cancion.titulo:
                actual = actual.izquierda
            else:
                actual = actual.derecha
        return None

    @classmethod
    def construir_balanceado(cls, canciones: List[Cancion]) -> "ArbolBusquedaCanciones":
        """Construye el árbol insertando las canciones en orden aleatorio,
        para evitar el caso degenerado (lista enlazada) y acercarse al
        caso promedio O(log n) descrito en la documentación de la clase.
        """
        arbol = cls()
        canciones_mezcladas = list(canciones)
        random.shuffle(canciones_mezcladas)
        for c in canciones_mezcladas:
            arbol.insertar(c)
        return arbol
