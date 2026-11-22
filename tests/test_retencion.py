"""Pruebas del validador de storyboard."""
import unittest

from retencion import validar


class RetencionTests(unittest.TestCase):
    def setUp(self):
        self.guion = {
            "tiempos": {"duracion": 18},
            "direccion": {
                "hook": "Una bandeja de entrada explota en pantalla",
                "payoff": "Los mensajes se convierten en un flujo ordenado",
                "familias": ["motion-graphics", "mixed-media"],
                "beats": [
                    {"inicio": 0, "fin": 2, "funcion": "hook", "familia": "motion-graphics", "visual": "Titular irrumpe sobre bandeja saturada"},
                    {"inicio": 2, "fin": 4.5, "funcion": "contexto", "familia": "mixed-media", "visual": "Recortes de mensajes caen en capas"},
                    {"inicio": 4.5, "fin": 7, "funcion": "tension", "familia": "motion-graphics", "visual": "Los mensajes se acumulan alrededor del reloj"},
                    {"inicio": 7, "fin": 9.5, "funcion": "demostracion", "familia": "mixed-media", "visual": "Tarjetas se conectan mediante una ruta visual"},
                    {"inicio": 9.5, "fin": 12, "funcion": "giro", "familia": "motion-graphics", "visual": "La ruta reorganiza los mensajes en un flujo"},
                    {"inicio": 12, "fin": 15, "funcion": "recompensa", "familia": "mixed-media", "visual": "El panel ordenado aparece por capas"},
                    {"inicio": 15, "fin": 18, "funcion": "cierre", "familia": "motion-graphics", "visual": "Payoff y llamada a conversar con JDT"},
                ],
            },
        }

    def test_storyboard_valido(self):
        self.assertTrue(validar(self.guion)["ok"])

    def test_hook_no_puede_tener_intro(self):
        self.guion["direccion"]["beats"][0]["inicio"] = 0.5
        self.assertFalse(validar(self.guion)["ok"])

    def test_detecta_plano_demasiado_largo(self):
        self.guion["direccion"]["beats"][1]["fin"] = 5.5
        self.assertFalse(validar(self.guion)["ok"])

    def test_detecta_hueco(self):
        self.guion["direccion"]["beats"][2]["inicio"] = 5.2
        self.assertFalse(validar(self.guion)["ok"])

    def test_exige_payoff_final(self):
        self.guion["direccion"]["beats"][-1]["funcion"] = "contexto"
        self.assertFalse(validar(self.guion)["ok"])


if __name__ == "__main__":
    unittest.main()
