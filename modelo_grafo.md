# Modelo del grafo de artistas (TP7 — Grafos)

Las cuatro decisiones del modelo, con su justificación.

## 1. Vértices: un artista

Cada vértice es un **artista** del catálogo (hoy 12). Se eligió el artista y no
la canción porque es lo que de forma natural "se conecta" con otros, y porque
con canciones casi todos los vértices quedarían unidos por tener el mismo
artista o el mismo género, sin aportar nada nuevo.

## 2. Aristas: dos artistas comparten género

Hay una arista entre dos artistas si **tienen canciones en un mismo género**.

- Es la relación más simple que se puede calcular con los datos que ya tiene
  el catálogo (no hace falta agregar información nueva).
- Un artista con canciones en dos géneros queda en dos grupos y **hace de
  puente** entre ellos: es lo que vuelve interesantes los caminos.

Se construye agrupando artistas por género y conectando entre sí a todos los
de un mismo grupo. Se reconstruye solo cada vez que cambian los datos.

## 3. Tipo de grafo: no dirigido y sin pesos

- **No dirigido:** "A comparte género con B" implica "B comparte género con
  A"; la relación es simétrica, así que no hay motivo para distinguir
  sentidos.
- **Sin pesos:** o se comparte género o no se comparte; no hay grados de
  conexión que medir. Por eso el camino más corto se calcula con BFS (menos
  aristas) y no hace falta Dijkstra.

## 4. Representación: lista de adyacencia

Se guarda un diccionario `{artista: [artistas conectados]}`.

| | Lista de adyacencia | Matriz de adyacencia |
|---|---|---|
| Memoria | O(V + E) | O(V²) |
| ¿Están conectados A y B? | O(grado) | O(1) |
| Vecinos de A | O(grado) | O(V) |
| Recorrer todo el grafo (BFS/DFS) | O(V + E) | O(V²) |

**Densidad esperada.** Con los datos actuales hay 12 vértices y 11 aristas de
66 posibles: densidad = 2E / (V·(V−1)) = **17%**. La matriz tendría 144
celdas y solo 22 con una conexión.

En un catálogo grande la densidad es aún menor: si los artistas se reparten
parejo en *g* géneros, cada uno se conecta con ≈ 1/*g* del resto, es decir,
unos 5% con 20 géneros. El grafo es **ralo**, así que la lista de adyacencia
ocupa mucho menos y recorre más rápido. Lo único que la matriz haría mejor
(saber en O(1) si dos artistas están conectados) es una consulta que la app
casi no usa: lo habitual es "¿con quién se conecta?", y eso es recorrer la
lista de vecinos.

## Consultas que soporta (grafo.py)

| Consulta | Algoritmo | Costo |
|---|---|---|
| Vecinos y grado de un artista | lectura de la lista | O(grado) |
| Camino más corto entre dos artistas | BFS con padres | O(V + E) |
| Artistas a N saltos | BFS con tope de distancia | O(V + E) |
| Grupos de artistas separados | componentes conexas (BFS) | O(V + E) |
| Recorridos | BFS y DFS | O(V + E) |

## Limitaciones y posible mejora

- Como cada género es un grupo donde todos se conectan, dentro de un género
  los caminos son siempre de 1 salto; las distancias mayores solo aparecen
  cuando un artista actúa de puente entre géneros.
- Una versión más rica podría agregar colaboraciones reales entre artistas
  (con un archivo de datos nuevo) y pesos para medir qué tan cerca están dos
  artistas; en ese caso el camino mínimo pasaría a requerir Dijkstra con la
  cola de prioridad del TP6.
