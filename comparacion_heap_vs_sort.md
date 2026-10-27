# Objetivo 6 — Colas de prioridad: que el sistema elija primero

## La necesidad

Un **ranking dinámico de recomendaciones**: mostrar las N mejores
canciones según un criterio que el usuario puede ajustar, y que el
ranking se mantenga al día cuando entran canciones nuevas.

## Función de prioridad (`prioridad.py`)

Se descartó usar solo la popularidad: siempre da el mismo orden, no
distingue canciones con igual puntaje y no deja al usuario inclinar el
ranking hacia lo que busca. La prioridad combina tres factores:

```
base      = (peso_popularidad * popularidad + peso_novedad * novedad)
            / (peso_popularidad + peso_novedad)
prioridad = base + bono_genero        (solo si el género es el preferido)
```

- **popularidad**: puntaje de la canción, de 0 a 100.
- **novedad**: el año llevado a una escala de 0 (1960 o antes) a 100
  (2026 o después).
- **bono de género**: +10 puntos al género que el usuario prefiere. Por
  eso la prioridad puede superar 100.

Tres criterios listos para usar: *popularidad* (100/0), *equilibrado*
(70/30) y *novedades* (30/70), cada uno con género preferido opcional. El
mismo catálogo da rankings distintos según el criterio, y eso es lo que lo
hace dinámico. Ejemplo real, con k-pop como género preferido:

```
TOP 5  (popularidad 70% / novedad 30%, +10 a 'k-pop')
 1. Dynamite - BTS                              103.8
 2. How You Like That - BLACKPINK               100.3
 3. Boy With Luv - BTS                           98.4
 4. Kill This Love - BLACKPINK                   97.7
 5. Blinding Lights - The Weeknd                 95.2
```

## El heap (`heap_prioridad.py`)

Heap binario **máximo escrito a mano** sobre una lista (sin `heapq`). Para
el nodo en la posición `i`: padre en `(i-1)//2`, hijos en `2i+1` y `2i+2`.
Invariante: cada nodo tiene prioridad mayor o igual que sus hijos, así que
la raíz es siempre el mejor elemento. Ante un empate sale primero el que
se insertó antes.

| Operación | Costo | Cómo |
|---|---|---|
| `ver_maximo()` | O(1) | leer la raíz |
| `insertar()` | O(log n) | agregar al final y subir |
| `extraer_maximo()` | O(log n) | llevar el último a la raíz y bajar |
| `desde_lista()` | **O(n)** | construcción bottom-up de Floyd |
| `mejores(N)` | **O(N log N)** | heap auxiliar de candidatos; no depende de n y no modifica el heap |

`desde_lista` baja cada nodo interno desde el último padre hasta la raíz:
cuesta O(n) y no O(n log n) porque la mayoría de los nodos están cerca de
las hojas y casi no tienen que bajar. `mejores(N)` aprovecha que el
siguiente mejor siempre es hijo de alguno ya elegido: arranca con la raíz
y, cada vez que elige un candidato, agrega sus dos hijos. Así toca a lo
sumo 2N+1 posiciones del heap sin importar su tamaño, y el heap queda
intacto para la próxima consulta.

## Integración en la app

- `CatalogoMusical.ranking(n, criterio)` devuelve el Top-N como
  `(canción, puntaje)`. La primera vez que se usa un criterio se construye
  su heap (O(n)) y se **guarda**; las consultas siguientes no reconstruyen
  nada.
- `top_n()` (opción 5, "top 10 populares") dejó de ordenar todo el
  catálogo y usa el heap.
- `agregar_cancion()` (opción 13) inserta la canción en la lista, en el
  árbol de títulos y en **cada heap ya guardado**, en O(log n) cada uno, y
  actualiza las categorías. El ranking cambia al instante.
- Opción 12: ranking con criterio, género preferido y cantidad a elección.

## ¿Por qué un heap y no ordenar todo cada vez?

1. **Se necesita el Top-N, no el orden total.** Ordenar las n canciones
   para quedarse con 10 hace trabajo de más: O(n log n) contra O(N log N).
2. **El ranking es dinámico.** Cada canción nueva obliga a ordenar de
   nuevo desde cero (O(n log n)); al heap le cuesta O(log n). Y mantener
   una lista ordenada tampoco sale gratis: insertar en el medio mueve
   elementos, O(n) por inserción.
3. **Cambiar de criterio** (otros pesos, otro género preferido) cambia
   todas las prioridades: reconstruir el heap cuesta O(n); reordenar,
   O(n log n).
4. **La consulta Top-N queda independiente del tamaño del catálogo**: con
   100.000 canciones sigue haciendo unas 55 comparaciones.

## Resultados medidos (`comparacion_heap_vs_sort.py`)

Catálogos sintéticos, criterio equilibrado, Top-10. Los tiempos de la
estrategia "ordenar todo" y del armado del heap incluyen calcular la
prioridad de las n canciones. Dato en `resultados_heap_vs_sort.csv`.

**Escenario 1 — consulta única** (catálogo recién cargado, un solo Top-10):

| n | Ordenar todo (ms) | Heap: construir (ms) | Heap: consulta (ms) |
|---:|---:|---:|---:|
| 1.000 | 0.57 | 1.11 | 0.047 |
| 10.000 | 6.10 | 10.97 | 0.052 |
| 100.000 | 84.93 | 224.71 | 0.070 |

**Comparaciones realizadas** (mide el algoritmo, no la máquina):

| n | Ordenar todo | Heap: construir | Heap: Top-10 |
|---:|---:|---:|---:|
| 1.000 | 8.641 | 1.855 | 54 |
| 10.000 | 119.827 | 18.866 | 52 |
| 100.000 | 1.528.975 | 187.973 | 55 |

**Escenario 2 — ranking dinámico** (entra una canción nueva y se pide el
Top-10, promedio por ronda sobre 50 rondas):

| n | Ordenar todo (ms) | Heap (ms) | Speedup |
|---:|---:|---:|---:|
| 1.000 | 0.61 | 0.0193 | 31.7x |
| 10.000 | 6.32 | 0.0185 | 342.2x |
| 100.000 | 85.48 | 0.0235 | **3.641x** |

En todas las corridas se verificó que ambas estrategias devuelven
exactamente el mismo Top-10.

## Lectura de los resultados

- Las **comparaciones** confirman la teoría. Ordenar crece como n log n
  (8.641 → 119.827 → 1.528.975). Construir el heap crece linealmente, unas
  1,9n (1.855 → 18.866 → 187.973). Y el Top-10 se queda en ~55 comparaciones
  aunque el catálogo sea 100 veces más grande.
- En la **consulta única, el tiempo favorece a `sorted()`**: con 100.000
  canciones tarda 85 ms contra 225 ms de construir el heap. No contradice
  la teoría: `sorted()` está implementado en C y este heap en Python puro,
  así que cada comparación del heap cuesta muchísimo más. Con una sola
  consulta y sin cambios posteriores, ordenar es perfectamente razonable.
- En el **ranking dinámico** el heap gana por mucho y la ventaja crece con
  el tamaño (31x, 342x, 3.641x): el heap ya construido absorbe cada canción
  nueva y responde el Top-10 en ~0,02 ms sin importar cuántas canciones
  haya, mientras que ordenar vuelve a pagar O(n log n) en cada ronda.

## Conclusión técnica

El heap es la estructura correcta para el ranking de MUSICTCN porque el
ranking es **dinámico y se consulta muchas veces**. Se paga una vez la
construcción, O(n); cada canción nueva cuesta O(log n); y cada Top-N
cuesta O(N log N), sin tocar el resto del catálogo. Ordenar todo cada vez
es la peor opción justamente en ese caso: repite un trabajo de O(n log n)
para descartar casi todo el resultado.

Ordenar sigue siendo una buena opción cuando hay **una sola consulta
sobre datos que no cambian**, y en ese caso no hace falta ningún heap.
También existe una variante para consulta única con N chico (un heap
acotado de tamaño N recorre el catálogo una sola vez en O(n log N)), pero
no sirve para el caso dinámico porque no conserva el resto del catálogo.

Limitación: cada criterio distinto guarda su propio heap en memoria
(O(n) por criterio). Con los pocos criterios de la app no es un problema;
con muchísimos criterios distintos habría que descartar los menos usados.
