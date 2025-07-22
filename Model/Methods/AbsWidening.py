import math
from math import log

def AbsWidening(LK, S, Iteration, h_0, h_1) -> float:
    """Абсолютное уширение"""
    delta_b = (LK - S[Iteration] / 2 / h_1) * log(h_0 / h_1) / 2
    return delta_b

# LK - длина дуги контакта
# S - массив раствора валков для проходов
# Iteration - номер итерации прокатки
# h_0 - толщина в начале итерации (начальная толщина)
# h_1 - толщина в конце итерации (конечная толщина)
# delta_b - абсолютное уширение