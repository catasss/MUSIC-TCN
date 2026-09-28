# MUSICTCN — v2

Programa de terminal para explorar un catálogo de canciones: buscar por
título/artista, buscar por título exacto y autocompletar (con un árbol
binario de búsqueda), listar, filtrar por género/año/popularidad y ver
un top 10.

Esta v2 incorpora el **Objetivo 3: "Poné un árbol en tu sistema"** —un
árbol binario de búsqueda ordenado por título, integrado a operaciones
reales del menú— sobre la base de la v1 (Objetivo 1: "Construí el
corazón del sistema").

## Estructura del proyecto

```
musictcn/
├── main.py                            # Interfaz de terminal (menú, entrada del usuario)
├── modelos.py                          # Clases del dominio: Cancion, Artista, Genero
├── gestor_musica.py                     # Clase CatalogoMusical: carga de datos y operaciones
├── arbol_canciones.py                   # Árbol binario de búsqueda (BST) ordenado por título
├── test_arbol_canciones.py              # Pruebas unitarias del árbol (14 tests)
├── comparacion_arbol_vs_secuencial.py   # Script de comparación de estrategias
├── comparacion_arbol_vs_secuencial.md   # Análisis de complejidad y conclusión (Objetivo 3)
├── resultados_arbol_vs_secuencial.csv   # Resultados reales de la comparación
├── datos/
│   ├── canciones.json                   # Datos de prueba (formato JSON)
│   └── canciones.csv                    # Los mismos datos de prueba en CSV
├── complejidad/                         # Objetivo 2: filtrado lineal vs. filtrado indexado
├── demo_v1.txt                          # Transcripción de una sesión de ejemplo (v1)
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
- **`gestor_musica.py`** es la interfaz entre los datos crudos y el resto
  del programa: `CatalogoMusical` sabe cargar canciones desde JSON o CSV,
  mantiene el árbol sincronizado con los datos, y expone las operaciones
  `buscar()`, `buscar_titulo_exacto()`, `autocompletar()`, `listar()`,
  `listar_ordenado_por_titulo()` y `filtrar()`, además de utilidades
  (`top_n()`, `generos_disponibles()`).
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
9. Explorar conexiones entre artistas (próximamente)
10. Obtener recomendaciones personalizadas (próximamente)
0. Salir
----------------------------------------
```

Elegí una opción escribiendo el número y presionando Enter.

## Operaciones implementadas en v2

| # | Operación | Estrategia | Descripción |
|---|-----------|-----------|-------------|
| 1 | Buscar (parcial) | Secuencial | Búsqueda parcial (sin distinguir mayúsculas) por título o artista |
| 2 | Buscar título exacto | Árbol (BST) | Búsqueda exacta O(log n) por título completo |
| 3 | Autocompletar | Árbol (BST) | Sugerencias por prefijo mientras se escribe |
| 4 | Explorar géneros | Filtrado | Lista los géneros disponibles y filtra por el elegido |
| 5 | Top 10 | Ordenamiento | Las 10 canciones con mayor popularidad |
| 6 | Listar | Ordenamiento | Lista todo el catálogo, con orden opcional |
| 7 | Listar ordenado (árbol) | Árbol (BST) | Recorrido inorder: alfabético, sin volver a ordenar |
| 8 | Filtrar | Filtrado | Filtra combinando género, rango de años y popularidad mínima |

Las opciones **9** (conexiones entre artistas) y **10** (recomendaciones
personalizadas) quedan planteadas en el menú pero marcadas como
"próximamente": requieren modelar colaboraciones entre artistas (un grafo)
y un perfil de usuario, fuera del alcance de esta v2.

## Objetivo 3: el árbol, en profundidad

Ver **`comparacion_arbol_vs_secuencial.md`** para: por qué se eligió
título como clave de ordenamiento, cómo se integra el árbol a
operaciones reales (no aisladas), y la comparación medida contra la
búsqueda secuencial (hasta **812x más rápido** con 100.000 canciones).

```bash
python3 -m unittest test_arbol_canciones.py -v      # pruebas del árbol
python3 comparacion_arbol_vs_secuencial.py            # comparación de estrategias
```

## Datos de prueba

`datos/canciones.json` contiene 15 canciones de ejemplo cubriendo los
géneros k-pop, rap, rock, pop y folk, con año y popularidad variados para
poder probar todas las operaciones (incluyendo casos sin resultados).
`datos/canciones.csv` tiene la misma información en CSV, y
`CatalogoMusical.cargar_desde_csv()` permite usarla en lugar del JSON si
se prefiere (basta con cambiar `RUTA_DATOS` en `main.py`).

## Demo de la v1

El archivo `demo_v1.txt` contiene la transcripción completa de una sesión
de ejemplo de la v1 (buscar "BTS", explorar el género k-pop, ver el top 10
y salir).

## Próximos pasos (fuera del alcance de v2)

- Clase `Usuario` con gustos/historial para recomendaciones personalizadas.
- Modelo de grafo de colaboraciones entre artistas (opciones "conexiones"
  y "camino de colaboraciones" del enunciado original).
- Balanceo automático del árbol (AVL o Rojo-Negro) para garantizar
  O(log n) incluso ante inserciones adversariales, no solo en el caso
  promedio.
- Persistencia de cambios (agregar/editar canciones) más allá de la carga
  inicial de datos.
