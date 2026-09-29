from datetime import date
from unittest.mock import Mock

import pytest

from trabajo import Trabajo
from sistema_registro import sistema_registro


@pytest.fixture(autouse=True)
def registro_vacio(monkeypatch):
    # cada test usa un registro nuevo y vacío; el original se restaura solo al terminar
    monkeypatch.setattr(Trabajo, "registro", sistema_registro())


def crear_trabajo(id_trabajo="J1", duracion_horas=4):
    return Trabajo(id_trabajo, "Cambiar rack", "Reemplazar el rack 3", duracion_horas, {"Redes"}, {"CCNA"}, Mock())


def test_init_agrega_el_trabajo_al_registro():
    trabajo = crear_trabajo()

    assert Trabajo.registro.trabajos == [trabajo]


def test_init_rechaza_id_repetido():
    trabajo = crear_trabajo("J1")

    with pytest.raises(ValueError):
        crear_trabajo("J1")
    assert Trabajo.registro.trabajos == [trabajo]


def test_init_invalido_no_queda_en_el_registro():
    with pytest.raises(ValueError):
        Trabajo("J1", "Cambiar rack", "", 0, set(), set(), Mock())

    assert Trabajo.registro.trabajos == []


# ---------- reparto_por_dia ----------

@pytest.mark.parametrize("duracion, esperado", [
    (4, [(date(2026, 9, 16), 4)]),
    (8, [(date(2026, 9, 16), 8)]),
    (12, [(date(2026, 9, 16), 8), (date(2026, 9, 17), 4)]),
    (16, [(date(2026, 9, 16), 8), (date(2026, 9, 17), 8)]),
    (20, [(date(2026, 9, 16), 8), (date(2026, 9, 17), 8), (date(2026, 9, 18), 4)]),
])
def test_reparto_por_dia_divide_en_bloques_de_8_horas(duracion, esperado):
    trabajo = crear_trabajo(duracion_horas=duracion)

    assert trabajo.reparto_por_dia(date(2026, 9, 16)) == esperado


def test_reparto_por_dia_cruza_fin_de_mes():
    trabajo = crear_trabajo(duracion_horas=10)

    assert trabajo.reparto_por_dia(date(2026, 9, 30)) == [(date(2026, 9, 30), 8), (date(2026, 10, 1), 2)]
