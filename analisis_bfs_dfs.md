# TP 8 — Recorridos de grafos: BFS y DFS

Se trabaja sobre el grafo de artistas de la v5 (`grafo.py`): vértice = artista,
arista = dos artistas comparten género; no dirigido, sin pesos, lista de
adyacencia. Todo lo de abajo se puede ver andando con
`python3 ejemplos_bfs_dfs.py` (salida en `ejemplos_bfs_dfs.txt`) y desde el
menú: opción 14 de `main_v6.py`, ítems 6, 7 y 8 (`demo_v6.txt`).

## Qué hace cada algoritmo

| | BFS (anchura) | DFS (profundidad) |
|---|---|---|
| Idea | Visita al origen, después a todos sus vecinos, después a los vecinos de los vecinos: **de a un nivel de distancia por vez**. | Elige un vecino y **sigue por esa cadena hasta el fondo**; recién cuando no puede avanzar retrocede y prueba otro. |
| Estructura auxiliar | **Cola** (FIFO): sale primero el que entró primero. | **Pila** (LIFO): sale primero el último que entró. |
| Marca de visitados | Sí (diccionario de distancias / padres). | Sí (conjunto). |
| En el código | `Grafo.bfs`, `distancias`, `bfs_buscar`, `camino_mas_corto` | `Grafo.dfs`, `dfs_arbol` |

Ejemplo real desde Eminem (grupo de rap: los 4 artistas están conectados entre sí):

```
BFS : Eminem [0] -> Travis Scott [1] -> Drake [1] -> Kendrick Lamar [1]
DFS : Eminem [0] -> Travis Scott [1] -> Drake [2] -> Kendrick Lamar [3]
```

Los dos visitan los mismos artistas. En BFS el número es la **distancia mínima**
(los tres están a 1 salto). En DFS es la **profundidad del camino que se siguió**
(se metió por Travis Scott → Drake → Kendrick), que puede ser mucho mayor que la
distancia real.

## Los dos casos de uso

### Caso BFS — "¿Cuál es el artista de otro género más cercano?"

*Me gusta Eminem y quiero descubrir k-pop: ¿por qué artista empiezo y cómo llego?*
`CatalogoMusical.artista_mas_cercano_de_genero(artista, genero)` →
`Grafo.bfs_buscar`.

**Por qué BFS:** explora por cantidad de saltos y corta apenas encuentra un
artista del género pedido. Como todas las aristas cuestan lo mismo, ese primer
hallazgo es de los más cercanos y la cadena devuelta es de las más cortas. Con
el catálogo + tres canciones puente (`ejemplos_bfs_dfs.txt`, sección 4):

```
Eminem -> k-pop: BLACKPINK, a 2 salto(s):  Eminem -> Drake -> BLACKPINK
Queen  -> rap  : Drake,     a 2 salto(s):  Queen -> Harry Styles -> Drake
Mercedes Sosa -> rap: ninguno alcanzable (grupos separados)
```

### Caso DFS — "Explorar toda la red de un artista en profundidad"

*Mostrame todo lo que se puede descubrir a partir de Queen, siguiendo una cadena
hasta el fondo antes de volver.* `CatalogoMusical.explorar_en_profundidad(artista)`
→ `Grafo.dfs_arbol`, que devuelve (artista, de quién se llegó, profundidad).

**Por qué DFS:** acá no se busca lo más cercano sino **recorrer todo lo
alcanzable**, cadena por cadena. El orden en profundidad da un árbol de
exploración que se muestra con sangría (sección 5 de `ejemplos_bfs_dfs.txt`).
Sirve también para saber qué queda **fuera** de la red (Mercedes Sosa).

## Complejidad

V = vértices (artistas), E = aristas (pares de artistas que comparten género).

| Operación | Tiempo | Espacio extra |
|---|---|---|
| `bfs`, `distancias` | **O(V + E)** | O(V) |
| `dfs`, `dfs_arbol` | **O(V + E)** | O(V + E) en el peor caso (ver nota) |
| `bfs_buscar` | O(V + E) peor caso; corta antes si encuentra | O(V) |
| `camino_mas_corto` | O(V + E) | O(V) |
| `componentes_conexas` (BFS repetido) | O(V + E) | O(V) |

**Por qué O(V + E):** cada vértice entra una sola vez a la cola (o se marca una
sola vez en el DFS) → O(V). Al sacarlo se recorre su lista de adyacencia
completa; sumando todos los vértices se mira cada arista **dos veces** (una desde
cada extremo, porque el grafo es no dirigido) → O(2E) = O(E). En total
O(V + E). Con una **matriz de adyacencia** habría que revisar una fila entera
de V celdas por vértice y el costo subiría a **O(V²)**, aunque haya pocas aristas.

**Mejor caso de `bfs_buscar`:** O(1)–O(g) si el primer vecino ya cumple. El peor
caso es cuando nadie cumple (o el único que cumple está lejos): recorre toda la
componente.

**Dos detalles de la implementación que importan para la complejidad:**

- La cola del BFS es una lista con un **índice de lectura** en vez de
  `lista.pop(0)`, que es O(n) y llevaría el BFS a O(V²) en el peor caso.
- El DFS es **iterativo** (pila explícita). Una versión recursiva tendría la
  misma complejidad temporal pero fallaría con `RecursionError` en cadenas largas:
  Python limita la recursión a ~1000 llamadas (se muestra en la sección 8 de
  `ejemplos_bfs_dfs.txt` con una cadena de 5000 artistas).

**Nota sobre el espacio del DFS:** esta implementación apila los vecinos no
visitados sin marcarlos todavía (se marcan al sacarlos), así que un mismo vértice
puede estar varias veces en la pila; en el peor caso hay O(E) entradas. El DFS
recursivo clásico usa O(V) de profundidad de llamadas. En BFS, la cola llega a
tener tantos elementos como el nivel más ancho.

**Medición** (`ejemplos_bfs_dfs.txt`, sección 7, grafos al azar con ~3 aristas por
vértice): al duplicar V y E el tiempo crece de forma aproximadamente
lineal, y el tiempo por (V + E) se mantiene en el mismo orden de magnitud (hay
ruido de medición, así que los números exactos cambian de una corrida a otra).
Es lo que predice O(V + E); si fuera O(V²) el tiempo se cuadruplicaría al duplicar.

**Qué significa E en MUSICTCN:** como se conecta a *todos* los artistas de un
mismo género entre sí, un género con k artistas aporta k(k−1)/2 aristas. En un
catálogo grande E crece como V²/(cantidad de géneros), así que el costo real de
recorrer el grafo lo domina E, no V.

## Diferencias y cuándo conviene cada uno

| | BFS | DFS |
|---|---|---|
| Orden de visita | Por niveles de distancia | Cadena hasta el fondo, después retrocede |
| ¿Camino más corto (en saltos)? | **Sí**, el primero que encuentra es mínimo | **No**: encuentra *un* camino, a veces larguísimo |
| Memoria típica | Crece con el **ancho** del grafo (nivel más ancho) | Crece con la **profundidad** de la cadena |
| Visitan lo mismo | Sí: todo lo alcanzable desde el origen | Sí |
| Conviene para | Camino mínimo, "el más cercano que cumple", artistas a N saltos | Explorar todo lo alcanzable, ver qué queda fuera, detectar ciclos, orden topológico, backtracking |

Mismo destino, distinto camino (sección 6 de `ejemplos_bfs_dfs.txt`):

```
Eminem a BTS
  BFS: Eminem -> Drake -> BLACKPINK -> BTS                                   (3 saltos)
  DFS: Eminem -> Travis Scott -> Drake -> The Weeknd -> Dua Lipa
        -> Harry Styles -> BLACKPINK -> BTS                                  (7 saltos)
```

**Regla práctica:** si la pregunta tiene la palabra *más cerca / más corto /
menos pasos* → BFS. Si la pregunta es *todo lo que se puede alcanzar / explorar
a fondo / ¿está conectado?* → DFS (aunque ahí BFS también sirve, y para
componentes conexas `grafo.py` usa BFS).

## Archivos de esta entrega (v6)

- `grafo.py`: se agregaron `dfs_arbol` y `bfs_buscar` (`dfs` y `camino_mas_corto`
  ahora se apoyan en ellos; mismo comportamiento que en la v5).
- `gestor_musica_v6.py`: `artista_mas_cercano_de_genero`, `explorar_en_profundidad`,
  `explorar_en_anchura`.
- `main_v6.py`: opción 14, ítems 6 (BFS), 7 (DFS) y 8 (comparación).
- `test_recorridos.py`: 25 pruebas (incluye comparar el DFS iterativo contra uno
  recursivo y el camino de BFS contra las distancias mínimas en grafos al azar).
- `ejemplos_bfs_dfs.py` / `.txt`, `demo_v6.txt`, este análisis.
