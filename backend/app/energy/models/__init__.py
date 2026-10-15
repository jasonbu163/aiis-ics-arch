"""价格唯一定义；不执行DDL。"""
from .energy_price import EnergyPrice
from .energy_price_hour import EnergyPriceHour
__all__ = ["EnergyPrice", "EnergyPriceHour"]
