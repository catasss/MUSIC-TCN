"""
gestor_musica.py
Módulo encargado de la gestión de datos del catálogo: cargar canciones
(desde JSON o CSV), y exponer las operaciones sobre el catálogo:
Buscar, Listar, Filtrar, y algunas utilidades extra (top N, géneros).

Este módulo define la "interfaz" entre los datos crudos (JSON/CSV) y
el resto del programa (Main.py), que solo debería hablar con
CatalogoMusical y nunca leer archivos directamente.
"""

import csv
import json
from typing import List, Optional

from modelos import Cancion, Artista, Genero


class CatalogoMusical:
    """Administra la colección de canciones y las operaciones sobre ella."""

    def __init__(self):
        self._canciones: List[Cancion] = []

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

    def cargar_desde_lista(self, canciones: List[Cancion]):
        """Útil para cargar datos de prueba definidos directamente en código."""
        self._canciones = list(canciones)

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

    # ------------------------------------------------------------------
    # Operación: Buscar
    # ------------------------------------------------------------------
    def buscar(self, texto: str) -> List[Cancion]:
        """Busca por coincidencia parcial (case-insensitive) en título o artista."""
        texto = texto.strip().lower()
        return [
            c for c in self._canciones
            if texto in c.titulo.lower() or texto in c.artista.lower()
        ]

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
