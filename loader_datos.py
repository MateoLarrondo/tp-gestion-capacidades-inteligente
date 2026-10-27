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
                # el padre ya fue creado antes porque guardar_datos escribe las áreas en orden de creación
        area_padre = next((p for p in AreaDeTrabajo.registro.areas if p.id_area == a.get("id_area_padre")), None)
        AreaDeTrabajo(a["id_area"], a["nombre"], set(a["credenciales_obligatorias"]), limites, area_padre)

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


def guardar_datos(ruta="data/datos_sistema.json"):
    """Escribe en el JSON el estado actual de áreas, personal y trabajos, con el
    mismo formato que lee cargar_datos."""
    datos = {
        "areas": [
            {
                "id_area": a.id_area,
                "nombre": a.nombre,
                "credenciales_obligatorias": sorted(a.credenciales_obligatorias),
                "limite_trabajador_por_franja": {f.value: n for f, n in a.limite_trabajador_por_franja.items()},
                "id_area_padre": a.area_padre.id_area if a.area_padre else None,
            }
            for a in AreaDeTrabajo.registro.areas
        ],
        "trabajadores": [
            {
                "id_trabajador": t.id_trabajador,
                "nombre": t.nombre,
                "franja_horaria": t.franja_horaria.value,
                "habilidades": sorted(t.habilidades),
                "credenciales": [
                    {
                        "nombre": c.nombre,
                        "fecha_obtencion": c.fecha_obtencion.isoformat(),
                        "fecha_expiracion": c.fecha_expiracion.isoformat(),
                    }
                    for c in t.credenciales
                ],
                "limite_horas_semanales": t.limite_horas_semanales,
                "area_a_cargo": getattr(t, "area_a_cargo", None),
            }
            for t in Trabajador.registro.trabajadores
        ],
        "trabajos": [
            {
                "id_trabajo": j.id_trabajo,
                "titulo": j.titulo,
                "descripcion": j.descripcion,
                "duracion_horas": j.duracion_horas,
                "habilidades_requeridas": sorted(j.habilidades_requeridas),
                "credenciales_requeridas": sorted(j.credenciales_requeridas),
                "area_trabajo": j.area_trabajo.id_area,
            }
            for j in Trabajo.registro.trabajos
        ],
    }
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
