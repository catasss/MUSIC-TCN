# TP 2 — Complejidad: ¿Qué tan rápido es?

## Operación crítica elegida

**Filtrar canciones por género con una popularidad mínima** (la operación
que ya estaba en `experimento.py`: `filtrar_canciones(catalogo, genero_buscado='Rock', popularidad_min=50)`).

## Nota sobre el punto de partida

El `experimento.py` original medía **una sola estrategia** (recorrido
lineal) para la operación de filtrado. Se actualizó ese mismo archivo
para que incluya y mida también una **segunda estrategia** (índice por
género + búsqueda binaria) sobre la misma necesidad, así el experimento
compara dos formas de resolver exactamente lo mismo. `estrategias_busqueda.py`
(secuencial vs. árbol) sigue aparte porque resuelve una operación
distinta —buscar por título exacto, no filtrar por género/popularidad—;
si preferís usarla como operación crítica del TP en vez del filtrado,
se puede rehacer el experimento con esa operación.

## Las dos estrategias comparadas

| Estrategia | Función en `experimento.py` | Idea |
|---|---|---|
| 1. Filtrado lineal | `filtrar_canciones()` | Recorre **todo** el catálogo, canción por canción, comparando género y popularidad. |
| 2. Filtrado indexado | `construir_indice_por_genero()` + `filtrar_indexado()` | Agrupa las canciones por género una sola vez y ordena cada grupo por popularidad. Cada consulta usa **búsqueda binaria** (`bisect`) para saltar directo al punto donde empiezan los resultados, sin recorrer el resto del catálogo. |

## Notación de complejidad

| Estrategia | Construcción previa | Por consulta | Espacial |
|---|---|---|---|
| Filtrado lineal | — (no necesita preprocesar nada) | **Θ(n)** — siempre recorre las n canciones, sin importar cuántas cumplan el filtro | O(1) extra |
| Filtrado indexado | **O(n log n)** — una sola vez, al cargar el catálogo | **O(log k + m)** — k = canciones de ese género, m = resultados que cumplen el filtro | O(n) para el índice |

El filtrado lineal es Θ(n) porque **siempre** tiene que mirar cada canción
para decidir si cumple o no la condición, sin atajos.

El filtrado indexado separa el costo en dos partes: `O(log k)` para
encontrar, por búsqueda binaria, dónde empiezan las canciones que superan
la popularidad mínima dentro del género (en vez de revisar canciones de
otros géneros, ya las descartó al agrupar), más `O(m)` inevitable para
devolver los m resultados (copiar la respuesta cuesta lo que cuesta,
ninguna estrategia puede evitarlo).

## Metodología del experimento

Script: `experimento.py` (versión actualizada; conserva `filtrar_canciones()`
tal cual estaba en el original y agrega las funciones de la estrategia 2).

- Catálogos sintéticos de **100, 1.000 y 100.000** canciones (los mismos
  tamaños que ya habían elegido), con género al azar entre Rock/Pop/Kpop/Rap
  y popularidad al azar entre 1 y 100.
- Se mide, para cada tamaño: el tiempo del filtrado lineal, el tiempo de
  **construir** el índice (costo único), y el tiempo de **consultar** el
  índice ya construido.
- Cada medición se repite 30 veces y se promedia, para reducir el ruido
  de mediciones tan rápidas (`time.perf_counter()`).

## Resultados medidos

**Filtro original (popularidad ≥ 50 — devuelve muchos resultados, ~12% del catálogo):**

| N | Filtrado lineal (s) | Índice: construcción (s) | Índice: consulta (s) | Speedup |
|---:|---:|---:|---:|---:|
| 100     | 0.000005 | 0.000036 | 0.00000052 | 9.5x |
| 1.000   | 0.000036 | 0.000260 | 0.00000070 | 52.1x |
| 100.000 | 0.004408 | 0.031986 | 0.00009239 | 47.7x |

**Filtro más selectivo (popularidad ≥ 95 — devuelve pocos resultados, ~1.5% del catálogo):**

| N | m (resultados) | Filtrado lineal (s) | Índice: consulta (s) | Speedup |
|---:|---:|---:|---:|---:|
| 100     | 1     | 0.0000039 | 0.00000058 | 6.6x |
| 1.000   | 16    | 0.0000287 | 0.00000058 | 49.5x |
| 100.000 | 1.481 | 0.0038045 | 0.00000895 | **425x** |

(la primera tabla también queda guardada en `resultados_experimento_tp2.csv`, generado por el `experimento.py` actualizado)

## Lectura de los resultados

- **Filtrado lineal**: al multiplicar N por 100 (de 1.000 a 100.000), el
  tiempo se multiplica por ~122x, un crecimiento aproximadamente
  proporcional a N — la firma de **O(n)**. No importa qué tan selectivo
  sea el filtro: siempre recorre todo el catálogo.
- **Filtrado indexado**: con el filtro selectivo, la consulta pasa de
  0.00000058 s a 0.00000895 s al pasar de 1.000 a 100.000 elementos — un
  crecimiento muchísimo más lento que N, compatible con `O(log k + m)`
  cuando m es chico.
- **El tamaño de m importa mucho**: con el filtro original (popularidad≥50,
  que deja pasar ~1 de cada 8 canciones), la consulta indexada en
  N=100.000 tarda 0.0000924 s — sigue siendo ~48x más rápida que la
  lineal, pero mucho menos espectacular que las 425x del filtro
  selectivo. Esto pasa porque, cuando el filtro deja pasar muchas
  canciones, copiar esos m resultados empieza a pesar tanto como la
  búsqueda binaria en sí. La ventaja teórica de O(log k) solo se nota
  del todo cuando la consulta es selectiva (m chico); si m crece
  proporcional a n, el costo de "armar la respuesta" también crece
  proporcional a n, aunque encontrarla sea casi instantáneo.
- **La construcción del índice no es gratis**: con 100.000 canciones
  cuesta ~0.032 s. Es un pago único al cargar el catálogo, no por cada
  consulta.

## Comparación y conclusión técnica

**¿Cuál conviene?**

- Si el catálogo se carga **una vez** al iniciar el programa y después se
  hacen **muchas consultas de filtrado** durante la sesión —el escenario
  típico de una app tipo MUSICTCN, donde el usuario prueba varios
  géneros y umbrales de popularidad desde el menú—, el **filtrado
  indexado conviene claramente**. El costo de construir el índice (31 ms
  con 100.000 canciones) se paga una sola vez y se amortiza con la
  primera o segunda consulta; a partir de ahí, cada filtro es entre 6x y
  más de 400x más rápido que recorrer todo el catálogo, dependiendo de
  qué tan selectivo sea el filtro.
- La ventaja es **mayor cuanto más selectivo es el filtro** (pocos
  resultados sobre un catálogo grande) y **menor cuando el filtro deja
  pasar una fracción grande del catálogo** — en ese caso extremo, el
  costo de devolver los resultados domina y ambas estrategias tienden a
  parecerse más (aunque el índice sigue ganando).
- Si el catálogo **cambia constantemente** (se agregan/eliminan
  canciones todo el tiempo) y solo se hace **una consulta** entre cada
  cambio, reconstruir el índice en cada modificación puede no valer la
  pena frente a la simplicidad del filtrado lineal.

**Conclusión:** para el caso de uso real —catálogo que se carga una vez y
se consulta muchas veces, con filtros normalmente selectivos (un género
puntual, popularidad alta)— el **filtrado indexado (O(log k + m)) es la
estrategia técnicamente superior**, y la diferencia se vuelve dramática
(cientos de veces más rápido) a medida que el catálogo crece y el filtro
es más específico. El filtrado lineal (O(n)) sigue siendo razonable para
catálogos chicos, para prototipos rápidos, o si el catálogo cambia tanto
que mantener un índice actualizado no compensa.
