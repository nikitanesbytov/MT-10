import math
def TempDrPlDeform(self):
    """Падение температуры вследствие пластической дфеормации"""
    TempDrPlDeform = 0,183*RelDef*math.log(h_0/h_1)
    return TempDrPlDeform

