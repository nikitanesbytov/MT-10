import time
from math import *
from matplotlib import pyplot as plt
import numpy as np
from RollingMill import RollingMill

class RollingMillSimulator(RollingMill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_log = [0]#Лог отображения нынешнего иммитируемого времени
        self.temperature_log = [self.StartTemp]#Лог изменения температуры сляба
        self.length_log = [self.L]#Лог изменения длины сляба
        self.height_log = [self.h_0]#Лог толщины сляба(перед началом прокатки)(мм)
        self.x_log = [0]#Лог начальной координаты сляба
        self.gap_log = [0]#Лог раствора валков(мм)
        self.speed_V = [0]#Лог скорости варщения валков(об/c)
        self.speed_V0 = [0]#Лог скорости вращения рольгангов до валков(об/c)
        self.speed_V1 = [0]#Лог скорости вращения рольгангов после валков(об/c)
        #Лог - это ныншнее значение представленных ТПов

    # def simulate_process(self):
    #     #Запуск симуляции   
        
    def _simulate_approach_to_rolls(self, n, filename="rolling_log.txt"):
        "Проход сляба к валкам"
        total_time = 0
        current_pos = 0

        current_time = self.time_log[-1]
        CurrentS = self.CurrentS[-1]
        initial_temp = self.StartTemp if n == 0 else self.temperature_log[-1]
        current_temp = initial_temp
        target_gap = self.S[n]
        gap_change_per_sec = self.VS

        time_gap = abs(self.S[n] - self.CurrentS[-1]) / self.VS # Время выставления зазора
        time_accel = self.V_Valk_Per[n] / self.accel # Время разгона валков
        time_move = self.d1 / (self.V0[n] * 1000) # Время движения сляба
        total_time = time_gap + time_accel + time_move
        final_temp = initial_temp - 50
        temp_drop_per_sec = (initial_temp - final_temp) / total_time

        speed_mm_per_sec = self.V0[n] * 1000
        target_speed_valk = self.V_Valk_Per[n]
        target_speed_V0 = self.V0[n]
        target_speed_V1 = self.V1[n]
        current_speed = self.speed_V[-1]
        speed_V0 = self.speed_V0[-1]
        speed_V1 = self.speed_V1[-1]
        acceleration = self.accel
        with open(filename, 'w') as f:
            f.write("Time(s)\tGap(mm)\tSpeed(rpm)\tTemp(C)\tPosition(mm)\n")
            #Выставление валков
            while abs(CurrentS - target_gap) > 0.1:
                if CurrentS < target_gap:
                    CurrentS = min(CurrentS + gap_change_per_sec, target_gap)
                else:
                    CurrentS = max(CurrentS - gap_change_per_sec, target_gap)
                
                self.time_log.append(current_time)
                self.gap_log.append(CurrentS)
                self.speed_V.append(0)
                self.time_log.append(current_temp)
                self.x_log.append(0)
                self.speed_V0.append(0)
                self.speed_V1.append(0)
                
                f.write(f"{current_time}\t{CurrentS:.10f}\t{current_speed:.10f}\t{current_temp:.10f}\t{speed_V0:.10f}\t{speed_V1:.10f}\t{current_pos:.10f}\n")
                
                current_time += 1
                current_temp -= temp_drop_per_sec
            #Разгон валков
            
            while current_speed < target_speed_valk and speed_V0 < target_speed_V0 and speed_V1 < target_speed_V1:
                current_speed = min(current_speed + acceleration, target_speed_valk)
                speed_V0 = min(target_speed_V0 + acceleration,target_speed_V0)
                speed_V1 = min(target_speed_V1 + acceleration,target_speed_V1)
                
                self.time_log.append(current_time)
                self.gap_log.append(CurrentS)
                self.speed_V.append(current_speed)
                self.time_log.append(current_temp)
                self.x_log.append(0)
                self.speed_V0.append(speed_V0)
                self.speed_V1.append(speed_V1)
                
                f.write(f"{current_time}\t{CurrentS:.10f}\t{current_speed:.10f}\t{current_temp:.10f}\t{speed_V0:.10f}\t{speed_V1:.10f}\t{current_pos:.10f}\n")               
                
                current_time += 1
                current_temp -= temp_drop_per_sec
            #Движение сляба
            
            while current_pos < self.d1:
                current_pos = min(current_pos + speed_mm_per_sec, self.d1)
                
                # Логирование
                self.time_log.append(current_time)
                self.gap_log.append(CurrentS)
                self.speed_V.append(current_speed)
                self.time_log.append(current_temp)
                self.x_log.append(current_pos)
                self.speed_V0.append(speed_V0)
                self.speed_V1.append(speed_V1)
                
                # Запись в файл
                f.write(f"{current_time}\t{CurrentS:.10f}\t{current_speed:.10f}\t{current_temp:.10f}\t{speed_V0:.10f}\t{speed_V1:.10f}\t{current_pos:.10f}\n")               
                
                current_time += 1
                current_temp -= temp_drop_per_sec
        pass
    
    def _simulate_rolling_pass(self,n):
        #1.Рассчет изменения длины
        h_0 = self.h_0 if n==0 else self.height_log[-1]
        h_1 = self.h_1 if n==0 else self.S[-1]
        RelDef = self.RelDef(h_0,h_1)
        FinalLength = self.FinalLength(h_0,h_1,self.L if n==0 else self.length_log[-1])
        #2.Рассчет усилия,момента и мощности и проверка этих показателей с максимальными
        ContactArcLen = self.ContactArcLen(self.DV,self.S[n])
        DefResistance = self.DefResistance(RelDef,ContactArcLen,self.speed_V[-1])
        AvrgPressure = self.AvrgPressure(DefResistance,ContactArcLen,h_0,h_1)
        Effort = self.Effort(ContactArcLen,AvrgPressure,self.b)
        Moment = self.Moment(ContactArcLen,h_0,h_1,Effort)
        Power = self.Power(Moment,self.speed_V*2*pi)
        #3.Рассчет падения температуры от пластической деформации и контакта с валками
        TempDrDConRoll = self.TempDrDConRoll(self.DV,h_0,h_1)
        TempDrPlDeform = self.TempDrPlDeform(RelDef,h_0,h_1)
        GenTempDrop = self.GenTemp(self.temperature_log[-1],TempDrDConRoll,TempDrPlDeform,TempDrBPass=0) 

    # def _simulate_exit_from_rolls(self):
    #     #1.Доход сляба до конечного концевика

    #     #2.Замедление рольгангов и валков до 0 скорости

    #     #3.Рассчет падения температуры

    # def _simulate_pause_between_passes(self):
    #     #1.Выдержка паузы и падение температуры во время этой паузы


    # def linear_interpolation(start, end, steps=60):
    #     step_size = (end - start) / steps
    #     return [start + step_size * i for i in range(steps + 1)]
    
    # def _log_data(self):



if __name__ == "__main__":
    # Параметры прокатки
    L = 100  # начальная длина сляба, мм
    b = 75   # ширина сляба, мм
    h_0 = 200  # начальная толщина, мм
    S = [100, 160, 140, 120, 100]  # целевые толщины по пропускам, мм
    StartTemp = 1200  # начальная температура, °C
    StartS = 10 # начальный раствор валков
    DV = 800   # диаметр валков, мм
    MV = 'Steel'  # материал валков
    MS = 'Carbon Steel'  # материал сляба
    OutTemp = 25  # температура валков, °C
    n = 5      # количество пропусков
    V0 = [0.7, 1.0, 1.0, 1.0, 1.0]  # начальная скорость, об/с
    V1 = [0.7, 1.0, 1.0, 1.0, 1.0]  # конечная скорость, об/с
    PauseBIter = 5  # пауза между пропусками, с
    V_Valk_Per = [0.7, 1.0, 1.0, 1.0, 1.0] # установка скоростей валков для каждого пропуска (об/с)
   
    simulator = RollingMillSimulator(
        L=L, b=b, h_0=h_0, S=S, StartTemp=StartTemp,
        DV=DV, MV=MV, MS=MS, OutTemp=OutTemp,
        n=n, V0=V0, V1=V1, PauseBIter=PauseBIter,V_Valk_Per = V_Valk_Per,StartS=StartS,
        MaxEffort=20000, MaxMoment=50000, MaxPower=50000,d1 = 10000,d2=10000
    )
    
    # Запуск симуляции
    result = simulator._simulate_approach_to_rolls(0)
  