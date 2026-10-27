# MUSICTCN — v4

Programa de terminal para explorar un catálogo de canciones: buscar por
título/artista, buscar por título exacto y autocompletar (con un árbol
binario de búsqueda), explorar el catálogo por categorías (con un árbol
general), listar, filtrar por género/año/popularidad y obtener un ranking
dinámico de recomendaciones (con una cola de prioridad).

Esta v4 incorpora el **Objetivo 6: "Que el sistema elija primero"** —un
heap binario escrito a mano que mantiene un ranking dinámico de
recomendaciones— sobre la base de la v3 (Objetivo 5: "Organizá tu
universo", árboles generales), la v2 (Objetivo 3: "Poné un árbol en tu
sistema") y la v1 (Objetivo 1: "Construí el corazón del sistema").

## Estructura del proyecto

```
musictcn/
├── main.py                            # Interfaz de terminal (menú, entrada del usuario)
├── modelos.py                          # Clases del dominio: Cancion, Artista, Genero
├── gestor_musica.py                     # Clase CatalogoMusical: carga de datos y operaciones
├── arbol_canciones.py                   # Árbol binario de búsqueda (BST) ordenado por título
├── arbol_avl.py                         # Árbol AVL (BST auto-balanceado) - Objetivo 4
├── arbol_general.py                     # Árbol general (n-ario) de categorías - Objetivo 5
├── heap_prioridad.py                    # Cola de prioridad: heap binario máximo a mano - Objetivo 6
├── prioridad.py                         # Función de prioridad (popularidad, novedad, género)
├── test_arbol_canciones.py              # Pruebas unitarias del BST (14 tests)
├── test_arbol_general.py                # Pruebas del árbol general y su integración (25 tests)
├── test_heap_prioridad.py               # Pruebas del heap, la prioridad y el ranking (34 tests)
├── ejemplos_recorridos.py               # Recorridos y búsquedas sobre la jerarquía real
├── ejemplos_recorridos.txt              # Salida de ejemplos_recorridos.py
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
- **`gestor_musica.py`** es la interfaz entre los datos crudos y el resto
  del programa: `CatalogoMusical` sabe cargar canciones desde JSON o CSV,
  mantiene los árboles y los heaps sincronizados con los datos, y expone
  las operaciones `buscar()`, `buscar_titulo_exacto()`, `autocompletar()`,
  `listar()`, `listar_ordenado_por_titulo()` y `filtrar()`, las de
  categorías (`canciones_de_categoria()`, `buscar_categoria()`,
  `ruta_categoria_de()`, `dibujar_categorias()`), las de ranking
  (`ranking()`, `agregar_cancion()`), además de utilidades (`top_n()`,
  `generos_disponibles()`).
- **`main.py`** solo se encarga de la interfaz de terminal (menú, `input()`,
  `print()`); nunca lee archivos ni conoce el árbol directamente —esa
  responsabilidad es de `gestor_musica.py`. Así los módulos quedan
  desacoplados.

## Requisitos

- Python 3.8 o superior (no usa librerías externas).

## Cómo ejecutar

```bash
cd musictcn
python3 main.py
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
14. Explorar conexiones entre artistas (próximamente)
15. Recomendaciones personalizadas por perfil (próximamente)
0. Salir
----------------------------------------
```

Elegí una opción escribiendo el número y presionando Enter.

## Operaciones implementadas en v4

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
| 13 | Agregar canción | Heap + BST | Inserta la canción en O(log n); el ranking se actualiza al instante |

Además, la opción **2** (título exacto) ahora muestra la categoría de la
canción (ej: `Música > Pop y derivados > K-pop > BTS`).

Las opciones **14** (conexiones entre artistas) y **15** (recomendaciones
personalizadas por perfil) quedan planteadas en el menú pero marcadas como
"próximamente": requieren modelar colaboraciones entre artistas (un grafo)
y un perfil de usuario, fuera del alcance de esta v4. Las canciones
agregadas con la opción 13 viven solo en memoria: no se guardan en los
archivos de datos.

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

(entre paréntesis, la cantidad de canciones de cada categoría)

Los niveles de familia y género salen de **`datos/categorias.json`**; los
nodos de **artista se generan a partir del catálogo cargado**, así que si
cambian las canciones, la jerarquía se reconstruye sola. Un género que la
taxonomía no conoce se ubica bajo un nodo "Otros" en vez de perderse.

### Búsquedas y recorridos

| Operación | Método | Complejidad |
|---|---|---|
| Buscar por nombre (exacto o parcial) | `buscar()`, `buscar_parcial()` | O(n) — los hermanos no están ordenados |
| Ruta desde la raíz | `ruta(nodo)` | O(h), h = altura |
| Preorden (padre → hijos) | `preorden()` | O(n) — mostrar la jerarquía de arriba hacia abajo |
| Postorden (hijos → padre) | `postorden()` | O(n) — valores del padre que dependen de los hijos |
| Por niveles (anchura) | `por_niveles()` | O(n) — todas las categorías de un mismo nivel |

Ejemplos de cada recorrido sobre la jerarquía real: **`ejemplos_recorridos.txt`**.

### Cómo se integra a la app

- Opción **9, Explorar categorías**: se navega eligiendo subcategorías;
  en cada nivel se ven la ruta (`Música > Pop y derivados > K-pop`), las
  subcategorías con su cantidad de canciones y las canciones de esa
  categoría ordenadas por popularidad.
- Opción **10**: la jerarquía completa con el recorrido a elección.
- Opción **11**: búsqueda de una categoría por nombre.
- Una familia agrupa las canciones de todos sus géneros; un artista, solo
  las suyas.

```bash
python3 -m unittest test_arbol_general.py test_arbol_canciones.py   # 39 pruebas
python3 ejemplos_recorridos.py                                       # recorridos de ejemplo
python3 main.py                                                      # la app (opciones 9, 10 y 11)
```

## Objetivo 6: colas de prioridad — Que el sistema elija primero

### Función de prioridad

La prioridad de una canción combina tres factores ajustables:

```
base      = (peso_popularidad * popularidad + peso_novedad * novedad)
            / (peso_popularidad + peso_novedad)
prioridad = base + bono_genero        (solo si el género es el preferido)
```

La *novedad* es el año llevado a una escala de 0 (1960) a 100 (2026) y el
bono de género es de +10 puntos (por eso la prioridad puede superar 100).
Hay tres criterios listos —popularidad, equilibrado (70/30) y novedades
(30/70)— y cada uno admite un género preferido. Ejemplo real:

```
TOP 5  (popularidad 70% / novedad 30%, +10 a 'k-pop')
 1. Dynamite - BTS                              103.8
 2. How You Like That - BLACKPINK               100.3
 3. Boy With Luv - BTS                           98.4
 4. Kill This Love - BLACKPINK                   97.7
 5. Blinding Lights - The Weeknd                 95.2
```

### El heap

`ColaPrioridad` es un heap binario máximo escrito a mano sobre una lista:
el hijo izquierdo de la posición `i` está en `2i+1`, el derecho en `2i+2`
y el padre en `(i-1)//2`. La raíz es siempre el mejor elemento.

| Operación | Costo |
|---|---|
| `ver_maximo()` | O(1) |
| `insertar()` | O(log n) |
| `extraer_maximo()` | O(log n) |
| `desde_lista()` (construcción de Floyd) | O(n) |
| `mejores(N)` (Top-N, sin modificar el heap) | O(N log N) |

### Cómo se integra a la app

- Opción **12, Ranking de recomendaciones**: se elige el criterio, el
  género preferido y cuántas canciones ver.
- Opción **13, Agregar canción**: la canción entra en cada heap ya
  construido en O(log n), y el ranking cambia al instante.
- Opción **5** (top 10 populares) también usa el heap en vez de ordenar
  todo el catálogo.
- Cada criterio construye su heap la primera vez que se usa y lo guarda.

### ¿Por qué un heap y no ordenar todo cada vez?

Porque solo se necesita el Top-N y no el orden total, y porque el ranking
cambia: cada canción nueva obliga a reordenar todo desde cero (O(n log n)),
mientras que al heap le cuesta O(log n). Resultados medidos con 100.000
canciones y Top-10:

| Escenario | Ordenar todo | Heap |
|---|---:|---:|
| Comparaciones (consulta única) | 1.528.975 | 187.973 al construir + 55 por Top-10 |
| Ranking dinámico (canción nueva + Top-10) | 85,48 ms | 0,0235 ms (**3.641x**) |

En una consulta única sobre datos que no cambian, `sorted()` gana en
tiempo (está escrito en C y este heap en Python puro): ahí ordenar es
razonable. La justificación completa, con todas las tablas y la
conclusión técnica, está en **`comparacion_heap_vs_sort.md`**.

```bash
python3 -m unittest test_heap_prioridad.py -v   # 34 pruebas del heap y el ranking
python3 comparacion_heap_vs_sort.py             # experimento heap vs ordenar todo
python3 main.py                                 # la app (opciones 12 y 13)
```

## Datos de prueba

`datos/canciones.json` contiene 15 canciones de ejemplo cubriendo los
géneros k-pop, rap, rock, pop y folk, con año y popularidad variados para
poder probar todas las operaciones (incluyendo casos sin resultados).
`datos/categorias.json` define la jerarquía de familias y géneros.
`datos/canciones.csv` tiene la misma información en CSV, y
`CatalogoMusical.cargar_desde_csv()` permite usarla en lugar del JSON si
se prefiere (basta con cambiar `RUTA_DATOS` en `main.py`).

## Demos

Transcripciones de sesiones reales de la app, una por versión:
`demo_v1.txt` (buscar, explorar género, top 10), `demo_v2.txt` (búsqueda
exacta, autocompletado y listado por inorder), `demo_v3.txt`
(jerarquía completa, buscar categoría y explorar categorías) y
`demo_v4.txt` (ranking con distintos criterios, agregar una canción y ver
cómo el ranking se actualiza).

## Próximos pasos (fuera del alcance de v4)

- Clase `Usuario` con gustos/historial para recomendaciones personalizadas.
- Modelo de grafo de colaboraciones entre artistas (opciones "conexiones"
  y "camino de colaboraciones" del enunciado original).
- Integrar el AVL (`arbol_avl.py`) como reemplazo del BST en
  `CatalogoMusical`, para garantizar O(log n) incluso ante inserciones
  adversariales, no solo en el caso promedio.
- Persistencia de las canciones agregadas (hoy viven solo en memoria).
- Un heap que actualice la prioridad de una canción ya insertada (por
  ejemplo, cuando cambia su popularidad) sin reconstruirlo.
