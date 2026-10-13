from area_de_trabajo import AreaDeTrabajo
from trabajador import Trabajador
from supervisor import Supervisor
from trabajo import Trabajo
from loader_datos import cargar_datos, guardar_datos


def test_cargar_datos_crea_todo():
    # se limpian los registros por si otros tests ya crearon objetos
    AreaDeTrabajo.registro.areas.clear()
    Trabajador.registro.trabajadores.clear()
    Trabajo.registro.trabajos.clear()

    cargar_datos()

    assert len(AreaDeTrabajo.registro.areas) == 2
    assert len(Trabajador.registro.trabajadores) == 5
    assert len(Trabajo.registro.trabajos) == 2
    supervisores = [t for t in Trabajador.registro.trabajadores if isinstance(t, Supervisor)]
    assert {s.area_a_cargo for s in supervisores} == {"A1", "A2"}
    assert all(t.horas_asignadas_semana == 0 for t in Trabajador.registro.trabajadores)


def test_guardar_y_volver_a_cargar(tmp_path):
    AreaDeTrabajo.registro.areas.clear()
    Trabajador.registro.trabajadores.clear()
    Trabajo.registro.trabajos.clear()
    cargar_datos()

    ruta = str(tmp_path / "copia.json")
    guardar_datos(ruta)

    AreaDeTrabajo.registro.areas.clear()
    Trabajador.registro.trabajadores.clear()
    Trabajo.registro.trabajos.clear()
    cargar_datos(ruta)

    assert len(AreaDeTrabajo.registro.areas) == 2
    assert len(Trabajador.registro.trabajadores) == 5
    assert len(Trabajo.registro.trabajos) == 2
    ana = next(t for t in Trabajador.registro.trabajadores if t.id_trabajador == "T1")
    assert {c.nombre for c in ana.credenciales} == {"Seguridad Industrial", "Soldadura Certificada"}
