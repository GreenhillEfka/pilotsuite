import unittest
from pilotsuite.core.lighting_policy import lighting_target,should_adjust
class LightingPolicyTests(unittest.TestCase):
    def test_daylight_reduces_target_and_mood_only_offsets_bounds(self):
        dark=lighting_target(outdoor_lux=50,occupied=True)
        bright=lighting_target(outdoor_lux=12000,occupied=True)
        self.assertGreater(dark["target"],bright["target"])
        self.assertFalse(dark["execution"]["allowed"])
        self.assertGreater(lighting_target(outdoor_lux=1000,occupied=True,atmosphere="focus")["target"],
                           lighting_target(outdoor_lux=1000,occupied=True,atmosphere="relax")["target"])
    def test_absence_or_bad_daylight_means_no_change(self):
        self.assertIsNone(lighting_target(outdoor_lux=50,occupied=False)["target"])
        self.assertIsNone(lighting_target(outdoor_lux=-1,occupied=True)["target"])
        self.assertFalse(should_adjust(50,None))
        self.assertFalse(should_adjust(50,53))
        self.assertTrue(should_adjust(50,60))
if __name__=="__main__": unittest.main()
