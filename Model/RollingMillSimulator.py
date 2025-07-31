import time
from math import *
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
        
    def linear_interpolation(self,start, end, steps) -> float:
        """
        Линейная интерполяция, возвращающая шаг изменения
        """
        if steps <= 0:
            raise ValueError("Количество шагов должно быть положительным")
        
        step_size = (end - start) / steps
        return step_size
    
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

        speed_mm_per_sec = self.V0[n] * pi * self.DR
        target_speed_valk = self.V_Valk_Per[n]
        target_speed_V0 = self.V0[n]
        target_speed_V1 = self.V1[n]
        current_speed = self.speed_V[-1]
        speed_V0 = self.speed_V0[-1]
        speed_V1 = self.speed_V1[-1]
        
        with open(filename, 'w') as f:
            #Выставление валков
            f.write(f"{'Time(s)':<5}{'Gap(mm)':>8}{'Speed(rpm)':>8}{'Temp(C)':>8}"
                    f"{'V0(rpm)':>8}{'V1(rpm)':>8}{'Position':>10}{'Length(mm)':>10}\n")
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
                self.length_log.append(self.length_log[-1])
                
                f.write(f"{current_time:<5d}{CurrentS:>8.1f}{current_speed:>8.1f}{current_temp:>8.1f}"
                        f"{speed_V0:>8.1f}{speed_V1:>8.1f}{current_pos:>10.1f}{self.length_log[-1]:>10.1f}\n")
                
                current_time += 1
                current_temp -= temp_drop_per_sec
            #Разгон валков
            
            while current_speed < target_speed_valk and speed_V0 < target_speed_V0 and speed_V1 < target_speed_V1:
                current_speed = min(current_speed + self.accel, target_speed_valk)
                speed_V0 = min(speed_V0 + self.accel, target_speed_V0)
                speed_V1 = min(speed_V1 + self.accel, target_speed_V1)
       
                self.time_log.append(current_time)
                self.gap_log.append(CurrentS)
                self.speed_V.append(current_speed)
                self.time_log.append(current_temp)
                self.x_log.append(0)
                self.speed_V0.append(speed_V0)
                self.speed_V1.append(speed_V1)
                self.length_log.append(self.length_log[-1])
                
                f.write(f"{current_time:<5d}{CurrentS:>8.1f}{current_speed:>8.1f}{current_temp:>8.1f}"
                        f"{speed_V0:>8.1f}{speed_V1:>8.1f}{current_pos:>10.1f}{self.length_log[-1]:>10.1f}\n")
                
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
                self.length_log.append(self.length_log[-1])
                
                # Запись в файл
                f.write(f"{current_time:<5d}{CurrentS:>8.1f}{current_speed:>8.1f}{current_temp:>8.1f}"
                        f"{speed_V0:>8.1f}{speed_V1:>8.1f}{current_pos:>10.1f}{self.length_log[-1]:>10.1f}\n")               
                
                current_time += 1
                current_temp -= temp_drop_per_sec
        pass
    
    def _simulate_rolling_pass(self,n,filename="rrolling_log.txt"):
        "Симуляция прохода сляба через валки"
        current_time = self.time_log[-1]
        start_time = self.time_log[-1]
        #1.Рассчет изменения длины
        h_0 = self.h_0 if n == 0 else self.height_log[-1]
        h_1 = self.S[n]
        RelDef = self.RelDef(h_0,h_1)
        start_length = self.length_log[-1]
        FinalLength = self.FinalLength(h_0,h_1,self.L if n == 0 else self.length_log[-1])
        rolling_time = abs((start_length + FinalLength) / ((self.V0[n] + self.V1[n])/2))
        def_for_sek = self.linear_interpolation(start_length,FinalLength,rolling_time) #изменение длины за секунду
        #2.Рассчет усилия,момента и мощности и проверка этих показателей с максимальными
        ContactArcLen = self.ContactArcLen(self.DV,self.S[n])
        DefResistance = self.DefResistance(RelDef,ContactArcLen,self.speed_V[-1])
        AvrgPressure = self.AvrgPressure(DefResistance,ContactArcLen,h_0,h_1)
        Effort = self.Effort(ContactArcLen,AvrgPressure,self.b)
        Moment = self.Moment(ContactArcLen,h_0,h_1,Effort)
        Power = self.Power(Moment,self.speed_V[n]*2*pi)
        #3.Рассчет падения температуры от пластической деформации и контакта с валками
        TempDrDConRoll = self.TempDrDConRoll(self.DV,h_0,h_1)
        TempDrPlDeform = self.TempDrPlDeform(RelDef,h_0,h_1)
        # GenTempDrop = self.GenTemp(self.temperature_log[-1],TempDrDConRoll,TempDrPlDeform,TempDrBPass=0) 
        with open(filename, 'w') as f:
            while current_time < start_time + rolling_time:
                self.length_log.append(self.length_log[-1] + def_for_sek)
                current_pos = min(self.x_log[-1] + self.V0[n] * 1000, self.d1)
                
                self.time_log.append(current_time)
                self.gap_log.append(self.CurrentS[-1])
                self.speed_V.append(self.speed_V[-1])
                self.time_log.append(current_time)
                self.x_log.append(current_pos)
                self.speed_V0.append(self.V0[n])
                self.speed_V1.append(self.V1[n])
                self.length_log.append(self.length_log[-1])

                f.write(f"{current_time:.1f}\t{self.CurrentS[-1]:.1f}\t{self.speed_V[-1]:.1f}\t{self.time_log[-1]:.1f}\t{self.V0[n]:.1f}\t{self.V1[n]:.1f}\t{current_pos:.1f}\t{self.length_log[-1]:.1f}\n")
                
                current_time += 1
        pass


    # def _simulate_exit_from_rolls(self):
    #     #1.Доход сляба до конечного концевика

    #     #2.Замедление рольгангов и валков до 0 скорости

    #     #3.Рассчет падения температуры

    # def _simulate_pause_between_passes(self):
    #     #1.Выдержка паузы и падение температуры во время этой паузы
 
    # def _log_data(self):

if __name__ == "__main__":
    # Параметры прокатки
    L = 1000  # начальная длина сляба, мм
    b = 75   # ширина сляба, мм
    h_0 = 200  # начальная толщина, мм
    S = [180, 160, 140, 120, 100]  # целевые толщины по пропускам, мм
    StartTemp = 1200  # начальная температура, °C
    StartS = 10 # начальный раствор валков
    DV = 300   # диаметр валков, мм
    DR = 100  # диаметр рольгангов, мм
    MV = 'Steel'  # материал валков
    MS = 'Carbon Steel'  # материал сляба
    OutTemp = 25  # температура валков, °C
    n = 5      # количество пропусков
    V0 = [10, 10, 0.7, 0.7, 0.7]  # начальная скорость(об/с)
    V1 = [5, 10, 0.7, 0.7, 0.7]  # конечная скорость(об/с)
    PauseBIter = 5  # пауза между пропусками, с
    V_Valk_Per = [5, 0.7, 0.7, 0.7, 0.7] # установка скоростей валков для каждого пропуска (об/с)
   
    simulator = RollingMillSimulator(
        L=L, b=b, h_0=h_0, S=S, StartTemp=StartTemp,
        DV=DV, MV=MV, MS=MS, OutTemp=OutTemp,DR=DR,
        n=n, V0=V0, V1=V1, PauseBIter=PauseBIter,V_Valk_Per = V_Valk_Per,StartS=StartS,
        MaxEffort=20000, MaxMoment=50000, MaxPower=50000,d1 = 10000,d2=10000
    )
    
    # Запуск симуляции
    result = simulator._simulate_approach_to_rolls(0)
    # simulator._simulate_rolling_pass(0)
  