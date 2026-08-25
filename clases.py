from datetime import date
from typing import List, Set


class Credencial:
    """Modela una credencial profesional con su período de vigencia."""

    def __init__(self, nombre: str, fecha_obtencion: date, fecha_expiracion: date):
        self.nombre = nombre
        self.fecha_obtencion = fecha_obtencion
        self.fecha_expiracion = fecha_expiracion

    def esta_activa(self, fecha_consulta: date):
        """Regla 2: Determina si la credencial está activa en una fecha específica."""
        return self.fecha_obtencion <= fecha_consulta <= self.fecha_expiracion

