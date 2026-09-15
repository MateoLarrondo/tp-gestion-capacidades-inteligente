from trabajador import Trabajador
from area_de_trabajo import AreaDeTrabajo
from trabajo import Trabajo
from supervisor import Supervisor
from enums import FranjaHoraria, EstadoAsignacion
from datetime import date
from typing import Optional

class SistemaAsignacion:
    """Modela el registro de asignación de una trabajo a un trabajador."""

    def __init__(
        self,
        id_asignacion: int,
        trabajo: Trabajo,
        fecha: date,
        franja_horaria: FranjaHoraria,
    ):
        self.id_asignacion = id_asignacion
        self.trabajo = trabajo
        self.trabajadores: set[Trabajador] = set()
        self.fecha = fecha
        self.franja_horaria = franja_horaria
        self.estado = EstadoAsignacion.PENDIENTE
        self.supervisor_aprobador: Optional[Supervisor] = None

    def formalizar(self, supervisor: Trabajador) -> None:
        """Solo un supervisor a cargo del área del trabajo puede aprobar."""
        if self.estado == EstadoAsignacion.APROBADA:
            raise ValueError("La asignación ya está aprobada.")

        if not self.trabajadores:
            raise ValueError("La asignación debe tener al menos un trabajador.")

        if not isinstance(supervisor, Supervisor):
            raise PermissionError(
                f"El usuario {supervisor.nombre} no tiene permisos de supervisor."
            )

        if supervisor.area_a_cargo != self.trabajo.area_trabajo:
            raise PermissionError(
                f"El supervisor {supervisor.nombre} no pertenece al área '{self.trabajo.area_trabajo.nombre}'."
            )

        for trabajador in self.trabajadores:
            if trabajador.excede_limite_horas(self.trabajo.duracion_horas):
                raise ValueError(
                    f"La asignación supera el límite semanal de {trabajador.nombre}."
                )
            if not self.trabajo.area_trabajo.tiene_cupo_disponible(
                self.fecha, self.franja_horaria, trabajador.id_trabajador
            ):
                raise ValueError(
                    f"No hay cupo disponible para {trabajador.nombre} en la franja asignada."
                )

        for trabajador in self.trabajadores:
            trabajador.sumar_horas(self.trabajo.duracion_horas)
            self.trabajo.area_trabajo.registrar_trabajador_en_franja(
                self.fecha, self.franja_horaria, trabajador.id_trabajador
            )

        self.estado = EstadoAsignacion.APROBADA
        self.supervisor_aprobador = supervisor
