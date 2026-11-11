"""
gestor_musica_v6.py
Extiende el gestor de música de la v5 para integrar la ejecución de las
consultas reales con BFS y DFS sobre el grafo de artistas.
"""

from typing import List, Optional, Dict
from gestor_musica_v5 import CatalogoMusicalV5  # Reutiliza el catálogo existente


class CatalogoMusicalV6(CatalogoMusicalV5):
    """Gestor v6 con soporte para consultas basadas en recorridos BFS y DFS."""

    def consultar_artista_mas_cercano_bfs(self, artista_origen: str) -> Optional[str]:
        """
        Consulta basada en BFS:
        ¿Cuál es el artista relacionado más cercano a un artista dado?
        Devuelve el primer vecino directo obtenido mediante el recorrido en anchura.
        """
        if not self.grafo_artistas.tiene_vertice(artista_origen):
            return None
        
        recorrido = self.grafo_artistas.bfs(artista_origen)
        # El elemento 0 es el origen, el elemento 1 es el más cercano a 1 salto de distancia
        if len(recorrido) > 1:
            return recorrido[1]
        return None

    def explorar_comunidad_profundidad_dfs(self, artista_origen: str) -> List[str]:
        """
        Consulta basada en DFS:
        Explora exhaustivamente en profundidad toda la red/comunidad de artistas
        conectada con el artista de origen.
        """
        if not self.grafo_artistas.tiene_vertice(artista_origen):
            return []
        
        return self.grafo_artistas.dfs(artista_origen)