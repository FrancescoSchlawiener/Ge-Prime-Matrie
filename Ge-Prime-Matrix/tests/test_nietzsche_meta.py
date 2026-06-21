import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.i_curve import analyze_pair

TANZLIED = """Das Tanzlied
Eines Abends ging Zarathustra mit seinen Jüngern durch den Wald; und als er nach einem Brunnen suchte, siehe, da kam er auf eine grüne Wiese, die von Bäumen und Gebüsch still umstanden war: auf der tanzten Mädchen miteinander. Sobald die Mädchen Zarathustra erkannten, ließen sie vom Tanze ab; Zarathustra aber trat mit freundlicher Gebärde zu ihnen und sprach diese Worte:
»Laßt vom Tanze nicht ab, ihr lieblichen Mädchen! Kein Spielverderber kam zu euch mit bösem Blick, kein Mädchen-Feind.
Gottes Fürsprecher bin ich vor dem Teufel: der aber ist der Geist der Schwere. Wie sollte ich, ihr Leichten, göttlichen Tänzen feind sein? Oder Mädchen-Füßen mit schönen Knöcheln?
Wohl bin ich ein Wald und eine Nacht dunkler Bäume: doch wer sich vor meinem Dunkel nicht scheut, der findet auch Rosenhänge unter meinen Zypressen.
Und auch den kleinen Gott findet er wohl, der den Mädchen der liebste ist: neben dem Brunnen liegt er, still, mit geschlossenen Augen.
Wahrlich, am hellen Tage schlief er mir ein, der Tagedieb! Haschte er wohl zuviel nach Schmetterlingen?
Zürnt mir nicht, ihr schönen Tanzenden, wenn ich den kleinen Gott ein wenig züchtige! Schreien wird er wohl und weinen – aber zum Lachen ist er noch im Weinen!
Und mit Tränen im Auge soll er euch um einen Tanz bitten; und ich selber will ein Lied zu seinem Tanze singen:
Ein Tanz- und Spottlied auf den Geist der Schwere, meinen allerhöchsten großmächtigsten Teufel, von dem sie sagen, daß er ›der Herr der Welt‹ sei.« –
Und dies ist das Lied, welches Zarathustra sang, als Kupido und die Mädchen zusammen tanzten."""

SCHLAFLIED = """Das Schlaflied
Eines Abends ging Zarathustra mit seinen Jüngern durch den Wald; und als er nach einem Brunnen suchte, siehe, da kam er auf eine grüne Wiese, die von Bäumen und Gebüsch still umstanden war: auf der schlaften Mädchen miteinander. Sobald die Mädchen Zarathustra erkannten, ließen sie vom Schlafe ab; Zarathustra aber trat mit freundlicher Gebärde zu ihnen und sprach diese Worte:
»Laßt vom Schlafe nicht ab, ihr lieblichen Mädchen! Kein Spielverderber kam zu euch mit bösem Blick, kein Mädchen-Feind.
Gottes Fürsprecher bin ich vor dem Teufel: der aber ist der Geist der Schwere. Wie sollte ich, ihr Leichten, göttlichen schläfen feind sein? Oder Mädchen-Füßen mit schönen Knöcheln?
Wohl bin ich ein Wald und eine Nacht dunkler Bäume: doch wer sich vor meinem Dunkel nicht scheut, der findet auch Rosenhänge unter meinen Zypressen.
Und auch den kleinen Gott findet er wohl, der den Mädchen der liebste ist: neben dem Brunnen liegt er, still, mit geschlossenen Augen.
Wahrlich, am hellen Tage schlief er mir ein, der Tagedieb! Haschte er wohl zuviel nach Schmetterlingen?
Zürnt mir nicht, ihr schönen Schlafenden, wenn ich den kleinen Gott ein wenig züchtige! Schreien wird er wohl und weinen – aber zum Lachen ist er noch im Weinen!
Und mit Tränen im Auge soll er euch um einen Schlaf bitten; und ich selber will ein Lied zu seinem Schlafe singen:
Ein Schlaf- und Spottlied auf den Geist der Schwere, meinen allerhöchsten großmächtigsten Teufel, von dem sie sagen, daß er ›der Herr der Welt‹ sei.« –
Und dies ist das Lied, welches Zarathustra sang, als Kupido und die Mädchen zusammen schlaften."""


class TestNietzscheMeta(unittest.TestCase):
    def test_tanzlied_vs_schlaflied_meta_ggt_high(self):
        result = analyze_pair(text_a=TANZLIED, text_b=SCHLAFLIED, db_audit_mode="off")
        meta_sim = result["meta_comparison"]["similarity_ratio"]
        self.assertGreater(meta_sim, 0.85, msg=f"expected high Meta-ggT, got {meta_sim}")

    def test_tanzlied_vs_schlaflied_sentence_sparklines(self):
        result = analyze_pair(text_a=TANZLIED, text_b=SCHLAFLIED, db_audit_mode="off")
        for side in ("semantic_a", "semantic_b"):
            sent = result[side]["sentences"]
            self.assertIsInstance(sent, list)
            self.assertGreater(len(sent), 0, msg=side)
        hc = result["hierarchy_comparison"]["semantic"]["sentence"]
        self.assertFalse(hc.get("dtw_failed", True))
        self.assertIn("geometry_score", hc)


if __name__ == "__main__":
    unittest.main()
