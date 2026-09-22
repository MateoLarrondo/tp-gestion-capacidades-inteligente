import unittest
from datetime import date
from unittest.mock import Mock, patch

from enums import FranjaHoraria as F
from credencial import Credencial
from trabajador import Trabajador


FECHA = date(2026, 9, 16)


def credencial_mock(nombre, activa):
    """Credencial falsa: solo interesa su nombre y lo que responde esta_activa."""
    credencial = Mock(spec=Credencial)
    credencial.nombre = nombre
    credencial.esta_activa.return_value = activa
    return credencial


class TestTrabajador(unittest.TestCase):

    def setUp(self):
        Trabajador.registro.trabajadores.clear()
        self.trabajador = Trabajador("W1", "Nico", F.MANIANA, {"Redes", "Soldadura"}, [], 40)

    def tearDown(self):
        Trabajador.registro.trabajadores.clear()

    # ---------- __init__ ----------

    def test_init_guarda_los_datos_y_arranca_sin_horas(self):
        self.assertEqual(self.trabajador.id_trabajador, "W1")
        self.assertEqual(self.trabajador.nombre, "Nico")
        self.assertEqual(self.trabajador.franja_horaria, F.MANIANA)
        self.assertEqual(self.trabajador.habilidades, {"Redes", "Soldadura"})
        self.assertEqual(self.trabajador.horas_asignadas_semana, 0.0)
        self.assertEqual(self.trabajador.atributos_opcionales, {})

    def test_init_agrega_al_trabajador_al_registro(self):
        self.assertIn(self.trabajador, Trabajador.registro.trabajadores)

    def test_init_invalido_no_queda_en_el_registro(self):
        with self.assertRaises(ValueError):
            Trabajador("W2", "Ana", F.TARDE, set(), [], 0)

        self.assertEqual(Trabajador.registro.trabajadores, [self.trabajador])

    # ---------- registrar_personal ----------

    def test_registrar_personal_guarda_atributos_opcionales_por_kwargs(self):
        trabajador = Trabajador.registrar_personal(
            "W2", "Ana", F.TARDE, {"Redes"}, 30, idioma="Ingles", area_origen="Mecanica"
        )

        self.assertIsInstance(trabajador, Trabajador)
        self.assertEqual(trabajador.credenciales, [])
        self.assertEqual(trabajador.atributos_opcionales, {"idioma": "Ingles", "area_origen": "Mecanica"})

    def test_registrar_personal_sin_kwargs_deja_atributos_vacios(self):
        trabajador = Trabajador.registrar_personal("W2", "Ana", F.TARDE, set(), 30)

        self.assertEqual(trabajador.atributos_opcionales, {})

    # ---------- obtener_credenciales_activas ----------

    def test_obtener_credenciales_activas_devuelve_solo_las_vigentes(self):
        self.trabajador.credenciales = [
            credencial_mock("CCNA", True),
            credencial_mock("Altura", False),
        ]

        self.assertEqual(self.trabajador.obtener_credenciales_activas(FECHA), {"CCNA"})

    def test_obtener_credenciales_activas_consulta_con_la_fecha_dada(self):
        credencial = credencial_mock("CCNA", True)
        self.trabajador.credenciales = [credencial]

        self.trabajador.obtener_credenciales_activas(FECHA)

        credencial.esta_activa.assert_called_once_with(FECHA)

    # ---------- tiene_habilidades ----------

    def test_tiene_habilidades_true_si_las_tiene_todas(self):
        self.assertTrue(self.trabajador.tiene_habilidades({"Redes"}))

    def test_tiene_habilidades_false_si_falta_alguna(self):
        self.assertFalse(self.trabajador.tiene_habilidades({"Redes", "Electricidad"}))

    # ---------- tiene_credenciales_activas ----------

    def test_tiene_credenciales_activas_true_si_estan_todas_vigentes(self):
        with patch.object(self.trabajador, "obtener_credenciales_activas", return_value={"CCNA", "Altura"}) as obtener:
            self.assertTrue(self.trabajador.tiene_credenciales_activas({"CCNA"}, FECHA))
        obtener.assert_called_once_with(FECHA)

    def test_tiene_credenciales_activas_false_si_falta_alguna(self):
        with patch.object(self.trabajador, "obtener_credenciales_activas", return_value={"CCNA"}):
            self.assertFalse(self.trabajador.tiene_credenciales_activas({"CCNA", "Altura"}, FECHA))

    # ---------- excede_limite_horas ----------

    def test_excede_limite_horas_false_si_queda_dentro_del_limite(self):
        self.trabajador.horas_asignadas_semana = 30

        self.assertFalse(self.trabajador.excede_limite_horas(10))

    def test_excede_limite_horas_true_si_se_pasa_del_limite(self):
        self.trabajador.horas_asignadas_semana = 35

        self.assertTrue(self.trabajador.excede_limite_horas(10))

    # ---------- sumar_horas ----------

    def test_sumar_horas_acumula_si_no_excede(self):
        with patch.object(self.trabajador, "excede_limite_horas", return_value=False):
            self.trabajador.sumar_horas(8)

        self.assertEqual(self.trabajador.horas_asignadas_semana, 8)

    def test_sumar_horas_lanza_error_si_excede(self):
        with patch.object(self.trabajador, "excede_limite_horas", return_value=True):
            with self.assertRaises(ValueError):
                self.trabajador.sumar_horas(8)

        self.assertEqual(self.trabajador.horas_asignadas_semana, 0.0)

    # ---------- reiniciar_semana ----------

    def test_reiniciar_semana_pone_las_horas_en_cero(self):
        self.trabajador.horas_asignadas_semana = 25

        self.trabajador.reiniciar_semana()

        self.assertEqual(self.trabajador.horas_asignadas_semana, 0.0)

    # ---------- reiniciar_semana_todos ----------

    def test_reiniciar_semana_todos_reinicia_a_todo_el_registro(self):
        otro = Trabajador("W2", "Ana", F.TARDE, set(), [], 30)

        with patch.object(Trabajador, "reiniciar_semana") as reiniciar:
            Trabajador.reiniciar_semana_todos()

        self.assertEqual(reiniciar.call_count, 2)
        self.assertEqual(Trabajador.registro.trabajadores, [self.trabajador, otro])

    # ---------- limite_horas_positivo ----------

    def test_limite_horas_positivo_no_falla_con_limite_valido(self):
        self.trabajador.limite_horas_positivo()

    def test_limite_horas_positivo_lanza_error_con_cero_o_negativo(self):
        for limite in (0, -5):
            self.trabajador.limite_horas_semanales = limite
            with self.assertRaises(ValueError):
                self.trabajador.limite_horas_positivo()

    # ---------- id_no_vacio ----------

    def test_id_no_vacio_no_falla_con_id_valido(self):
        self.trabajador.id_no_vacio()

    def test_id_no_vacio_lanza_error_con_id_vacio(self):
        self.trabajador.id_trabajador = ""

        with self.assertRaises(ValueError):
            self.trabajador.id_no_vacio()

    # ---------- tiempo_libre ----------

    def test_tiempo_libre_es_limite_menos_horas_asignadas(self):
        self.trabajador.horas_asignadas_semana = 12

        self.assertEqual(self.trabajador.tiempo_libre(), 28)

    # ---------- esta_ocupado / registrar_ocupacion ----------

    def test_esta_ocupado_false_si_no_registro_esa_franja(self):
        self.assertFalse(self.trabajador.esta_ocupado(F.MANIANA, FECHA))

    def test_registrar_ocupacion_marca_solo_esa_franja_y_fecha(self):
        self.trabajador.registrar_ocupacion(F.MANIANA, FECHA)

        self.assertTrue(self.trabajador.esta_ocupado(F.MANIANA, FECHA))
        self.assertFalse(self.trabajador.esta_ocupado(F.TARDE, FECHA))
        self.assertFalse(self.trabajador.esta_ocupado(F.MANIANA, date(2026, 9, 17)))

    # ---------- esta_disponible ----------

    def test_esta_disponible_true_si_cumple_todo(self):
        with patch.object(self.trabajador, "esta_ocupado", return_value=False), \
                patch.object(self.trabajador, "tiempo_libre", return_value=10):
            self.assertTrue(self.trabajador.esta_disponible(F.MANIANA, FECHA))

    def test_esta_disponible_false_si_es_otra_franja(self):
        with patch.object(self.trabajador, "esta_ocupado", return_value=False), \
                patch.object(self.trabajador, "tiempo_libre", return_value=10):
            self.assertFalse(self.trabajador.esta_disponible(F.NOCHE, FECHA))

    def test_esta_disponible_false_si_esta_ocupado(self):
        with patch.object(self.trabajador, "esta_ocupado", return_value=True), \
                patch.object(self.trabajador, "tiempo_libre", return_value=10):
            self.assertFalse(self.trabajador.esta_disponible(F.MANIANA, FECHA))

    def test_esta_disponible_false_si_no_le_quedan_horas(self):
        with patch.object(self.trabajador, "esta_ocupado", return_value=False), \
                patch.object(self.trabajador, "tiempo_libre", return_value=0):
            self.assertFalse(self.trabajador.esta_disponible(F.MANIANA, FECHA))

    # ---------- disponibles_en ----------

    def _trabajo_mock(self):
        trabajo = Mock()
        trabajo.habilidades_requeridas = {"Redes"}
        trabajo.credenciales_requeridas = {"CCNA"}
        trabajo.duracion_horas = 4
        trabajo.area_trabajo.credenciales_obligatorias = {"Altura"}
        trabajo.area_trabajo.tiene_cupo_disponible.return_value = True
        return trabajo

    def _hacer_apto(self, trabajador):
        """Mockea los chequeos del trabajador para que pase todos los filtros."""
        trabajador.esta_disponible = Mock(return_value=True)
        trabajador.tiene_habilidades = Mock(return_value=True)
        trabajador.tiene_credenciales_activas = Mock(return_value=True)
        trabajador.excede_limite_horas = Mock(return_value=False)

    def test_disponibles_en_devuelve_los_que_pasan_todos_los_filtros(self):
        otro = Trabajador("W2", "Ana", F.MANIANA, set(), [], 30)
        self._hacer_apto(self.trabajador)
        self._hacer_apto(otro)

        resultado = Trabajador.disponibles_en(self._trabajo_mock(), FECHA, F.MANIANA)

        self.assertEqual(resultado, [self.trabajador, otro])

    def test_disponibles_en_excluye_a_quien_falla_algun_filtro(self):
        filtros = {
            "esta_disponible": False,
            "tiene_habilidades": False,
            "tiene_credenciales_activas": False,
            "excede_limite_horas": True,
        }
        for metodo, valor in filtros.items():
            with self.subTest(filtro=metodo):
                self._hacer_apto(self.trabajador)
                setattr(self.trabajador, metodo, Mock(return_value=valor))

                resultado = Trabajador.disponibles_en(self._trabajo_mock(), FECHA, F.MANIANA)

                self.assertEqual(resultado, [])

    def test_disponibles_en_excluye_si_el_area_no_tiene_cupo(self):
        self._hacer_apto(self.trabajador)
        trabajo = self._trabajo_mock()
        trabajo.area_trabajo.tiene_cupo_disponible.return_value = False

        resultado = Trabajador.disponibles_en(trabajo, FECHA, F.MANIANA)

        self.assertEqual(resultado, [])
        trabajo.area_trabajo.tiene_cupo_disponible.assert_called_once_with(FECHA, F.MANIANA, "W1")


if __name__ == "__main__":
    unittest.main()
