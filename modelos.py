"""
modelos.py
Clases principales del dominio de MUSICTCN.

Todas las clases usan atributos "privados" (prefijo _) y exponen
el acceso a través de @property (getters). Donde tiene sentido,
también se agregan setters con validación básica.
"""


class Cancion:
    """Representa una canción del catálogo."""

    def __init__(self, id_cancion: int, titulo: str, artista: str,
                 genero: str, anio: int, popularidad: int):
        self._id = id_cancion
        self._titulo = titulo
        self._artista = artista
        self._genero = genero  # Los géneros que manejamos: kpop, rap, rock, pop, etc.
        self._anio = anio
        self._popularidad = popularidad  # Puntaje del 1 al 100

    # --- Getters (propiedades de solo lectura) ---
    @property
    def id(self) -> int:
        return self._id

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def artista(self) -> str:
        return self._artista

    @property
    def genero(self) -> str:
        return self._genero

    @property
    def anio(self) -> int:
        return self._anio

    @property
    def popularidad(self) -> int:
        return self._popularidad

    # --- Setter con validación (ejemplo de encapsulamiento real) ---
    @popularidad.setter
    def popularidad(self, valor: int):
        if not (0 <= valor <= 100):
            raise ValueError("La popularidad debe estar entre 0 y 100")
        self._popularidad = valor

    def __str__(self):
        return (f"[{self._id}] {self._titulo} - {self._artista} "
                f"({self._genero}) - Año: {self._anio} - "
                f"Popularidad: {self._popularidad}")

    def __repr__(self):
        return f"Cancion(id={self._id}, titulo={self._titulo!r})"


class Artista:
    """Agrupa la información de un artista y sus canciones dentro del catálogo."""

    def __init__(self, nombre: str):
        self._nombre = nombre
        self._canciones = []  # lista protegida de objetos Cancion

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def canciones(self):
        # devolvemos una copia para no exponer la lista interna
        return list(self._canciones)

    def agregar_cancion(self, cancion: "Cancion"):
        if cancion.artista != self._nombre:
            raise ValueError("La canción no pertenece a este artista")
        self._canciones.append(cancion)

    @property
    def generos(self):
        return sorted({c.genero for c in self._canciones})

    @property
    def popularidad_promedio(self) -> float:
        if not self._canciones:
            return 0.0
        return sum(c.popularidad for c in self._canciones) / len(self._canciones)

    def __str__(self):
        return f"{self._nombre} - {len(self._canciones)} canción(es) - géneros: {', '.join(self.generos)}"


class Genero:
    """Agrupa canciones que comparten un mismo género musical."""

    def __init__(self, nombre: str):
        self._nombre = nombre
        self._canciones = []

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def canciones(self):
        return list(self._canciones)

    def agregar_cancion(self, cancion: "Cancion"):
        if cancion.genero != self._nombre:
            raise ValueError("La canción no pertenece a este género")
        self._canciones.append(cancion)

    def __str__(self):
        return f"{self._nombre} ({len(self._canciones)} canciones)"
