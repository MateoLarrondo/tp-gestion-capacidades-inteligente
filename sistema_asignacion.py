from datetime import date
from typing import Dict, Optional, Tuple

from enums import FranjaHoraria, EstadoAsignacion
from trabajador import Trabajador
from supervisor import Supervisor
from trabajo import Trabajo


class SistemaAsignacion:
    """Modela el registro de asignación de una trabajo a un trabajador."""

    # Registro de qué (labor, fecha, franja) ya está comprometido, para
    # que una misma labor no pueda proponerse dos veces en ese momento (regla 7).
    _asignaciones_activas: Dict[Tuple[str, date, FranjaHoraria], "SistemaAsignacion"] = {}

    def __init__(
        self,
        id_asignacion: int,
        trabajo: Trabajo,
        fecha: date,
        franja_horaria: FranjaHoraria,
    ):
        self.id_asignacion = id_asignacion
        self.trabajo = trabajo
        self.trabajador: Optional[Trabajador] = None
        self.fecha = fecha
        self.franja_horaria = franja_horaria
        self.estado = EstadoAsignacion.PENDIENTE
        self.supervisor_aprobador: Optional[Supervisor] = None

    def agregar_trabajador(self, trabajador: Trabajador) -> None:
        """Propone un trabajador para la asignación, validando aptitud, disponibilidad,
        carga horaria y cupo, y reservando esos recursos de inmediato (reglas 4, 5, 6, 7, 9, 10)."""
        if self.estado == EstadoAsignacion.APROBADA:
            raise ValueError("No se pueden agregar trabajadores a una asignación aprobada.")
        if self.trabajador is not None:
            raise ValueError(
                f"La labor '{self.trabajo.titulo}' ya tiene asignado a {self.trabajador.nombre}."
            )

        clave = (self.trabajo.id_trabajo, self.fecha, self.franja_horaria)
        asignacion_existente = SistemaAsignacion._asignaciones_activas.get(clave)
        if asignacion_existente is not None and asignacion_existente is not self:
            raise ValueError(
                f"La labor '{self.trabajo.titulo}' ya tiene una asignación el {self.fecha} "
                f"en la franja {self.franja_horaria.value}."
            )

        if not trabajador.esta_disponible(self.franja_horaria, self.fecha):
            raise ValueError(
                f"{trabajador.nombre} no está disponible el {self.fecha} en la franja {self.franja_horaria.value}."
            )
        if not trabajador.tiene_habilidades(self.trabajo.habilidades_requeridas):
            raise ValueError(
                f"{trabajador.nombre} no posee las habilidades requeridas para '{self.trabajo.titulo}'."
            )
        if not trabajador.tiene_credenciales_activas(self.trabajo.credenciales_requeridas, self.fecha):
            raise ValueError(
                f"{trabajador.nombre} no tiene activas las credenciales que exige '{self.trabajo.titulo}'."
            )
        area = self.trabajo.area_trabajo
        if not trabajador.tiene_credenciales_activas(area.credenciales_obligatorias, self.fecha):
            raise ValueError(f"{trabajador.nombre} no es apto para el área '{area.nombre}'.")
        if trabajador.excede_limite_horas(self.trabajo.duracion_horas):
            raise ValueError(
                f"La carga laboral de {trabajador.nombre} sería excesiva: supera el límite semanal de "
                f"{trabajador.limite_horas_semanales} hs."
            )
        if not area.tiene_cupo_disponible(self.fecha, self.franja_horaria, trabajador.id_trabajador):
            raise ValueError(
                f"La franja {self.franja_horaria.value} del {self.fecha} en '{area.nombre}' está completa."
            )

        trabajador.sumar_horas(self.trabajo.duracion_horas)
        trabajador.registrar_ocupacion(self.franja_horaria, self.fecha)
        area.registrar_trabajador_en_franja(self.fecha, self.franja_horaria, trabajador.id_trabajador)

        self.trabajador = trabajador
        SistemaAsignacion._asignaciones_activas[clave] = self

    def formalizar(self, supervisor: Trabajador) -> None:
        """Solo un supervisor a cargo del área del trabajo puede aprobar."""
        if self.estado == EstadoAsignacion.APROBADA:
            raise ValueError("La asignación ya está aprobada.")

        if self.trabajador is None:
            raise ValueError("La asignación debe tener un trabajador propuesto.")

        if not isinstance(supervisor, Supervisor):
            raise PermissionError(
                f"El usuario {supervisor.nombre} no tiene permisos de supervisor."
            )

        if supervisor.area_a_cargo != self.trabajo.area_trabajo:
            raise PermissionError(
                f"El supervisor {supervisor.nombre} no pertenece al área '{self.trabajo.area_trabajo.nombre}'."
            )

        self.estado = EstadoAsignacion.APROBADA
        self.supervisor_aprobador = supervisor
