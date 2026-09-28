"""
arbol_canciones.py
Árbol Binario de Búsqueda (BST) para el catálogo de MUSICTCN.

Clave de ordenamiento elegida: el TÍTULO de la canción.
¿Por qué título y no rating o año? Porque la operación crítica real del
sistema (Objetivo 1 y Objetivo 2 del proyecto) es "buscar una canción",
y el usuario casi siempre busca por título (rara vez por "dame la
canción con rating 87"). Ordenar por título también nos permite listar
el catálogo alfabéticamente sin volver a ordenar cada vez (recorrido
inorder) y hacer autocompletado por prefijo, que son necesidades reales
de una app de música.

Esta implementación NO es de juguete: se integra directamente en
CatalogoMusical (gestor_musica.py) y reemplaza/complementa operaciones
reales del menú (ver main.py, v2).
"""

import random
from typing import List, Optional

from modelos import Cancion


class _NodoArbol:
    __slots__ = ("cancion", "izquierda", "derecha")

    def __init__(self, cancion: Cancion):
        self.cancion = cancion
        self.izquierda: Optional["_NodoArbol"] = None
        self.derecha: Optional["_NodoArbol"] = None


class ArbolCanciones:
    """BST de canciones ordenado por título.

    Complejidad (n = cantidad de canciones):
        - Inserción / búsqueda exacta: O(log n) promedio, O(n) peor caso
          (árbol degenerado si se insertan títulos ya ordenados alfabéticamente).
        - Recorridos (inorder/preorder/postorder): O(n) siempre, visitan
          cada nodo una vez.
        - Espacio: O(n).

    Esta implementación no se autobalancea (no es AVL ni Rojo-Negro). Por
    eso `construir_balanceado` inserta las canciones en orden aleatorio,
    para evitar el caso degenerado en la práctica.
    """

    def __init__(self):
        self._raiz: Optional[_NodoArbol] = None
        self._cantidad = 0

    def __len__(self):
        return self._cantidad

    # ------------------------------------------------------------------
    # Inserción
    # ------------------------------------------------------------------
    def insertar(self, cancion: Cancion):
        self._cantidad += 1
        if self._raiz is None:
            self._raiz = _NodoArbol(cancion)
            return
        actual = self._raiz
        while True:
            if cancion.titulo == actual.cancion.titulo:
                # título duplicado: reemplazamos la canción de ese nodo
                actual.cancion = cancion
                self._cantidad -= 1  # no agregamos un nodo nuevo
                return
            elif cancion.titulo < actual.cancion.titulo:
                if actual.izquierda is None:
                    actual.izquierda = _NodoArbol(cancion)
                    return
                actual = actual.izquierda
            else:
                if actual.derecha is None:
                    actual.derecha = _NodoArbol(cancion)
                    return
                actual = actual.derecha

    @classmethod
    def construir_balanceado(cls, canciones: List[Cancion]) -> "ArbolCanciones":
        """Inserta las canciones en orden aleatorio para evitar el caso
        degenerado (equivalente a una lista enlazada) y acercarse al caso
        promedio O(log n)."""
        arbol = cls()
        mezcladas = list(canciones)
        random.shuffle(mezcladas)
        for c in mezcladas:
            arbol.insertar(c)
        return arbol

    # ------------------------------------------------------------------
    # Búsqueda exacta
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Autocompletado / búsqueda por prefijo (funcionalidad real: sugerir
    # títulos mientras el usuario escribe)
    # ------------------------------------------------------------------
    def buscar_por_prefijo(self, prefijo: str, max_resultados: int = 10) -> List[Cancion]:
        """Devuelve hasta max_resultados canciones cuyo título empieza
        con el prefijo dado, en orden alfabético.

        Aprovecha que el árbol ya está ordenado por título: descarta
        subárboles enteros que no pueden contener el prefijo (todo lo que
        es estrictamente menor al prefijo, o estrictamente mayor a
        cualquier título que empiece con el prefijo), en vez de revisar
        canción por canción como haría una búsqueda secuencial.
        """
        if not prefijo:
            return self.recorrido_inorder()[:max_resultados]

        # cota superior: el string más chico que ya NO puede empezar con
        # el prefijo (p.ej. prefijo "Dyn" -> límite "Dyo"). Todo título
        # que empiece con "Dyn" es, alfabéticamente, menor a "Dyo".
        limite_superior = prefijo[:-1] + chr(ord(prefijo[-1]) + 1)

        resultados: List[Cancion] = []
        self._recolectar_por_prefijo(self._raiz, prefijo, limite_superior, resultados, max_resultados)
        return resultados

    def _recolectar_por_prefijo(self, nodo, prefijo, limite_superior, resultados, max_resultados):
        if nodo is None or len(resultados) >= max_resultados:
            return
        titulo = nodo.cancion.titulo

        # si titulo >= prefijo, todavía puede haber coincidencias a la izquierda
        if titulo >= prefijo:
            self._recolectar_por_prefijo(nodo.izquierda, prefijo, limite_superior, resultados, max_resultados)

        if len(resultados) < max_resultados and titulo.startswith(prefijo):
            resultados.append(nodo.cancion)

        # si titulo < limite_superior, todavía puede haber coincidencias a la derecha
        if len(resultados) < max_resultados and titulo < limite_superior:
            self._recolectar_por_prefijo(nodo.derecha, prefijo, limite_superior, resultados, max_resultados)

    # ------------------------------------------------------------------
    # Recorridos
    # ------------------------------------------------------------------
    def recorrido_inorder(self) -> List[Cancion]:
        """Izquierda -> raíz -> derecha. Devuelve las canciones ordenadas
        alfabéticamente por título (uso real: listar el catálogo ordenado
        sin tener que volver a ordenarlo en cada llamada)."""
        resultado: List[Cancion] = []
        self._inorder(self._raiz, resultado)
        return resultado

    def _inorder(self, nodo, acumulado):
        if nodo is None:
            return
        self._inorder(nodo.izquierda, acumulado)
        acumulado.append(nodo.cancion)
        self._inorder(nodo.derecha, acumulado)

    def recorrido_preorder(self) -> List[Cancion]:
        """Raíz -> izquierda -> derecha. Útil para reconstruir el árbol
        (por ejemplo, para copiarlo o serializarlo) preservando su forma."""
        resultado: List[Cancion] = []
        self._preorder(self._raiz, resultado)
        return resultado

    def _preorder(self, nodo, acumulado):
        if nodo is None:
            return
        acumulado.append(nodo.cancion)
        self._preorder(nodo.izquierda, acumulado)
        self._preorder(nodo.derecha, acumulado)

    def recorrido_postorder(self) -> List[Cancion]:
        """Izquierda -> derecha -> raíz. Útil, por ejemplo, para liberar o
        eliminar el árbol de abajo hacia arriba."""
        resultado: List[Cancion] = []
        self._postorder(self._raiz, resultado)
        return resultado

    def _postorder(self, nodo, acumulado):
        if nodo is None:
            return
        self._postorder(nodo.izquierda, acumulado)
        self._postorder(nodo.derecha, acumulado)
        acumulado.append(nodo.cancion)
