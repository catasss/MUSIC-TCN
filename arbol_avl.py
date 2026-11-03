""" 
Misión 4: AVL - El árbol también puede enfermarse
Comparamos BST vs AVL
"""

# ---------------------------------------
# 1.BST común (para que comparemos)
#------------------------------------

class NodoBST:
    def __init__(self, clave):
        self.clave = clave 
        self.izq = None
        self.der = None

class BST:
    def __init__(self):
        self.raiz = None

    def insertar(self, clave):
        self.raiz = self._insertar(self.raiz, clave)

    def _insertar(self, nodo, clave):
        if nodo is None:
            return NodoBST(clave)
        if clave < nodo.clave:
            nodo.izq = self._insertar(nodo.izq, clave)
        elif clave > nodo.clave:
            nodo.der = self._insertar(nodo.der, clave)
            return nodo

def altura(self)>
    return self._altura(self.raiz)

def _altura(self, nodo):
    if nodo is None:
        return 0
    return 1 + max(self._altura(nod.izq), self._altura(nodo.der))

def buscar(self, clave):
    """Devuelve (encontrrado, cantidad_de_comparacione)"""
    return self._buscar(self.raiz, clave, 0)

def _buscar(self, nodo, clave, comparaciones):
    if nodo is None:
        return (False, comparaciones)
    comparaciones += 1
    if clave == nodo.clave:
        return (True, comparaciones)
    elif clave < nodo.clave:
        return self._buscar(nodo.izq, clave, comparaciones)
    else:
        return self._buscar(nodo.der, clave, comparaciones)

def imprimir(self):
    """Imprime el arbol en formato ASCII"""
    self._imprimir(self.raiz, "", True)

def _imprimir(self, nodo, prefijo, es_ultimo):
    if nodo is None:
        return 
    conector = "└── " if es_ultimo else "├── "
    print(f"{prefijo}{conector}{nodo.clave}")
    nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
    hijos = []
    if nodo.izq:
        hijos.append(nodo.izq, False)
        if nodo.der:
            hijos.append(nodo.der, True)
        for i, (hijo, _) in enumerate(hijos):
            self._imprimir(hijo, nuevo_prefijo, i == len(hijos) - 1)


#---------------------------------------
# 2. AVL Tree con rotaciones
#------------------------------------

class NodoAVL:
    def __init__(self, clave):
        self.clave = clave
        self.izq = None
        self.der = None
        self.altura = 1


class AVL:
    def __init__(self):
        self.raiz = None

    # --- Utilidades ---

    @staticmethod
    def _altura(nodo):
        return nodo.altura if nodo else 0

    @staticmethod
    def _balance(nodo):
        return AVL._altura(nodo.izq) - AVL._altura(nodo.der) if nodo else 0

    def _actualizar(self, nodo):
        nodo.altura = 1 + max(self._altura(nodo.izq), self._altura(nodo.der))

    # --- Rotaciones ---

    def _rotar_derecha(self, y):
        """Rotación derecha (caso LL)."""
        x = y.izq
        T2 = x.der
        x.der = y
        y.izq = T2
        self._actualizar(y)
        self._actualizar(x)
        return x

    def _rotar_izquierda(self, x):
        """Rotación izquierda (caso RR)."""
        y = x.der
        T2 = y.izq
        y.izq = x
        x.der = T2
        self._actualizar(x)
        self._actualizar(y)
        return y

    # --- Inserción ---

    def insertar(self, clave):
        self.raiz = self._insertar(self.raiz, clave)

    def _insertar(self, nodo, clave):
        if nodo is None:
            return NodoAVL(clave)

        if clave < nodo.clave:
            nodo.izq = self._insertar(nodo.izq, clave)
        elif clave > nodo.clave:
            nodo.der = self._insertar(nodo.der, clave)
        else:
            return nodo  # no duplicados

        self._actualizar(nodo)
        balance = self._balance(nodo)

        # Caso LL
        if balance > 1 and clave < nodo.izq.clave:
            return self._rotar_derecha(nodo)

        # Caso RR
        if balance < -1 and clave > nodo.der.clave:
            return self._rotar_izquierda(nodo)

        # Caso LR
        if balance > 1 and clave > nodo.izq.clave:
            nodo.izq = self._rotar_izquierda(nodo.izq)
            return self._rotar_derecha(nodo)

        # Caso RL
        if balance < -1 and clave < nodo.der.clave:
            nodo.der = self._rotar_derecha(nodo.der)
            return self._rotar_izquierda(nodo)

        return nodo

    # --- Búsqueda ---

    def buscar(self, clave):
        """Devuelve (encontrado, cantidad_de_comparaciones)."""
        return self._buscar(self.raiz, clave, 0)

    def _buscar(self, nodo, clave, comparaciones):
        if nodo is None:
            return (False, comparaciones)
        comparaciones += 1
        if clave == nodo.clave:
            return (True, comparaciones)
        elif clave < nodo.clave:
            return self._buscar(nodo.izq, clave, comparaciones)
        else:
            return self._buscar(nodo.der, clave, comparaciones)

    # --- Imprimir ---

    def imprimir(self):
        self._imprimir(self.raiz, "", True)

    def _imprimir(self, nodo, prefijo, es_ultimo):
        if nodo is None:
            return
        conector = "└── " if es_ultimo else "├── "
        print(f"{prefijo}{conector}{nodo.clave} (h={nodo.altura})")
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
        hijos = []
        if nodo.izq:
            hijos.append(nodo.izq)
        if nodo.der:
            hijos.append(nodo.der)
        for i, hijo in enumerate(hijos):
            self._imprimir(hijo, nuevo_prefijo, i == len(hijos) - 1)


# ─────────────────────────────────────────────
# 3. Demo comparativa
# ─────────────────────────────────────────────

def demo_comparativa():
    """
    Inserta títulos en orden alfabético (caso desbalance)
    y compara BST vs AVL.
    """
    # Títulos en orden alfabético → degenera el BST
    titulos_ordenados = [
        "Aurora", "Bailando", "Cielo", "Danza", "Estrella",
        "Fuego", "Girasol", "Horizonte", "Ilusión", "Jardín",
        "Karma", "Luna", "Marea", "Noche", "Océano",
        "Pájaros", "Quimera", "Río", "Sombra", "Trovador"
    ]

    print("=" * 60)
    print("  MISIÓN 4: BST vs AVL — Caso desbalance")
    print("  Insertando títulos en orden alfabético")
    print("=" * 60)

    # --- BST común ---
    bst = BST()
    for t in titulos_ordenados:
        bst.insertar(t)

    # --- AVL ---
    avl = AVL()
    for t in titulos_ordenados:
        avl.insertar(t)

    n = len(titulos_ordenados)

    print(f"\n Datos: {n} títulos insertados en orden alfabético\n")

    # Altura
    h_bst = bst.altura()
    h_avl = avl.altura()
    print(f"  Altura BST: {h_bst}  (degenerado, tipo lista enlazada)")
    print(f"  Altura AVL: {h_avl}  (balanceado, O(log n))")
    print(f"  → La AVL es {h_bst // h_avl}x más baja\n")

    # Búsqueda del último elemento (peor caso)
    ultimo = titulos_ordenados[-1]
    _, comp_bst = bst.buscar(ultimo)
    _, comp_avl = avl.buscar(ultimo)
    print(f"  Búsqueda de '{ultimo}' (peor caso):")
    print(f"    BST: {comp_bst} comparaciones")
    print(f"    AVL: {comp_avl} comparaciones")
    print(f"    → La AVL usa {comp_bst - comp_avl} menos comparaciones\n")

    # Búsqueda del primer elemento
    primero = titulos_ordenados[0]
    _, comp_bst2 = bst.buscar(primero)
    _, comp_avl2 = avl.buscar(primero)
    print(f"  Búsqueda de '{primero}':")
    print(f"    BST: {comp_bst2} comparaciones")
    print(f"    AVL: {comp_avl2} comparaciones\n")

    # Imprimir árboles
    print("   BST (degenerado):")
    bst.imprimir()
    print()
    print("   AVL (balanceado):")
    avl.imprimir()

    print("\n" + "=" * 60)
    print("  CONCLUSIÓN")
    print("=" * 60)
    print("""
  • BST con inserción ordenada → altura = n (O(n) por operación)
  • AVL con las mismas inserciones → altura = O(log n)
  • Para n=20: BST hace hasta 20 comparaciones, AVL solo ~5
  • Para n=1000: BST → 1000, AVL → ~10
  • El balance NO es opcional: es lo que garantiza la
    complejidad O(log n) que hace útil al árbol.
""")


# ─────────────────────────────────────────────
# 4. Punto de entrada (ejecutar directamente)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    demo_comparativa()


input("\nPresioná Enter para salir...")   

















