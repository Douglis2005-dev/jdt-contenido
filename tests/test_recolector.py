import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import recolector


class TemasPropiosTest(unittest.TestCase):
    def _con_historial(self, datos):
        tmp = Path(tempfile.mkdtemp()) / "historial.json"
        tmp.write_text(json.dumps(datos), encoding="utf-8")
        return mock.patch.object(recolector, "HISTORIAL", tmp)

    def test_siempre_hay_tema_propio(self):
        with self._con_historial([]):
            temas = recolector.temas_propios()
        self.assertEqual(len(temas), 5)
        for t in temas:
            self.assertTrue(t["url"].startswith("jdt:"))
            self.assertTrue(t["servicio"])
            self.assertFalse(t["requiere_fuente_externa"])

    def test_los_usados_van_al_final(self):
        primero = "jdt:" + recolector.TEMAS_JDT[0][0]
        with self._con_historial([{"url": primero, "titulo": "x", "fecha": "2026-11-22T00:00:00+00:00"}]):
            temas = recolector.temas_propios(limite=len(recolector.TEMAS_JDT))
        self.assertNotEqual(temas[0]["url"], primero)
        self.assertEqual(temas[-1]["url"], primero)

    def test_todos_usados_sigue_entregando(self):
        historial = [
            {"url": f"jdt:{slug}", "titulo": t, "fecha": f"2026-11-{10 + i:02d}T00:00:00+00:00"}
            for i, (slug, t, _) in enumerate(recolector.TEMAS_JDT)
        ]
        with self._con_historial(historial):
            temas = recolector.temas_propios(limite=1)
        self.assertEqual(temas[0]["url"], "jdt:" + recolector.TEMAS_JDT[0][0])

    def test_recolectar_sin_red_trae_plan_b(self):
        def falla(*a, **k):
            raise OSError("bloqueado por el proxy")
        with self._con_historial([]), mock.patch.object(recolector, "_get_json", falla):
            datos = recolector.recolectar(25)
        self.assertEqual(datos["temas"], [])
        self.assertTrue(datos["temas_propios_jdt"])


if __name__ == "__main__":
    unittest.main()
