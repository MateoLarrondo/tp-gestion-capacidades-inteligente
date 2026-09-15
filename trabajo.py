from area_de_trabajo import AreaDeTrabajo
from typing import Set  


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
