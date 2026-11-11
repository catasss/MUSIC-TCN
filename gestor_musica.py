"""Compatibilidad: expone el gestor de la versión 4 bajo el nombre histórico.

El README y los tests de la v4 importan `gestor_musica`, mientras que el
repositorio conserva el archivo versionado `gestor_musica_v4.py`.
"""
from gestor_musica_v4 import CatalogoMusical

__all__ = ["CatalogoMusical"]
