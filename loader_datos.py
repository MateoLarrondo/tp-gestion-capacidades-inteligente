import json
from datetime import date

from enums import FranjaHoraria, EstadoAsignacion
from credencial import Credencial
from area_de_trabajo import AreaDeTrabajo
from trabajador import Trabajador
from supervisor import Supervisor
from trabajo import Trabajo
from sistema_asignacion import SistemaAsignacion


def cargar_datos(ruta="data/datos_sistema.json"):
    """Crea áreas, personal y trabajos, y devuelve las asignaciones en orden.

    Se llama al iniciar el sistema, con los registros y las reservas vacíos.
    """
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
            trabajador = Supervisor(*argumentos, t["area_a_cargo"])
        else:
            trabajador = Trabajador(*argumentos)
        trabajador.atributos_opcionales = t.get("atributos_opcionales", {})

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

    asignaciones = []
    ids_recuperados = set()
    for posicion, a in enumerate(datos.get("asignaciones", []), start=1):
        try:
            id_asignacion = a["id_asignacion"]
            if type(id_asignacion) is not int or id_asignacion <= 0:
                raise ValueError("El ID debe ser un entero positivo.")
            if id_asignacion in ids_recuperados:
                raise ValueError(f"El ID {id_asignacion} está repetido.")
            trabajo = next((j for j in Trabajo.registro.trabajos
                            if j.id_trabajo == a["id_trabajo"]), None)
            trabajador = next((t for t in Trabajador.registro.trabajadores
                               if t.id_trabajador == a["id_trabajador"]), None)
            if trabajo is None:
                raise ValueError(f"No existe el trabajo {a['id_trabajo']!r}.")
            if trabajador is None:
                raise ValueError(f"No existe el trabajador {a['id_trabajador']!r}.")
            estado = EstadoAsignacion(a["estado"])
            id_supervisor = a["id_supervisor_aprobador"]
            supervisor = None
            if estado == EstadoAsignacion.APROBADA:
                supervisor = next((t for t in Trabajador.registro.trabajadores
                                   if t.id_trabajador == id_supervisor), None)
                if not isinstance(supervisor, Supervisor):
                    raise ValueError(f"No existe un supervisor con ID {id_supervisor!r}.")
                if supervisor.area_a_cargo != trabajo.area_trabajo.id_area:
                    raise ValueError("El supervisor aprobador no está a cargo del área del trabajo.")
            elif id_supervisor is not None:
                raise ValueError("Una asignación pendiente no puede tener supervisor aprobador.")

            asignacion = SistemaAsignacion(
                id_asignacion, trabajo, date.fromisoformat(a["fecha"]),
                FranjaHoraria(a["franja_horaria"]),
            )
            # Este método recupera todas las reservas y suma las horas una sola vez.
            asignacion.agregar_trabajador(trabajador)
            if estado == EstadoAsignacion.APROBADA:
                asignacion.formalizar(supervisor)
            asignaciones.append(asignacion)
            ids_recuperados.add(id_asignacion)
        except (KeyError, ValueError, TypeError, PermissionError) as error:
            raise ValueError(
                f"Error al cargar la asignación en posición {posicion}: {error}"
            ) from error
    return asignaciones


def guardar_datos(ruta="data/datos_sistema.json", asignaciones=None):
    """Guarda áreas, personal y trabajos, y opcionalmente sus asignaciones.

    Con None conserva las asignaciones guardadas; con [] las elimina.
    """
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
                "atributos_opcionales": t.atributos_opcionales,
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
    if asignaciones is not None:
        datos["asignaciones"] = [
            {
                "id_asignacion": a.id_asignacion,
                "id_trabajo": a.trabajo.id_trabajo,
                "id_trabajador": a.trabajador.id_trabajador if a.trabajador else None,
                "fecha": a.fecha.isoformat(),
                "franja_horaria": a.franja_horaria.value,
                "estado": a.estado.value,
                "id_supervisor_aprobador": (
                    a.supervisor_aprobador.id_trabajador if a.supervisor_aprobador else None
                ),
            }
            for a in asignaciones
        ]
    else:
        # Las llamadas antiguas conservan las asignaciones del archivo existente.
        try:
            with open(ruta, encoding="utf-8") as archivo:
                anteriores = json.load(archivo)
        except FileNotFoundError:
            anteriores = {}
        if "asignaciones" in anteriores:
            datos["asignaciones"] = anteriores["asignaciones"]

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
