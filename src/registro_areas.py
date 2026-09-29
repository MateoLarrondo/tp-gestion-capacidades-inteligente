class registro_areas:
    """Clase que representa el registro de las áreas de trabajo."""

    def __init__(self):
        self.areas = []

    def registrar_area(self, area):
        """Agrega el área, rechazando identificadores repetidos."""
        if self.existe_area(area.id_area):
            raise ValueError(f"Ya existe un área con el ID '{area.id_area}'.")
        self.areas.append(area)

    def existe_area(self, id_area):
        return any(a.id_area == id_area for a in self.areas)
