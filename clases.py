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
        self.horas_asignadas_semana: float = 0.0
        # Regla 8: Roles y facultades de supervisión
        self.es_supervisor = es_supervisor

    def obtener_credenciales_activas(self, fecha_consulta: date) -> Set[str]:
        """Devuelve el conjunto de nombres de credenciales vigentes a la fecha dada."""
        return {
            c.nombre for c in self.credenciales if c.esta_activa(fecha_consulta)
        }

    def tiene_habilidades(self, habilidades_requeridas: Set[str]) -> bool:
        """Verifica si posee el total de habilidades exigidas."""
        return habilidades_requeridas.issubset(self.habilidades)

    def tiene_credenciales_activas(
        self, credenciales_requeridas: Set[str], fecha_consulta: date
    ) -> bool:
        """Regla 4 y 10: Valida que posea todas las credenciales requeridas y que estén vigentes."""
        activas = self.obtener_credenciales_activas(fecha_consulta)
        return credenciales_requeridas.issubset(activas)

    def excede_limite_horas(self, horas_nueva_labor: float) -> bool:
        """Regla 5: Comprueba si añadir una nueva labor excede la carga semanal máxima."""
        return (
            self.horas_asignadas_semana + horas_nueva_labor
        ) > self.limite_horas_semanales

    def acumular_horas(self, horas: float) -> None:
        """Regla 9: Asigna las horas de una nueva labor al total acumulado semanal."""
        if self.excede_limite_horas(horas):
            raise ValueError(
                f"La asignación supera el límite semanal de {self.limite_horas_semanales} hs de {self.nombre}."
            )
        self.horas_asignadas_semana += horas

    def reiniciar_semana(self) -> None:
        """Regla 12: Restablece la contabilidad de horas al inicio de un nuevo ciclo."""
        self.horas_asignadas_semana = 0.0