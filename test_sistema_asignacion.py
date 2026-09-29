from datetime import date
from unittest.mock import Mock

import pytest

from enums import FranjaHoraria as F, EstadoAsignacion
from trabajador import Trabajador
from supervisor import Supervisor
from trabajo import Trabajo
from sistema_asignacion import SistemaAsignacion


FECHA = date(2026, 9, 16)


def trabajo_mock(id_trabajo="T1"):
    """Labor falsa con un área cuyo cupo está disponible."""
    trabajo = Mock(spec=Trabajo)
    trabajo.id_trabajo = id_trabajo
    trabajo.titulo = "Cambiar rack"
    trabajo.duracion_horas = 4
    trabajo.habilidades_requeridas = {"Redes"}
    trabajo.credenciales_requeridas = {"CCNA"}
    trabajo.area_trabajo = Mock()
    trabajo.area_trabajo.id_area = "A1"
    trabajo.area_trabajo.nombre = "Sala de Servidores"
    trabajo.area_trabajo.credenciales_obligatorias = {"Altura"}
    trabajo.area_trabajo.tiene_cupo_disponible.return_value = True
    return trabajo


def trabajador_apto(id_trabajador="W1"):
    """Trabajador falso que pasa todas las validaciones de agregar_trabajador."""
    trabajador = Mock(spec=Trabajador)
    trabajador.id_trabajador = id_trabajador
    trabajador.nombre = "Nico"
    trabajador.limite_horas_semanales = 40
    trabajador.esta_disponible.return_value = True
    trabajador.tiene_habilidades.return_value = True
    trabajador.tiene_credenciales_activas.return_value = True
    trabajador.excede_limite_horas.return_value = False
    return trabajador


def supervisor_del_area():
    supervisor = Mock(spec=Supervisor)
    supervisor.nombre = "Laura"
    supervisor.area_a_cargo = "A1"
    return supervisor


@pytest.fixture(autouse=True)
def asignaciones_vacias(monkeypatch):
    # vacía las asignaciones activas durante el test y restaura su contenido al terminar
    monkeypatch.setattr(SistemaAsignacion, "_asignaciones_activas", {})


@pytest.fixture
def trabajo():
    return trabajo_mock()


@pytest.fixture
def area(trabajo):
    return trabajo.area_trabajo


@pytest.fixture
def asignacion(trabajo):
    return SistemaAsignacion(1, trabajo, FECHA, F.MANIANA)


# ---------- __init__ ----------

def test_init_arranca_pendiente_sin_trabajador_ni_supervisor(asignacion, trabajo):
    assert asignacion.id_asignacion == 1
    assert asignacion.trabajo is trabajo
    assert asignacion.fecha == FECHA
    assert asignacion.franja_horaria == F.MANIANA
    assert asignacion.estado == EstadoAsignacion.PENDIENTE
    assert asignacion.trabajador is None
    assert asignacion.supervisor_aprobador is None


# ---------- agregar_trabajador ----------

def test_agregar_trabajador_apto_reserva_horas_ocupacion_y_cupo(asignacion, area):
    trabajador = trabajador_apto()

    asignacion.agregar_trabajador(trabajador)

    assert asignacion.trabajador is trabajador
    trabajador.sumar_horas.assert_called_once_with(4)
    trabajador.registrar_ocupacion.assert_called_once_with(F.MANIANA, FECHA)
    area.registrar_trabajador_en_franja.assert_called_once_with(FECHA, F.MANIANA, "W1")
    assert SistemaAsignacion._asignaciones_activas[("T1", FECHA, F.MANIANA)] is asignacion


def test_agregar_trabajador_rechaza_si_la_asignacion_esta_aprobada(asignacion):
    asignacion.estado = EstadoAsignacion.APROBADA

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador_apto())


def test_agregar_trabajador_rechaza_si_ya_tiene_trabajador(asignacion):
    asignacion.agregar_trabajador(trabajador_apto("W1"))

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador_apto("W2"))


def test_agregar_trabajador_rechaza_labor_ya_asignada_en_esa_franja(asignacion, trabajo):
    """Regla 7: la misma labor no puede comprometerse dos veces en la misma fecha y franja."""
    SistemaAsignacion(2, trabajo, FECHA, F.MANIANA).agregar_trabajador(trabajador_apto("W1"))
    trabajador = trabajador_apto("W2")

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador)
    trabajador.sumar_horas.assert_not_called()


def test_agregar_trabajador_rechaza_si_no_esta_disponible(asignacion):
    trabajador = trabajador_apto()
    trabajador.esta_disponible.return_value = False

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador)
    trabajador.sumar_horas.assert_not_called()


def test_agregar_trabajador_rechaza_si_no_tiene_habilidades(asignacion):
    trabajador = trabajador_apto()
    trabajador.tiene_habilidades.return_value = False

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador)
    trabajador.tiene_habilidades.assert_called_once_with({"Redes"})


@pytest.mark.parametrize("credencial_faltante", [{"CCNA"}, {"Altura"}], ids=["de_la_labor", "del_area"])
def test_agregar_trabajador_rechaza_sin_credenciales(asignacion, credencial_faltante):
    trabajador = trabajador_apto()
    trabajador.tiene_credenciales_activas.side_effect = lambda requeridas, fecha: requeridas != credencial_faltante

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador)


def test_agregar_trabajador_rechaza_si_excede_limite_de_horas(asignacion):
    trabajador = trabajador_apto()
    trabajador.excede_limite_horas.return_value = True

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador)
    trabajador.excede_limite_horas.assert_called_once_with(4)


def test_agregar_trabajador_rechaza_si_el_area_no_tiene_cupo(asignacion, area):
    area.tiene_cupo_disponible.return_value = False

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador(trabajador_apto())
    area.registrar_trabajador_en_franja.assert_not_called()
    assert asignacion.trabajador is None


# ---------- agregar_trabajador sin indicar trabajador ----------

def trabajador_con_horas_libres(id_trabajador, horas_libres):
    trabajador = trabajador_apto(id_trabajador)
    trabajador.tiempo_libre.return_value = horas_libres
    return trabajador


def test_agregar_trabajador_sin_argumento_propone_al_de_mas_horas_libres(asignacion, trabajo, monkeypatch):
    poco_libre = trabajador_con_horas_libres("W1", 5)
    mas_libre = trabajador_con_horas_libres("W2", 30)
    medio_libre = trabajador_con_horas_libres("W3", 12)
    disponibles_en = Mock(return_value=[poco_libre, mas_libre, medio_libre])
    monkeypatch.setattr(Trabajador, "disponibles_en", disponibles_en)

    asignacion.agregar_trabajador()

    disponibles_en.assert_called_once_with(trabajo, FECHA, F.MANIANA)
    assert asignacion.trabajador is mas_libre
    mas_libre.sumar_horas.assert_called_once_with(4)
    poco_libre.sumar_horas.assert_not_called()
    medio_libre.sumar_horas.assert_not_called()


def test_agregar_trabajador_sin_argumento_rechaza_si_no_hay_aptos(asignacion, monkeypatch):
    monkeypatch.setattr(Trabajador, "disponibles_en", Mock(return_value=[]))

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador()
    assert asignacion.trabajador is None


def test_agregar_trabajador_sin_argumento_no_busca_si_ya_tiene_trabajador(asignacion, monkeypatch):
    asignacion.agregar_trabajador(trabajador_apto("W1"))
    disponibles_en = Mock(return_value=[trabajador_con_horas_libres("W2", 30)])
    monkeypatch.setattr(Trabajador, "disponibles_en", disponibles_en)

    with pytest.raises(ValueError):
        asignacion.agregar_trabajador()
    disponibles_en.assert_not_called()


# ---------- formalizar ----------

def test_formalizar_aprueba_con_supervisor_del_area(asignacion):
    asignacion.trabajador = trabajador_apto()
    supervisor = supervisor_del_area()

    asignacion.formalizar(supervisor)

    assert asignacion.estado == EstadoAsignacion.APROBADA
    assert asignacion.supervisor_aprobador is supervisor


def test_formalizar_rechaza_si_ya_esta_aprobada(asignacion):
    asignacion.trabajador = trabajador_apto()
    asignacion.estado = EstadoAsignacion.APROBADA

    with pytest.raises(ValueError):
        asignacion.formalizar(supervisor_del_area())


def test_formalizar_rechaza_sin_trabajador_propuesto(asignacion):
    with pytest.raises(ValueError):
        asignacion.formalizar(supervisor_del_area())


def test_formalizar_rechaza_si_no_es_supervisor(asignacion):
    asignacion.trabajador = trabajador_apto()

    with pytest.raises(PermissionError):
        asignacion.formalizar(trabajador_apto("W9"))
    assert asignacion.estado == EstadoAsignacion.PENDIENTE


def test_formalizar_rechaza_supervisor_de_otra_area(asignacion):
    asignacion.trabajador = trabajador_apto()
    supervisor = supervisor_del_area()
    supervisor.area_a_cargo = "A2"

    with pytest.raises(PermissionError):
        asignacion.formalizar(supervisor)
    assert asignacion.supervisor_aprobador is None
