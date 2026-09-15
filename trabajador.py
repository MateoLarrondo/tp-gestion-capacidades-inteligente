import enums as e
from datetime import date
import credencial as c
from typing import List, Set

class Trabajador:
    """Modela al trabajador, sus competencias, horas acumuladas y rol."""

    def __init__(
        self,
        id_trabajador: str,
        nombre: str,
        franja_horaria: e.FranjaHoraria,
        habilidades: Set[str],
        credenciales: List[c.Credencial],
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

