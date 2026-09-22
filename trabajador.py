from datetime import date
from typing import Dict, List, Set

from enums import FranjaHoraria
from credencial import Credencial
from trabajo import Trabajo
from sistema_registro import sistema_registro


class Trabajador:
    """Modela al trabajador, sus competencias, horas acumuladas y rol."""

    # NUEVO: registro de todos los trabajadores creados (incluye supervisores)
    registro = sistema_registro()

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
        # NUEVO: (fecha, franja) en las que ya tiene una asignación aprobada
        self._franjas_ocupadas: Set[tuple[date, FranjaHoraria]] = set()
        # atributos variables por rol (idiomas, área de origen, turno preferido, etc.)
        self.atributos_opcionales: Dict[str, object] = {}
        self.id_no_vacio()
        self.limite_horas_positivo()
        # NUEVO: se registra solo si pasó las validaciones
        Trabajador.registro.registrar_trabajador(self)

    @classmethod
    def registrar_personal(
        cls,
        id_trabajador: str,
        nombre: str,
        franja_horaria: FranjaHoraria,
        habilidades: Set[str],
        limite_horas_semanales: float,
        **atributos,
    ):
        """Registra un nuevo trabajador aceptando atributos opcionales variables según
        el rol (idiomas, área de origen, turno preferido, certificaciones iniciales, etc.)
        sin declarar un parámetro nuevo por cada uno; quedan disponibles en atributos_opcionales."""
        trabajador = Trabajador(id_trabajador, nombre, franja_horaria, habilidades, [], limite_horas_semanales)
        trabajador.atributos_opcionales = dict(atributos)
        return trabajador

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

    @classmethod
    def reiniciar_semana_todos(cls):
        """Reestablece a cero la carga horaria de todo el personal registrado (regla 12)."""
        for t in cls.registro.trabajadores:
            t.reiniciar_semana()

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

    # ---------- NUEVO: disponibilidad ----------

    def esta_ocupado(self, franja_horaria: FranjaHoraria, fecha: date):
        """Indica si ya tiene una asignación aprobada en esa franja y fecha."""
        return (fecha, franja_horaria) in self._franjas_ocupadas

    def registrar_ocupacion(self, franja_horaria: FranjaHoraria, fecha: date):
        """Marca la franja y fecha como ocupadas."""
        self._franjas_ocupadas.add((fecha, franja_horaria))

    def esta_disponible(self, franja_horaria: FranjaHoraria, fecha: date):
        """Disponible = trabaja en esa franja, no está ocupado y le quedan horas."""
        return (
            self.franja_horaria == franja_horaria
            and not self.esta_ocupado(franja_horaria, fecha)
            and self.tiempo_libre() > 0
        )

    @classmethod
    def disponibles_en(
        cls, trabajo: Trabajo, fecha: date, franja_horaria: FranjaHoraria
    ):
        """Devuelve los trabajadores disponibles para una labor, franja y fecha dadas (regla 11):
        con habilidades y credenciales activas (de la labor y del área), que no excedan su límite
        de horas semanales y para los que la franja del área aún tenga cupo."""
        area = trabajo.area_trabajo
        disponibles = []
        for t in cls.registro.trabajadores:
            if not t.esta_disponible(franja_horaria, fecha):
                continue
            if not t.tiene_habilidades(trabajo.habilidades_requeridas):
                continue
            if not t.tiene_credenciales_activas(trabajo.credenciales_requeridas, fecha):
                continue
            if not t.tiene_credenciales_activas(area.credenciales_obligatorias, fecha):
                continue
            if t.excede_limite_horas(trabajo.duracion_horas):
                continue
            if not area.tiene_cupo_disponible(fecha, franja_horaria, t.id_trabajador):
                continue
            disponibles.append(t)
        return disponibles