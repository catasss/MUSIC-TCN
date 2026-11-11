"""
gestor_musica.py
Módulo encargado de la gestión de datos del catálogo: cargar canciones
(desde JSON o CSV), y exponer las operaciones sobre el catálogo:
Buscar, Listar, Filtrar, y algunas utilidades extra (top N, géneros).

v2: además de la lista de canciones, se mantiene un ArbolCanciones
(BST ordenado por título) que se reconstruye cada vez que se cargan
datos. Se usa para tres operaciones reales:
    - buscar_titulo_exacto(): búsqueda exacta O(log n) en vez de O(n).
    - autocompletar(): sugerencias por prefijo mientras el usuario escribe.
    - listar_ordenado_por_titulo(): recorrido inorder, sin tener que
      volver a ordenar la lista en cada llamada.

v3: además se mantiene un árbol general (ArbolCategorias) con la
jerarquía Música > familia > género > artista. La taxonomía de familias
y géneros viene de datos/categorias.json; los nodos de artista se
generan a partir de las canciones realmente cargadas. Se usa para
explorar el catálogo por categorías y para ubicar cada canción en la
jerarquía.

v4: se agrega un ranking dinámico de recomendaciones con colas de
prioridad (heap binario, heap_prioridad.py). Para cada criterio de
prioridad (prioridad.py) se construye una sola vez un heap y se guarda;
pedir el Top-N cuesta O(N log N) sin ordenar el catálogo, y agregar una
canción nueva la inserta en cada heap guardado en O(log n).

Este módulo define la "interfaz" entre los datos crudos (JSON/CSV) y
el resto del programa (Main.py), que solo debería hablar con
CatalogoMusical y nunca leer archivos ni el árbol directamente.
"""

import csv
import json
from typing import Dict, List, Optional, Tuple

from modelos import Cancion, Artista, Genero
from arbol_canciones import ArbolCanciones
from arbol_general import ArbolCategorias, NodoCategoria
from heap_prioridad import ColaPrioridad
from prioridad import CriterioPrioridad


class CatalogoMusical:
    """Administra la colección de canciones y las operaciones sobre ella."""

    def __init__(self):
        self._canciones: List[Cancion] = []
        self._arbol: Optional[ArbolCanciones] = None
        self._taxonomia: Optional[dict] = None          # familias y géneros (JSON)
        self._categorias: Optional[ArbolCategorias] = None
        # un heap ya construido por cada criterio de prioridad usado
        self._rankings: Dict[CriterioPrioridad, ColaPrioridad] = {}

    # ------------------------------------------------------------------
    # Carga de datos
    # ------------------------------------------------------------------
    def cargar_desde_json(self, ruta: str):
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        self._canciones = [
            Cancion(
                id_cancion=item["id"],
                titulo=item["titulo"],
                artista=item["artista"],
                genero=item["genero"],
                anio=item["anio"],
                popularidad=item["popularidad"],
            )
            for item in datos
        ]
        self._reconstruir_arbol()

    def cargar_desde_csv(self, ruta: str):
        canciones = []
        with open(ruta, "r", encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                canciones.append(
                    Cancion(
                        id_cancion=int(fila["id"]),
                        titulo=fila["titulo"],
                        artista=fila["artista"],
                        genero=fila["genero"],
                        anio=int(fila["anio"]),
                        popularidad=int(fila["popularidad"]),
                    )
                )
        self._canciones = canciones
        self._reconstruir_arbol()

    def cargar_desde_lista(self, canciones: List[Cancion]):
        """Útil para cargar datos de prueba definidos directamente en código."""
        self._canciones = list(canciones)
        self._reconstruir_arbol()

    def _reconstruir_arbol(self):
        """Se llama cada vez que cambian los datos. Mantiene el árbol
        sincronizado con la lista de canciones."""
        self._arbol = ArbolCanciones.construir_balanceado(self._canciones)
        self._reconstruir_categorias()
        self._rankings = {}  # los datos cambiaron: los heaps viejos ya no sirven

    # ------------------------------------------------------------------
    # Categorías (árbol general)
    # ------------------------------------------------------------------
    def cargar_categorias_desde_json(self, ruta: str):
        """Carga la taxonomía (familias y géneros) y arma la jerarquía
        completa agregando, bajo cada género, los artistas del catálogo."""
        with open(ruta, "r", encoding="utf-8") as f:
            self._taxonomia = json.load(f)
        self._reconstruir_categorias()

    def _reconstruir_categorias(self):
        if self._taxonomia is None:
            return
        arbol = ArbolCategorias.desde_dict(self._taxonomia)

        # Artistas por género, en el orden en que aparecen en el catálogo
        artistas_por_genero = {}
        for c in self._canciones:
            artistas = artistas_por_genero.setdefault(c.genero.lower(), [])
            if c.artista not in artistas:
                artistas.append(c.artista)

        for genero, artistas in sorted(artistas_por_genero.items()):
            nodo_genero = arbol.buscar_por_genero(genero)
            if nodo_genero is None:
                # género del catálogo que la taxonomía no conoce
                otros = arbol.buscar("Otros")
                if otros is None:
                    otros = arbol.raiz.agregar_hijo(NodoCategoria("Otros"))
                nodo_genero = otros.agregar_hijo(NodoCategoria(genero.capitalize(), genero=genero))
            for artista in sorted(artistas):
                nodo_genero.agregar_hijo(NodoCategoria(artista, genero=genero, artista=artista))

        self._categorias = arbol

    @property
    def categorias(self) -> Optional[ArbolCategorias]:
        return self._categorias

    def canciones_de_categoria(self, nodo: NodoCategoria) -> List[Cancion]:
        """Canciones que cubre una categoría (por popularidad descendente):
        un nodo de artista -> las de ese artista; cualquier otro nodo ->
        todas las de los géneros de su subárbol."""
        if self._categorias is None:
            return []
        if nodo.artista is not None:
            elegidas = [c for c in self._canciones if c.artista == nodo.artista]
        else:
            generos = set(self._categorias.generos_de(nodo))
            elegidas = [c for c in self._canciones if c.genero.lower() in generos]
        return sorted(elegidas, key=lambda c: c.popularidad, reverse=True)

    def buscar_categoria(self, texto: str) -> List[NodoCategoria]:
        """Categorías cuyo nombre contiene el texto (género, familia o artista)."""
        if self._categorias is None:
            return []
        return self._categorias.buscar_parcial(texto)

    def ruta_categoria_de(self, cancion: Cancion) -> str:
        """Ubicación de una canción en la jerarquía, ej:
        'Música > Pop y derivados > K-pop > BTS'."""
        if self._categorias is None:
            return ""
        nodo = None
        for n in self._categorias.preorden():
            if n.artista == cancion.artista and n.genero and n.genero.lower() == cancion.genero.lower():
                nodo = n
                break
        if nodo is None:
            return ""
        return " > ".join(self._categorias.ruta(nodo))

    def dibujar_categorias(self) -> str:
        """Jerarquía completa en texto, con la cantidad de canciones por nodo."""
        if self._categorias is None:
            return ""
        return self._categorias.dibujar(
            etiqueta=lambda n: f"{n.nombre} ({len(self.canciones_de_categoria(n))})"
        )

    # ------------------------------------------------------------------
    # Ranking dinámico de recomendaciones (cola de prioridad / heap)
    # ------------------------------------------------------------------
    def _heap_para(self, criterio: CriterioPrioridad) -> ColaPrioridad:
        """Heap del criterio: se construye la primera vez (O(n)) y se guarda."""
        heap = self._rankings.get(criterio)
        if heap is None:
            heap = ColaPrioridad.desde_lista((c, criterio.puntaje(c)) for c in self._canciones)
            self._rankings[criterio] = heap
        return heap

    def ranking(self, n: int = 5,
                criterio: Optional[CriterioPrioridad] = None) -> List[Tuple[Cancion, float]]:
        """Top-N según el criterio, como lista de (canción, puntaje).

        Costo: O(N log N) una vez que el heap del criterio existe, sin
        importar cuántas canciones tenga el catálogo. Cambiar de criterio
        (pesos o género preferido) construye un heap nuevo, O(n)."""
        if criterio is None:
            criterio = CriterioPrioridad.popularidad()
        return self._heap_para(criterio).mejores(n)

    def siguiente_id(self) -> int:
        return max((c.id for c in self._canciones), default=0) + 1

    def agregar_cancion(self, cancion: Cancion):
        """Agrega una canción y mantiene sincronizadas todas las estructuras:
        la lista, el árbol de títulos (O(log n)), cada heap de ranking ya
        construido (O(log n) cada uno) y la jerarquía de categorías."""
        if any(c.id == cancion.id for c in self._canciones):
            raise ValueError(f"Ya existe una canción con id {cancion.id}")
        if self.buscar_titulo_exacto(cancion.titulo) is not None:
            raise ValueError(f"Ya existe una canción con el título '{cancion.titulo}'")

        self._canciones.append(cancion)
        if self._arbol is None:
            self._arbol = ArbolCanciones()
        self._arbol.insertar(cancion)
        for criterio, heap in self._rankings.items():
            heap.insertar(cancion, criterio.puntaje(cancion))
        self._reconstruir_categorias()

    # ------------------------------------------------------------------
    # Operación: Listar
    # ------------------------------------------------------------------
    def listar(self, orden_por: Optional[str] = None, descendente: bool = False) -> List[Cancion]:
        """Devuelve todas las canciones, opcionalmente ordenadas.

        orden_por: 'titulo' | 'artista' | 'anio' | 'popularidad'
        """
        canciones = list(self._canciones)
        if orden_por:
            canciones.sort(key=lambda c: getattr(c, orden_por), reverse=descendente)
        return canciones

    def listar_ordenado_por_titulo(self) -> List[Cancion]:
        """Igual que listar(orden_por='titulo'), pero usando el árbol
        (recorrido inorder) en vez de volver a ordenar la lista completa
        cada vez que se llama."""
        if self._arbol is None:
            return []
        return self._arbol.recorrido_inorder()

    # ------------------------------------------------------------------
    # Operación: Buscar
    # ------------------------------------------------------------------
    def buscar(self, texto: str) -> List[Cancion]:
        """Busca por coincidencia PARCIAL (case-insensitive) en título o
        artista. Al ser una búsqueda por subcadena (no por clave exacta),
        no se puede resolver con el árbol de forma más eficiente que
        recorriendo la lista: sigue siendo O(n), a propósito."""
        texto = texto.strip().lower()
        return [
            c for c in self._canciones
            if texto in c.titulo.lower() or texto in c.artista.lower()
        ]

    def buscar_titulo_exacto(self, titulo: str) -> Optional[Cancion]:
        """Búsqueda EXACTA por título usando el árbol: O(log n) promedio
        en vez de recorrer las n canciones."""
        if self._arbol is None:
            return None
        return self._arbol.buscar(titulo)

    def autocompletar(self, prefijo: str, max_resultados: int = 10) -> List[Cancion]:
        """Sugerencias de títulos que empiezan con el prefijo escrito,
        en orden alfabético. Usa el árbol para descartar subárboles
        enteros en vez de revisar canción por canción."""
        if self._arbol is None:
            return []
        return self._arbol.buscar_por_prefijo(prefijo, max_resultados)

    # ------------------------------------------------------------------
    # Operación: Filtrar
    # ------------------------------------------------------------------
    def filtrar(self, genero: Optional[str] = None, anio_min: Optional[int] = None,
                anio_max: Optional[int] = None, popularidad_min: Optional[int] = None) -> List[Cancion]:
        resultado = list(self._canciones)
        if genero:
            resultado = [c for c in resultado if c.genero.lower() == genero.lower()]
        if anio_min is not None:
            resultado = [c for c in resultado if c.anio >= anio_min]
        if anio_max is not None:
            resultado = [c for c in resultado if c.anio <= anio_max]
        if popularidad_min is not None:
            resultado = [c for c in resultado if c.popularidad >= popularidad_min]
        return resultado

    # ------------------------------------------------------------------
    # Utilidades extra (soporte para futuras opciones del menú)
    # ------------------------------------------------------------------
    def top_n(self, n: int = 10) -> List[Cancion]:
        """Las n más populares. Usa el heap en vez de ordenar todo el catálogo."""
        return [c for c, _ in self.ranking(n, CriterioPrioridad.popularidad())]

    def generos_disponibles(self) -> List[str]:
        return sorted({c.genero for c in self._canciones})

    def artistas_disponibles(self) -> List[str]:
        return sorted({c.artista for c in self._canciones})

    def canciones_por_artista(self, artista: str) -> List[Cancion]:
        return [c for c in self._canciones if c.artista.lower() == artista.lower()]

    def __len__(self):
        return len(self._canciones)

