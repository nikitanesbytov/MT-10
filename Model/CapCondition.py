import math
from math import tan
from math import acos

def CapCondition(Mu, S, DV, Iteration) -> bool:
    """Условие захвата"""
    alpha = acos(1 - (S[Iteration] / DV))
    
    CapCon = (Mu >= tan(alpha))
    return CapCon