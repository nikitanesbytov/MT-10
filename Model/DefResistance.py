def DefResistance(self,sigmaOD,u,a,eps,b,t,c):
    """Сопротивление деформации"""
    Sigmaf = sigmaOD*u**a(10*eps)**b(t/1000)**-c
    return Sigmaf
#a,b,c - Коэффициенты зависящие от марки стали
#u - 
#sigmaOD - Базисное значение сопротивления деформации
#eps - Степень деформации