"""
ЛАБОРАТОРНАЯ РАБОТА 5. UNIT-ТЕСТИРОВАНИЕ

Принцип unit-тестирования: проверяется каждая отдельная единица кода
(unit) — как правило, один метод одного класса — в ИЗОЛЯЦИИ от остальной
системы. В отличие от чёрного ящика (ЛР1), где мы проверяли поведение
приложения только по входу/выходу согласно требованиям, здесь мы прицельно
тестируем КАЖДЫЙ метод каждого класса, включая внутренние детали его
реализации (например, где именно происходит округление результата).

Тесты сгруппированы по классам (Vehicle, Trip, TripCostCalculator) —
для каждого класса своя группа тестов, что отражает модульную структуру
самого приложения.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vehicle import Vehicle
from trip import Trip
from calculator import TripCostCalculator


# ===========================================================================
# UNIT-ТЕСТЫ КЛАССА Vehicle
# ===========================================================================

class TestVehicle:
    """Юнит-тесты для класса Vehicle — тестируем его изолированно от
    остальных классов приложения."""

    def test_create_valid_vehicle(self):
        """Конструктор корректно сохраняет переданные значения."""
        v = Vehicle(fuel_consumption_l_per_100km=7.5, fuel_price_per_liter=55)
        assert v.fuel_consumption == 7.5
        assert v.fuel_price == 55

    def test_invalid_fuel_consumption_negative_raises_error(self):
        """Метод __init__ бросает ValueError на отрицательный расход."""
        with pytest.raises(ValueError, match="Расход топлива"):
            Vehicle(fuel_consumption_l_per_100km=-1, fuel_price_per_liter=55)

    def test_invalid_fuel_consumption_zero_raises_error(self):
        """Метод __init__ бросает ValueError на нулевой расход."""
        with pytest.raises(ValueError):
            Vehicle(fuel_consumption_l_per_100km=0, fuel_price_per_liter=55)

    def test_invalid_fuel_price_negative_raises_error(self):
        """Метод __init__ бросает ValueError на отрицательную цену."""
        with pytest.raises(ValueError, match="Цена топлива"):
            Vehicle(fuel_consumption_l_per_100km=7.5, fuel_price_per_liter=-10)

    def test_invalid_fuel_price_zero_raises_error(self):
        """Метод __init__ бросает ValueError на нулевую цену."""
        with pytest.raises(ValueError):
            Vehicle(fuel_consumption_l_per_100km=7.5, fuel_price_per_liter=0)

    def test_repr_returns_readable_string(self):
        """Метод __repr__ возвращает строку, содержащую оба параметра."""
        v = Vehicle(fuel_consumption_l_per_100km=7.5, fuel_price_per_liter=55)
        representation = repr(v)
        assert "7.5" in representation
        assert "55" in representation
        assert "Vehicle" in representation


# ===========================================================================
# UNIT-ТЕСТЫ КЛАССА Trip
# ===========================================================================

class TestTrip:
    """Юнит-тесты для класса Trip — тестируем его изолированно, без
    привязки к Vehicle или TripCostCalculator."""

    def test_create_valid_trip_with_default_passengers(self):
        """Параметр passengers по умолчанию равен 1."""
        t = Trip(distance_km=100)
        assert t.distance_km == 100
        assert t.passengers == 1

    def test_create_valid_trip_with_default_extra_costs(self):
        """Параметр extra_costs по умолчанию — пустой список, а не None."""
        t = Trip(distance_km=100)
        assert t.extra_costs == []
        assert isinstance(t.extra_costs, list)

    def test_two_trips_have_independent_extra_costs_lists(self):
        """
        Важная проверка на уровне unit-теста: у двух РАЗНЫХ объектов Trip,
        созданных без явного extra_costs, списки должны быть независимыми
        (это же проверяет отсутствие классической ошибки Python с
        изменяемым значением по умолчанию в аргументах функции).
        """
        trip1 = Trip(distance_km=100)
        trip2 = Trip(distance_km=200)

        trip1.extra_costs.append(500)

        assert trip1.extra_costs == [500]
        assert trip2.extra_costs == []  # у trip2 список должен остаться пустым

    def test_invalid_distance_zero_raises_error(self):
        with pytest.raises(ValueError, match="Расстояние"):
            Trip(distance_km=0)

    def test_invalid_distance_negative_raises_error(self):
        with pytest.raises(ValueError):
            Trip(distance_km=-50)

    def test_invalid_passengers_zero_raises_error(self):
        with pytest.raises(ValueError, match="пассажиров"):
            Trip(distance_km=100, passengers=0)

    def test_total_extra_costs_with_empty_list(self):
        """Метод total_extra_costs на пустом списке возвращает 0."""
        t = Trip(distance_km=100, extra_costs=[])
        assert t.total_extra_costs() == 0

    def test_total_extra_costs_with_single_value(self):
        t = Trip(distance_km=100, extra_costs=[250])
        assert t.total_extra_costs() == 250

    def test_total_extra_costs_with_multiple_values(self):
        """Метод total_extra_costs корректно суммирует несколько значений."""
        t = Trip(distance_km=100, extra_costs=[100, 50.5, 25])
        assert t.total_extra_costs() == 175.5

    def test_repr_returns_readable_string(self):
        t = Trip(distance_km=100, passengers=2, extra_costs=[50])
        representation = repr(t)
        assert "100" in representation
        assert "2" in representation


# ===========================================================================
# UNIT-ТЕСТЫ КЛАССА TripCostCalculator
# ===========================================================================

class TestTripCostCalculator:
    """
    Юнит-тесты для класса TripCostCalculator. Каждый метод
    (fuel_liters_used, fuel_cost, total_cost, cost_per_passenger)
    тестируется отдельно, чтобы точно локализовать ошибку, если
    она возникнет именно в одном конкретном методе.
    """

    def test_fuel_liters_used_typical_values(self):
        """
        Метод fuel_liters_used: 300 км при расходе 7.5 л/100км.
        300 / 100 * 7.5 = 22.5
        """
        calc = TripCostCalculator(Vehicle(7.5, 55), Trip(300))
        assert calc.fuel_liters_used() == 22.5

    def test_fuel_liters_used_is_not_rounded(self):
        """
        Важная деталь реализации: метод fuel_liters_used НЕ округляет
        результат (в отличие от fuel_cost). Проверяем это явно, так как
        это может повлиять на точность дальнейших вычислений.
        """
        calc = TripCostCalculator(Vehicle(6.7, 47.3), Trip(133))
        liters = calc.fuel_liters_used()
        assert liters == 133 / 100 * 6.7  # длинная, неокруглённая дробь
        assert liters != round(liters, 2)  # подтверждаем, что округления не было

    def test_fuel_cost_rounds_to_two_decimals(self):
        """
        Метод fuel_cost ДОЛЖЕН округлять результат до 2 знаков после
        запятой (в отличие от fuel_liters_used).
        """
        calc = TripCostCalculator(Vehicle(6.7, 47.3), Trip(133))
        cost = calc.fuel_cost()
        assert cost == round(cost, 2)
        assert cost == 421.49

    def test_total_cost_without_extra_costs_equals_fuel_cost(self):
        """Если доп. расходов нет, общая стоимость должна совпадать
        со стоимостью топлива."""
        calc = TripCostCalculator(Vehicle(7.5, 55), Trip(300))
        assert calc.total_cost() == calc.fuel_cost()

    def test_total_cost_adds_extra_costs_to_fuel_cost(self):
        calc = TripCostCalculator(Vehicle(7.5, 55), Trip(300, extra_costs=[500]))
        assert calc.total_cost() == calc.fuel_cost() + 500

    def test_cost_per_passenger_divides_total_cost_correctly(self):
        """
        Метод cost_per_passenger: 350.0 руб на 3 пассажиров.
        350 / 3 = 116.666... -> округление до 116.67
        """
        calc = TripCostCalculator(Vehicle(7, 50), Trip(100, passengers=3))
        assert calc.cost_per_passenger() == 116.67

    def test_cost_per_passenger_with_single_passenger_equals_total_cost(self):
        """При одном пассажире стоимость на пассажира равна общей стоимости."""
        calc = TripCostCalculator(Vehicle(7.5, 55), Trip(300, passengers=1))
        assert calc.cost_per_passenger() == calc.total_cost()
