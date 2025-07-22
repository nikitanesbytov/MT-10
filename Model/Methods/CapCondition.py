import math
from math import tan
from math import acos

def CapCondition(Mu, S, Iteration, DV) -> bool:
    """Условие захвата"""
    alpha = acos(1 - (S[Iteration] / DV))
    
    CapCon = (Mu >= tan(alpha))
    return CapCon

# Mu - коэффициент трения
# S - массив раствора валков для проходов
# Iteration - номер итерации прокатки
# DV - диаметр валков
# alpha - угол захвата
# CapCon - условие захвата сляба валками (True/False)