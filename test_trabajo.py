from unittest.mock import Mock

import pytest

from trabajo import Trabajo
from sistema_registro import sistema_registro


@pytest.fixture(autouse=True)
def registro_vacio(monkeypatch):
    # cada test usa un registro nuevo y vacío; el original se restaura solo al terminar
    monkeypatch.setattr(Trabajo, "registro", sistema_registro())


def crear_trabajo(id_trabajo="J1"):
    return Trabajo(id_trabajo, "Cambiar rack", "Reemplazar el rack 3", 4, {"Redes"}, {"CCNA"}, Mock())


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
