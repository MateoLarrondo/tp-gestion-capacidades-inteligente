from datetime import date

import pytest

from enums import FranjaHoraria as F
from trabajador import Trabajador
from area_de_trabajo import AreaDeTrabajo
from trabajo import Trabajo
from sistema_asignacion import SistemaAsignacion


def test_agregar_trabajador_rechaza_si_no_es_apto():
    """Un trabajador sin las habilidades/credenciales que exige la labor no debe poder proponerse (reglas 4 y 10)."""
    area = AreaDeTrabajo("A1", "Sala de Servidores", {"Trabajo en Altura"}, {F.MANIANA: 2})
    trabajo = Trabajo("T1", "Cambiar rack", "desc", 4, {"Redes"}, {"CCNA"}, area)
    pepe = Trabajador("P1", "Pepe", F.MANIANA, set(), [], 40)
    asignacion = SistemaAsignacion(1, trabajo, date(2026, 9, 16), F.MANIANA)

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(pepe)


def test_registrar_personal_guarda_atributos_opcionales_por_kwargs():
    """registrar_personal debe guardar cualquier atributo extra recibido por **kwargs."""
    trabajador = Trabajador.registrar_personal(
        "W1", "Nico", F.MANIANA, {"Redes"}, 40, idioma="Ingles", area_origen="Mecanica"
    )

    assert trabajador.atributos_opcionales == {"idioma": "Ingles", "area_origen": "Mecanica"}
