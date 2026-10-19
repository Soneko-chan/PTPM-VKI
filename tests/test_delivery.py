import unittest
import sys
import os

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Delivery import calculate_delivery_cost


class TestDeliveryBasicCost(unittest.TestCase):
    """
    Группа 1: Базовые сценарии расчета стоимости.
    Проверяет основную формулу: База + (Расстояние * Тариф) и весовые коэффициенты.
    """

    def test_basic_delivery_standard_package(self):
        """Тест 1: Базовая доставка обычной посылки (легкий вес)"""
        cost, date = calculate_delivery_cost(2.0, 100, "обычный", False)
        self.assertEqual(cost, 700)
        self.assertEqual(date, "2026-09-04")

    def test_delivery_with_medium_weight(self):
        """Тест 2: Доставка посылки среднего веса (коэффициент 1.2)"""
        cost, _ = calculate_delivery_cost(10.0, 100, "обычный", False)
        self.assertEqual(cost, 840)

    def test_delivery_with_heavy_weight(self):
        """Тест 3: Доставка тяжелой посылки (коэффициент 1.5)"""
        cost, _ = calculate_delivery_cost(25.0, 100, "обычный", False)
        self.assertEqual(cost, 1050)

    def test_boundary_weight_5kg(self):
        """Тест 19: Граничное значение веса ровно 5 кг (без коэффициента)"""
        cost, _ = calculate_delivery_cost(5.0, 100, "обычный", False)
        self.assertEqual(cost, 700)


class TestDeliveryPackageTypes(unittest.TestCase):
    """
    Группа 2: Проверка доплат за тип упаковки.
    Проверяет фиксированные надбавки для хрупких и опасных грузов.
    """

    def test_fragile_package_surcharge(self):
        """Тест 4: Доплата за хрупкую посылку (+300 руб.)"""
        cost, _ = calculate_delivery_cost(2.0, 100, "хрупкий", False)
        self.assertEqual(cost, 1000)

    def test_dangerous_package_surcharge(self):
        """Тест 5: Доплата за опасную посылку (+1000 руб.)"""
        cost, _ = calculate_delivery_cost(2.0, 100, "опасный", False)
        self.assertEqual(cost, 1700)


class TestDeliveryExpressLogic(unittest.TestCase):
    """
    Группа 3: Логика экспресс-доставки.
    Выявляет баги в расчете стоимости и времени для экспресс-режима.
    """

    def test_express_delivery_reduces_cost_bug(self):
        """Тест 6: Экспресс НЕДОЛЖНА уменьшать стоимость (БАГ!)"""
        cost_normal, _ = calculate_delivery_cost(2.0, 100, "обычный", False)
        cost_express, _ = calculate_delivery_cost(2.0, 100, "обычный", True)
        self.assertGreater(cost_express, cost_normal,
                          "Экспресс-доставка должна стоить дороже обычной!")

    def test_express_delivery_time_calculation(self):
        """Тест 17: Расчет времени для экспресса на длинной дистанции"""
        _, date = calculate_delivery_cost(2.0, 1000, "обычный", True)
        self.assertEqual(date, "2026-09-04")

    def test_express_delivery_zero_days_bug(self):
        """Тест 18: Экспресс может дать 0 дней доставки (БАГ!)"""
        _, date = calculate_delivery_cost(2.0, 100, "обычный", True)
        self.assertNotEqual(date, "2026-09-03",
                           "Дата доставки не может быть равна дате отправки!")

    def test_combined_heavy_fragile_express(self):
        """Тест 20: Комбинированный тест (тяжелый + хрупкий + экспресс)"""
        cost, date = calculate_delivery_cost(30.0, 1000, "хрупкий", True)
        self.assertEqual(cost, 4050) # Ожидаем баг в стоимости
        self.assertEqual(date, "2026-09-04")


class TestDeliveryValidation(unittest.TestCase):
    """
    Группа 4: Валидация входных данных.
    Проверяет возврат ошибки (-1, "0000-00-00") при некорректных параметрах.
    """

    def test_invalid_weight_too_light(self):
        """Тест 7: Вес меньше минимального (0.1 кг)"""
        cost, date = calculate_delivery_cost(0.05, 100, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_weight_too_heavy(self):
        """Тест 8: Вес больше максимального (50 кг)"""
        cost, date = calculate_delivery_cost(55.0, 100, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_negative_weight(self):
        """Тест 12: Отрицательный вес"""
        cost, date = calculate_delivery_cost(-5.0, 100, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_distance_too_short(self):
        """Тест 9: Расстояние меньше минимального (1 км)"""
        cost, date = calculate_delivery_cost(2.0, 0, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_distance_too_long(self):
        """Тест 10: Расстояние больше максимального (5000 км)"""
        cost, date = calculate_delivery_cost(2.0, 5001, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_package_type(self):
        """Тест 11: Неверный тип посылки"""
        cost, date = calculate_delivery_cost(2.0, 100, "электроника", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")


class TestDeliveryBoundaryValues(unittest.TestCase):
    """
    Группа 5: Граничные значения (Boundary Values).
    Проверяет работу системы на краях допустимых диапазонов.
    """

    def test_minimum_valid_weight(self):
        """Тест 13: Минимально допустимый вес (0.1 кг)"""
        cost, date = calculate_delivery_cost(0.1, 100, "обычный", False)
        self.assertNotEqual(cost, -1)
        self.assertNotEqual(date, "0000-00-00")

    def test_maximum_valid_weight(self):
        """Тест 14: Максимально допустимый вес (50 кг)"""
        cost, _ = calculate_delivery_cost(50.0, 100, "обычный", False)
        self.assertEqual(cost, 1050)

    def test_minimum_valid_distance(self):
        """Тест 15: Минимально допустимое расстояние (1 км)"""
        cost, date = calculate_delivery_cost(2.0, 1, "обычный", False)
        self.assertEqual(cost, 205)
        self.assertEqual(date, "2026-09-04")

    def test_maximum_valid_distance(self):
        """Тест 16: Максимально допустимое расстояние (5000 км)"""
        cost, date = calculate_delivery_cost(2.0, 5000, "обычный", False)
        self.assertEqual(cost, 25200)
        self.assertEqual(date, "2026-09-13")


if __name__ == '__main__':
    unittest.main()