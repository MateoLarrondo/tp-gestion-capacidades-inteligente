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

    def fechas_validas(self, fecha_inicio: date, fecha_fin: date):
        """Regla 3: Verifica si un rango de fechas es válido."""
        if fecha_inicio > fecha_fin:
            raise ValueError(
                f"Fecha de inicio {fecha_inicio} no puede ser posterior a la fecha de fin {fecha_fin}."
            )
        if fecha_fin < self.fecha_obtencion or fecha_inicio > self.fecha_expiracion:
            raise ValueError(
                f"El rango {fecha_inicio} - {fecha_fin} no coincide con la vigencia de la credencial {self.nombre}."
            )
        
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

    def limite_horas_valido(self):
        """Regla 11: Verifica que el límite de horas semanales sea positivo."""
        if self.limite_horas_semanales <= 0:
            raise ValueError(
                f"El límite de horas semanales debe ser positivo para {self.nombre}."
            )
    
class AreaTrabajo:
    """Modela un área de trabajo y sus requisitos de acceso."""

    def __init__(
        self,
        id_area: str,
        nombre: str,
        supervisor: Personal,
        credenciales_requeridas: Set[str],
        cupos_por_franja: dict,
    ):
        self.id_area = id_area
        self.nombre = nombre
        self.supervisor = supervisor
        self.credenciales_requeridas = set(credenciales_requeridas)
        self.cupos_por_franja = cupos_por_franja
        self.personas_asignadas_por_franja = {}

    def tiene_cupo(self, franja: str):
        """Regla 6: Verifica si todavía hay capacidad en una franja horaria."""
        cantidad_actual = self.personas_asignadas_por_franja.get(franja, 0)
        limite = self.cupos_por_franja.get(franja, 0)

        return cantidad_actual < limite

    def ocupar_cupo(self, franja: str):
        """Registra una nueva persona asignada a una franja."""
        if not self.tiene_cupo(franja):
            raise ValueError(
                f"La franja {franja} del área {self.nombre} está completa."
            )

        self.personas_asignadas_por_franja[franja] = (
            self.personas_asignadas_por_franja.get(franja, 0) + 1
        )

    def validar_limite_personal_por_franja(self):
        """Regla 7: Asegura que el número de personas asignadas no exceda los cupos."""
        for franja, cantidad in self.personas_asignadas_por_franja.items():
            limite = self.cupos_por_franja.get(franja, 0)
            if cantidad > limite:
                raise ValueError(
                    f"El área {self.nombre} tiene {cantidad} personas en la franja {franja}, "
                    f"excediendo el límite de {limite}."
                )