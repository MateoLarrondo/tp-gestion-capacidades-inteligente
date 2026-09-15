from datetime import date

class Credencial:
    """Modela una credencial profesional con su período de vigencia."""


    def __init__(self, nombre: str, fecha_obtencion: date, fecha_expiracion: date):
        self.nombre = nombre
        self.fecha_obtencion = fecha_obtencion
        self.fecha_expiracion = fecha_expiracion
        self.validar_fechas()

    def esta_activa(self, fecha_consulta: date):
        """Determina si la credencial está activa en una fecha específica."""
        return self.fecha_obtencion <= fecha_consulta <= self.fecha_expiracion

    def validar_fechas(self):
        """Asegura que la fecha de obtención preceda a la de expiración."""
        if self.fecha_obtencion >= self.fecha_expiracion:
            raise ValueError(
                f"La fecha de obtención {self.fecha_obtencion} debe ser anterior a la de expiración {self.fecha_expiracion}."
            )
