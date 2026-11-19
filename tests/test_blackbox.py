"""
ЛАБОРАТОРНАЯ РАБОТА 1. ТЕСТИРОВАНИЕ ЧЁРНОГО ЯЩИКА

Принцип чёрного ящика: тестировщик НЕ смотрит на исходный код и НЕ знает,
как именно реализована логика внутри. Тестовые случаи строятся только на
основе требований (спецификации) к приложению: что должно происходить на
определённых входных данных.

Используемые техники чёрного ящика:
1. Разбиение на классы эквивалентности (Equivalence Partitioning) —
   входные данные делятся на группы, где поведение программы одинаково.
2. Анализ граничных значений (Boundary Value Analysis) —
   отдельно проверяются значения на границе допустимого диапазона.

Требования (спецификация) к приложению "Расчёт стоимости поездки":
    - расход топлива (л/100км) должен быть положительным числом;
    - цена топлива (руб/л) должна быть положительным числом;
    - расстояние поездки (км) должно быть положительным числом;
    - количество пассажиров должно быть положительным целым числом;
    - если какое-либо значение <= 0, приложение должно вернуть ошибку.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vehicle import Vehicle
from trip import Trip
from calculator import TripCostCalculator


# ---------------------------------------------------------------------------
# КЛАСС ЭКВИВАЛЕНТНОСТИ 1: расход топлива (fuel_consumption)
# ---------------------------------------------------------------------------

def test_ec01_valid_fuel_consumption():
    """Допустимый класс: положительное число -> объект создаётся успешно."""
    v = Vehicle(fuel_consumption_l_per_100km=7.5, fuel_price_per_liter=55)
    assert v.fuel_consumption == 7.5


def test_ec02_invalid_fuel_consumption_negative():
    """Недопустимый класс: отрицательное число -> ошибка."""
    with pytest.raises(ValueError):
        Vehicle(fuel_consumption_l_per_100km=-5, fuel_price_per_liter=55)


def test_bv01_fuel_consumption_boundary_zero():
    """Граничное значение: 0 (нижняя граница, невалидна) -> ошибка."""
    with pytest.raises(ValueError):
        Vehicle(fuel_consumption_l_per_100km=0, fuel_price_per_liter=55)


def test_bv02_fuel_consumption_boundary_minimal_valid():
    """Граничное значение: чуть больше нуля (0.01) -> валидно."""
    v = Vehicle(fuel_consumption_l_per_100km=0.01, fuel_price_per_liter=55)
    assert v.fuel_consumption == 0.01


# ---------------------------------------------------------------------------
# КЛАСС ЭКВИВАЛЕНТНОСТИ 2: цена топлива (fuel_price)
# ---------------------------------------------------------------------------

def test_ec03_valid_fuel_price():
    """Допустимый класс: положительное число -> объект создаётся успешно."""
    v = Vehicle(fuel_consumption_l_per_100km=7.5, fuel_price_per_liter=55)
    assert v.fuel_price == 55


def test_ec04_invalid_fuel_price_zero():
    """Недопустимый класс: цена = 0 -> ошибка."""
    with pytest.raises(ValueError):
        Vehicle(fuel_consumption_l_per_100km=7.5, fuel_price_per_liter=0)


# ---------------------------------------------------------------------------
# КЛАСС ЭКВИВАЛЕНТНОСТИ 3: расстояние поездки (distance_km)
# ---------------------------------------------------------------------------

def test_ec05_valid_distance():
    """Допустимый класс: положительное число -> объект создаётся успешно."""
    t = Trip(distance_km=300, passengers=1)
    assert t.distance_km == 300


def test_ec06_invalid_distance_negative():
    """Недопустимый класс: отрицательное расстояние -> ошибка."""
    with pytest.raises(ValueError):
        Trip(distance_km=-100, passengers=1)


def test_bv03_distance_boundary_zero():
    """Граничное значение: 0 км (невалидно) -> ошибка."""
    with pytest.raises(ValueError):
        Trip(distance_km=0, passengers=1)


# ---------------------------------------------------------------------------
# КЛАСС ЭКВИВАЛЕНТНОСТИ 4: количество пассажиров (passengers)
# ---------------------------------------------------------------------------

def test_ec07_valid_passengers():
    """Допустимый класс: положительное целое -> объект создаётся успешно."""
    t = Trip(distance_km=100, passengers=4)
    assert t.passengers == 4


def test_ec08_invalid_passengers_zero():
    """Недопустимый класс: 0 пассажиров -> ошибка (нельзя делить на 0)."""
    with pytest.raises(ValueError):
        Trip(distance_km=100, passengers=0)


def test_bv04_passengers_boundary_one():
    """Граничное значение: 1 пассажир (нижняя валидная граница) -> ОК."""
    t = Trip(distance_km=100, passengers=1)
    assert t.passengers == 1


# ---------------------------------------------------------------------------
# ФУНКЦИОНАЛЬНЫЕ ПРОВЕРКИ: корректность расчёта на "нормальных" входных данных
# (проверяем результат ТОЛЬКО по входу/выходу, не заглядывая в реализацию)
# ---------------------------------------------------------------------------

def test_calc01_fuel_cost_typical_values():
    """
    Вход: расход 7.5 л/100км, цена 55 руб/л, расстояние 300 км.
    Ожидаемый результат по спецификации:
        литров = 300 / 100 * 7.5 = 22.5
        стоимость топлива = 22.5 * 55 = 1237.5
    """
    vehicle = Vehicle(7.5, 55)
    trip = Trip(distance_km=300, passengers=1)
    calc = TripCostCalculator(vehicle, trip)

    assert calc.fuel_liters_used() == 22.5
    assert calc.fuel_cost() == 1237.5


def test_calc02_total_cost_with_extra_costs():
    """
    Вход: та же поездка + доп. расходы 500 руб.
    Ожидаемый результат: общая стоимость = 1237.5 + 500 = 1737.5
    """
    vehicle = Vehicle(7.5, 55)
    trip = Trip(distance_km=300, passengers=1, extra_costs=[500])
    calc = TripCostCalculator(vehicle, trip)

    assert calc.total_cost() == 1737.5


def test_calc03_cost_per_passenger_split_correctly():
    """
    Вход: общая стоимость 1737.5 руб, 3 пассажира.
    Ожидаемый результат: 1737.5 / 3 = 579.17 (округление до 2 знаков)
    """
    vehicle = Vehicle(7.5, 55)
    trip = Trip(distance_km=300, passengers=3, extra_costs=[500])
    calc = TripCostCalculator(vehicle, trip)

    assert calc.cost_per_passenger() == 579.17


def test_calc04_no_extra_costs_defaults_to_zero():
    """
    Вход: поездка без указания доп. расходов.
    Ожидаемый результат: доп. расходы = 0, не ошибка.
    """
    vehicle = Vehicle(7.5, 55)
    trip = Trip(distance_km=100, passengers=1)
    calc = TripCostCalculator(vehicle, trip)

    assert trip.total_extra_costs() == 0
    assert calc.total_cost() == calc.fuel_cost()
