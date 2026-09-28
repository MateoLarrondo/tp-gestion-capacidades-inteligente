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
        area_a_cargo: str,
    ):
        # se valida antes de super() para que un supervisor sin área no quede en el registro
        if not area_a_cargo:
            raise ValueError("El área a cargo del supervisor no puede estar vacía.")
        if not AreaDeTrabajo.registro.existe_area(area_a_cargo):
            raise ValueError(f"No existe un área con el ID '{area_a_cargo}'.")
        super().__init__(
            id_trabajador = id_trabajador,
            nombre = nombre,
            franja_horaria = franja_horaria,
            habilidades = habilidades,
            credenciales = credenciales,
            limite_horas_semanales = limite_horas_semanales,
        )
        # id del área (ej: "A1"), se compara contra trabajo.area_trabajo.id_area
        self.area_a_cargo = area_a_cargo

    @classmethod
    def registrar_personal(
        cls,
        id_trabajador: str,
        nombre: str,
        franja_horaria: e.FranjaHoraria,
        habilidades: Set[str],
        limite_horas_semanales: float,
        area_a_cargo: str,
        **atributos,
    ):
        """Igual que Trabajador.registrar_personal, pero además exige el área a cargo."""
        supervisor = cls(id_trabajador, nombre, franja_horaria, habilidades, [], limite_horas_semanales, area_a_cargo)
        supervisor.atributos_opcionales = dict(atributos)
        return supervisor
