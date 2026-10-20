from datetime import date

import pytest

from enums import FranjaHoraria as F
from area_de_trabajo import AreaDeTrabajo
from registro_areas import registro_areas


FECHA = date(2026, 9, 16)


@pytest.fixture(autouse=True)
def registro_vacio(monkeypatch):
    # cada test usa un registro nuevo y vacío; el original se restaura solo al terminar
    monkeypatch.setattr(AreaDeTrabajo, "registro", registro_areas())


def test_reiniciar_semana_libera_el_cupo():
    area = AreaDeTrabajo("A1", "Taller", set(), {F.MANIANA: 1})
    area.registrar_trabajador_en_franja(FECHA, F.MANIANA, "W1")
    assert not area.tiene_cupo_disponible(FECHA, F.MANIANA, "W2")

    area.reiniciar_semana()

    assert area.tiene_cupo_disponible(FECHA, F.MANIANA, "W2")
