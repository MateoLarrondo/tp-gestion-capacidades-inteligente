from enum import Enum

class FranjaHoraria(Enum):
    MANIANA = "Mañana"
    TARDE = "Tarde"
    NOCHE = "Noche"


class EstadoAsignacion(Enum):
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"

# Horas de trabajo que abarca cada franja horaria; es el máximo que un trabajador
# puede trabajar en un día, ya que solo trabaja en su franja.
HORAS_POR_FRANJA = 8
