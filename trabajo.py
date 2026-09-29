from datetime import date, timedelta
from area_de_trabajo import AreaDeTrabajo
from typing import List, Set, Tuple
from enums import HORAS_POR_FRANJA
from sistema_registro import sistema_registro


class Trabajo:
    """Una trabajo con su duración, requisitos y el área donde se realiza."""

    # registro de todos los trabajos creados, para que el id sea único
    registro = sistema_registro()

    def __init__(
        self,
        id_trabajo: str,
        titulo: str,
        descripcion: str,
        duracion_horas: float,
        habilidades_requeridas: Set[str],
        credenciales_requeridas: Set[str],
        area_trabajo: AreaDeTrabajo,
    ):
        self.id_trabajo = id_trabajo
        self.titulo = titulo
        self.descripcion = descripcion
        self.duracion_horas = duracion_horas
        self.habilidades_requeridas = set(habilidades_requeridas)
        self.credenciales_requeridas = set(credenciales_requeridas)
        self.area_trabajo = area_trabajo
        self.id_no_vacio()
        self.titulo_no_vacio()
        self.validar_duracion_horas()
        self.areatrabajo_no_nulo()
        # se registra solo si pasó las validaciones
        Trabajo.registro.registrar_trabajo(self)

    def validar_duracion_horas(self):
        """Asegura que la duración del trabajo sea positiva."""
        if self.duracion_horas <= 0:
            raise ValueError(
                f"La duración del trabajo {self.titulo} debe ser mayor a cero. Valor dado: {self.duracion_horas}"
            )

    def reparto_por_dia(self, fecha_inicio: date) -> List[Tuple[date, float]]:
        """Reparte la duración del trabajo en días consecutivos desde fecha_inicio, con
        un máximo de HORAS_POR_FRANJA por día. Ej: 12 hs -> [(día 1, 8), (día 2, 4)]."""
        reparto = []
        horas_restantes = self.duracion_horas
        fecha = fecha_inicio
        while horas_restantes > 0:
            horas_del_dia = min(horas_restantes, HORAS_POR_FRANJA)
            reparto.append((fecha, horas_del_dia))
            horas_restantes -= horas_del_dia
            fecha += timedelta(days=1)
        return reparto

    def id_no_vacio(self):
        """Asegura que el identificador del trabajo no esté vacío."""
        if not self.id_trabajo:
            raise ValueError("El identificador del trabajo no puede estar vacío.")

    def titulo_no_vacio(self):
        """Asegura que el título del trabajo no esté vacío."""
        if not self.titulo:
            raise ValueError("El título del trabajo no puede estar vacío.")

    def areatrabajo_no_nulo(self):
        """Asegura que el área de trabajo no sea nula."""
        if self.area_trabajo is None:
            raise ValueError("El área de trabajo no puede ser nula.")
