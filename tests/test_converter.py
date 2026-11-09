import unittest
from src.Converter import Converter


class TestConverter(unittest.TestCase):

    # ===== Диапазон x >= 100.7 → 1000 =====
    def test_x_equal_100_7_returns_1000(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_x_greater_than_100_7_returns_1000(self):
        self.assertEqual(Converter.do(999.9), 1000)
        self.assertEqual(Converter.do(1000.0), 1000)

    # ===== Диапазон 0 < x < 100.7 → int(x) =====
    def test_x_between_0_and_100_7(self):
        self.assertEqual(Converter.do(0.1), 0)
        self.assertEqual(Converter.do(1.5), 1)
        self.assertEqual(Converter.do(65.7), 65)
        self.assertEqual(Converter.do(100.6), 100)

    # ===== x == 0.0 → ValueError =====
    def test_x_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    # ===== Диапазон -30.4 <= x < 0 → int(x) - 5 =====
    def test_x_between_minus_30_4_and_0(self):
        self.assertEqual(Converter.do(-0.1), -5)      # int(-0.1) = 0 → 0 - 5
        self.assertEqual(Converter.do(-1.5), -6)      # int(-1.5) = -1 → -1 - 5
        self.assertEqual(Converter.do(-30.4), -35)    # int(-30.4) = -30 → -30 - 5

    # ===== Диапазон x <= -30.5 → -2000 =====
    def test_x_less_or_equal_minus_30_5(self):
        self.assertEqual(Converter.do(-30.5), -2000)
        self.assertEqual(Converter.do(-94.5), -2000)
        self.assertEqual(Converter.do(-1000.0), -2000)


if __name__ == "__main__":
    unittest.main()