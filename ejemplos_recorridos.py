"""
ejemplos_recorridos.py
Ejemplos de recorridos y búsquedas sobre el árbol general de MUSICTCN
(TP5 - Árboles generales), usando el catálogo real de datos/.

Ejecutar con:
    python3 ejemplos_recorridos.py
    python3 ejemplos_recorridos.py > ejemplos_recorridos.txt
"""

import os

from gestor_musica_v3 import CatalogoMusical
from modelos import Cancion

CARPETA = os.path.dirname(os.path.abspath(__file__))


def titulo(texto):
    print("\n" + "=" * 64)
    print(texto)
    print("=" * 64)


def main():
    cat = CatalogoMusical()
    cat.cargar_desde_json(os.path.join(CARPETA, "datos", "canciones.json"))
    cat.cargar_categorias_desde_json(os.path.join(CARPETA, "datos", "categorias.json"))
    arbol = cat.categorias
    conteo = cat.conteo_por_categoria()

    titulo("1. El árbol (entre paréntesis, cantidad de canciones)")
    print(arbol.dibujar(etiqueta=lambda n: f"{n.nombre} ({conteo[n]})"))
    print(f"\nNodos: {arbol.cantidad()} | Niveles: {arbol.altura()} | Hojas: {len(arbol.hojas())}")

    titulo("2. PREORDEN: el padre antes que sus hijos")
    print("Uso: mostrar la jerarquía de arriba hacia abajo; también es el")
    print("orden en que 'buscar' encuentra el primer nodo con ese nombre.\n")
    print(" -> ".join(n.nombre for n in arbol.preorden()))

    titulo("3. POSTORDEN: los hijos antes que el padre")
    print("Uso: cuando el valor de un padre depende de sus hijos. Acá se")
    print("calcula cuántas canciones tiene cada categoría: cada artista cuenta")
    print("las suyas y cada nodo superior suma lo que ya calcularon sus hijos.\n")
    for nodo in arbol.postorden():
        if nodo.artista is not None:
            detalle = "artista: cuenta sus canciones"
        else:
            hijos = [f"{h.nombre}={conteo[h]}" for h in nodo.hijos]
            detalle = "suma de " + ", ".join(hijos)
        print(f"  {nodo.nombre:<20} {conteo[nodo]:>2}   ({detalle})")

    titulo("4. POR NIVELES (anchura): un nivel a la vez")
    print("Uso: ver qué tan 'ancho' es cada nivel (familias, géneros, artistas).\n")
    nombres_nivel = ["raíz", "familias", "géneros", "artistas"]
    for i, nodos in enumerate(arbol.por_niveles()):
        etiqueta = nombres_nivel[i] if i < len(nombres_nivel) else f"nivel {i}"
        print(f"  Nivel {i} ({etiqueta}): " + ", ".join(n.nombre for n in nodos))

    titulo("5. Recorrer solo un subárbol (desde 'Pop y derivados')")
    pop = arbol.buscar("Pop y derivados")
    print(arbol.dibujar(desde=pop, etiqueta=lambda n: f"{n.nombre} ({conteo[n]})"))
    print("\nPreorden desde ahí :", " -> ".join(n.nombre for n in arbol.preorden(pop)))
    print("Postorden desde ahí:", " -> ".join(n.nombre for n in arbol.postorden(pop)))
    print("Géneros que cubre  :", ", ".join(arbol.generos_de(pop)))
    print("Canciones          :")
    for c in cat.canciones_de_categoria(pop):
        print("   ", c.titulo, "-", c.artista)

    titulo("6. Búsquedas")
    nodo = arbol.buscar("k-pop")
    print("buscar('k-pop')           ->", nodo.nombre, "| ruta:", " > ".join(arbol.ruta(nodo)))
    print("buscar_parcial('pop')     ->", [n.nombre for n in arbol.buscar_parcial("pop")])
    print("buscar_por_genero('rap')  ->", arbol.buscar_por_genero("rap").nombre)
    print("buscar('Jazz')            ->", arbol.buscar("Jazz"))
    dynamite = cat.buscar_titulo_exacto("Dynamite")
    print("ruta de 'Dynamite'        ->", cat.ruta_categoria_de(dynamite))

    titulo("7. El árbol crece solo: un género nuevo cae en 'Otros'")
    extra = Cancion(99, "Cumbia Test", "Los Test", "cumbia", 2000, 50)
    cat.cargar_desde_lista(cat.listar() + [extra])
    arbol = cat.categorias
    conteo = cat.conteo_por_categoria()
    otros = arbol.buscar("Otros")
    print(arbol.dibujar(desde=otros, etiqueta=lambda n: f"{n.nombre} ({conteo[n]})"))
    print("\nruta de 'Cumbia Test'     ->", cat.ruta_categoria_de(extra))
    print(f"Total del catálogo ahora   -> {conteo[arbol.raiz]} canciones")


if __name__ == "__main__":
    main()
