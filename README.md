# MUSICTCN — v6

Programa de terminal para explorar un catálogo de canciones: buscar por
título/artista, buscar por título exacto y autocompletar (con un árbol
binario de búsqueda), explorar el catálogo por categorías (con un árbol
general), listar, filtrar por género/año/popularidad, obtener un ranking
dinámico de recomendaciones (con una cola de prioridad) y explorar las
conexiones entre artistas y sus recorridos (con un grafo y algoritmos BFS / DFS).

Esta v6 incorpora el **Objetivo 8: recorridos de grafos** —implementación de BFS
y DFS para responder consultas reales de cercanía y exploración profunda sobre
la red de artistas— sobre la base de la v5 (Objetivo 7: grafos y modelo de
conexiones), la v4 (Objetivo 6: "Que el sistema elija primero", colas de
prioridad), la v3 (Objetivo 5: "Organizá tu universo", árboles generales), la v2
(Objetivo 3: "Poné un árbol en tu sistema") y la v1 (Objetivo 1: "Construí el
corazón del sistema").

### Versiones y archivos de entrada

| Versión | Programa | Gestor de datos | Qué suma |
|---|---|---|---|
| v4 | `main.py` | `gestor_musica.py` | hasta el ranking con heap (opciones 1 a 13) |
| v5 | `main_v5.py` | `gestor_musica_v5.py` | la v4 más el grafo de artistas (opción 14) |
| **v6** | **`main_v6.py`** | **`gestor_musica_v6.py`** | la v5 más recorridos BFS y DFS para casos de uso reales |

La v6 es la versión más reciente. Las versiones anteriores se conservan sin
cambios, y los módulos compartidos (`modelos.py`, los árboles, el heap,
`prioridad.py`, `grafo.py`) sirven para todas.

## Estructura del proyecto

```
musictcn/
├── main_v6.py                         # Interfaz de terminal de la v6 (incluye recorridos TP 8)
├── gestor_musica_v6.py                # CatalogoMusical de la v6: v5 más métodos de consulta BFS/DFS
├── main_v5.py                         # Interfaz de terminal de la v5
├── gestor_musica_v5.py                # CatalogoMusical de la v5: la v4 más el grafo de artistas
├── main.py                            # Interfaz de terminal de la v4
├── modelos.py                          # Clases del dominio: Cancion, Artista, Genero
├── gestor_musica.py                     # CatalogoMusical de la v4: carga de datos y operaciones
├── arbol_canciones.py                   # Árbol binario de búsqueda (BST) ordenado por título
├── arbol_avl.py                         # Árbol AVL (BST auto-balanceado) - Objetivo 4
├── arbol_general.py                     # Árbol general (n-ario) de categorías - Objetivo 5
├── heap_prioridad.py                    # Cola de prioridad: heap binario máximo a mano - Objetivo 6
├── prioridad.py                         # Función de prioridad (popularidad, novedad, género)
├── grafo.py                             # Grafo no dirigido y sin pesos, BFS y DFS a mano - Objetivo 7 y 8
├── modelo_grafo.md                      # Modelo del grafo: decisiones y justificación (Objetivo 7)
├── analisis_complejidad_tp8.md          # Análisis de complejidad y casos de uso BFS/DFS (Objetivo 8)
├── test_arbol_canciones.py              # Pruebas unitarias del BST (14 tests)
├── test_arbol_general.py                # Pruebas del árbol general y su integración (25 tests)
├── test_heap_prioridad.py               # Pruebas del heap, la prioridad y el ranking (34 tests)
├── test_recorridos.py                   # Pruebas unitarias de BFS y DFS en el grafo (Objetivo 8)
├── ejemplos_recorridos.py               # Recorridos y búsquedas sobre la jerarquía real
├── ejemplos_recorridos.txt              # Salida de ejemplos_recorridos.py
├── ejemplos_consultas_grafo.py          # Consultas de ejemplo sobre el grafo de artistas
├── ejemplos_consultas_grafo.txt         # Salida de ejemplos_consultas_grafo.py
├── comparacion_arbol_vs_secuencial.py   # Script de comparación de estrategias
├── comparacion_arbol_vs_secuencial.md   # Análisis de complejidad y conclusión (Objetivo 3)
├── resultados_arbol_vs_secuencial.csv   # Resultados reales de la comparación
├── comparacion_heap_vs_sort.py          # Experimento: heap vs ordenar todo (Objetivo 6)
├── comparacion_heap_vs_sort.md          # Justificación del heap, resultados y conclusión
├── resultados_heap_vs_sort.csv          # Resultados reales del experimento
├── datos/
│   ├── canciones.json                   # Datos de prueba (formato JSON)
│   ├── canciones.csv                    # Los mismos datos de prueba en CSV
│   └── categorias.json                  # Taxonomía: familias y géneros (Objetivo 5)
├── complejidad/                         # Objetivo 2: análisis de complejidad
│   ├── estrategias_busqueda.py          #   búsqueda secuencial vs. árbol (por título)
│   ├── experimento_complejidad.py       #   script de la comparación anterior
│   ├── analisis_complejidad.md          #   análisis y conclusión técnica
│   ├── resultados.csv                   #   resultados medidos
│   └── filtrado/                        #   filtrado lineal vs. filtrado indexado
│       ├── experimento.py
│       ├── resultados_experimento_tp2.csv
│       └── analisis_complejidad_tp2.md
├── demo_v1.txt                          # Transcripción de una sesión de ejemplo (v1)
├── demo_v2.txt                          # Transcripción de una sesión de ejemplo (v2)
├── demo_v3.txt                          # Transcripción de una sesión de ejemplo (v3)
├── demo_v4.txt                          # Transcripción de una sesión de ejemplo (v4)
├── demo_v5.txt                          # Transcripción de una sesión de ejemplo (v5)
└── README.md
```

### Diseño

- **`modelos.py`** define las clases del dominio (`Cancion`, `Artista`, `Genero`).
  Los atributos son privados (prefijo `_`) y se exponen mediante `@property`
  (getters), con al menos un setter validado (`Cancion.popularidad`) como
  ejemplo de encapsulamiento real.
- **`arbol_canciones.py`** define `ArbolCanciones`, un árbol binario de
  búsqueda ordenado por título, con inserción, búsqueda exacta, búsqueda
  por prefijo (autocompletado) y los tres recorridos (inorder, preorder,
  postorder).
- **`arbol_general.py`** define `ArbolCategorias` y `NodoCategoria`: un
  árbol general donde cada nodo tiene cualquier cantidad de hijos y
  conoce a su padre. Incluye búsquedas (exacta, parcial, por género),
  ruta desde la raíz, tres recorridos (preorden, postorden, por niveles)
  y un dibujo en texto de la jerarquía.
- **`heap_prioridad.py`** define `ColaPrioridad`: un heap binario máximo
  implementado a mano sobre una lista (sin `heapq`), con inserción,
  extracción del máximo, construcción en O(n) y consulta Top-N que no
  modifica el heap.
- **`prioridad.py`** define `CriterioPrioridad`: la función de prioridad,
  que combina popularidad, novedad (año) y un bono para el género
  preferido, con pesos ajustables.
- **`grafo.py`** define `Grafo`: un grafo no dirigido y sin pesos,
  implementado a mano con lista de adyacencia (un diccionario
  `{vértice: [vecinos]}`) y sin librerías de grafos. Es genérico: sirve
  con cualquier valor hashable como vértice. Incluye vecinos y grado,
  densidad, recorridos BFS (con cola) y DFS (con pila), distancias en saltos,
  camino más corto y componentes conexas.
- **`gestor_musica.py`** (v4), **`gestor_musica_v5.py`** (v5) y
  **`gestor_musica_v6.py`** (v6) son la interfaz entre los datos crudos y el resto
  del programa: `CatalogoMusical` sabe cargar canciones desde JSON o CSV,
  mantiene los árboles, los heaps y el grafo sincronizados con los datos. La v6
  agrega las consultas basadas en recorridos reales (`consultar_artista_mas_cercano_bfs`
  y `explorar_comunidad_profundidad_dfs`).
- **`main.py`** (y sus versiones v5 y v6) solo se encarga de la interfaz de terminal
  (menú, `input()`, `print()`); nunca lee archivos ni conoce los árboles o grafos
  directamente —esa responsabilidad es del gestor. Así los módulos quedan desacoplados.

## Requisitos

- Python 3.8 o superior (no usa librerías externas).

## Cómo ejecutar

```bash
cd musictcn
python3 main_v6.py     # v6, la más reciente (con recorridos BFS y DFS para TP 8)
python3 main_v5.py     # v5 (con grafo de artistas)
python3 main.py        # v4 (hasta ranking con heap)
```

Vas a ver un menú como este:

```
========================================
 MUSICTCN
========================================
1. Buscar canción o artista (texto parcial)
2. Buscar canción por título exacto (árbol)
3. Autocompletar título (árbol)
4. Explorar géneros (k-pop, rap, rock, pop, ...)
5. Ver top 10 de canciones populares
6. Listar todo el catálogo
7. Listar ordenado alfabéticamente (árbol - inorder)
8. Filtrar canciones
9. Explorar categorías (árbol general)
10. Ver jerarquía completa de categorías (recorridos)
11. Buscar categoría por nombre
12. Ranking de recomendaciones (heap)
13. Agregar canción (el ranking se actualiza)
14. Explorar conexiones entre artistas (grafo)
15. Explorar la red con BFS / DFS (TP 8)
16. Recomendaciones personalizadas por perfil (próximamente)
0. Salir
----------------------------------------
```

Elegí una opción escribiendo el número y presionando Enter.

## Operaciones implementadas en v6

| # | Operación | Estrategia | Descripción |
|---|-----------|-----------|-------------|
| 1 | Buscar (parcial) | Secuencial | Búsqueda parcial (sin distinguir mayúsculas) por título o artista |
| 2 | Buscar título exacto | Árbol (BST) | Búsqueda exacta O(log n) por título completo |
| 3 | Autocompletar | Árbol (BST) | Sugerencias por prefijo mientras se escribe |
| 4 | Explorar géneros | Filtrado | Lista los géneros disponibles y filtra por el elegido |
| 5 | Top 10 | Heap | Las 10 canciones con mayor popularidad, sin ordenar todo el catálogo |
| 6 | Listar | Ordenamiento | Lista todo el catálogo, con orden opcional |
| 7 | Listar ordenado (árbol) | Árbol (BST) | Recorrido inorder: alfabético, sin volver a ordenar |
| 8 | Filtrar | Filtrado | Filtra combinando género, rango de años y popularidad mínima |
| 9 | Explorar categorías | Árbol general | Navegación interactiva: se baja a una subcategoría y se sube con 0 |
| 10 | Jerarquía completa | Árbol general | Árbol dibujado, preorden, postorden o por niveles |
| 11 | Buscar categoría | Árbol general | Búsqueda parcial de género, familia o artista, con su ruta y canciones |
| 12 | Ranking de recomendaciones | Heap | Top-N según un criterio ajustable (popularidad, novedad, género preferido) |
| 13 | Agregar canción | Heap + BST + grafo | Inserta la canción en O(log n); el ranking y el grafo se actualizan al instante |
| 14 | Conexiones entre artistas | Grafo | Submenú: ver el grafo, conexiones, camino más corto, saltos y grupos |
| 15 | Explorar la red (TP 8) | Grafo (BFS / DFS) | Consultas reales: artista más cercano (BFS) y exploración en profundidad (DFS) |

## Objetivo 2: complejidad — ¿Qué tan rápido es?

Se resolvió la misma necesidad con dos estrategias distintas, midiendo
tiempos reales con distintos tamaños de catálogo y expresando el
resultado en notación O().

**a) Buscar una canción por título** (`complejidad/`): búsqueda secuencial
O(n) vs. árbol binario de búsqueda O(log n) promedio. Tiempo promedio por
búsqueda:

| N | Secuencial (ms) | Árbol (ms) |
|---:|---:|---:|
| 100 | 0.0020 | 0.0005 |
| 1.000 | 0.0193 | 0.0008 |
| 10.000 | 0.2494 | 0.0012 |
| 100.000 | 2.1507 | 0.0031 |

**b) Filtrar por género y popularidad** (`complejidad/filtrado/`): recorrido
lineal Θ(n) vs. índice por género + búsqueda binaria, O(log k + m) por
consulta tras una construcción única de O(n log n). Con el filtro
popularidad ≥ 50 el índice es entre 9x y 52x más rápido; con uno más
selectivo (≥ 95) llega a ~425x con 100.000 canciones. La ventaja baja
cuando el filtro devuelve muchos resultados, porque copiarlos también
cuesta.

Conclusión: como el catálogo se carga una vez y se consulta muchas veces,
conviene la estructura con preprocesamiento; la búsqueda lineal solo gana
en simplicidad para catálogos chicos o que cambian constantemente. Detalle
en `complejidad/analisis_complejidad.md` y
`complejidad/filtrado/analisis_complejidad_tp2.md`.

```bash
cd complejidad && python3 experimento_complejidad.py     # búsqueda: secuencial vs. árbol
cd complejidad/filtrado && python3 experimento.py        # filtrado: lineal vs. indexado
```

## Objetivo 3: el árbol, en profundidad

Ver **`comparacion_arbol_vs_secuencial.md`** para: por qué se eligió
título como clave de ordenamiento, cómo se integra el árbol a
operaciones reales (no aisladas), y la comparación medida contra la
búsqueda secuencial (hasta **812x más rápido** con 100.000 canciones).

```bash
python3 -m unittest test_arbol_canciones.py -v      # pruebas del árbol
python3 comparacion_arbol_vs_secuencial.py            # comparación de estrategias
```

## Objetivo 4: AVL — El árbol también puede enfermarse

### ¿Qué es el problema?

Un BST común se **degenera** cuando los datos se insertan en orden
(ascendente o descendente). En ese caso, el árbol se convierte en una
lista enlazada y la búsqueda pasa de **O(log n)** a **O(n)**.

### Solución: Árbol AVL

El AVL es un BST auto-balanceado que usa **rotaciones** para mantener
la altura en **O(log n)** siempre.

| Rotación | Caso |
|----------|------|
| Derecha (LL) | Hijo izquierdo crece a la izquierda |
| Izquierda (RR) | Hijo derecho crece a la derecha |
| Izq-Der (LR) | Hijo izquierdo crece a la derecha |
| Der-Izq (RL) | Hijo derecho crece a la izquierda |

### Demo comparativa

Insertando 20 títulos en orden alfabético:

| Métrica | BST común | AVL |
|---------|-----------|-----|
| Altura | 20 (degenerado) | 5 (balanceado) |
| Búsqueda peor caso | 20 comparaciones | 5 comparaciones |

### Cómo ejecutar

```bash
python arbol_avl.py
```

## Objetivo 5: árboles generales — Organizá tu universo

### La jerarquía

Una canción pertenece a un género, un género a una familia, y la familia
a "Música": es una jerarquía natural del dominio, y un árbol general
(n-ario) la representa mejor que una lista o un BST, porque cada nodo
puede tener cualquier cantidad de hijos y no hay un orden de búsqueda
entre ellos.

```
Música (15)
├── Pop y derivados (7)
│   ├── Pop (3)
│   │   ├── Dua Lipa (1)
│   │   ├── Harry Styles (1)
│   │   └── The Weeknd (1)
│   └── K-pop (4)
│       ├── BLACKPINK (2)
│       └── BTS (2)
├── Rock y alternativo (3)
│   └── Rock (3) ...
├── Hip-hop (4)
│   └── Rap (4) ...
└── Folklore y raíces (1)
    └── Folk (1) ...
```

Los niveles de familia y género salen de **`datos/categorias.json`**; los
nodos de **artista se generan a partir del catálogo cargado**, así que si
cambian las canciones, la jerarquía se reconstruye sola.

```bash
python3 -m unittest test_arbol_general.py test_arbol_canciones.py   # 39 pruebas
python3 ejemplos_recorridos.py                                       # recorridos de ejemplo
```

## Objetivo 6: colas de prioridad — Que el sistema elija primero

### El heap

`ColaPrioridad` es un heap binario máximo escrito a mano sobre una lista.
Permite construir el ranking en O(n) y consultar Top-N en O(N log N) sin
reordenar el catálogo completo.

```bash
python3 -m unittest test_heap_prioridad.py -v   # 34 pruebas del heap y el ranking
python3 comparacion_heap_vs_sort.py             # experimento heap vs ordenar todo
```

## Objetivo 7: grafos — el grafo de artistas

El detalle de diseño del grafo no dirigido implementado con lista de adyacencia
está en **`modelo_grafo.md`**.

## Objetivo 8: recorridos de grafos (BFS y DFS) — Explorá la red

En la **versión 6** se implementan y analizan formalmente los algoritmos de
recorrido **BFS** (Breadth-First Search) y **DFS** (Depth-First Search) sobre el
grafo de artistas, respondiendo a las consignas del TP 8.

### Casos de uso reales definidos

1. **Caso de uso BFS: Artista relacionado más cercano**
   - **Consulta:** *"¿Cuál es el artista relacionado más cercano a X?"*
   - **Algoritmo:** **BFS** (utilizando una **Cola / FIFO**).
   - **Por qué conviene:** BFS explora radialmente nivel por nivel. En grafos no
     pesados, garantiza encontrar el camino o nodo destino con la menor cantidad
     de saltos (aristas).

2. **Caso de uso DFS: Exploración exhaustiva de comunidad musical**
   - **Consulta:** *"Explorá todas las relaciones del artista X en profundidad"*.
   - **Algoritmo:** **DFS** (utilizando una **Pila / LIFO**).
   - **Por qué conviene:** DFS sigue una rama de conexiones tan lejos como sea
     posible antes de hacer *backtracking*, lo que permite recorrer exhaustivamente
     toda una componente conexa o comunidad de influencias.

### Análisis de complejidad

| Algoritmo | Complejidad Temporal | Complejidad Espacial | Estructura Principal |
|---|:---:|:---:|---|
| **BFS** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Cola (FIFO) + Visitados |
| **DFS** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Pila (LIFO) + Visitados |

*Donde $V$ es el número de vértices (artistas) y $E$ es el número de aristas (géneros compartidos).*

Toda la documentación teórica detallada se encuentra en **`analisis_complejidad_tp8.md`**.

```bash
python3 -m unittest test_recorridos.py -v   # Pruebas unitarias de BFS y DFS (TP 8)
python3 main_v6.py                           # Ejecución interactiva de la v6
```

## Datos de prueba

`datos/canciones.json` contiene 15 canciones de ejemplo cubriendo los
géneros k-pop, rap, rock, pop y folk. `datos/categorias.json` define la
jerarquía de familias y géneros.

## Demos

Transcripciones de sesiones reales de la app: `demo_v1.txt`, `demo_v2.txt`,
`demo_v3.txt`, `demo_v4.txt` y `demo_v5.txt`.

## Próximos pasos (fuera del alcance de v6)

- Clase `Usuario` con gustos/historial para recomendaciones personalizadas (opción 16).
- Pesos reales en las aristas del grafo y camino mínimo ponderado con Dijkstra.
- Persistencia de canciones agregadas.
