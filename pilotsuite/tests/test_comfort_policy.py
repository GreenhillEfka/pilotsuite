import unittest
from pilotsuite.core.comfort_policy import media_intent,climate_intent
class ComfortPolicyTests(unittest.TestCase):
    def test_media_preserves_manual_or_existing_use(self):
        self.assertEqual("preserve",media_intent(occupied=True,atmosphere="relax",already_playing=True)["intent"])
        self.assertEqual("none",media_intent(occupied=True,atmosphere="relax",manual_block=True)["intent"])
        self.assertEqual("suggest",media_intent(occupied=True,atmosphere="relax")["intent"])
    def test_climate_keeps_window_and_humidity_semantics_separate(self):
        self.assertEqual("hold",climate_intent(occupied=True,temperature=18,target=21,window_open=True)["intent"])
        r=climate_intent(occupied=True,temperature=18,target=21,humidity=70)
        self.assertEqual("warm",r["intent"]); self.assertIn("not proof",r["note"])
        self.assertFalse(r["execution"]["allowed"])
if __name__=="__main__": unittest.main()
