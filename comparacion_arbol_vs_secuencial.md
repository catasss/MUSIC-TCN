# Objetivo 3 — Árbol Binario de Búsqueda: comparación de estrategias

## Clave de ordenamiento elegida

**Título de la canción.** Se descartaron `rating`/popularidad y `año`
porque no son claves naturales de búsqueda para el usuario (nadie busca
"la canción con popularidad 87"); el título es, en la práctica, lo que
el usuario escribe en un buscador de música. Ordenar por título también
habilita, gratis, dos funcionalidades reales adicionales: listar el
catálogo alfabéticamente sin volver a ordenarlo (recorrido inorder) y
autocompletar mientras el usuario escribe (búsqueda por prefijo).

## Dónde vive el árbol y cómo se integra (no es un árbol de juguete)

- **`arbol_canciones.py`** — la clase `ArbolCanciones`: inserción,
  búsqueda exacta, búsqueda por prefijo, y los tres recorridos.
- **`gestor_musica.py`** (`CatalogoMusical`) — mantiene el árbol
  **sincronizado** con los datos: se reconstruye automáticamente cada
  vez que se cargan canciones (`_reconstruir_arbol()`, llamado desde
  `cargar_desde_json`, `cargar_desde_csv` y `cargar_desde_lista`).
  Expone tres métodos reales que usan el árbol:
  - `buscar_titulo_exacto(titulo)` — búsqueda exacta O(log n) en vez de
    recorrer las n canciones.
  - `autocompletar(prefijo, max_resultados)` — sugerencias mientras se
    escribe, usando `buscar_por_prefijo` del árbol.
  - `listar_ordenado_por_titulo()` — recorrido inorder, en vez de
    ordenar la lista con `sort()` en cada llamada.
- **`main.py`** (v2) — el menú del programa tiene tres opciones nuevas
  que llaman directamente a esos métodos: **"2. Buscar canción por
  título exacto (árbol)"**, **"3. Autocompletar título (árbol)"** y
  **"7. Listar ordenado alfabéticamente (árbol - inorder)"**. No es una
  demo aislada: es parte del menú real que ya usa el usuario.

## Inserción, búsqueda y recorridos

| Operación | Método | Complejidad |
|---|---|---|
| Insertar | `ArbolCanciones.insertar()` | O(log n) promedio, O(n) peor caso |
| Buscar exacto | `ArbolCanciones.buscar()` | O(log n) promedio, O(n) peor caso |
| Buscar por prefijo | `ArbolCanciones.buscar_por_prefijo()` | O(log n + m), m = resultados |
| Recorrido inorder | `ArbolCanciones.recorrido_inorder()` | O(n) — visita cada nodo una vez, en orden alfabético |
| Recorrido preorder | `ArbolCanciones.recorrido_preorder()` | O(n) — raíz, izquierda, derecha |
| Recorrido postorder | `ArbolCanciones.recorrido_postorder()` | O(n) — izquierda, derecha, raíz |

El caso promedio O(log n) se sostiene porque `construir_balanceado()`
inserta las canciones en **orden aleatorio** (no en orden alfabético),
evitando que el árbol degenere en una cadena. Esto está verificado con
pruebas (ver abajo).

## Pruebas (`test_arbol_canciones.py`)

14 pruebas unitarias con `unittest`, todas en verde:

- Inserción y búsqueda: árbol vacío, un elemento, varios elementos,
  título inexistente, título duplicado (reemplaza sin duplicar nodo).
- Recorridos: sobre el árbol de ejemplo de la consigna
  (`Matrix` con hijos `Inception`/`Titanic`) se verifica que inorder da
  `[Inception, Matrix, Titanic]`, preorder da `[Matrix, Inception,
  Titanic]` y postorder da `[Inception, Titanic, Matrix]`; y sobre un
  árbol de 500 canciones se verifica que el inorder siempre coincide con
  `sorted()`.
- Búsqueda por prefijo: coincidencias ordenadas, prefijo sin resultados,
  respeta `max_resultados`, prefijo vacío devuelve todo, y una
  verificación cruzada contra fuerza bruta con 300 canciones y varios
  prefijos.

```bash
python3 -m unittest test_arbol_canciones.py -v
# Ran 14 tests in 0.005s — OK
```

## Comparación contra la búsqueda secuencial

Script: `comparacion_arbol_vs_secuencial.py`. Misma metodología que ya
se usó en el TP2 (catálogos sintéticos, 200 búsquedas por tamaño, mitad
títulos existentes y mitad inexistentes, promediadas con
`time.perf_counter()`, semilla fija para reproducibilidad). La
"búsqueda secuencial" es la misma estrategia de línea base del TP2:
recorrer la lista comparando título por título.

### Resultados medidos

| N | Secuencial (ms) | Árbol (ms) | Construcción del árbol (ms) | Speedup |
|---:|---:|---:|---:|---:|
| 100     | 0.0023 | 0.0006 | 0.12   | 3.7x |
| 1.000   | 0.0203 | 0.0009 | 1.90   | 22.1x |
| 10.000  | 0.2407 | 0.0013 | 27.54  | 185.2x |
| 100.000 | 2.2651 | 0.0028 | 509.75 | **812.3x** |

(también en `resultados_arbol_vs_secuencial.csv`)

### Lectura

- La **secuencial** crece proporcional a n (al multiplicar n por 10, el
  tiempo se multiplica por ~9-12x cada vez): la firma de **O(n)**.
- El **árbol** apenas crece (de 0.0006 ms a 0.0028 ms al pasar de 100 a
  100.000 elementos, un factor de 4.7x mientras n creció 1.000x): la
  firma de **O(log n)**.
- La ventaja se dispara con el tamaño: de 3.7x con 100 canciones a
  **812x** con 100.000. Con un catálogo real de streaming (millones de
  canciones), esta diferencia es la que separa una búsqueda instantánea
  de una que tarda segundos.
- **Construir el árbol no es gratis** (510 ms con 100.000 canciones),
  pero es un costo único al cargar el catálogo (`_reconstruir_arbol()`
  se llama una vez por carga, no en cada búsqueda), que se amortiza
  apenas el usuario hace un puñado de búsquedas.

## Conclusión técnica

Para la operación crítica de MUSICTCN —buscar una canción, muchas veces,
sobre un catálogo que se carga una vez y después se consulta
repetidamente— el **árbol binario de búsqueda es la estrategia
correcta**, y no por una diferencia marginal: a partir de unos pocos
miles de canciones la búsqueda secuencial deja de ser viable para una
app interactiva, mientras que el árbol se mantiene prácticamente
instantáneo. Por eso en la v2 el árbol no quedó como una estructura de
datos aislada: reemplaza la forma en que el sistema resuelve la
búsqueda exacta por título, el autocompletado y el listado ordenado,
que son necesidades reales del usuario, no ejercicios de práctica.

La búsqueda secuencial (`buscar()`, opción 1 del menú) se mantuvo
para el caso de **coincidencia parcial** en título o artista (ej.
"dyna" encuentra "Dynamite"): esa no es una búsqueda por clave exacta,
así que el árbol —ordenado por título completo— no puede resolverla más
rápido que O(n); ahí sigue siendo la estrategia correcta.
