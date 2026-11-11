# TP 8: Recorridos de Grafos (BFS y DFS) — MUSIC-TCN v6

Este documento detalla el análisis teórico, la justificación de uso y la complejidad computacional de los algoritmos de recorrido en grafos implementados en la **versión 6** de **MUSIC-TCN**.

---

## 1. Algoritmos Implementados

### BFS (Breadth-First Search / Búsqueda en Anchura)
* **Descripción:** Explora la red de artistas nivel por nivel. Comienza en el artista de origen, visita a todos sus vecinos directos (distancia 1 salto), luego a los vecinos de estos (distancia 2 saltos), y así sucesivamente.
* **Estructura Auxiliar:** Utiliza una **Cola (FIFO)**.
* **Propiedad Clave:** En un grafo no pesado, BFS garantiza encontrar el camino con la **menor cantidad de aristas (saltos)** entre dos nodos.

### DFS (Depth-First Search / Búsqueda en Profundidad)
* **Descripción:** Explora lo más profundo posible a lo largo de cada rama de la red antes de hacer *backtracking* (retroceder). Visita una cadena completa de relaciones hasta llegar a un extremo no visitado antes de explorar caminos alternativos.
* **Estructura Auxiliar:** Utiliza una **Pila (LIFO)**.
* **Propiedad Clave:** Es ideal para exploración exhaustiva de toda la componente conexa o la detección de estructuras compuestas dentro del grafo.

---

## 2. Casos de Uso Reales en MUSIC-TCN

### Caso de Uso 1 (BFS): Artista o Recomendación Relacionada Más Cercana
* **Consulta:** *¿Cuál es el artista relacionado más cercano a un artista dado?* (Ejemplo del enunciado: *"¿Cuál es la película/artista relacionada más cercana a Matrix?"*).
* **Algoritmo Elegido:** **BFS**.
* **Justificación:** BFS expande la búsqueda en forma radial por niveles de distancia. El primer vértice que cumple la condición durante el recorrido BFS está garantizado a estar a la menor distancia en saltos (distancia 1).

### Caso de Uso 2 (DFS): Exploración Exhaustiva de Comunidad Musical
* **Consulta:** *Explorar en profundidad toda la red conexa de artistas relacionados con un artista de origen.* (Ejemplo del enunciado: *"Explorá todas las películas/artistas relacionadas con Matrix, en profundidad"*).
* **Algoritmo Elegido:** **DFS**.
* **Justificación:** DFS recorre exhaustivamente la componente conexa completa sumergiéndose por las ramas más profundas de la red, lo que permite mapear cadenas de influencia o comunidades completas antes de cambiar de rama.

---

## 3. Análisis de Complejidad Computacional

| Algoritmo | Complejidad Temporal | Complejidad Espacial (Memoria) | Estructura Principal |
| :--- | :--- | :--- | :--- |
| **BFS** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Cola (FIFO) + Conjunto de Visitados |
| **DFS** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Pila (LIFO) + Conjunto de Visitados |

*Donde $V$ es la cantidad de vértices (artistas) y $E$ es la cantidad de aristas (conexiones por género en la red).*

### Explicación:
1. **Tiempo $\mathcal{O}(V + E)$:** En el peor de los casos (grafo totalmente conexo o al explorar toda la componente), cada vértice $V$ es ingresado/removido de la estructura auxiliar una sola vez, y cada arista $E$ se examina una vez por cada extremo (debido a la representación por Lista de Adyacencia).
2. **Memoria $\mathcal{O}(V)$:** En el peor caso, la estructura de visitados y la cola/pila guardan a lo sumo $V$ elementos.

---

## 4. Cuadro Comparativo: ¿Cuándo conviene cada uno?

| Criterio | BFS (Búsqueda en Anchura) | DFS (Búsqueda en Profundidad) |
| :--- | :--- | :--- |
| **Objetivo principal** | Encontrar caminos más cortos o elementos cercanos. | Explorar ramificaciones profundas o la totalidad del grafo. |
| **Comportamiento** | Nivel por nivel (amplitud). | Rama por rama (profundidad). |
| **Estrucutra interna** | Cola (FIFO). | Pila (LIFO) / Recursión. |
| **Uso en MUSIC-TCN** | Buscar el artista más cercano a N saltos. | Mapear la comunidad completa ramificada a partir de un artista. |