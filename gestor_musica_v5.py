"""
gestor_musica_v5.py
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

v5: se agrega un grafo de artistas (Grafo, grafo.py): cada vértice es un
artista y dos artistas están conectados si comparten género. Es no
dirigido, sin pesos y con lista de adyacencia. Se reconstruye junto con
los demás índices cuando cambian los datos y permite preguntar con quién
se conecta un artista, el camino más corto entre dos artistas, qué
artistas hay a N saltos y qué grupos de artistas están separados.

Este módulo define la "interfaz" entre los datos crudos (JSON/CSV) y
el resto del programa (main), que solo debería hablar con
CatalogoMusical y nunca leer archivos ni el árbol directamente.
"""

import csv
import json
from typing import Dict, List, Optional, Tuple

from modelos import Cancion, Artista, Genero
from arbol_canciones import ArbolCanciones
from arbol_general import ArbolCategorias, NodoCategoria
from heap_prioridad import ColaPrioridad
from grafo import Grafo
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
        self._grafo: Optional[Grafo] = None             # artistas conectados por género

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
        self._reconstruir_grafo()
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
        self._reconstruir_grafo()

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
        self._reconstruir_grafo()

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

    # ------------------------------------------------------------------
    # Grafo de artistas (v5)
    # ------------------------------------------------------------------
    @property
    def grafo(self) -> Grafo:
        return self._grafo

    def _reconstruir_grafo(self):
        """Vértice = artista. Arista = dos artistas comparten género.

        Se agrupan los artistas por género y se conecta a todos los de un
        mismo grupo entre sí. Un artista con canciones en dos géneros queda
        en dos grupos y hace de puente entre ellos."""
        grafo = Grafo()
        por_genero: Dict[str, List[str]] = {}
        for c in self._canciones:
            grafo.agregar_vertice(c.artista)
            artistas = por_genero.setdefault(c.genero.strip().lower(), [])
            if c.artista not in artistas:
                artistas.append(c.artista)
        for artistas in por_genero.values():
            for i in range(len(artistas)):
                for j in range(i + 1, len(artistas)):
                    grafo.agregar_arista(artistas[i], artistas[j])
        self._grafo = grafo

    def artistas(self) -> List[str]:
        """Todos los artistas del catálogo, ordenados alfabéticamente."""
        return sorted(self._grafo.vertices(), key=str.lower) if self._grafo else []

    def buscar_artista(self, texto: str) -> Optional[str]:
        """Nombre exacto de un artista a partir de lo que escribió el usuario:
        coincidencia exacta (sin importar mayúsculas) o, si no hay, una
        coincidencia parcial única. None si no hay o es ambigua."""
        texto = texto.strip().lower()
        if not texto:
            return None
        nombres = self.artistas()
        for nombre in nombres:
            if nombre.lower() == texto:
                return nombre
        parciales = [n for n in nombres if texto in n.lower()]
        return parciales[0] if len(parciales) == 1 else None

    def generos_de_artista(self, artista: str) -> List[str]:
        return sorted({c.genero.strip().lower() for c in self._canciones
                       if c.artista == artista})

    def artistas_relacionados(self, artista: str) -> List[str]:
        """Artistas conectados directamente con el dado (comparten género)."""
        return sorted(self._grafo.vecinos(artista), key=str.lower)

    def camino_entre_artistas(self, origen: str, destino: str) -> Optional[List[str]]:
        """Camino más corto entre dos artistas, o None si no están conectados."""
        return self._grafo.camino_mas_corto(origen, destino)

    def artistas_a_n_saltos(self, artista: str, saltos: int) -> List[Tuple[str, int]]:
        """Artistas alcanzables en hasta `saltos` pasos, como (nombre, pasos),
        de los más cercanos a los más lejanos. No incluye al artista."""
        distancias = self._grafo.distancias(artista, max_saltos=saltos)
        return sorted(((a, d) for a, d in distancias.items() if a != artista),
                      key=lambda par: (par[1], par[0].lower()))

    def grupos_de_artistas(self) -> List[List[str]]:
        """Grupos de artistas que se pueden alcanzar entre sí (componentes
        conexas), del más grande al más chico; cada uno ordenado por nombre."""
        return [sorted(g, key=str.lower) for g in self._grafo.componentes_conexas()]

    def __len__(self):
        return len(self._canciones)

