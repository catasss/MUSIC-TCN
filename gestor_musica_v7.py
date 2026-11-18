"""
gestor_musica_v7.py  (TP09 - Optimización, versión 7)

Extiende el CatalogoMusical de la v6 con el camino mínimo ponderado
(Dijkstra). No modifica la v6: la hereda y solo agrega lo nuevo.

Peso de una arista entre dos artistas = 1 + diferencia de popularidad
promedio / 10. Dos artistas de popularidad parecida están "más cerca"
(peso cercano a 1); uno muy popular y otro poco popular, más lejos.
"""
from typing import List, Optional, Tuple

from gestor_musica_v6 import CatalogoMusical as CatalogoMusicalV6
from camino_minimo import GrafoPonderado


class CatalogoMusical(CatalogoMusicalV6):

    def _popularidad_promedio(self, artista: str) -> float:
        pops = [c.popularidad for c in self._canciones if c.artista == artista]
        return sum(pops) / len(pops) if pops else 0.0

    def _peso_entre(self, a: str, b: str) -> float:
        diferencia = abs(self._popularidad_promedio(a) - self._popularidad_promedio(b))
        return 1 + diferencia / 10

    def grafo_ponderado(self) -> GrafoPonderado:
        """Copia del grafo de artistas con peso en cada arista. Se arma al
        consultar, así siempre refleja las canciones agregadas."""
        return GrafoPonderado.desde_grafo(self._grafo, self._peso_entre)

    def camino_minimo_entre_artistas(self, origen: str, destino: str
                                     ) -> Optional[Tuple[List[str], float]]:
        """Camino de menor costo total entre dos artistas (Dijkstra):
        ([origen, ..., destino], costo) o None si no están conectados.
        O((V + E) log V)."""
        return self.grafo_ponderado().camino_minimo(origen, destino)
