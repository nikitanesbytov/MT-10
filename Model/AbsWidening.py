import math
from math import log

def AbsWidening(LK, S, Iteration, h_0, h_1) -> float:
    """Абсолютное уширение"""
    delta_b = (LK - S[Iteration] / 2 / h_1) * log(h_0 / h_1) / 2
    return delta_b