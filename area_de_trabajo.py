from datetime import date
from typing import Set, Dict
from enums import FranjaHoraria

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

