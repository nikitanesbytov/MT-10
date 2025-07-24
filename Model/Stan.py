from math import *

class RollingMill:
    def __init__(self, L,b,h_0,StartTemp,OutTemp,PauseBIter,S,DV):
        #Параметры сляба(Задает оператор)
        self.L = L #Длина сляба
        self.b = b #Ширина сляба
        self.h_0 = h_0 #Начальная ширина сляба
        self.StartTemp = StartTemp #Начальная температура сляба(Температура выдачи из печи)
       
        #Параметры по умолчанию
        self.ZK = 0 #Жесткость клети
        self.DV = DV #Диаметр валков
        self.MV = 0 #Материал валков
        self.MaxEffort = 0 #Максимально усилие 
        self.MaxMoment = 0 #Максимельный момент
        self.TempV = OutTemp #Задаваемая температура в цехе приравнивается к температуре валков
        #Констатны?

        #Настройка ТП
        self.S = S #Раствор валков(Массив)(Задает оператор)
        self.V0 = V0 #Скорость рольгангов до валков
        self.V1 = V1 #Скорость рольгангов после валков
        self.PauseBIter = PauseBIter #Пауза между итерациями 

    def RelDef(self, h_0, h_1) -> float:
        "Относительная деформация"
        RelDef = (h_0 - h_1) / h_0
        return RelDef
    
    def TempDrBPass(self,h_0,h_1,Kst,Tvx,P,Cn,Pn,Nv,TempDrDConRoll,LB,Avg_V) -> float:
        "Падение температуры между пропусками"
        Numerator = Kst * (Tvx + 2300 * P * (log(1/(1-(h_0-h_1)/h_1))/(Cn*Pn)) * Nv - TempDrDConRoll + 273)**4 * LB * 10**-12
        Denominator = h_1 * Avg_V
        TempDrBPass = Numerator / Denominator
        return TempDrBPass
    
    def TempDrDConRoll(self,TempV0,TempV1,h_0,h_1,LK,Avg_V) -> float:
        "Падение температуры вследствие контакта с валками"
        TempDrDConRoll = (4,87*(TempV0-TempV1))/(h_0 + h_1)*sqrt((2*LK*h_0-1)/(10**3(h_0 + h_1)*Avg_V))
        return TempDrDConRoll
   
    def TempDrPlDeform(self,RelDef,h_0,h_1) -> float:
        "Падение температуры вследствие пластической дфеормации"
        TempDrPlDeform = 0,183*RelDef*log(h_0/h_1)
        return TempDrPlDeform
    
    def GenTemp(self,Tvx,TempDrPlDeform,TempDrDConRoll,TempDrBPass) -> float:
        "Общая температура"
        GenTemp = Tvx - TempDrDConRoll + TempDrPlDeform - TempDrBPass
        pass

    def DefResistance(self,sigmaOD,u,a,RelDef,b,t,c) -> float:
        "Сопротивление деформации"
        Sigmaf = sigmaOD*u**a(10*RelDef)**b(t/1000)**-c
        return Sigmaf
    
    def Moment(self,LK,Hcp,P):
        "Расчет момента прокатки, кНм"
        psi = 0,498 - 0,283 * LK / Hcp
        Moment = 2 * P * psi * LK
        return Moment
    
    def Effort(self,LK,b):
        "Расчет усилия прокатки"
        F = LK * b
        P = Pcp * F
        return P
    
    def Power(self,M,omega) -> float:
        """Рассчет мощности прокатки
        М - Крутящий момент на валках(Н*м)
        omega - угловая скорость вращения валков(рад/c)
        N - Мощность прокатки(Вт)
        """
        N = M * omega 
        return N

    def CapCondition(self, Mu, S, Iteration, DV) -> bool:
        "Условие захвата"
        alpha = acos(1 - (S[Iteration] / DV))
        CapCon = (Mu >= tan(alpha))
        return CapCon
    
    def FricCoef(self,MV, MS, V0, TempS) -> float:
        "Коэффициент трения"
        if (MV == 'Steel'): 
            k1 = 1
        elif(MV == 'Cast Iron'):
            k1 = 0.8

        if (V0 <= 3):
            k2 = 0.8
        elif (V0 > 3):
            k2 = 1.53 * V0 ** (-0.47)

        if (MS == 'Carbon Steel'): 
            k3 = 1
        elif (MS == 'Austenitic steel'):
            k3 = 1.47

        Mu = k1 * k2 * k3 * (1.05 - 0.0005 * TempS) 
        return Mu
    
    def AvrgPressure(self,LK, h_average, sigma) -> float:
        """Среднее давление на валки"""
        if ((LK/h_average) <= 2):
            n_frict = 1 + (LK/h_average)/6
        elif (((LK/h_average) > 2) and ((LK/h_average) <= 4)):
            n_frict = 1 + (LK/h_average)/5
        elif ((LK/h_average) > 4):
            n_frict = 1 + (LK/h_average)/4

        n_zone = (LK / h_average) ** -0.4
       
        P = 1.15 * n_frict * n_zone * sigma 
        return P
    
    def ContactArcLen(self,DV, S, Iteration) -> float:
        "Длина дуги контакта"
        LK = sqrt(DV * S[Iteration] / 2)
        return LK
    
    def ContactArea(self,b_0, b_1, LK) -> float:
        "Площадь контакта"
        b_average = (b_0 + b_1) / 2
        F = b_average * LK
        return F
    
    def AbsWidening(self,LK, S, Iteration, h_0, h_1) -> float:
        "Абсолютное уширение"
        delta_b = (LK - S[Iteration] / 2 / h_1) * log(h_0 / h_1) / 2
        return delta_b
            


    

