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

Este módulo define la "interfaz" entre los datos crudos (JSON/CSV) y
el resto del programa (Main.py), que solo debería hablar con
CatalogoMusical y nunca leer archivos ni el árbol directamente.
"""

import csv
import json
from typing import List, Optional

from modelos import Cancion, Artista, Genero
from arbol_canciones import ArbolCanciones


class CatalogoMusical:
    """Administra la colección de canciones y las operaciones sobre ella."""

    def __init__(self):
        self._canciones: List[Cancion] = []
        self._arbol: Optional[ArbolCanciones] = None

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

