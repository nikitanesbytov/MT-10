import time
from math import *
from RollingMill import RollingMill
import random
import pymodbus


class RollingMillSimulator(RollingMill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_log = [0]#Лог отображения нынешнего иммитируемого времени
        self.temperature_log = [self.StartTemp]#Лог изменения температуры сляба
        self.length_log = [self.L]#Лог изменения длины сляба
        self.height_log = [self.h_0]#Лог толщины сляба(перед началом прокатки)(мм)
        self.x_log = [self.L]#Лог начальной координаты сляба
        self.x1_log = [0]#Лог конечной координаты сляба
        self.pyrometr_1 = [self.TempV]#Лог пирометра перед валками
        self.pyrometr_2 = [self.TempV]#Лог пирометра после валков
        self.gap_log = [0]#Лог раствора валков(мм)
        self.speed_V = [0]#Лог скорости варщения валков(об/c)
        self.speed_V0 = [0]#Лог скорости вращения рольгангов до валков(об/c)
        self.speed_V1 = [0]#Лог скорости вращения рольгангов после валков(об/c)
        self.effort_log = [0]#Лог усилия прокаткатки(кН)
        self.moment_log = [0]#Лог момента прокаткатки(кН*м)
        self.power_log = [0]#Лог мощности прокатки(кВт)
        self.time_step = 0.1#Шаг времени
        #Лог - это ныншнее значение представленных ТПов

    def roughness(self,number,Range) -> float:
        'Генерация случайного отклонения на +- 5 процентов от заданного числа для симуляции неровностей сляба'
        five_percent = number * Range
        random_deviation = random.uniform(-five_percent, five_percent)
        return random_deviation
        
    def linear_interpolation(self,start, end, steps) -> float:
        "Линейная интерполяция, возвращающая шаг смещения величины"
        if steps <= 0:
            raise ValueError("Количество шагов должно быть положительным")
        step_size = (end - start) / steps
        return step_size
    
    def save_logs_to_file(self, filename="rolling_log.txt"):
        "Сохраняет логи в файл в виде отформатированной таблицы"
        with open(filename, 'w') as f:
            col_widths = {
                'Time': 8,
                'Gap': 8,
                'Speed_V': 8,
                # 'Pyro1': 8,
                # 'Pyro2': 8,
                'Temp': 8,
                'Pos_x': 8,
                'Pos_x1': 8,
                'Speed_V0': 8,
                'Speed_V1': 8,
                'Length': 8 ,
                'Effort' : 8,
                'Moment' : 8,
                'Power' : 8
            }
            # Заголовки таблицы
            headers = [
                f"{'Time':<{col_widths['Time']}}",
                f"{'Gap':<{col_widths['Gap']}}",
                f"{'Speed_V':<{col_widths['Speed_V']}}",
                f"{'Speed_V0':<{col_widths['Speed_V0']}}",
                f"{'Speed_V1':<{col_widths['Speed_V1']}}",
                # f"{'Pyro1':<{col_widths['Pyro1']}}",
                # f"{'Pyro2':<{col_widths['Pyro2']}}",
                f"{'Temp':<{col_widths['Temp']}}",
                f"{'Pos_x':<{col_widths['Pos_x']}}",
                f"{'Pos_x1':<{col_widths['Pos_x1']}}",
                f"{'Length':<{col_widths['Length']}}",
                f"{'Effort':<{col_widths['Effort']}}",
                f"{'Moment':<{col_widths['Moment']}}",
                f"{'Power':<{col_widths['Power']}}"

            ]
            f.write(" | ".join(headers) + "\n")
            f.write("-" * (sum(col_widths.values()) + 3 * (len(col_widths) - 1)) + "\n")
            
            # Данные
            for i in range(len(self.time_log)):
                row = [
                    f"{self.time_log[i]:<{col_widths['Time']}.1f}",
                    f"{self.gap_log[i]:<{col_widths['Gap']}.1f}",
                    f"{self.speed_V[i]:<{col_widths['Speed_V']}.1f}",
                    f"{self.speed_V0[i]:<{col_widths['Speed_V0']}.1f}",
                    f"{self.speed_V1[i]:<{col_widths['Speed_V1']}.1f}",
                    # f"{self.pyrometr_1[i]:<{col_widths['Pyro1']}.1f}",
                    # f"{self.pyrometr_2[i]:<{col_widths['Pyro2']}.1f}",
                    f"{self.temperature_log[i]:<{col_widths['Temp']}.1f}",
                    f"{self.x_log[i]:<{col_widths['Pos_x']}.1f}",
                    f"{self.x1_log[i]:<{col_widths['Pos_x1']}.1f}",
                    f"{self.length_log[i]:<{col_widths['Length']}.1f}",
                    f"{self.effort_log[i]:<{col_widths['Effort']}.1f}",
                    f"{self.moment_log[i]:<{col_widths['Moment']}.1f}",
                    f"{self.power_log[i]:<{col_widths['Power']}.1f}"
                ]
                f.write(" | ".join(row) + "\n")
    
    def _update_logs(self, time, gap, speed_V, temp, pyrometr_1,pyrometr_2, pos_x, pos_x1, speed_V0, speed_V1, length, effort,moment,power):
        "Обновление внутренних логов без записи в файл"
        self.time_log.append(time)
        self.gap_log.append(gap)
        self.speed_V.append(speed_V)
        self.pyrometr_1.append(pyrometr_1)
        self.pyrometr_2.append(pyrometr_2)
        self.temperature_log.append(temp)
        self.x_log.append(pos_x)
        self.x1_log.append(pos_x1)
        self.speed_V0.append(speed_V0)
        self.speed_V1.append(speed_V1)
        self.length_log.append(length)
        self.effort_log.append(effort)
        self.moment_log.append(moment)
        self.power_log.append(power)

    def _simulate_approach_to_rolls(self):
        "Проход сляба к валкам (чистая версия без работы с файлами)"
        current_pos_x = self.x_log[-1]
        current_pos_x1 = self.x1_log[-1]
        current_time = self.time_log[-1] if self.time_log else 0
        CurrentS = self.CurrentS[-1] 
        initial_temp = self.StartTemp
        current_temp = initial_temp
        target_gap = self.S
        
        gap_change_per_ms = self.VS * self.time_step 
        start_time = self.time_log[-1]
        
        time_gap = (abs(self.S - CurrentS)) / (self.VS)
        time_accel = ((self.V_Valk_Per) / (self.accel))
        time_accel_V0 = ((self.V0) / (self.accel))
        S1 = ((self.accel) * time_accel_V0**2)/2
        S2 = (self.d1 - self.L) - S1
        time_max_speed = (S2 / (self.V0))
        time_move = (time_accel_V0 + time_max_speed)
        total_time = time_gap + time_accel + time_move

        # SpeedOfRolling = self.SpeedOfRolling(self.DV,self.V_Valk_Per[n])
        # final_temp = self.TempDrBPass(self.L if n == 0 else self.length_log[-1],SpeedOfRolling,self.temperature_log[-1])
        # print(final_temp)
        final_temp = initial_temp - 50
        temp_drop_per_ms = ((initial_temp - final_temp) / total_time) * self.time_step
        
        current_speed = self.speed_V[-1] if self.speed_V else 0
        speed_V0 = self.speed_V0[-1] if self.speed_V0 else 0
        speed_V1 = self.speed_V1[-1] if self.speed_V1 else 0
        current_length = self.length_log[-1] if self.length_log else 0
        
        # Фаза 1: Выставление зазора валков
        while CurrentS != target_gap:
            CurrentS = min(CurrentS + gap_change_per_ms, target_gap) if CurrentS < target_gap else max(CurrentS - gap_change_per_ms, target_gap)
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            self._update_logs(current_time, CurrentS, 0, current_temp,self.TempV,self.TempV, self.x_log[-1],0, speed_V0, speed_V1, current_length,0,0,0)

        # Фаза 2: Разгон валков
        while current_speed != self.V_Valk_Per:
            current_speed = current_speed + self.accel * self.time_step
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            self._update_logs(current_time, CurrentS, current_speed, current_temp, self.TempV, self.TempV,self.x_log[-1],0, 0, 0, current_length,0,0,0)
        
        # Фаза 3: Движение сляба
        while  current_pos_x != self.d1:
            speed_V0 = min(speed_V0 + self.accel * self.time_step, self.V0)
            speed_V1 = min(speed_V1 + self.accel * self.time_step, self.V1)
            current_pos_x = min(current_pos_x + speed_V0 * self.time_step, self.d1)
            current_pos_x1 = min(current_pos_x1 + speed_V0 * self.time_step, self.d1-self.L)
            current_length = self.length_log[-1] if self.length_log else 0
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            self._update_logs(current_time, CurrentS, current_speed, current_temp, self.TempV,self.TempV, current_pos_x,current_pos_x1, speed_V0, speed_V1, current_length,0,0,0)
    
    def _simulate_rolling_pass(self):
        "Симуляция прохода сляба через валки"
        start_time = self.time_log[-1]
        current_time = self.time_log[-1]
        
        x = self.x_log[-1]
        x1 = self.x1_log[-1]
    
        #1.Рассчет изменения длины
        h_0 = self.h_0
        h_1 = self.S 
        RelDef = self.RelDef(h_0,h_1)
        start_length = self.length_log[-1]
        FinalLength = self.FinalLength(h_0,h_1,self.L)
        rolling_time = abs(((start_length + FinalLength)/2) / ((self.V0 + self.V1)/2))
        def_for_sek = self.linear_interpolation(start_length,FinalLength,rolling_time) #Изменение длины за секунду
        
        #2.Рассчет падения температуры от пластической деформации и контакта с валками
        RelDef = self.RelDef(h_0,h_1)
        ContactArcLen = self.ContactArcLen(self.DV,h_0=h_0,h_1=h_1)
        DefResistance = self.DefResistance(RelDef=RelDef,LK=ContactArcLen,V=self.speed_V[-1],CurrentTemp=self.temperature_log[-1],SteelGrade=self.SteelGrade)
        SpeedOfRolling = self.SpeedOfRolling(DV=self.DV,V=self.speed_V[-1])
        TempDrDConRoll = self.TempDrDConRoll(DV=self.DV,h_0=h_0,h_1=h_1,Temp=self.temperature_log[-1],SpeedOfRolling=SpeedOfRolling)
        TempDrPlDeform = self.TempDrPlDeform(DefResistance=DefResistance,h_0=h_0,h_1=h_1)
        GenTemp = self.GenTemp(Temp=self.temperature_log[-1],TempDrDConRoll=TempDrDConRoll,TempDrPlDeform=TempDrPlDeform,TempDrBPass=0) 
        
        part = self.L / 5
        x0_0 = x
        x0_1 = x0_0 - part
        x1_1 = x0_1 - part
        x2_1 = x1_1 - part
        x3_1 = x2_1 - part
        x4_1 = x1
        arr_h_0 = [h_0 + self.roughness(h_0,0.01),h_0 + self.roughness(h_0,0.01),h_0 + self.roughness(h_0,0.01),h_0 + self.roughness(h_0,0.01),h_0 + self.roughness(h_0,0.01)]
        h_1 = self.S
        while x4_1 < self.d1:
            x0_0 = x0_0 + self.speed_V[-1] * self.time_step + def_for_sek
            x0_1 = x0_1 + self.speed_V[-1] * self.time_step
            x1_1 = x1_1 + self.speed_V[-1] * self.time_step
            x2_1 = x2_1 + self.speed_V[-1] * self.time_step
            x3_1 = x3_1 + self.speed_V[-1] * self.time_step
            x4_1 = x4_1 + self.speed_V[-1] * self.time_step
            length = self.length_log[-1] + def_for_sek
            
            if x0_1 < self.d1 and x1_1 < self.d1 and x2_1 < self.d1 and x3_1 < self.d1 and x4_1 < self.d1:
                RelDef = self.RelDef(arr_h_0[0],h_1)
                ContactArcLen = self.ContactArcLen(self.DV,h_0=h_0,h_1=h_1)
                DefResistance = self.DefResistance(RelDef=RelDef,LK=ContactArcLen,V=self.speed_V[-1],CurrentTemp=self.temperature_log[-1],SteelGrade=self.SteelGrade)
                AvrgPressure = self.AvrgPressure(DefResistance=DefResistance,LK=ContactArcLen,h_0=arr_h_0[0],h_1=h_1)
                Effort = self.Effort(LK=ContactArcLen,b=self.b,AvrgPressure=AvrgPressure)
                Moment = self.Moment(LK=ContactArcLen,h_0=h_0,h_1=h_1,Effort=Effort/1000)
                Power = self.Power(Moment,self.speed_V[-1]/self.R)
            if x0_1 >= self.d1 and x1_1 < self.d1 and x2_1 < self.d1 and x3_1 < self.d1 and x4_1 < self.d1:
                RelDef = self.RelDef(arr_h_0[1],h_1)
                ContactArcLen = self.ContactArcLen(self.DV,h_0,h_1)
                DefResistance = self.DefResistance(RelDef=RelDef,LK=ContactArcLen,V=self.speed_V[-1],CurrentTemp=self.temperature_log[-1],SteelGrade=self.SteelGrade)
                AvrgPressure = self.AvrgPressure(DefResistance=DefResistance,LK=ContactArcLen,h_0=arr_h_0[1],h_1=h_1)
                Effort = self.Effort(LK=ContactArcLen,b=self.b,AvrgPressure=AvrgPressure)
                Moment = self.Moment(LK=ContactArcLen,h_0=h_0,h_1=h_1,Effort=Effort/1000)
                Power = self.Power(Moment,self.speed_V[-1]/self.R)
            if x0_1 >= self.d1 and x1_1 >= self.d1 and x2_1 < self.d1 and x3_1 < self.d1 and x4_1 < self.d1:
                RelDef = self.RelDef(arr_h_0[2],h_1)
                DefResistance = self.DefResistance(RelDef=RelDef,LK=ContactArcLen,V=self.speed_V[-1],CurrentTemp=self.temperature_log[-1],SteelGrade=self.SteelGrade)
                AvrgPressure = self.AvrgPressure(DefResistance=DefResistance,LK=ContactArcLen,h_0=arr_h_0[2],h_1=h_1)
                Effort = self.Effort(LK=ContactArcLen,b=self.b,AvrgPressure=AvrgPressure)
                Moment = self.Moment(LK=ContactArcLen,h_0=h_0,h_1=h_1,Effort=Effort/1000)
                Power = self.Power(Moment,self.speed_V[-1]/self.R)
            if x0_1 >= self.d1 and x1_1 >= self.d1 and x2_1 >= self.d1 and x3_1 < self.d1 and x4_1 < self.d1:
                RelDef = self.RelDef(arr_h_0[3],h_1)
                ContactArcLen = self.ContactArcLen(self.DV,h_0,h_1)
                DefResistance = self.DefResistance(RelDef=RelDef,LK=ContactArcLen,V=self.speed_V[-1],CurrentTemp=self.temperature_log[-1],SteelGrade=self.SteelGrade)
                AvrgPressure = self.AvrgPressure(DefResistance=DefResistance,LK=ContactArcLen,h_0=arr_h_0[3],h_1=h_1)
                Effort = self.Effort(LK=ContactArcLen,b=self.b,AvrgPressure=AvrgPressure)
                Moment = self.Moment(LK=ContactArcLen,h_0=h_0,h_1=h_1,Effort=Effort/1000)
                Power = self.Power(Moment,self.speed_V[-1]/self.R)
            if x0_1 >= self.d1 and x1_1 >= self.d1 and x2_1 >= self.d1 and x3_1 >= self.d1 and x4_1 < self.d1:
                RelDef = self.RelDef(arr_h_0[4],h_1)
                ContactArcLen = self.ContactArcLen(self.DV,h_0,h_1)
                DefResistance = self.DefResistance(RelDef=RelDef,LK=ContactArcLen,V=self.speed_V[-1],CurrentTemp=self.temperature_log[-1],SteelGrade=self.SteelGrade)
                AvrgPressure = self.AvrgPressure(DefResistance=DefResistance,LK=ContactArcLen,h_0=arr_h_0[4],h_1=h_1)
                Effort = self.Effort(LK=ContactArcLen,b=self.b,AvrgPressure=AvrgPressure)
                Moment = self.Moment(LK=ContactArcLen,h_0=h_0,h_1=h_1,Effort=Effort/1000)
                Power = self.Power(Moment,self.speed_V[-1]/self.R)
            
            current_time += self.time_step
            self._update_logs(current_time, self.gap_log[-1], self.speed_V[-1], GenTemp, self.TempV,self.TempV, x0_0, x4_1, self.speed_V0[-1], self.speed_V1[-1], length,Effort/1000,Moment/1000,Power/1000)   
        pass

    def _simulate_exit_from_rolls(self):
        "Симуляция дохода сляба до концевика"
        current_time = self.time_log[-1]
        current_temp = self.temperature_log[-1]
        #1.Рассчет падения температуры  
        distance_to_cover = (self.d1 + self.d2) - self.x_log[-1]
        time_first_cycle = distance_to_cover / self.speed_V1[-1]
        time_brake_speed = self.speed_V[-1] / self.accel
        time_brake_V0 = self.speed_V0[-1] / self.accel  
        time_brake_V1 = self.speed_V1[-1] / self.accel
        time_second_cycle = max(time_brake_speed, time_brake_V0, time_brake_V1)
        total_time = time_first_cycle + time_second_cycle + self.PauseBIter
        final_temp = current_temp - 100
        temp_drop_per_ms = ((current_temp - final_temp) / total_time) * self.time_step
        #2.Доход сляба до конечного концевика
        while self.x_log[-1] < self.d1 + self.d2 :
            x = min(self.x_log[-1] + self.speed_V1[-1] * self.time_step,self.d1 + self.d2)
            x1 = self.x1_log[-1] + self.speed_V1[-1] * self.time_step
            current_temp -= temp_drop_per_ms
            current_time += self.time_step
            self._update_logs(current_time, self.gap_log[-1], self.speed_V[-1], current_temp, self.TempV,self.TempV, x, x1, self.speed_V0[-1], self.speed_V1[-1], self.length_log[-1],0,0,0)
        #3.Замедление рольгангов и валков до 0 скорости
        current_speed = self.speed_V[-1]
        current_V0 = self.speed_V0[-1]
        current_V1 = self.speed_V1[-1]
        while current_speed > 0 or current_V0 > 0 or current_V1 > 0:
            current_speed = max(current_speed - self.accel * self.time_step,0)
            current_V0 = max(current_V0 - self.accel * self.time_step,0)
            current_V1 = max(current_V1 - self.accel * self.time_step,0)
            current_temp -= temp_drop_per_ms
            current_time += self.time_step
            self._update_logs(current_time,self.gap_log[-1],current_speed,current_temp,self.TempV,self.TempV,self.x_log[-1],self.x1_log[-1],current_V0,current_V1,self.length_log[-1],0,0,0)
    pass
        
    # def auto_process(self):
    #     #Автоматический режим работы
    
    # def manual_process(self):
    #     #Ручной режим работы  

    def alarm_stop(self):
        "Аварийный останов"
        while self.speed_V[-1] > 0 or self.speed_V0[-1] > 0 or self.speed_V1[-1] > 0 or self.CurrentS[-1] != self.StartS:
            current_speed = max(current_speed - self.accel * self.time_step,0)
            current_V0 = max(current_V0 - self.accel * self.time_step,0)
            current_V1 = max(current_V1 - self.accel * self.time_step,0)
            currentS = min(currentS + self.VS,self.StartS)       


def start(Num_of_revol_rolls,Roll_pos,Num_of_revol_0rollg,Num_of_revol_1rollg,Dir_of_rot,Dir_of_rot_rolg,Mode,Dir_of_rot_valk,Speed_of_diverg):
    # Параметры прокатки
    L = 100  # начальная длина сляба, мм
    b = 75   # ширина сляба, мм
    h_0 = 75  # начальная толщина, мм
    StartTemp = 1200  # начальная температура, °C
    StartS = 200 # начальный раствор валков
    DV = 300   # диаметр валков, мм
    DR = 100  # диаметр рольгангов, мм
    MV = 'Steel'  # материал валков
    MS = 'Carbon Steel'  # материал сляба
    OutTemp = 25  # температура валков, °C
    PauseBIter = 5  # пауза между пропусками, с
    V_Valk_Per = 0 # Скорость валков (мм/c)
    SteelGrade = "Ст3сп" #Марка стали
    
    S = Roll_pos  #Расхождение валков, мм
    V0 = (2 * pi * DR/2 * Num_of_revol_0rollg) / 60  # начальная скорость(мм/с)
    V1 = (2 * pi * DR/2 * Num_of_revol_1rollg) / 60  # конечная скорость(мм/с) 
    V_Valk_Per = 200#(2 * pi * DV/2 * Num_of_revol_rolls) / 60 # Скорость валков (мм/c)
    Dir_of_rot = Dir_of_rot #Направление вращения валков
    Dir_of_rot_rolg = Dir_of_rot_rolg #Направление вращения левых рольгангов
    Mode = Mode #Отправка на частотник флага ручного режима
    Dir_of_rot_valk = Dir_of_rot_valk #Направление движения валков 
    
    simulator = RollingMillSimulator(
        L=L,b=b,h_0=h_0,S=S,StartTemp=StartTemp,
        DV=DV,MV=MV,MS=MS,OutTemp=OutTemp,DR=DR,SteelGrade=SteelGrade,
        V0=V0,V1=V1,PauseBIter=PauseBIter,VS=Speed_of_diverg,
        d1=1500,d2=1500,V_Valk_Per=V_Valk_Per,StartS=StartS,
    )
    print("Начало симуляции")
    simulator._simulate_approach_to_rolls()
    print("Сляб подошел к валкам")
    simulator._simulate_rolling_pass()
    print("Сляб покинул валки")
    simulator._simulate_exit_from_rolls()
    print("Сляб дошел до конца прокатного стана")

    #Создание лога
    simulator.save_logs_to_file("my_logs.txt")
    print("Симуляция окончена")