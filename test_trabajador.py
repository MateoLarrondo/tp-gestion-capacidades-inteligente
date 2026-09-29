from datetime import date
from unittest.mock import Mock

import pytest

from enums import FranjaHoraria as F
from credencial import Credencial
from trabajador import Trabajador
from supervisor import Supervisor
from area_de_trabajo import AreaDeTrabajo
from sistema_registro import sistema_registro
from registro_areas import registro_areas


FECHA = date(2026, 9, 16)


def credencial_mock(nombre, activa):
    """Credencial falsa: solo interesa su nombre y lo que responde esta_activa."""
    credencial = Mock(spec=Credencial)
    credencial.nombre = nombre
    credencial.esta_activa.return_value = activa
    return credencial


def trabajo_mock():
    trabajo = Mock()
    trabajo.habilidades_requeridas = {"Redes"}
    trabajo.credenciales_requeridas = {"CCNA"}
    trabajo.duracion_horas = 4
    trabajo.area_trabajo.credenciales_obligatorias = {"Altura"}
    trabajo.area_trabajo.tiene_cupo_disponible.return_value = True
    return trabajo


def hacer_apto(trabajador):
    """Mockea los chequeos del trabajador para que pase todos los filtros."""
    trabajador.esta_disponible = Mock(return_value=True)
    trabajador.tiene_habilidades = Mock(return_value=True)
    trabajador.tiene_credenciales_activas = Mock(return_value=True)
    trabajador.excede_limite_horas = Mock(return_value=False)


@pytest.fixture(autouse=True)
def registros_vacios(monkeypatch):
    # cada test usa registros nuevos y vacíos; los originales se restauran solos al terminar
    monkeypatch.setattr(Trabajador, "registro", sistema_registro())
    monkeypatch.setattr(AreaDeTrabajo, "registro", registro_areas())
    AreaDeTrabajo("A1", "Taller", set(), {F.TARDE: 2})


@pytest.fixture
def trabajador():
    return Trabajador("W1", "Nico", F.MANIANA, {"Redes", "Soldadura"}, [], 40)


# ---------- __init__ ----------

def test_init_guarda_los_datos_y_arranca_sin_horas(trabajador):
    assert trabajador.id_trabajador == "W1"
    assert trabajador.nombre == "Nico"
    assert trabajador.franja_horaria == F.MANIANA
    assert trabajador.habilidades == {"Redes", "Soldadura"}
    assert trabajador.horas_asignadas_semana == 0.0
    assert trabajador.atributos_opcionales == {}


def test_init_agrega_al_trabajador_al_registro(trabajador):
    assert trabajador in Trabajador.registro.trabajadores


def test_init_invalido_no_queda_en_el_registro(trabajador):
    with pytest.raises(ValueError):
        Trabajador("W2", "Ana", F.TARDE, set(), [], 0)

    assert Trabajador.registro.trabajadores == [trabajador]


def test_init_rechaza_id_repetido(trabajador):
    with pytest.raises(ValueError):
        Trabajador("W1", "Ana", F.TARDE, set(), [], 30)

    assert Trabajador.registro.trabajadores == [trabajador]


# ---------- registrar_personal ----------

def test_registrar_personal_desde_supervisor_devuelve_un_supervisor():
    supervisor = Supervisor.registrar_personal("S1", "Laura", F.TARDE, set(), 30, "A1", idioma="Ingles")

    assert isinstance(supervisor, Supervisor)
    assert supervisor.area_a_cargo == "A1"
    assert supervisor.atributos_opcionales == {"idioma": "Ingles"}


@pytest.mark.parametrize("area", ["", "A9"], ids=["sin_area", "area_inexistente"])
def test_supervisor_con_area_invalida_no_queda_en_el_registro(trabajador, area):
    with pytest.raises(ValueError):
        Supervisor("S1", "Laura", F.TARDE, set(), [], 30, area)

    assert Trabajador.registro.trabajadores == [trabajador]


def test_registrar_personal_guarda_atributos_opcionales_por_kwargs():
    trabajador = Trabajador.registrar_personal(
        "W2", "Ana", F.TARDE, {"Redes"}, 30, idioma="Ingles", area_origen="Mecanica"
    )

    assert isinstance(trabajador, Trabajador)
    assert trabajador.credenciales == []
    assert trabajador.atributos_opcionales == {"idioma": "Ingles", "area_origen": "Mecanica"}


def test_registrar_personal_sin_kwargs_deja_atributos_vacios():
    trabajador = Trabajador.registrar_personal("W2", "Ana", F.TARDE, set(), 30)

    assert trabajador.atributos_opcionales == {}


# ---------- obtener_credenciales_activas ----------

def test_obtener_credenciales_activas_devuelve_solo_las_vigentes(trabajador):
    trabajador.credenciales = [
        credencial_mock("CCNA", True),
        credencial_mock("Altura", False),
    ]

    assert trabajador.obtener_credenciales_activas(FECHA) == {"CCNA"}


def test_obtener_credenciales_activas_consulta_con_la_fecha_dada(trabajador):
    credencial = credencial_mock("CCNA", True)
    trabajador.credenciales = [credencial]

    trabajador.obtener_credenciales_activas(FECHA)

    credencial.esta_activa.assert_called_once_with(FECHA)


# ---------- tiene_habilidades ----------

@pytest.mark.parametrize("requeridas, esperado", [
    ({"Redes"}, True),
    ({"Redes", "Electricidad"}, False),
])
def test_tiene_habilidades(trabajador, requeridas, esperado):
    assert trabajador.tiene_habilidades(requeridas) is esperado


# ---------- tiene_credenciales_activas ----------

def test_tiene_credenciales_activas_true_si_estan_todas_vigentes(trabajador, monkeypatch):
    obtener = Mock(return_value={"CCNA", "Altura"})
    monkeypatch.setattr(trabajador, "obtener_credenciales_activas", obtener)

    assert trabajador.tiene_credenciales_activas({"CCNA"}, FECHA)
    obtener.assert_called_once_with(FECHA)


def test_tiene_credenciales_activas_false_si_falta_alguna(trabajador, monkeypatch):
    monkeypatch.setattr(trabajador, "obtener_credenciales_activas", Mock(return_value={"CCNA"}))

    assert not trabajador.tiene_credenciales_activas({"CCNA", "Altura"}, FECHA)


# ---------- excede_limite_horas ----------

@pytest.mark.parametrize("asignadas, esperado", [(30, False), (35, True)])
def test_excede_limite_horas(trabajador, asignadas, esperado):
    trabajador.horas_asignadas_semana = asignadas

    assert trabajador.excede_limite_horas(10) is esperado


# ---------- sumar_horas ----------

def test_sumar_horas_acumula_si_no_excede(trabajador, monkeypatch):
    monkeypatch.setattr(trabajador, "excede_limite_horas", Mock(return_value=False))

    trabajador.sumar_horas(8)

    assert trabajador.horas_asignadas_semana == 8


def test_sumar_horas_lanza_error_si_excede(trabajador, monkeypatch):
    monkeypatch.setattr(trabajador, "excede_limite_horas", Mock(return_value=True))

    with pytest.raises(ValueError):
        trabajador.sumar_horas(8)
    assert trabajador.horas_asignadas_semana == 0.0


# ---------- reiniciar_semana ----------

def test_reiniciar_semana_pone_las_horas_en_cero(trabajador):
    trabajador.horas_asignadas_semana = 25

    trabajador.reiniciar_semana()

    assert trabajador.horas_asignadas_semana == 0.0


# ---------- reiniciar_semana_todos ----------

def test_reiniciar_semana_todos_reinicia_a_todo_el_registro(trabajador, monkeypatch):
    otro = Trabajador("W2", "Ana", F.TARDE, set(), [], 30)
    reiniciar = Mock()
    monkeypatch.setattr(Trabajador, "reiniciar_semana", reiniciar)

    Trabajador.reiniciar_semana_todos()

    assert reiniciar.call_count == 2
    assert Trabajador.registro.trabajadores == [trabajador, otro]


# ---------- limite_horas_positivo ----------

def test_limite_horas_positivo_no_falla_con_limite_valido(trabajador):
    trabajador.limite_horas_positivo()


@pytest.mark.parametrize("limite", [0, -5])
def test_limite_horas_positivo_lanza_error_con_cero_o_negativo(trabajador, limite):
    trabajador.limite_horas_semanales = limite

    with pytest.raises(ValueError):
        trabajador.limite_horas_positivo()


# ---------- id_no_vacio ----------

def test_id_no_vacio_no_falla_con_id_valido(trabajador):
    trabajador.id_no_vacio()


def test_id_no_vacio_lanza_error_con_id_vacio(trabajador):
    trabajador.id_trabajador = ""

    with pytest.raises(ValueError):
        trabajador.id_no_vacio()


# ---------- tiempo_libre ----------

def test_tiempo_libre_es_limite_menos_horas_asignadas(trabajador):
    trabajador.horas_asignadas_semana = 12

    assert trabajador.tiempo_libre() == 28


# ---------- esta_ocupado / registrar_ocupacion ----------

def test_esta_ocupado_false_si_no_registro_esa_franja(trabajador):
    assert not trabajador.esta_ocupado(F.MANIANA, FECHA)


def test_registrar_ocupacion_marca_solo_esa_franja_y_fecha(trabajador):
    trabajador.registrar_ocupacion(F.MANIANA, FECHA)

    assert trabajador.esta_ocupado(F.MANIANA, FECHA)
    assert not trabajador.esta_ocupado(F.TARDE, FECHA)
    assert not trabajador.esta_ocupado(F.MANIANA, date(2026, 9, 17))


# ---------- esta_disponible ----------

@pytest.mark.parametrize("franja, ocupado, libre, esperado", [
    (F.MANIANA, False, 10, True),
    (F.NOCHE, False, 10, False),
    (F.MANIANA, True, 10, False),
    (F.MANIANA, False, 0, False),
], ids=["cumple_todo", "otra_franja", "ocupado", "sin_horas"])
def test_esta_disponible(trabajador, monkeypatch, franja, ocupado, libre, esperado):
    monkeypatch.setattr(trabajador, "esta_ocupado", Mock(return_value=ocupado))
    monkeypatch.setattr(trabajador, "tiempo_libre", Mock(return_value=libre))

    assert trabajador.esta_disponible(franja, FECHA) is esperado


# ---------- disponibles_en ----------

def test_disponibles_en_devuelve_los_que_pasan_todos_los_filtros(trabajador):
    otro = Trabajador("W2", "Ana", F.MANIANA, set(), [], 30)
    hacer_apto(trabajador)
    hacer_apto(otro)

    resultado = Trabajador.disponibles_en(trabajo_mock(), FECHA, F.MANIANA)

    assert resultado == [trabajador, otro]


@pytest.mark.parametrize("metodo, valor", [
    ("esta_disponible", False),
    ("tiene_habilidades", False),
    ("tiene_credenciales_activas", False),
    ("excede_limite_horas", True),
])
def test_disponibles_en_excluye_a_quien_falla_algun_filtro(trabajador, metodo, valor):
    hacer_apto(trabajador)
    setattr(trabajador, metodo, Mock(return_value=valor))

    resultado = Trabajador.disponibles_en(trabajo_mock(), FECHA, F.MANIANA)

    assert resultado == []


def test_disponibles_en_excluye_si_el_area_no_tiene_cupo(trabajador):
    hacer_apto(trabajador)
    trabajo = trabajo_mock()
    trabajo.area_trabajo.tiene_cupo_disponible.return_value = False

    resultado = Trabajador.disponibles_en(trabajo, FECHA, F.MANIANA)

    assert resultado == []
    trabajo.area_trabajo.tiene_cupo_disponible.assert_called_once_with(FECHA, F.MANIANA, "W1")
