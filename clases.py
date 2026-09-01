from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Set

class Credencial:
    """Modela una credencial profesional con su período de vigencia."""

    def __init__(self, nombre: str, fecha_obtencion: date, fecha_expiracion: date):
        self.nombre = nombre
        self.fecha_obtencion = fecha_obtencion
        self.fecha_expiracion = fecha_expiracion

    def esta_activa(self, fecha_consulta: date):
        """Regla 2: Determina si la credencial está activa en una fecha específica."""
        return self.fecha_obtencion <= fecha_consulta <= self.fecha_expiracion

class Personal:
    """Modela al trabajador, sus competencias, horas acumuladas y rol."""

    def __init__(
        self,
        id_personal: str,
        nombre: str,
        habilidades: Set[str],
        credenciales: List[Credencial],
        limite_horas_semanales: float,
        es_supervisor: bool = False,
    ):
        # Regla 1: Identificador único, datos básicos y carga horaria inicializada en 0
        self.id_personal = id_personal
        self.nombre = nombre
        self.habilidades = set(habilidades)
        self.credenciales = credenciales
        self.limite_horas_semanales = limite_horas_semanales
        self.horas_asignadas_semana = 0.0

        # Regla 8: Roles y facultades de supervisión
        self.es_supervisor = es_supervisor

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
        """Regla 4 y 10: Valida que posea todas las credenciales requeridas y que estén vigentes."""
        activas = self.obtener_credenciales_activas(fecha_consulta)
        return credenciales_requeridas.issubset(activas)

    def excede_limite_horas(self, horas_nueva_labor: float):
        """Regla 5: Comprueba si añadir una nueva labor excede la carga semanal máxima."""
        return (
            self.horas_asignadas_semana + horas_nueva_labor
        ) > self.limite_horas_semanales

    def acumular_horas(self, horas: float):
        """Regla 9: Asigna las horas de una nueva labor al total acumulado semanal."""
        if self.excede_limite_horas(horas):
            raise ValueError(
                f"La asignación supera el límite semanal de {self.limite_horas_semanales} hs de {self.nombre}."
            )

        self.horas_asignadas_semana += horas

    def reiniciar_semana(self):
        """Regla 12: Restablece la contabilidad de horas al inicio de un nuevo ciclo."""
        self.horas_asignadas_semana = 0.0

class EstadoAsignacion(Enum):
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"


class AreaDeTrabajo:
    """Modela un área de trabajo con sus credenciales obligatorias y cupos por franja."""

    def __init__(
        self,
        id_area: str,
        nombre: str,
        credenciales_obligatorias: Set[str],
        limite_personal_por_franja: Dict[str, int],
    ):
        self.id_area = id_area
        self.nombre = nombre
        # Regla 10
        self.credenciales_obligatorias = set(credenciales_obligatorias)
        # Regla 6
        self.limite_personal_por_franja = limite_personal_por_franja
        # {(fecha, franja): set(id_personal)}
        self._personal_asignado_por_franja: Dict[tuple, Set[str]] = {}

    def tiene_cupo_disponible(self, fecha: date, franja_horaria: str, id_personal: str) -> bool:
        """Regla 6: verifica si la franja tiene capacidad en la fecha dada."""
        limite = self.limite_personal_por_franja.get(franja_horaria, 0)
        personal_actual = self._personal_asignado_por_franja.get((fecha, franja_horaria), set())
        if id_personal in personal_actual:
            return True
        return len(personal_actual) < limite

    def registrar_personal_en_franja(self, fecha: date, franja_horaria: str, id_personal: str) -> None:
        clave = (fecha, franja_horaria)
        if clave not in self._personal_asignado_por_franja:
            self._personal_asignado_por_franja[clave] = set()
        self._personal_asignado_por_franja[clave].add(id_personal)


class Labor:
    """Regla 3: una labor con su duración, requisitos y el área donde se realiza."""

    def __init__(
        self,
        id_labor: str,
        titulo: str,
        descripcion: str,
        duracion_horas: float,
        habilidades_requeridas: Set[str],
        credenciales_requeridas: Set[str],
        area_trabajo: AreaDeTrabajo,
    ):
        self.id_labor = id_labor
        self.titulo = titulo
        self.descripcion = descripcion
        self.duracion_horas = duracion_horas
        self.habilidades_requeridas = set(habilidades_requeridas)
        self.credenciales_requeridas = set(credenciales_requeridas)
        self.area_trabajo = area_trabajo

class Asignacion:
    """Modela el registro de asignación de una labor a un trabajador."""

    def __init__(
        self,
        id_asignacion: str,
        labor: Labor,
        trabajador: Personal,
        fecha: date,
        franja_horaria: str,
    ):
        self.id_asignacion = id_asignacion
        self.labor = labor
        self.trabajador = trabajador
        self.fecha = fecha
        self.franja_horaria = franja_horaria
        # Regla 8: nace 'Pendiente'
        self.estado = EstadoAsignacion.PENDIENTE
        self.supervisor_aprobador: Optional[Personal] = None

    def formalizar(self, supervisor: Personal) -> None:
        """Regla 8: solo un supervisor puede aprobar."""
        if not supervisor.es_supervisor:
            raise PermissionError(f"El usuario {supervisor.nombre} no tiene permisos de supervisor.")
        self.estado = EstadoAsignacion.APROBADA
        self.supervisor_aprobador = supervisor
