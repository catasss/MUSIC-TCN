"""
main_v6.py
Punto de entrada de la aplicación MUSIC-TCN v6. Incorpora la opción del TP 8:
Recorridos BFS y DFS para explorar la red musical.
"""

from gestor_musica_v6 import CatalogoMusicalV6


def menu_recorridos(gestor: CatalogoMusicalV6):
    print("\n--- EXPLORACIÓN DE LA RED (TP 8: BFS / DFS) ---")
    artista = input("Ingrese el nombre del artista de origen: ").strip()

    if not gestor.grafo_artistas.tiene_vertice(artista):
        print(f"❌ El artista '{artista}' no se encuentra en la red.")
        return

    print("\n1. [BFS] Encontrar el artista relacionado más cercano")
    print("2. [DFS] Explorar en profundidad toda la red desde el artista")
    opcion = input("Seleccione una opción (1-2): ").strip()

    if opcion == "1":
        cercano = gestor.consultar_artista_mas_cercano_bfs(artista)
        if cercano:
            print(f"\n🔍 [BFS] El artista más cercano a '{artista}' es: **{cercano}** (distancia = 1 arista).")
        else:
            print(f"\n🔍 [BFS] El artista '{artista}' no tiene conexiones.")
    elif opcion == "2":
        red = gestor.explorar_comunidad_profundidad_dfs(artista)
        print(f"\n🌲 [DFS] Orden de exploración exhaustiva en profundidad ({len(red)} artistas alcanzables):")
        for i, a in enumerate(red, start=1):
            print(f"  {i}. {a}")
    else:
        print("Opción inválida.")


def main():
    gestor = CatalogoMusicalV6()
    gestor.cargar_canciones_json("datos/canciones.json")
    
    while True:
        print("\n=== MUSIC-TCN (Versión 6 - TP8 Recorridos) ===")
        print("1. Buscar / Listar catálogo")
        print("2. Recomendaciones por Prioridad (Heap)")
        print("3. Explorar Red Musical con BFS / DFS (TP8)")
        print("4. Salir")
        
        op = input("Opción: ").strip()
        if op == "1":
            print(f"Total canciones: {len(gestor.listar_todas())}")
        elif op == "2":
            print("Función de Heaps (TP7)")
        elif op == "3":
            menu_recorridos(gestor)
        elif op == "4":
            print("¡Hasta luego!")
            break


if __name__ == "__main__":
    main()