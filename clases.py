from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Set

class FranjaHoraria(Enum):
    MANIANA = "Mañana"
    TARDE = "Tarde"
    NOCHE = "Noche"


class EstadoAsignacion(Enum):
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"


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


class Trabajador:
    """Modela al trabajador, sus competencias, horas acumuladas y rol."""

    def __init__(
        self,
        id_trabajador: str,
        nombre: str,
        franja_horaria: FranjaHoraria,
        habilidades: Set[str],
        credenciales: List[Credencial],
        limite_horas_semanales: float,
    ):
        self.id_trabajador = id_trabajador
        self.nombre = nombre
        self.franja_horaria = franja_horaria
        self.habilidades = set(habilidades)
        self.credenciales = list(credenciales)
        self.limite_horas_semanales = limite_horas_semanales
        self.horas_asignadas_semana = 0.0
        self.id_no_vacio()
        self.limite_horas_positivo()

    def obtener_credenciales_activas(self, fecha_consulta: date):
        """Devuelve el conjunto de nombres de credenciales vigentes a la fecha dada."""
        return {
            c.nombre for c in self.credenciales if c.esta_activa(fecha_consulta)
        }

    def tiene_habilidades(self, habilidades_requeridas: Set[str]):
        """Verifica si posee el total de habilidades exigidas."""
        return habilidades_requeridas.issubset(self.habilidades)

    def tiene_credenciales_activas(
        self, credenciales_requeridas: Set[str], fecha_consulta: date
    ):
        """Valida que posea todas las credenciales requeridas y que estén vigentes."""
        activas = self.obtener_credenciales_activas(fecha_consulta)
        return credenciales_requeridas.issubset(activas)

    def excede_limite_horas(self, horas_nueva_trabajo: float):
        """Comprueba si añadir una nueva trabajo excede la carga semanal máxima."""
        return (
            self.horas_asignadas_semana + horas_nueva_trabajo
        ) > self.limite_horas_semanales

    def sumar_horas(self, horas: float):
        """Asigna las horas de una nueva trabajo al total acumulado semanal."""
        if self.excede_limite_horas(horas):
            raise ValueError(
                f"La asignación supera el límite semanal de {self.limite_horas_semanales} hs de {self.nombre}."
            )

        self.horas_asignadas_semana += horas

    def reiniciar_semana(self):
        """Restablece la contabilidad de horas al inicio de un nuevo ciclo."""
        self.horas_asignadas_semana = 0.0

    def limite_horas_positivo(self):
        """Asegura que el límite de horas semanales sea un valor positivo."""
        if self.limite_horas_semanales <= 0:
            raise ValueError(
                f"El límite de horas semanales para {self.nombre} debe ser mayor a cero. Valor dado: {self.limite_horas_semanales}"
            )

    def id_no_vacio(self):
        """Asegura que el identificador del trabajador no esté vacío."""
        if not self.id_trabajador:
            raise ValueError("El identificador del trabajador no puede estar vacío.")

    def tiempo_libre(self):
        """Calcula el tiempo libre disponible del trabajador en la semana."""
        return self.limite_horas_semanales - self.horas_asignadas_semana


class AreaDeTrabajo:
    """Modela un área de trabajo con sus credenciales obligatorias y cupos por franja."""

    def __init__(
        self,
        id_area: str,
        nombre: str,
        credenciales_obligatorias: Set[str],
        limite_trabajador_por_franja: Dict[FranjaHoraria, int],
    ):
        self.id_area = id_area
        self.nombre = nombre
        self.credenciales_obligatorias = set(credenciales_obligatorias)
        self.limite_trabajador_por_franja = limite_trabajador_por_franja
        self._trabajador_asignado_por_franja_por_fecha: Dict[tuple[date, FranjaHoraria], set[str]] = {}
        self.validar_limite_trabajador_por_franja()
        self.id_no_nulo()

    def tiene_cupo_disponible(
        self, fecha: date, franja_horaria: FranjaHoraria, id_trabajador: str
    ) -> bool:
        """Verifica si la franja tiene capacidad en la fecha dada."""
        limite = self.limite_trabajador_por_franja.get(franja_horaria, 0)
        trabajador_actual = self._trabajador_asignado_por_franja_por_fecha.get(
            (fecha, franja_horaria), set()
        )
        if id_trabajador in trabajador_actual:
            return True
        return len(trabajador_actual) < limite

    def registrar_trabajador_en_franja(
        self, fecha: date, franja_horaria: FranjaHoraria, id_trabajador: str
    ):
        clave = (fecha, franja_horaria)
        if clave not in self._trabajador_asignado_por_franja_por_fecha:
            self._trabajador_asignado_por_franja_por_fecha[clave] = set()
        self._trabajador_asignado_por_franja_por_fecha[clave].add(id_trabajador)

    def validar_limite_trabajador_por_franja(self):
        """Asegura que los límites de trabajador por franja sean positivos."""
        for franja, limite in self.limite_trabajador_por_franja.items():
            if limite <= 0:
                raise ValueError(
                    f"El límite de trabajador para la franja '{franja}' en el área '{self.nombre}' debe ser mayor a cero. Valor dado: {limite}"
                )

    def id_no_nulo(self):
        """Asegura que el identificador del área no sea nulo."""
        if not self.id_area:
            raise ValueError("El identificador del área de trabajo no puede ser nulo.")


class Supervisor(Trabajador):
    """trabajador con facultades para formalizar asignaciones pertenecientes a su área."""

    def __init__(
        self,
        id_trabajador: str,
        nombre: str,
        franja_horaria: FranjaHoraria,
        habilidades: Set[str],
        credenciales: List[Credencial],
        limite_horas_semanales: float,
        area_a_cargo: AreaDeTrabajo,
    ):
        super().__init__(
            id_trabajador = id_trabajador,
            nombre = nombre,
            franja_horaria = franja_horaria,
            habilidades = habilidades,
            credenciales = credenciales,
            limite_horas_semanales = limite_horas_semanales,
        )
        self.area_a_cargo = area_a_cargo


class Trabajo:
    """Una trabajo con su duración, requisitos y el área donde se realiza."""

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

    def validar_duracion_horas(self):
        """Asegura que la duración de la trabajo sea positiva."""
        if self.duracion_horas <= 0:
            raise ValueError(
                f"La duración de la trabajo {self.titulo} debe ser mayor a cero. Valor dado: {self.duracion_horas}"
            )

    def id_no_vacio(self):
        """Asegura que el identificador de la trabajo no esté vacío."""
        if not self.id_trabajo:
            raise ValueError("El identificador de la trabajo no puede estar vacío.")

    def titulo_no_vacio(self):
        """Asegura que el título de la trabajo no esté vacío."""
        if not self.titulo:
            raise ValueError("El título de la trabajo no puede estar vacío.")

    def areatrabajo_no_nulo(self):
        """Asegura que el área de trabajo no sea nula."""
        if self.area_trabajo is None:
            raise ValueError("El área de trabajo no puede ser nula.")


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

        area = self.trabajo.area_trabajo
        ocupados = area._trabajador_asignado_por_franja_por_fecha.get(
            (self.fecha, self.franja_horaria), set()
        )
        ids_nuevos = {trabajador.id_trabajador for trabajador in self.trabajadores}
        limite = area.limite_trabajador_por_franja.get(self.franja_horaria, 0)

        if len(ocupados | ids_nuevos) > limite:
            raise ValueError(
                f"No hay cupo disponible en la franja {self.franja_horaria.value} para la fecha {self.fecha}."
            )

        for trabajador in self.trabajadores:
            if trabajador.excede_limite_horas(self.trabajo.duracion_horas):
                raise ValueError(
                    f"La asignación supera el límite semanal de {trabajador.nombre}."
                )

        for trabajador in self.trabajadores:
            trabajador.sumar_horas(self.trabajo.duracion_horas)
            area.registrar_trabajador_en_franja(
                self.fecha, self.franja_horaria, trabajador.id_trabajador
            )

        self.estado = EstadoAsignacion.APROBADA
        self.supervisor_aprobador = supervisor
