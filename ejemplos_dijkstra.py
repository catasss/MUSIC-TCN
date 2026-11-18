"""Caso de prueba del TP9: camino mínimo entre artistas. Salida en ejemplos_dijkstra.txt"""
from grafo_ponderado import construir_grafo_artistas

generos = {a: ["pop"] for a in ["Dua Lipa", "Harry Styles", "The Weeknd", "Taylor Swift", "Billie Eilish"]}
popularidad = {"Dua Lipa": 95, "Harry Styles": 88, "The Weeknd": 80, "Taylor Swift": 72, "Billie Eilish": 60}
g = construir_grafo_artistas(generos, popularidad)

origen, destino = "Dua Lipa", "Billie Eilish"
print(f"Grafo: {g}")
bfs = g.camino_mas_corto(origen, destino)
dij, costo = g.camino_minimo(origen, destino)
print(f"\nBFS (menos saltos):  {' -> '.join(bfs)}  | saltos {len(bfs)-1} | costo {g.costo_de(bfs):.2f}")
print(f"Dijkstra (menor costo): {' -> '.join(dij)}  | saltos {len(dij)-1} | costo {costo:.2f}")
print("\nDijkstra rodea por artistas intermedios porque un salto grande de "
      "popularidad cuesta mucho más que varios chicos.")
