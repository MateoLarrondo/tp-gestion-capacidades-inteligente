from enum import Enum

class FranjaHoraria(Enum):
    MANIANA = "Mañana"
    TARDE = "Tarde"
    NOCHE = "Noche"


class EstadoAsignacion(Enum):
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"