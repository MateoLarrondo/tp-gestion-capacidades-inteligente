class sistema_registro:
    """Clase que representa el sistema de registro de trabajadores y trabajos."""

    def __init__(self):
        self.trabajadores = []
        self.trabajos = []

    def registrar_trabajador(self, trabajador):
        """Agrega al trabajador, rechazando identificadores repetidos (regla 1)."""
        if any(t.id_trabajador == trabajador.id_trabajador for t in self.trabajadores):
            raise ValueError(f"Ya existe un trabajador con el ID '{trabajador.id_trabajador}'.")
        self.trabajadores.append(trabajador)

    def registrar_trabajo(self, trabajo):
        """Agrega el trabajo, rechazando identificadores repetidos (regla 3)."""
        if any(t.id_trabajo == trabajo.id_trabajo for t in self.trabajos):
            raise ValueError(f"Ya existe un trabajo con el ID '{trabajo.id_trabajo}'.")
        self.trabajos.append(trabajo)
