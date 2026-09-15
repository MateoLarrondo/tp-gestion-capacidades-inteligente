import enums as e
from trabajador import Trabajador
from area_de_trabajo import AreaDeTrabajo
from typing import List, Set
from credencial import Credencial

class Supervisor(Trabajador):
    """trabajador con facultades para formalizar asignaciones pertenecientes a su área."""

    def __init__(
        self,
        id_trabajador: str,
        nombre: str,
        franja_horaria: e.FranjaHoraria,
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
