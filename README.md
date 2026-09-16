# MUSIC-TCN

Programa de terminal para explorar un catálogo de canciones: buscar por título/artista, listar, filtrar por género/año/popularidad y ver un top 10.

Esta v1 cubre la **Misión 1: "Construí el corazón del sistema"** — transformar la idea en un programa funcional mínimo.

## Estructura del proyecto

```
musictcn/
├── main.py              # Interfaz de terminal (menú, entrada del usuario)
├── modelos.py            # Clases del dominio: Cancion, Artista, Genero
├── gestor_musica.py       # Clase CatalogoMusical: carga de datos y operaciones
├── datos/
│   ├── canciones.json     # Datos de prueba (formato JSON)
│   └── canciones.csv      # Los mismos datos de prueba en CSV
├── demo_v1.txt            # Transcripción de una sesión de ejemplo
└── README.md
```

### Diseño

- **`modelos.py`** define las clases del dominio (`Cancion`, `Artista`, `Genero`).
  Los atributos son privados (prefijo `_`) y se exponen mediante `@property`
  (getters), con al menos un setter validado (`Cancion.popularidad`) como
  ejemplo de encapsulamiento real.
- **`gestor_musica.py`** es la interfaz entre los datos crudos y el resto del
  programa: `CatalogoMusical` sabe cargar canciones desde JSON o CSV, y
  expone las operaciones `buscar()`, `listar()` y `filtrar()`, además de
  utilidades (`top_n()`, `generos_disponibles()`).
- **`main.py`** solo se encarga de la interfaz de terminal (menú, `input()`,
  `print()`); nunca lee archivos directamente ni conoce el formato de los
  datos — esa responsabilidad es de `gestor_musica.py`. Así los módulos
  quedan desacoplados.

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
1. Buscar canción o artista
2. Explorar géneros (k-pop, rap, rock, pop, ...)
3. Ver top 10 de canciones populares
4. Listar todo el catálogo
5. Filtrar canciones
6. Explorar conexiones entre artistas (próximamente)
7. Obtener recomendaciones personalizadas (próximamente)
0. Salir
----------------------------------------
```

Elegí una opción escribiendo el número y presionando Enter.

## Operaciones implementadas en v1

| # | Operación | Descripción |
|---|-----------|-------------|
| 1 | Buscar    | Búsqueda parcial (sin distinguir mayúsculas) por título o artista |
| 2 | Explorar géneros | Lista los géneros disponibles y filtra por el elegido |
| 3 | Top 10    | Las 10 canciones con mayor popularidad |
| 4 | Listar    | Lista todo el catálogo, con orden opcional (título, artista, año, popularidad) |
| 5 | Filtrar   | Filtra combinando género, rango de años y popularidad mínima |

Las opciones **6** (conexiones entre artistas) y **7** (recomendaciones
personalizadas) quedan planteadas en el menú pero marcadas como
"próximamente": requieren modelar colaboraciones entre artistas (un grafo)
y un perfil de usuario, que no forman parte del alcance mínimo de esta v1.

## Datos de prueba

`datos/canciones.json` contiene 15 canciones de ejemplo cubriendo los
géneros k-pop, rap, rock, pop y folk, con año y popularidad variados para
poder probar todas las operaciones (incluyendo casos sin resultados).
`datos/canciones.csv` tiene la misma información en CSV, y
`CatalogoMusical.cargar_desde_csv()` permite usarla en lugar del JSON si
se prefiere (basta con cambiar `RUTA_DATOS` en `main.py`).

## Demo de la v1

El archivo `demo_v1.txt` contiene la transcripción completa de una sesión
de ejemplo (buscar "BTS", explorar el género k-pop, ver el top 10 y salir),
generada corriendo el programa real.

## Próximos pasos (fuera del alcance de v1)

- Clase `Usuario` con gustos/historial para recomendaciones personalizadas.
- Modelo de grafo de colaboraciones entre artistas (opciones 5 "conexiones"
  y "camino de colaboraciones" del enunciado original).
- Persistencia de cambios (agregar/editar canciones) más allá de la carga
  inicial de datos.
