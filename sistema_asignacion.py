from datetime import date
from typing import Optional

from enums import FranjaHoraria, EstadoAsignacion
from trabajador import Trabajador
from supervisor import Supervisor
from trabajo import Trabajo


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

    # NUEVO: forma de sumar trabajadores a la asignación
    def agregar_trabajador(self, trabajador: Trabajador) -> None:
        """Agrega un trabajador si está disponible en la franja y fecha de la asignación."""
        if self.estado == EstadoAsignacion.APROBADA:
            raise ValueError("No se pueden agregar trabajadores a una asignación aprobada.")
        if not trabajador.esta_disponible(self.franja_horaria, self.fecha):
            raise ValueError(
                f"{trabajador.nombre} no está disponible el {self.fecha} en la franja {self.franja_horaria.value}."
            )
        self.trabajadores.add(trabajador)

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
            # NUEVO: se vuelve a chequear por si se ocupó después de agregarlo
            if not trabajador.esta_disponible(self.franja_horaria, self.fecha):
                raise ValueError(
                    f"{trabajador.nombre} ya no está disponible en la franja asignada."
                )
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
            trabajador.registrar_ocupacion(self.franja_horaria, self.fecha)  # NUEVO
            self.trabajo.area_trabajo.registrar_trabajador_en_franja(
                self.fecha, self.franja_horaria, trabajador.id_trabajador
            )

        self.estado = EstadoAsignacion.APROBADA
        self.supervisor_aprobador = supervisor