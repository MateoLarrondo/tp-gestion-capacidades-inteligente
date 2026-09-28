import unittest
from unittest.mock import Mock

from trabajo import Trabajo


def crear_trabajo(id_trabajo="J1"):
    return Trabajo(id_trabajo, "Cambiar rack", "Reemplazar el rack 3", 4, {"Redes"}, {"CCNA"}, Mock())


class TestTrabajo(unittest.TestCase):

    def setUp(self):
        Trabajo.registro.trabajos.clear()

    def tearDown(self):
        Trabajo.registro.trabajos.clear()

    def test_init_agrega_el_trabajo_al_registro(self):
        trabajo = crear_trabajo()

        self.assertEqual(Trabajo.registro.trabajos, [trabajo])

    def test_init_rechaza_id_repetido(self):
        trabajo = crear_trabajo("J1")

        with self.assertRaises(ValueError):
            crear_trabajo("J1")
        self.assertEqual(Trabajo.registro.trabajos, [trabajo])

    def test_init_invalido_no_queda_en_el_registro(self):
        with self.assertRaises(ValueError):
            Trabajo("J1", "Cambiar rack", "", 0, set(), set(), Mock())

        self.assertEqual(Trabajo.registro.trabajos, [])


if __name__ == "__main__":
    unittest.main()
