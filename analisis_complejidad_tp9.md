# Objetivo 9: Optimización — camino mínimo entre artistas (v7)

## Problema
Dados dos artistas, encontrar la cadena de artistas conectados de **menor costo** que los une.

## Definición de "costo"
Vértice = artista. Arista = dos artistas comparten género.
`costo(A, B) = 1 + ((popularidad_A − popularidad_B) / 10)²`, con popularidad media de 0 a 100.
- El 1 es el costo base de dar un paso.
- El término cuadrático hace que un salto grande de popularidad cueste mucho más que varios chicos: es más "natural" pasar de un artista a otro de popularidad parecida.
- El costo nunca baja de 1: no hay pesos negativos.

## Algoritmo elegido: Dijkstra con heap
| Propiedad del grafo | Consecuencia |
|---|---|
| Tiene pesos | BFS no sirve (cuenta aristas, no costo) |
| Pesos ≥ 0 | Dijkstra es correcto (Bellman-Ford solo hace falta con pesos negativos) |
| No dirigido | Cada arista se guarda en ambas listas con el mismo costo |
| Ralo (pocas aristas vs V²) | Lista de adyacencia + heap, no matriz |

Se reutiliza la `ColaPrioridad` (heap máximo) del Objetivo 6 guardando la prioridad como `-costo`, así sale primero el de menor costo. Los costos desactualizados que quedan en el heap se descartan al extraerlos (eliminación perezosa).

## Complejidad
- Cada vértice se fija una vez; cada arista se relaja a lo sumo dos veces (no dirigido).
- Cada relajación inserta en el heap: O(log E) = O(log V).
- **Tiempo: O((V + E) log V).** Con arreglo en vez de heap sería O(V²).
- **Espacio: O(V + E)** (lista de adyacencia, distancias, padres y heap).
- Construcción del grafo: O(V + Σ kᵍ²), con kᵍ = artistas del género g.

## Caso de prueba
`ejemplos_dijkstra.py` (salida en `ejemplos_dijkstra.txt`): de Dua Lipa a Billie Eilish, BFS elige el salto directo (1 salto, costo 13.25) y Dijkstra rodea por tres artistas intermedios (4 saltos, costo 7.21).
`test_dijkstra.py` (12 pruebas): camino mínimo ≠ camino con menos saltos, sin camino, vértice inexistente, costo negativo rechazado, y comparación contra Floyd-Warshall en 30 grafos aleatorios.

## Ordenamiento topológico
No se incorporó: el dominio no tiene dependencias del tipo "ver X antes que Y" y el grafo es no dirigido.
