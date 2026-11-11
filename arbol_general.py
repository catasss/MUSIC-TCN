"""
arbol_general.py
Árbol general (n-ario) para representar la jerarquía natural del dominio
de MUSICTCN:

    Música
    ├── Pop y derivados
    │   ├── Pop
    │   │   ├── The Weeknd
    │   │   └── ...
    │   └── K-pop
    │       └── BTS
    ├── Rock y alternativo
    └── ...

Niveles: raíz (Música) -> familia -> género -> artista.

A diferencia del BST/AVL (arbol_canciones.py), acá cada nodo puede tener
cualquier cantidad de hijos y NO hay relación de orden entre ellos: el
árbol modela una relación "es parte de" (K-pop es parte de Pop y
derivados), no una clave de búsqueda.

Cada nodo guarda:
    - nombre:  etiqueta visible de la categoría.
    - genero:  (opcional) género del catálogo asociado a ese nodo.
    - artista: (opcional) artista asociado, para los nodos hoja de artista.
"""

from collections import deque
from typing import Callable, List, Optional


class NodoCategoria:
    """Nodo de un árbol general: tiene un padre y una lista de hijos."""

    __slots__ = ("_nombre", "_genero", "_artista", "_hijos", "_padre")

    def __init__(self, nombre: str, genero: Optional[str] = None,
                 artista: Optional[str] = None):
        self._nombre = nombre
        self._genero = genero
        self._artista = artista
        self._hijos: List["NodoCategoria"] = []
        self._padre: Optional["NodoCategoria"] = None

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def genero(self) -> Optional[str]:
        return self._genero

    @property
    def artista(self) -> Optional[str]:
        return self._artista

    @property
    def hijos(self) -> List["NodoCategoria"]:
        return list(self._hijos)  # copia: no exponemos la lista interna

    @property
    def padre(self) -> Optional["NodoCategoria"]:
        return self._padre

    @property
    def es_hoja(self) -> bool:
        return not self._hijos

    def agregar_hijo(self, hijo: "NodoCategoria") -> "NodoCategoria":
        hijo._padre = self
        self._hijos.append(hijo)
        return hijo

    def __repr__(self):
        return f"NodoCategoria({self._nombre!r})"


def _normalizar(texto: str) -> str:
    return texto.strip().lower()


class ArbolCategorias:
    """Árbol general de categorías.

    Complejidad (n = cantidad de nodos):
        - agregar un hijo a un nodo ya conocido: O(1)
        - buscar por nombre: O(n) (no hay orden entre hermanos, hay que
          recorrer)
        - ruta desde la raíz: O(h), h = altura
        - recorridos (preorden, postorden, por niveles): O(n)
    """

    def __init__(self, raiz: NodoCategoria):
        self._raiz = raiz

    @property
    def raiz(self) -> NodoCategoria:
        return self._raiz

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    @classmethod
    def desde_dict(cls, datos: dict) -> "ArbolCategorias":
        """Arma el árbol desde un diccionario anidado:
        {"nombre": ..., "genero": ..., "hijos": [ {...}, ... ]}"""
        def construir(d: dict) -> NodoCategoria:
            nodo = NodoCategoria(d["nombre"], genero=d.get("genero"),
                                 artista=d.get("artista"))
            for hijo in d.get("hijos", []):
                nodo.agregar_hijo(construir(hijo))
            return nodo
        return cls(construir(datos))

    def agregar(self, nombre_padre: str, nodo: NodoCategoria) -> NodoCategoria:
        padre = self.buscar(nombre_padre)
        if padre is None:
            raise ValueError(f"No existe la categoría padre '{nombre_padre}'")
        return padre.agregar_hijo(nodo)

    # ------------------------------------------------------------------
    # Búsquedas
    # ------------------------------------------------------------------
    def buscar(self, nombre: str) -> Optional[NodoCategoria]:
        """Primer nodo (en preorden) cuyo nombre coincide exactamente,
        sin distinguir mayúsculas."""
        objetivo = _normalizar(nombre)
        for nodo in self.preorden():
            if _normalizar(nodo.nombre) == objetivo:
                return nodo
        return None

    def buscar_parcial(self, texto: str) -> List[NodoCategoria]:
        """Todos los nodos cuyo nombre contiene el texto."""
        texto = _normalizar(texto)
        return [n for n in self.preorden() if texto in _normalizar(n.nombre)]

    def buscar_por_genero(self, genero: str) -> Optional[NodoCategoria]:
        """Nodo de género (no de artista) asociado a un género del catálogo."""
        objetivo = _normalizar(genero)
        for nodo in self.preorden():
            if nodo.genero and nodo.artista is None and _normalizar(nodo.genero) == objetivo:
                return nodo
        return None

    def ruta(self, nodo: NodoCategoria) -> List[str]:
        """Nombres desde la raíz hasta el nodo (ej: Música > Pop > K-pop)."""
        camino = []
        actual: Optional[NodoCategoria] = nodo
        while actual is not None:
            camino.append(actual.nombre)
            actual = actual.padre
        camino.reverse()
        return camino

    # ------------------------------------------------------------------
    # Recorridos
    # ------------------------------------------------------------------
    def preorden(self, desde: Optional[NodoCategoria] = None) -> List[NodoCategoria]:
        """Padre -> hijos (de izquierda a derecha). Sirve para mostrar la
        jerarquía de arriba hacia abajo."""
        resultado: List[NodoCategoria] = []
        self._preorden(desde or self._raiz, resultado)
        return resultado

    def _preorden(self, nodo, acumulado):
        acumulado.append(nodo)
        for hijo in nodo._hijos:
            self._preorden(hijo, acumulado)

    def postorden(self, desde: Optional[NodoCategoria] = None) -> List[NodoCategoria]:
        """Hijos -> padre. Sirve cuando el valor de un padre depende de
        sus hijos (ej: contar canciones por categoría)."""
        resultado: List[NodoCategoria] = []
        self._postorden(desde or self._raiz, resultado)
        return resultado

    def _postorden(self, nodo, acumulado):
        for hijo in nodo._hijos:
            self._postorden(hijo, acumulado)
        acumulado.append(nodo)

    def por_niveles(self, desde: Optional[NodoCategoria] = None) -> List[List[NodoCategoria]]:
        """Recorrido en anchura (BFS): devuelve una lista por nivel."""
        inicio = desde or self._raiz
        niveles: List[List[NodoCategoria]] = []
        cola = deque([(inicio, 0)])
        while cola:
            nodo, nivel = cola.popleft()
            if nivel == len(niveles):
                niveles.append([])
            niveles[nivel].append(nodo)
            for hijo in nodo._hijos:
                cola.append((hijo, nivel + 1))
        return niveles

    # ------------------------------------------------------------------
    # Propiedades del árbol
    # ------------------------------------------------------------------
    def cantidad(self) -> int:
        return len(self.preorden())

    def altura(self) -> int:
        """Cantidad de niveles (un árbol con solo la raíz tiene altura 1)."""
        return len(self.por_niveles())

    def hojas(self) -> List[NodoCategoria]:
        return [n for n in self.preorden() if n.es_hoja]

    def generos_de(self, nodo: NodoCategoria) -> List[str]:
        """Géneros del catálogo que cubre el subárbol de un nodo."""
        vistos: List[str] = []
        for n in self.preorden(nodo):
            if n.genero and _normalizar(n.genero) not in vistos:
                vistos.append(_normalizar(n.genero))
        return vistos

    # ------------------------------------------------------------------
    # Dibujo en texto
    # ------------------------------------------------------------------
    def dibujar(self, desde: Optional[NodoCategoria] = None,
                etiqueta: Optional[Callable[[NodoCategoria], str]] = None) -> str:
        """Devuelve el árbol dibujado con ├── y └── (como en la consigna)."""
        etiqueta = etiqueta or (lambda n: n.nombre)
        inicio = desde or self._raiz
        lineas = [etiqueta(inicio)]

        def recorrer(nodo, prefijo):
            hijos = nodo._hijos
            for i, hijo in enumerate(hijos):
                es_ultimo = i == len(hijos) - 1
                lineas.append(prefijo + ("└── " if es_ultimo else "├── ") + etiqueta(hijo))
                recorrer(hijo, prefijo + ("    " if es_ultimo else "│   "))

        recorrer(inicio, "")
        return "\n".join(lineas)
