from area_de_trabajo import AreaDeTrabajo
from trabajador import Trabajador
from supervisor import Supervisor
from trabajo import Trabajo
from loader_datos import cargar_datos


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
