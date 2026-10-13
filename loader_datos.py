import json
from datetime import date

from enums import FranjaHoraria
from credencial import Credencial
from area_de_trabajo import AreaDeTrabajo
from trabajador import Trabajador
from supervisor import Supervisor
from trabajo import Trabajo


def cargar_datos(ruta="data/datos_sistema.json"):
    """Lee el JSON y crea áreas, personal y trabajos (en ese orden, porque el
    supervisor necesita que su área exista y el trabajo necesita su área)."""
    with open(ruta, encoding="utf-8") as archivo:
        datos = json.load(archivo)

    for a in datos["areas"]:
        limites = {FranjaHoraria(f): n for f, n in a["limite_trabajador_por_franja"].items()}
        AreaDeTrabajo(a["id_area"], a["nombre"], set(a["credenciales_obligatorias"]), limites)

    for t in datos["trabajadores"]:
        credenciales = [
            Credencial(c["nombre"], date.fromisoformat(c["fecha_obtencion"]), date.fromisoformat(c["fecha_expiracion"]))
            for c in t["credenciales"]
        ]
        argumentos = (
            t["id_trabajador"],
            t["nombre"],
            FranjaHoraria(t["franja_horaria"]),
            set(t["habilidades"]),
            credenciales,
            t["limite_horas_semanales"],
        )
        if t["area_a_cargo"]:
            Supervisor(*argumentos, t["area_a_cargo"])
        else:
            Trabajador(*argumentos)

    for j in datos["trabajos"]:
        area = next(a for a in AreaDeTrabajo.registro.areas if a.id_area == j["area_trabajo"])
        Trabajo(
            j["id_trabajo"],
            j["titulo"],
            j["descripcion"],
            j["duracion_horas"],
            set(j["habilidades_requeridas"]),
            set(j["credenciales_requeridas"]),
            area,
        )
