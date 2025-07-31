from math import *

class RollingMill:
    def __init__(self,DR,L,b,h_0,StartTemp,DV,MV,MS,OutTemp,n,V0,V1,S,PauseBIter,V_Valk_Per,StartS,MaxEffort,MaxMoment,MaxPower,d1,d2):
        #Параметры сляба(Задает оператор)
        self.L = L #Начальная длина сляба(мм)
        self.b = b #Ширина сляба(мм)
        self.h_0 = h_0 #Начальная толщина сляба(мм)
        self.h_1 = 0 #Конечная толщина сляба(мм)
        self.StartTemp = StartTemp #Начальная температура сляба(Температура выдачи из печи)(°C)
       
        #Параметры по умолчанию
        self.ZK = 0 #Жесткость клети
        self.DV = DV #Диаметр валков(мм)
        self.DR = DR #Диаметр рольгангов(мм)
        self.R = DV/2 #Радиус валков(мм)
        self.MV = MV #Материал валков
        self.MS = MS  #Материал сляба
        self.MaxEffort = MaxEffort #Максимально усилие(кН)
        self.MaxMoment = MaxMoment #Максимельный момент(кНм)
        self.MaxPower = MaxPower #Максимальная мощность(Вт)
        self.TempV = OutTemp #Температура валков(°C)
        self.d1 = d1 #Расстояние пути до валков(мм)
        self.d2 = d2 #Расстояние пути после валков(мм)

        #Настройка ТП
        self.CurrentS = [StartS] #Нынешнее положение раствора валков
        self.n = n #Количество итераций прокатки
        self.V1 = V1 #Скорость рольгангов после валков(об/c)
        self.V0 = V0 #Скорость рольгангов до валков(об/c)
        self.VS = 10 #Скорость выставления валков(мм/c)
        self.accel = 0.67 #Рагон валков и рольгангов(об/c)
        self.S = S #Раствор валков(Массив)(Задает оператор)(мм)
        self.V_Valk_Per = V_Valk_Per #Заданная скорость валков оператором в об/мин
        self.V_Valk = [] #Заданная скорость валков(Массив)(об/c)
        self.PauseBIter = PauseBIter #Пауза между итерациями(с)

    def RelDef(self, h_0, h_1) -> float:
        "Относительная деформация"
        RelDef = (h_0 - h_1) / h_0
        return RelDef
    
    def TempDrBPass(self,FinalLength,DV,w,Temp,h_1) -> float:
        "Падение температуры между пропусками"
        V = pi * DV * w * (1 + 0.05)
        TempDrBPass = (17.5 * 10**-12) * ((FinalLength/V) + 3*100)/(h_1/1000) * (Temp+273)**4
        #V - скорость прокатки(м/c)
        #Temp - температура в проходе(°C)
        #w - частота вращения валков(об/c)
        return TempDrBPass
    
    def TempDrDConRoll(self,DV,h_0,h_1) -> float:
        "Падение температуры вследствие контакта с валками"
        TempDrDConRoll = 0.216 * sqrt(DV/2 * acos(1-((h_0-h_1)/DV)))/(h_0 + h_1)
        #DV - диаметр валков(мм)
        return TempDrDConRoll
   
    def TempDrPlDeform(self,RelDef,h_0,h_1) -> float:
        "Падение температуры вследствие пластической деформации"
        TempDrPlDeform = 0,183*RelDef*log(h_0/h_1)
        #RelDef - Степень деформации
        return TempDrPlDeform
    
    def GenTemp(self,Temp,TempDrBPass,TempDrDConRoll,TempDrPlDeform) -> float:
        "Общая температура после итерации прокатки"
        GenTemp = Temp + TempDrPlDeform - TempDrDConRoll - TempDrBPass
        #Temp - температура в проходе(°C)
        return GenTemp

    def DefResistance(self,RelDef,LK,V) -> float:
        "Сопротивление деформации"
        a = 0.124
        b = 0.167
        c = -2.8
        t = 1000
        sigmaOD = 0.87
        u = (V/LK * RelDef)
        Sigmaf = sigmaOD * (u**a) * ((10*RelDef)**b) * ((t/1000)**-c)
        #a,b,c - Коэффициенты зависящие от марки стали
        #u - Средняя скорость деформации(1/c)
        #V - Скорость валков(м/c)
        #sigmaOD - Базисное значение сопротивления деформации
        #RelDef - Степень деформации
        #t - базовая температура при которой определяются коэффициенты(1000°C)
        return Sigmaf
    
    def Moment(self,LK,h_0,h_1,P):
        "Расчет момента прокатки(кНм)"
        h_average = (h_1 + h_0)/2
        psi = 0.498 - 0.283 * LK / h_average
        Moment = 2 * P * psi * LK
        return Moment
    
    def Effort(self,LK,b,AvrgPressure):
        "Расчет усилия прокатки"
        F = LK * b
        P = AvrgPressure * F
        return P
    
    def Power(self,M,omega) -> float:
        "Рассчет мощности прокатки(Вт)"
        N = M * omega 
        # М - Крутящий момент на валках(Н*м)
        # omega - угловая скорость вращения валков(рад/c)
        # N - Мощность прокатки(Вт)
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
    
    def AvrgPressure(self,LK,h_1,h_0, DefResistance) -> float:
        "Среднее давление на валки"
        h_average = (h_1 + h_0)/2
        if ((LK/h_average) <= 2):
            n_frict = 1 + (LK/h_average)/6
        elif (((LK/h_average) > 2) and ((LK/h_average) <= 4)):
            n_frict = 1 + (LK/h_average)/5
        elif ((LK/h_average) > 4):
            n_frict = 1 + (LK/h_average)/4

        n_zone = (LK / h_average) ** -0.4
       
        P = 1.15 * n_frict * n_zone * DefResistance 
        return P
    
    def ContactArcLen(self,DV,S) -> float:
        "Длина дуги контакта"
        LK = sqrt(DV * S / 2)
        return LK
    
    # def ContactArea(self,b_0, b_1, LK) -> float:
    #     "Площадь контакта"
    #     b_average = (b_0 + b_1) / 2
    #     F = b_average * LK
    #     return F
    
    # def AbsWidening(self,LK, S, Iteration, h_0, h_1) -> float:
    #     "Абсолютное уширение"
    #     delta_b = (LK - S[Iteration] / 2 / h_1) * log(h_0 / h_1) / 2
    #     return delta_b

    def FinalLength(self,h_0,h_1,L):
        FinalLength = L * (h_0 / h_1)
        return FinalLength
            


     

