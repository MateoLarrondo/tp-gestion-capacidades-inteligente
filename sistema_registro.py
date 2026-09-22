class sistema_registro:
    """Clase que representa el sistema de registro de trabajadores y trabajos."""

    def __init__(self):
        self.trabajadores = []


    def registrar_trabajador(self, trabajador):
        self.trabajadores.append(trabajador)
