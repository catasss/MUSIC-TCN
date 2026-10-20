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

v3: además se mantiene un ArbolCategorias (árbol general / n-ario,
ver arbol_general.py) con la jerarquía del dominio:

    Música > familia (Pop y derivados) > género (K-pop) > artista (BTS)

Las familias y géneros se definen en datos/categorias.json; los nodos de
artista NO se escriben a mano: se generan desde el catálogo real cada vez
que cambian los datos. Un género que no figura en el JSON cae en la
familia "Otros" (se crea sola). Operaciones nuevas:
    - categorias / cargar_categorias_desde_json()
    - canciones_de_categoria(), ruta_categoria_de(), buscar_categoria()
    - conteo_por_categoria()  (recorrido en postorden)

Este módulo define la "interfaz" entre los datos crudos (JSON/CSV) y
el resto del programa (main), que solo debería hablar con
CatalogoMusical y nunca leer archivos ni los árboles directamente.
"""

import copy
import csv
import json
from typing import Dict, List, Optional

from modelos import Cancion, Artista, Genero
from arbol_canciones import ArbolCanciones
from arbol_general import ArbolCategorias, NodoCategoria

NOMBRE_OTROS = "Otros"


class CatalogoMusical:
    """Administra la colección de canciones y las operaciones sobre ella."""

    def __init__(self):
        self._canciones: List[Cancion] = []
        self._arbol: Optional[ArbolCanciones] = None
        # v3: plantilla (familias y géneros) y árbol general ya armado
        self._plantilla_categorias: Optional[dict] = None
        self._categorias: Optional[ArbolCategorias] = None

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
        self._actualizar_estructuras()

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
        self._actualizar_estructuras()

    def cargar_desde_lista(self, canciones: List[Cancion]):
        """Útil para cargar datos de prueba definidos directamente en código."""
        self._canciones = list(canciones)
        self._actualizar_estructuras()

    def _reconstruir_arbol(self):
        """Se llama cada vez que cambian los datos. Mantiene el árbol
        sincronizado con la lista de canciones."""
        self._arbol = ArbolCanciones.construir_balanceado(self._canciones)

    def _actualizar_estructuras(self):
        """Reconstruye todos los índices derivados de la lista de canciones."""
        self._reconstruir_arbol()
        self._reconstruir_categorias()

    # ------------------------------------------------------------------
    # v3: árbol general de categorías
    # ------------------------------------------------------------------
    def cargar_categorias_desde_json(self, ruta: str):
        """Lee la jerarquía (familias y géneros) desde un JSON anidado
        {"nombre": ..., "genero": ..., "hijos": [...]} y arma el árbol."""
        with open(ruta, "r", encoding="utf-8") as f:
            self._plantilla_categorias = json.load(f)
        self._reconstruir_categorias()

    @property
    def categorias(self) -> Optional[ArbolCategorias]:
        return self._categorias

    def _reconstruir_categorias(self):
        """Arma el árbol a partir de la plantilla y agrega, bajo cada
        género, un nodo por cada artista que aparece en el catálogo."""
        if self._plantilla_categorias is None:
            self._categorias = None
            return
        arbol = ArbolCategorias.desde_dict(copy.deepcopy(self._plantilla_categorias))
        pares = sorted({(c.genero, c.artista) for c in self._canciones},
                       key=lambda p: (p[0].lower(), p[1].lower()))
        for genero, artista in pares:
            nodo_genero = arbol.buscar_por_genero(genero)
            if nodo_genero is None:
                # Género que la jerarquía no conoce: va a "Otros".
                otros = arbol.buscar(NOMBRE_OTROS)
                if otros is None:
                    otros = arbol.raiz.agregar_hijo(NodoCategoria(NOMBRE_OTROS))
                nodo_genero = otros.agregar_hijo(
                    NodoCategoria(genero.strip().capitalize(), genero=genero))
            nodo_genero.agregar_hijo(
                NodoCategoria(artista, genero=genero, artista=artista))
        self._categorias = arbol

    def canciones_de_categoria(self, nodo: NodoCategoria) -> List[Cancion]:
        """Canciones que caen dentro del subárbol de un nodo.

        - Nodo de artista: solo las canciones de ese artista en ese género.
        - Cualquier otro nodo: las de todos los géneros que cubre su subárbol.
        """
        if self._categorias is None:
            return []
        if nodo.artista is not None:
            genero = nodo.genero.strip().lower()
            return [c for c in self._canciones
                    if c.artista == nodo.artista and c.genero.strip().lower() == genero]
        generos = set(self._categorias.generos_de(nodo))
        return [c for c in self._canciones if c.genero.strip().lower() in generos]

    def ruta_categoria_de(self, cancion: Cancion) -> Optional[str]:
        """Ej: 'Música > Pop y derivados > K-pop > BTS'."""
        if self._categorias is None:
            return None
        genero = cancion.genero.strip().lower()
        for nodo in self._categorias.preorden():
            if (nodo.artista == cancion.artista and nodo.genero
                    and nodo.genero.strip().lower() == genero):
                return " > ".join(self._categorias.ruta(nodo))
        return None

    def buscar_categoria(self, texto: str) -> List[NodoCategoria]:
        """Categorías cuyo nombre contiene el texto (parcial, sin mayúsculas)."""
        if self._categorias is None:
            return []
        return self._categorias.buscar_parcial(texto)

    def conteo_por_categoria(self) -> Dict[NodoCategoria, int]:
        """Cantidad de canciones por nodo, calculada con un recorrido en
        POSTORDEN: el valor de un padre depende del de sus hijos, así que
        primero se resuelven los hijos. Los nodos de artista cuentan sus
        canciones; los demás suman a sus hijos. O(n) en nodos."""
        conteo: Dict[NodoCategoria, int] = {}
        if self._categorias is None:
            return conteo
        for nodo in self._categorias.postorden():
            if nodo.artista is not None:
                conteo[nodo] = len(self.canciones_de_categoria(nodo))
            else:
                conteo[nodo] = sum(conteo[h] for h in nodo.hijos)
        return conteo

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
        return sorted(self._canciones, key=lambda c: c.popularidad, reverse=True)[:n]

    def generos_disponibles(self) -> List[str]:
        return sorted({c.genero for c in self._canciones})

    def artistas_disponibles(self) -> List[str]:
        return sorted({c.artista for c in self._canciones})

    def canciones_por_artista(self, artista: str) -> List[Cancion]:
        return [c for c in self._canciones if c.artista.lower() == artista.lower()]

    def __len__(self):
        return len(self._canciones)

