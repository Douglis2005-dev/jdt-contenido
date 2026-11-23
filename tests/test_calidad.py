"""Regresiones del sistema de calificaciones y cola de mejoras."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import calidad


class CalidadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "videos").mkdir()
        (self.root / "borradores").mkdir()
        (self.root / "banners").mkdir()
        self.calificaciones = self.root / "calificaciones.md"
        self.estado = self.root / "calidad_estado.json"
        self.lecciones = self.root / "lecciones.md"
        self.patches = [
            patch.object(calidad, "CARPETA", self.root),
            patch.object(calidad, "CALIFICACIONES", self.calificaciones),
            patch.object(calidad, "ESTADO", self.estado),
            patch.object(calidad, "LECCIONES", self.lecciones),
        ]
        for p in self.patches:
            p.start()
        self.addCleanup(self._cleanup_patches)

    def _cleanup_patches(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()

    def escribir_nota(self, ident, nota, comentario=""):
        self.calificaciones.write_text(
            "# Calificaciones\n\n| ID | Nota | Comentario |\n|---|---|---|\n"
            f"| {ident} | {nota} | {comentario} |\n",
            encoding="utf-8",
        )

    def test_contenidos_detecta_mp4_aunque_no_haya_borrador(self):
        ident = "2026-11-21-2358-logo-particulas-cian"
        (self.root / "videos" / f"{ident}.mp4").write_bytes(b"mp4")
        self.assertIn(ident, calidad.contenidos())

    def test_nota_baja_de_mp4_sin_guion_entra_a_mejora(self):
        ident = "2026-11-21-2358-logo-particulas-cian"
        (self.root / "videos" / f"{ident}.mp4").write_bytes(b"mp4")
        self.escribir_nota(ident, "3.6", "Falta voz en off y CTA.")
        estado = calidad.estado()
        self.assertEqual(estado["modo"], "mejora")
        self.assertEqual(estado["contenido_a_mejorar"]["id"], ident)
        self.assertTrue(estado["contenido_a_mejorar"]["requiere_reconstruccion"])
        self.assertIn("video", estado["contenido_a_mejorar"]["archivos"])

    def test_id_valido_sin_archivos_no_se_ignora(self):
        ident = "2026-11-21-2358-brazo-robotico-logo"
        self.escribir_nota(ident, "2.7", "No hay locución ni beneficio comercial.")
        estado = calidad.estado()
        self.assertEqual(estado["modo"], "mejora")
        self.assertEqual(estado["contenido_a_mejorar"]["id"], ident)
        self.assertTrue(estado["contenido_a_mejorar"]["requiere_reconstruccion"])
        self.assertEqual(estado["contenido_a_mejorar"]["archivos"], {})
        self.assertIn(ident, estado["mejoras_sin_guion_original"])

    def test_no_cuenta_version_liviana_como_contenido_independiente(self):
        ident = "2026-11-21-2358-logo-particulas-cian"
        (self.root / "videos" / f"{ident}-liviano.mp4").write_bytes(b"mp4")
        self.assertNotIn(f"{ident}-liviano", calidad.contenidos())

    def test_prefijo_ambiguo_no_se_asigna_a_varias_versiones(self):
        base = "2026-11-21-2358-pieza"
        ids = [base, f"{base}-v2"]
        self.escribir_nota("2026-11-21-2358", "4.0", "Bajo.")
        notas, avisos = calidad.leer_calificaciones(ids)
        self.assertEqual(notas, {})
        self.assertTrue(any("coincide con varios" in aviso for aviso in avisos))


if __name__ == "__main__":
    unittest.main()
