from enums import FranjaHoraria as F
from area_de_trabajo import AreaDeTrabajo


def test_credenciales_efectivas_suma_las_de_los_ancestros():
    AreaDeTrabajo.registro.areas.clear()
    planta = AreaDeTrabajo("P1", "Planta", {"Seguridad Industrial"}, {F.MANIANA: 5})
    linea = AreaDeTrabajo("L1", "Línea de Ensamble", {"Trabajo en Altura"}, {F.MANIANA: 3}, planta)
    estacion = AreaDeTrabajo("E1", "Estación Robótica", {"Robótica Nivel 2"}, {F.MANIANA: 1}, linea)

    # caso base: el área raíz solo exige lo suyo
    assert planta.credenciales_efectivas() == {"Seguridad Industrial"}
    # paso recursivo: cada nivel suma las credenciales de todos los de arriba
    assert linea.credenciales_efectivas() == {"Seguridad Industrial", "Trabajo en Altura"}
    assert estacion.credenciales_efectivas() == {"Seguridad Industrial", "Trabajo en Altura", "Robótica Nivel 2"}