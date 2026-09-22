import unittest
from datetime import date
from unittest.mock import Mock

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


class TestSistemaAsignacion(unittest.TestCase):

    def setUp(self):
        SistemaAsignacion._asignaciones_activas.clear()
        self.trabajo = trabajo_mock()
        self.area = self.trabajo.area_trabajo
        self.asignacion = SistemaAsignacion(1, self.trabajo, FECHA, F.MANIANA)

    def tearDown(self):
        SistemaAsignacion._asignaciones_activas.clear()

    # ---------- __init__ ----------

    def test_init_arranca_pendiente_sin_trabajador_ni_supervisor(self):
        self.assertEqual(self.asignacion.id_asignacion, 1)
        self.assertIs(self.asignacion.trabajo, self.trabajo)
        self.assertEqual(self.asignacion.fecha, FECHA)
        self.assertEqual(self.asignacion.franja_horaria, F.MANIANA)
        self.assertEqual(self.asignacion.estado, EstadoAsignacion.PENDIENTE)
        self.assertIsNone(self.asignacion.trabajador)
        self.assertIsNone(self.asignacion.supervisor_aprobador)

    # ---------- agregar_trabajador ----------

    def test_agregar_trabajador_apto_reserva_horas_ocupacion_y_cupo(self):
        trabajador = trabajador_apto()

        self.asignacion.agregar_trabajador(trabajador)

        self.assertIs(self.asignacion.trabajador, trabajador)
        trabajador.sumar_horas.assert_called_once_with(4)
        trabajador.registrar_ocupacion.assert_called_once_with(F.MANIANA, FECHA)
        self.area.registrar_trabajador_en_franja.assert_called_once_with(FECHA, F.MANIANA, "W1")
        self.assertIs(SistemaAsignacion._asignaciones_activas[("T1", FECHA, F.MANIANA)], self.asignacion)

    def test_agregar_trabajador_rechaza_si_la_asignacion_esta_aprobada(self):
        self.asignacion.estado = EstadoAsignacion.APROBADA

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador_apto())

    def test_agregar_trabajador_rechaza_si_ya_tiene_trabajador(self):
        self.asignacion.agregar_trabajador(trabajador_apto("W1"))

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador_apto("W2"))

    def test_agregar_trabajador_rechaza_labor_ya_asignada_en_esa_franja(self):
        """Regla 7: la misma labor no puede comprometerse dos veces en la misma fecha y franja."""
        SistemaAsignacion(2, self.trabajo, FECHA, F.MANIANA).agregar_trabajador(trabajador_apto("W1"))
        trabajador = trabajador_apto("W2")

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador)
        trabajador.sumar_horas.assert_not_called()

    def test_agregar_trabajador_rechaza_si_no_esta_disponible(self):
        trabajador = trabajador_apto()
        trabajador.esta_disponible.return_value = False

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador)
        trabajador.sumar_horas.assert_not_called()

    def test_agregar_trabajador_rechaza_si_no_tiene_habilidades(self):
        trabajador = trabajador_apto()
        trabajador.tiene_habilidades.return_value = False

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador)
        trabajador.tiene_habilidades.assert_called_once_with({"Redes"})

    def test_agregar_trabajador_rechaza_sin_credenciales_de_la_labor(self):
        trabajador = trabajador_apto()
        trabajador.tiene_credenciales_activas.side_effect = lambda requeridas, fecha: requeridas != {"CCNA"}

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador)

    def test_agregar_trabajador_rechaza_sin_credenciales_del_area(self):
        trabajador = trabajador_apto()
        trabajador.tiene_credenciales_activas.side_effect = lambda requeridas, fecha: requeridas != {"Altura"}

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador)

    def test_agregar_trabajador_rechaza_si_excede_limite_de_horas(self):
        trabajador = trabajador_apto()
        trabajador.excede_limite_horas.return_value = True

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador)
        trabajador.excede_limite_horas.assert_called_once_with(4)

    def test_agregar_trabajador_rechaza_si_el_area_no_tiene_cupo(self):
        self.area.tiene_cupo_disponible.return_value = False
        trabajador = trabajador_apto()

        with self.assertRaises(ValueError):
            self.asignacion.agregar_trabajador(trabajador)
        self.area.registrar_trabajador_en_franja.assert_not_called()
        self.assertIsNone(self.asignacion.trabajador)

    # ---------- formalizar ----------

    def _supervisor_del_area(self):
        supervisor = Mock(spec=Supervisor)
        supervisor.nombre = "Laura"
        supervisor.area_a_cargo = self.area
        return supervisor

    def test_formalizar_aprueba_con_supervisor_del_area(self):
        self.asignacion.trabajador = trabajador_apto()
        supervisor = self._supervisor_del_area()

        self.asignacion.formalizar(supervisor)

        self.assertEqual(self.asignacion.estado, EstadoAsignacion.APROBADA)
        self.assertIs(self.asignacion.supervisor_aprobador, supervisor)

    def test_formalizar_rechaza_si_ya_esta_aprobada(self):
        self.asignacion.trabajador = trabajador_apto()
        self.asignacion.estado = EstadoAsignacion.APROBADA

        with self.assertRaises(ValueError):
            self.asignacion.formalizar(self._supervisor_del_area())

    def test_formalizar_rechaza_sin_trabajador_propuesto(self):
        with self.assertRaises(ValueError):
            self.asignacion.formalizar(self._supervisor_del_area())

    def test_formalizar_rechaza_si_no_es_supervisor(self):
        self.asignacion.trabajador = trabajador_apto()

        with self.assertRaises(PermissionError):
            self.asignacion.formalizar(trabajador_apto("W9"))
        self.assertEqual(self.asignacion.estado, EstadoAsignacion.PENDIENTE)

    def test_formalizar_rechaza_supervisor_de_otra_area(self):
        self.asignacion.trabajador = trabajador_apto()
        supervisor = self._supervisor_del_area()
        supervisor.area_a_cargo = Mock()

        with self.assertRaises(PermissionError):
            self.asignacion.formalizar(supervisor)
        self.assertIsNone(self.asignacion.supervisor_aprobador)


if __name__ == "__main__":
    unittest.main()
