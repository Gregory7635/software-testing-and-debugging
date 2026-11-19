from vehicle import Vehicle
from trip import Trip


class TripCostCalculator:
    """
    Вычисляет стоимость поездки на основе параметров автомобиля и поездки.
    """

    def __init__(self, vehicle: Vehicle, trip: Trip):
        self.vehicle = vehicle
        self.trip = trip

    def fuel_liters_used(self) -> float:
        return (self.trip.distance_km / 100) * self.vehicle.fuel_consumption

    def fuel_cost(self) -> float:
        return round(self.fuel_liters_used() * self.vehicle.fuel_price, 2)

    def total_cost(self) -> float:
        return round(self.fuel_cost() + self.trip.total_extra_costs(), 2)

    def cost_per_passenger(self) -> float:
        return round(self.total_cost() / self.trip.passengers, 2)
