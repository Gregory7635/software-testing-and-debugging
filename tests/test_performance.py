"""
ЛАБОРАТОРНАЯ РАБОТА 4. НЕФУНКЦИОНАЛЬНОЕ ТЕСТИРОВАНИЕ
Вид: Тестирование производительности (Performance testing)

Принцип тестирования производительности: проверяется не ЧТО делает
программа (это задача функционального тестирования), а КАК БЫСТРО и
СТАБИЛЬНО она это делает. Тестовый случай считается пройденным, если
время выполнения операции укладывается в заранее заданный допустимый
порог (лимит).

В данной работе измеряется:
    1. Время выполнения одной типовой операции расчёта (отклик системы
       на единичный запрос пользователя).
    2. Суммарное время выполнения большого количества однотипных
       операций подряд (поведение при многократном использовании).
    3. Время обработки поездки с аномально большим списком
       дополнительных расходов (устойчивость структуры данных к росту
       объёма входных данных).
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vehicle import Vehicle
from trip import Trip
from calculator import TripCostCalculator


# Допустимые пороги времени выполнения (заданы заведомо с запасом
# относительно измеренных реальных значений, чтобы тест был стабильным
# на разном оборудовании).
MAX_TIME_SINGLE_OPERATION_SEC = 0.05        # 50 мс на одну операцию
MAX_TIME_100K_OPERATIONS_SEC = 2.0          # 2 сек на 100 000 операций
MAX_TIME_1M_EXTRA_COSTS_SEC = 1.0           # 1 сек на сумму 1 000 000 расходов


def test_perf01_single_calculation_response_time():
    """
    Проверка отклика системы на единичный, типовой запрос пользователя.
    Пользователь не должен ждать результата заметное время.
    """
    start = time.perf_counter()

    vehicle = Vehicle(7.5, 55)
    trip = Trip(distance_km=300, passengers=2, extra_costs=[100])
    calc = TripCostCalculator(vehicle, trip)
    result = calc.total_cost()

    elapsed = time.perf_counter() - start

    assert result > 0
    assert elapsed < MAX_TIME_SINGLE_OPERATION_SEC, (
        f"Операция заняла {elapsed:.4f} сек, что превышает допустимый порог "
        f"{MAX_TIME_SINGLE_OPERATION_SEC} сек"
    )


def test_perf02_bulk_operations_throughput():
    """
    Проверка производительности при многократном повторении расчёта
    (например, если бы приложение обрабатывало множество поездок подряд —
    сценарий пакетной обработки).
    """
    iterations = 100_000

    start = time.perf_counter()
    for _ in range(iterations):
        vehicle = Vehicle(7.5, 55)
        trip = Trip(distance_km=300, passengers=2, extra_costs=[100, 50])
        calc = TripCostCalculator(vehicle, trip)
        calc.total_cost()
    elapsed = time.perf_counter() - start

    assert elapsed < MAX_TIME_100K_OPERATIONS_SEC, (
        f"{iterations} операций заняли {elapsed:.4f} сек, что превышает "
        f"допустимый порог {MAX_TIME_100K_OPERATIONS_SEC} сек"
    )


def test_perf03_large_extra_costs_list_performance():
    """
    Проверка устойчивости производительности при аномально большом
    объёме входных данных — список из 1 000 000 дополнительных расходов
    (граничный случай для нефункционального тестирования: не корректность
    результата, а именно скорость его получения).
    """
    huge_extra_costs = [10.0] * 1_000_000

    start = time.perf_counter()
    trip = Trip(distance_km=300, passengers=2, extra_costs=huge_extra_costs)
    total = trip.total_extra_costs()
    elapsed = time.perf_counter() - start

    assert total == 10_000_000.0
    assert elapsed < MAX_TIME_1M_EXTRA_COSTS_SEC, (
        f"Обработка 1 000 000 элементов заняла {elapsed:.4f} сек, что "
        f"превышает допустимый порог {MAX_TIME_1M_EXTRA_COSTS_SEC} сек"
    )
