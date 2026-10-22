"""Pure counts-only §4.01(a) sampling planning tests."""
import unittest
from fbi_oversight_sampling import estimate, SamplingInputError


def spec(**kwargs):
    return {"channeler_population": 100, "recipient_population": 500,
            "confidence_percent": 95, "margin_percent": 5,
            "method": "simple_random", **kwargs}


class SamplingTests(unittest.TestCase):
    def test_finite_population_estimates_are_independent(self):
        result = estimate(spec())
        self.assertEqual(result["section"], "4.01(a)")
        self.assertGreater(result["recipient_sample_estimate"], result["channeler_sample_estimate"])
        self.assertLessEqual(result["recipient_sample_estimate"], 500)
        self.assertLessEqual(result["channeler_sample_estimate"], 100)

    def test_empty_population_is_not_sampled(self):
        result = estimate(spec(channeler_population=0, recipient_population=0))
        self.assertEqual(result["channeler_sample_estimate"], 0)
        self.assertEqual(result["recipient_sample_estimate"], 0)

    def test_population_one_requires_one_and_not_more(self):
        result = estimate(spec(channeler_population=1, recipient_population=1))
        self.assertEqual(result["channeler_sample_estimate"], 1)

    def test_confidence_and_margin_change_estimate(self):
        small = estimate(spec(confidence_percent=90, margin_percent=10))
        large = estimate(spec(confidence_percent=99, margin_percent=2))
        self.assertLess(small["recipient_sample_estimate"], large["recipient_sample_estimate"])

    def test_no_estimate_is_an_official_approval_or_selection(self):
        result = estimate(spec())
        for flag in ("entities_selected", "representative_sample_verified",
                     "combined_state_federal_audit_program_approved",
                     "sample_audit_conducted", "production_ready"):
            self.assertFalse(result[flag])

    def test_rejects_free_text_identifiers_and_unsupported_method(self):
        for invalid in (
            {"entity_names": "do not collect"},
            {"sampled_ora": "private"},
        ):
            with self.assertRaises(SamplingInputError):
                estimate({**spec(), **invalid})
        for bad in (
            spec(method="purposeful"),
            spec(channeler_population=True),
            spec(recipient_population=-1),
            spec(channeler_population=1000001),
            spec(confidence_percent=96),
            spec(margin_percent=0),
            spec(recipient_population="500"),
        ):
            with self.assertRaises(SamplingInputError):
                estimate(bad)


if __name__ == "__main__":
    unittest.main()
