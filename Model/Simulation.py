from Stan import RollingMill

#Момент, усилие на валках, координаты, температура сляба, скорость вращения, направление вращения, длина сляба(для ПЛК)
if __name__ == "__main__":
    Process = RollingMill()
    n = 10 #Задает оператор(количество прокатов)
    flag = 0 #0 - процесс приостанволен/1 - процесс запущен
    flag1 = 0 #0 - До валков/ 1 - В валках/2 - После валков
    x = [] #Посекундный массив для координаты начала сляба
    x_end = [] #Посекундный массив для координаты конца сляба
    
    for i in range(n):
        RelDef = Process.RelDef() #1 
        while flag == 1:
            if flag1 == 0:
                if Process.V_Valk[i] != CurrentV[t]:
                    CurrentV[t] = CurrentV[t] + Process.accel #Иммитируем ускорение валков до заданной скорости
                else:
                    x[t] = x[t] + Process.V0 #Расчет его координаты
                    TempDrBPass = Process.TempDrBPass()
                    GenTemp[t] = Process.GenTemp(TempDrDConRoll = 0,TempDrPlDeform=0,TempDrBPass=TempDrBPass) #Рассчет нынешней температуры сляба?
                    if x[t] >= Process.d1:
                        FricCoff = Process.FricCoef(GenTemp[t])
                        if Process.CapCondition(FricCoff):
                            flag1 = 1
                        else:
                            pass #Warning
            if flag1 == 1:
                x[t] = x[t] + Process.V1 #Расчет его координаты
                ContactArcLen = Process.ContactArcLen()
                TempDrDConRoll = Process.TempDrDConRoll(Process.V_Valk[n],ContactArcLen)
                TempDrPlDeform = Process.TempDrPlDeform(RelDef)
                GenTemp[t] = Process.GenTemp(TempDrBPass = 0,TempDrDConRoll=TempDrDConRoll ,TempDrPlDeform=TempDrPlDeform) #Рассчет нынешней температуры сляба?
                
                DefResistance = Process.DefResistance(ContactArcLen,RelDef)
                AvrgPressure = Process.AvrgPressure(DefResistance,ContactArcLen)

                
                Effort = Process.Effort(AvrgPressure,ContactArcLen)
                if Effort > Process.MaxEffort:
                    pass #Warning
                Moment = Process.Moment(ContactArcLen,Effort)
                if Moment > Process.MaxMoment:
                    pass #Warning
                Power = Process.Power(Moment,Process.V_Valk_Per[n])
                if Power > Process.MaxPower:
                    pass #Warning
                
                FinalLength = Process.FinalLength()
                
                if x[t] - FinalLength >= Process.d1:
                    flag1 = 2








    