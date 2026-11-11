"""
prioridad.py
Función de prioridad del ranking de recomendaciones de MUSICTCN.

¿Por qué una combinación de factores y no solo la popularidad?
Ordenar solo por popularidad siempre devuelve lo mismo y no permite
"recomendar": dos canciones con la misma popularidad no se distinguen, y
el usuario no puede inclinar el ranking hacia lo que busca. Por eso la
prioridad combina tres factores, todos ajustables:

    base      = (peso_popularidad * popularidad + peso_novedad * novedad)
                / (peso_popularidad + peso_novedad)
    prioridad = base + bono_genero   (solo si el género es el preferido)

    - popularidad: el puntaje de la canción (0 a 100).
    - novedad:     qué tan reciente es, llevada a una escala de 0 a 100
                   (ANIO_MIN -> 0, ANIO_MAX -> 100).
    - bono:        puntos extra para el género que el usuario prefiere.

Al ser pesos y bono parámetros, el mismo catálogo da rankings distintos
según el criterio: eso es lo que hace al ranking "dinámico".
"""

from typing import Optional

from modelos import Cancion


class CriterioPrioridad:
    """Define cómo se calcula la prioridad de una canción.

    Es inmutable y comparable (se puede usar como clave de diccionario),
    para que el catálogo pueda guardar un heap ya construido por criterio.
    """

    ANIO_MIN = 1960   # canción de este año o anterior: novedad 0
    ANIO_MAX = 2026   # canción de este año o posterior: novedad 100

    def __init__(self, peso_popularidad: float = 1.0, peso_novedad: float = 0.0,
                 genero_preferido: Optional[str] = None, bono_genero: float = 10.0):
        if peso_popularidad < 0 or peso_novedad < 0:
            raise ValueError("Los pesos no pueden ser negativos")
        if peso_popularidad + peso_novedad == 0:
            raise ValueError("Al menos un peso debe ser mayor que cero")
        if bono_genero < 0:
            raise ValueError("El bono de género no puede ser negativo")
        self._peso_popularidad = float(peso_popularidad)
        self._peso_novedad = float(peso_novedad)
        self._genero_preferido = genero_preferido.strip().lower() if genero_preferido else None
        self._bono_genero = float(bono_genero)

    # --- presets habituales ---
    @classmethod
    def popularidad(cls, genero_preferido: Optional[str] = None) -> "CriterioPrioridad":
        return cls(1.0, 0.0, genero_preferido)

    @classmethod
    def equilibrado(cls, genero_preferido: Optional[str] = None) -> "CriterioPrioridad":
        return cls(0.7, 0.3, genero_preferido)

    @classmethod
    def novedades(cls, genero_preferido: Optional[str] = None) -> "CriterioPrioridad":
        return cls(0.3, 0.7, genero_preferido)

    # --- getters ---
    @property
    def peso_popularidad(self) -> float:
        return self._peso_popularidad

    @property
    def peso_novedad(self) -> float:
        return self._peso_novedad

    @property
    def genero_preferido(self) -> Optional[str]:
        return self._genero_preferido

    @property
    def bono_genero(self) -> float:
        return self._bono_genero

    # --- cálculo ---
    @classmethod
    def novedad(cls, anio: int) -> float:
        """Año de la canción llevado a una escala de 0 a 100."""
        escala = (anio - cls.ANIO_MIN) / (cls.ANIO_MAX - cls.ANIO_MIN) * 100
        return max(0.0, min(100.0, escala))

    def puntaje(self, cancion: Cancion) -> float:
        total = self._peso_popularidad + self._peso_novedad
        base = (self._peso_popularidad * cancion.popularidad
                + self._peso_novedad * self.novedad(cancion.anio)) / total
        if self._genero_preferido and cancion.genero.lower() == self._genero_preferido:
            base += self._bono_genero
        return base

    def __call__(self, cancion: Cancion) -> float:
        return self.puntaje(cancion)

    # --- identidad (para usarlo como clave de diccionario) ---
    def _clave(self):
        return (self._peso_popularidad, self._peso_novedad,
                self._genero_preferido, self._bono_genero)

    def __eq__(self, otro):
        return isinstance(otro, CriterioPrioridad) and self._clave() == otro._clave()

    def __hash__(self):
        return hash(self._clave())

    def descripcion(self) -> str:
        total = self._peso_popularidad + self._peso_novedad
        pop = round(self._peso_popularidad / total * 100)
        texto = f"popularidad {pop}% / novedad {100 - pop}%"
        if self._genero_preferido:
            texto += f", +{self._bono_genero:g} a '{self._genero_preferido}'"
        return texto

    def __repr__(self):
        return f"CriterioPrioridad({self.descripcion()})"
