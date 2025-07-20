import math
from math import sqrt

def ContactArcLen(DV, S, Iteration) -> float:
    """Длина дуги контакта"""
    LK = sqrt(DV * S[Iteration] / 2)
    return LK