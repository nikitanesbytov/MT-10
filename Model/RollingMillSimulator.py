from math import *
from RollingMill import RollingMill
import random

class RollingMillSimulator(RollingMill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_log = [0]#Лог отображения нынешнего иммитируемого времени
        self.temperature_log = [self.StartTemp]#Лог изменения температуры сляба
        self.length_log = [self.L]#Лог изменения длины сляба
        self.height_log = [self.h_0]#Лог толщины сляба(перед началом прокатки)(мм)
        self.LeftCap = [1]#Левый концевик
        self.RightCap = [0]#Правый концевик
        self.x_log = [self.L if self.LeftCap[-1] == 1 else self.d1+self.d2 + self.d]#Лог начальной координаты сляба
        self.x1_log = [0 if self.LeftCap[-1] == 1 else (self.d1+self.d2+self.d) - self.L]#Лог конечной координаты сляба
        self.pyrometr_1 = [self.TempV]#Лог пирометра перед валками
        self.pyrometr_2 = [self.TempV]#Лог пирометра после валков
        self.gap_log = [self.CurrentS]#Лог раствора валков(мм)
        self.speed_V = [0]#Лог скорости варщения валков(об/c)
        self.speed_V0 = [0]#Лог скорости вращения рольгангов до валков(об/c)
        self.speed_V1 = [0]#Лог скорости вращения рольгангов после валков(об/c)
        self.effort_log = [0]#Лог усилия прокаткатки(кН)
        self.moment_log = [0]#Лог момента прокаткатки(кН*м)
        self.power_log = [0]#Лог мощности прокатки(кВт)
        self.Gap_feedbackLog = [0]#Лог флага обратной свзяи о выхождении раствора на заданную уставку 
        self.Speed_V_feedbackLog = [0]#Лог флага обратной свзяи о выхождении скорости валков на заданную уставку
        self.time_step = 0.1#Шаг времени
        #Лог - это ныншнее значение представленных ТПов

    def roughness(self,number,Range) -> float:
        'Генерация случайного отклонения на +- n процентов от заданного числа для симуляции неровностей сляба'
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
                'Pyro1': 8,
                'Pyro2': 8,
                'Temp': 8,
                'Effort' : 8,
                'Gap': 8,   
                'Speed_V': 8,
                'Speed_V0': 8,
                'Speed_V1': 8,
                'LeftCap': 8,
                'RightCap': 8,
                'Moment' : 8,
                'Power' : 8,
                'GapFeedback': 8,
                'Speed_V_feedback': 8,
                'x(deb)' : 8,
                'x1(deb)' : 8,
                'length(deb)': 8
            }
            # Заголовки таблицы
            headers = [
                f"{'Time':<{col_widths['Time']}}",
                f"{'Pyro1':<{col_widths['Pyro1']}}",
                f"{'Pyro2':<{col_widths['Pyro2']}}",
                f"{'Temp':<{col_widths['Temp']}}",
                f"{'Effort':<{col_widths['Effort']}}",
                f"{'Gap':<{col_widths['Gap']}}",
                f"{'Speed_V':<{col_widths['Speed_V']}}",
                f"{'Speed_V0':<{col_widths['Speed_V0']}}",
                f"{'Speed_V1':<{col_widths['Speed_V1']}}",
                f"{'LeftCap':<{col_widths['LeftCap']}}",
                f"{'RightCap':<{col_widths['RightCap']}}",
                f"{'Moment':<{col_widths['Moment']}}",
                f"{'Power':<{col_widths['Power']}}",
                f"{'GapFeedback':<{col_widths['GapFeedback']}}",
                f"{'Speed_V_feedback':<{col_widths['Speed_V_feedback']}}"
                f"{'x(deb)':<{col_widths['x(deb)']}}",
                f"{'x1(deb)':<{col_widths['x1(deb)']}}",
                f"{'length(deb)':<{col_widths['length(deb)']}}"


            ]
            f.write(" | ".join(headers) + "\n")
            f.write("-" * (sum(col_widths.values()) + 3 * (len(col_widths) - 1)) + "\n")
            
            # Данные
            for i in range(len(self.time_log)):
                row = [
                    f"{self.time_log[i]:<{col_widths['Time']}}",
                    f"{self.pyrometr_1[i]:<{col_widths['Pyro1']}}",
                    f"{self.pyrometr_2[i]:<{col_widths['Pyro2']}}",
                    f"{self.temperature_log[i]:<{col_widths['Temp']}}",
                    f"{self.effort_log[i]:<{col_widths['Effort']}}",
                    f"{self.gap_log[i]:<{col_widths['Gap']}}",
                    f"{self.speed_V[i]:<{col_widths['Speed_V']}}",
                    f"{self.speed_V0[i]:<{col_widths['Speed_V0']}}",
                    f"{self.speed_V1[i]:<{col_widths['Speed_V1']}}",
                    f"{self.LeftCap[i]:<{col_widths['LeftCap']}}",
                    f"{self.RightCap[i]:<{col_widths['RightCap']}}",
                    f"{self.moment_log[i]:<{col_widths['Moment']}}",
                    f"{self.power_log[i]:<{col_widths['Power']}}",
                    f"{self.Gap_feedbackLog[i]:<{col_widths['GapFeedback']}}",
                    f"{self.Speed_V_feedbackLog[i]:<{col_widths['Speed_V_feedback']}}"
                    f"{self.x_log[i]:<{col_widths['x(deb)']}}",
                    f"{self.x1_log[i]:<{col_widths['x1(deb)']}}",
                    f"{self.length_log[i]:<{col_widths['length(deb)']}}",
                    
                ]
                f.write(" | ".join(row) + "\n")
    
    def _update_logs(self, time, gap, speed_V, temp, pyrometr_1,pyrometr_2, pos_x, pos_x1, speed_V0, speed_V1, length, effort,moment,power,LeftCap,RightCap,Gap_feedback,Speed_V_feedback):
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
        self.LeftCap.append(LeftCap)
        self.RightCap.append(RightCap)
        self.Gap_feedbackLog.append(Gap_feedback)
        self.Speed_V_feedbackLog.append(Speed_V_feedback)

    def _simulate_approach_to_rolls(self):
        "Проход сляба к валкам"
        Gap_flag = self.Gap_feedbackLog[-1]
        Speed_V_flag = self.Speed_V_feedbackLog[-1]
        
        current_pos_x = self.x_log[-1]
        current_pos_x1 = self.x1_log[-1]
        current_time = self.time_log[-1] 
        CurrentS = self.gap_log[-1] 
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
        
        current_speed = self.speed_V[-1] 
        speed_V0 = self.speed_V0[-1] 
        speed_V1 = self.speed_V1[-1] 
        current_length = self.length_log[-1] 

        if self.Dir_of_rot == 0:
            target_SpeedV1 = round(self.V0 * (self.h_0 / self.h_1),2)
            self.V1 = target_SpeedV1
        else:
            target_speed_V0 = round(self.V1 * (self.h_0 / self.h_1),2)
            self.V0 = target_speed_V0
        

        # Фаза 1: Выставление зазора валков
        while CurrentS != target_gap:
            CurrentS = min(CurrentS + gap_change_per_ms, target_gap) if CurrentS < target_gap else max(CurrentS - gap_change_per_ms, target_gap)
            if CurrentS == self.S:
                Gap_flag = 1
            else:
                Gap_flag = 0
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            current_time += self.time_step
            self._update_logs(time=round(current_time,2), 
                              gap=round(CurrentS,2), 
                              speed_V=0, 
                              temp=round(current_temp,2),
                              pyrometr_1=round(self.TempV,2),
                              pyrometr_2=round(self.TempV,2), 
                              pos_x=round(self.x_log[-1],2),
                              pos_x1=round(self.x1_log[-1]), 
                              speed_V0=round(speed_V0,2), 
                              speed_V1=round(speed_V1,2), 
                              length=round(current_length,2),
                              effort=0,
                              moment=0,
                              power=0,
                              LeftCap=self.LeftCap[-1],
                              RightCap=self.RightCap[-1],
                              Gap_feedback = Gap_flag,
                              Speed_V_feedback = Speed_V_flag) 

        # Фаза 2: Разгон валков
        while current_speed != self.V_Valk_Per:
            current_speed = min(current_speed + self.accel * self.time_step,self.V_Valk_Per) 
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            if current_speed == self.V_Valk_Per:
                Speed_V_flag = 1
            self._update_logs(time=round(current_time,2), 
                              gap=round(CurrentS,2), 
                              speed_V=round(current_speed,2), 
                              temp=round(current_temp,2), 
                              pyrometr_1=round(self.TempV,2), 
                              pyrometr_2=round(self.TempV,2),
                              pos_x=round(self.x_log[-1],2),
                              pos_x1=round(self.x1_log[-1],2), 
                              speed_V0=0, 
                              speed_V1=0, 
                              length=round(current_length,2),
                              effort=0,
                              moment=0,
                              power=0,
                              LeftCap=self.LeftCap[-1],
                              RightCap=self.RightCap[-1],
                              Gap_feedback = Gap_flag,
                              Speed_V_feedback = Speed_V_flag)
        
        # Фаза 3: Движение сляба                    
        if self.Dir_of_rot == 0:
            while current_pos_x != self.d1 + self.d/2:
                cur_LeftCap = self.LeftCap[-1]
                cur_RightCap = self.RightCap[-1]
                if current_pos_x > 0:
                    cur_LeftCap = 0
                speed_V0 = min(speed_V0 + self.accel * self.time_step, self.V0)
                speed_V1 = min(speed_V1 + self.accel * self.time_step, target_SpeedV1)
                current_pos_x = min(current_pos_x + speed_V0 * self.time_step, self.d1 + self.d/2) 
                current_pos_x1 = min(current_pos_x1 + speed_V0 * self.time_step, self.d1 + self.d/2 - self.L)
                current_length = self.length_log[-1]
                current_time += self.time_step
                current_temp = max(current_temp - temp_drop_per_ms, final_temp)
                self._update_logs(time=round(current_time,2), 
                                gap=round(CurrentS,2), 
                                speed_V=round(current_speed,2), 
                                temp=round(current_temp,2), 
                                pyrometr_1=round(self.TempV,2),
                                pyrometr_2=round(self.TempV,2), 
                                pos_x=round(current_pos_x,2),
                                pos_x1=round(current_pos_x1,2), 
                                speed_V0=round(speed_V0,2), 
                                speed_V1=round(speed_V1,2), 
                                length=round(current_length,2),
                                effort=0,
                                moment=0,
                                power=0,
                                LeftCap=cur_LeftCap,
                                RightCap=cur_RightCap,
                                Gap_feedback = Gap_flag,
                                Speed_V_feedback = Speed_V_flag)
        else:
            while current_pos_x1 > self.d1 + self.d:
                cur_LeftCap = self.LeftCap[-1]
                cur_RightCap = self.RightCap[-1]
                if current_pos_x < self.d1+self.d2+self.d:
                    cur_RightCap = 0
                speed_V0 = min(speed_V0 + self.accel * self.time_step, target_speed_V0)
                speed_V1 = min(speed_V1 + self.accel * self.time_step, self.V1)
                current_pos_x = max(current_pos_x - speed_V1 * self.time_step, self.d1+self.L+self.d/2)
                current_pos_x1 = max(current_pos_x1 - speed_V1 * self.time_step, self.d1+self.d/2)
                current_time += self.time_step
                current_temp = max(current_temp - temp_drop_per_ms, final_temp)
                self._update_logs(time=round(current_time,2), 
                                gap=round(CurrentS,2), 
                                speed_V=round(current_speed,2), 
                                temp=round(current_temp,2), 
                                pyrometr_1=round(self.TempV,2),
                                pyrometr_2=round(self.TempV,2), 
                                pos_x=round(current_pos_x,2),
                                pos_x1=round(current_pos_x1,2), 
                                speed_V0=round(speed_V0,2), 
                                speed_V1=round(speed_V1,2), 
                                length=round(current_length,2),
                                effort=0,
                                moment=0,
                                power=0,
                                LeftCap=cur_LeftCap,
                                RightCap=cur_RightCap,
                                Gap_feedback = Gap_flag,
                                Speed_V_feedback = Speed_V_flag)

    def _simulate_rolling_pass(self):
        "Симуляция прохода сляба через валки"
        current_pos_x = self.x_log[-1]
        current_pos_x1 = self.x1_log[-1]
        current_length = self.length_log[-1]
        current_time = self.time_log[-1]

        #1.Рассчет изменения длины
        h_0 = self.h_0
        h_1 = self.S 
        RelDef = self.RelDef(h_0,h_1)
        start_length = self.length_log[-1]
        FinalLength = round(self.FinalLength(h_0,h_1,self.L),2)
 
        #2.Рассчет падения температуры от пластической деформации и контакта с валками
        RelDef = self.RelDef(h_0,h_1)
        ContactArcLen = self.ContactArcLen(self.DV,h_0=h_0,h_1=h_1)
        DefResistance = self.DefResistance(RelDef=RelDef,LK=ContactArcLen,V=self.speed_V[-1],CurrentTemp=self.temperature_log[-1],SteelGrade=self.SteelGrade)
        AvrgPressure = self.AvrgPressure(DefResistance=DefResistance,LK=ContactArcLen,h_0=h_0,h_1=h_1)
        Effort = self.Effort(LK=ContactArcLen,b=self.b,AvrgPressure=AvrgPressure)
        Moment = self.Moment(LK=ContactArcLen,h_0=h_0,h_1=h_1,Effort=Effort/1000)
        Power = self.Power(Moment,self.speed_V[-1]/self.R)
        SpeedOfRolling = self.SpeedOfRolling(DV=self.DV,V=self.speed_V[-1])
        TempDrDConRoll = self.TempDrDConRoll(DV=self.DV,h_0=h_0,h_1=h_1,Temp=self.temperature_log[-1],SpeedOfRolling=SpeedOfRolling)
        TempDrPlDeform = self.TempDrPlDeform(DefResistance=DefResistance,h_0=h_0,h_1=h_1)
        GenTemp = self.GenTemp(Temp=self.temperature_log[-1],TempDrDConRoll=TempDrDConRoll,TempDrPlDeform=TempDrPlDeform,TempDrBPass=0) 
          
        if self.Dir_of_rot == 0:
            while current_pos_x1 < self.d1 + self.d/2:
                current_pos_x = min(current_pos_x + self.speed_V1[-1] * self.time_step,self.d1+self.d/2 + (self.L + (FinalLength - start_length)) + 1)
                current_pos_x1 = min(current_pos_x1 + self.speed_V0[-1] * self.time_step,self.d1 + self.d/2 + 1)
                current_length = abs((current_pos_x - current_pos_x1))
                Effort += self.roughness(Effort,0.03)
                Moment += self.roughness(Moment,0.03)
                Power += self.roughness(Power,0.03)
                current_time += self.time_step
                self._update_logs(time=round(current_time,2), 
                              gap=round(self.gap_log[-1],2), 
                              speed_V=round(self.speed_V[-1],2), 
                              temp=round(GenTemp,2), 
                              pyrometr_1=round(self.TempV,2),
                              pyrometr_2=round(self.TempV,2), 
                              pos_x=round(current_pos_x,2), 
                              pos_x1=round(current_pos_x1,2), 
                              speed_V0=round(self.speed_V0[-1],2), 
                              speed_V1=round(self.speed_V1[-1],2), 
                              length=round(current_length,2),
                              effort=round(Effort/1000,2),
                              moment=round(Moment/1000,2),
                              power= round(Power/1000,2),
                              LeftCap=self.LeftCap[-1],
                              RightCap=self.RightCap[-1],
                              Gap_feedback = self.Gap_feedbackLog[-1],
                              Speed_V_feedback = self.Speed_V_feedbackLog[-1]
                              )   
        else:
            while current_pos_x > self.d1 + self.d:
                current_pos_x = max(current_pos_x - self.speed_V1[-1] * self.time_step,self.d1 + self.d/2 - 1)
                current_pos_x1 = max(current_pos_x1 - self.speed_V0[-1] * self.time_step,self.d1 + self.d/2 - (self.L + (FinalLength - start_length)) - 1)
                current_length = abs((current_pos_x - current_pos_x1))
                Effort += self.roughness(Effort,0.03)
                Moment += self.roughness(Moment,0.03)
                Power += self.roughness(Power,0.03)
                current_time += self.time_step
                self._update_logs(time=round(current_time,2), 
                              gap=round(self.gap_log[-1],2), 
                              speed_V=round(self.speed_V[-1],2), 
                              temp=round(GenTemp,2), 
                              pyrometr_1=round(self.TempV,2),
                              pyrometr_2=round(self.TempV,2), 
                              pos_x=round(current_pos_x,2), 
                              pos_x1=round(current_pos_x1,2), 
                              speed_V0=round(self.speed_V0[-1],2), 
                              speed_V1=round(self.speed_V1[-1],2), 
                              length=round(current_length,2),
                              effort=round(Effort/1000,2),
                              moment=round(Moment/1000,2),
                              power= round(Power/1000,2),
                              LeftCap=self.LeftCap[-1],
                              RightCap=self.RightCap[-1],
                              Gap_feedback = self.Gap_feedbackLog[-1],
                              Speed_V_feedback = self.Speed_V_feedbackLog[-1]
                              )   
        pass

    def _simulate_exit_from_rolls(self):
        "Симуляция дохода сляба до концевика"
        Speed_V_flag = self.Speed_V_feedbackLog[-1]
        current_time = self.time_log[-1]
        current_temp = self.temperature_log[-1]
        LeftCap = self.LeftCap[-1]
        RightCap = self.RightCap[-1]
        #1.Рассчет падения температуры  
        distance_to_cover = (self.d/2 + self.d2) - self.x_log[-1]
        time_first_cycle = distance_to_cover / self.speed_V1[-1]
        time_brake_speed = self.speed_V[-1] / self.accel
        time_brake_V0 = self.speed_V0[-1] / self.accel  
        time_brake_V1 = self.speed_V1[-1] / self.accel
        time_second_cycle = max(time_brake_speed, time_brake_V0, time_brake_V1)
        total_time = time_first_cycle + time_second_cycle + self.PauseBIter
        final_temp = current_temp - 100
        temp_drop_per_ms = ((current_temp - final_temp) / total_time) * self.time_step
        #2.Доход сляба до конечного концевика
        if self.Dir_of_rot == 0:
            while self.x_log[-1] < self.d1 + self.d2 + self.d :
                x = min(self.x_log[-1] + self.speed_V1[-1] * self.time_step,self.d1 + self.d2 + self.d)
                x1 = min(self.x1_log[-1] + self.speed_V1[-1] * self.time_step,self.d1 + self.d2 + self.d - self.length_log[-1])
                if x == self.d1 + self.d2 + self.d:
                    RightCap = 1
                current_temp -= temp_drop_per_ms
                current_time += self.time_step
                self._update_logs(time=round(current_time,2), 
                                gap=round(self.gap_log[-1],2), 
                                speed_V=round(self.speed_V[-1],2), 
                                temp=round(current_temp,2), 
                                pyrometr_1=round(self.TempV,2),
                                pyrometr_2=round(self.TempV,2), 
                                pos_x=round(x,2), 
                                pos_x1=round(x1,2), 
                                speed_V0=round(self.speed_V0[-1],2), 
                                speed_V1=round(self.speed_V1[-1],2), 
                                length=round(self.length_log[-1],2),
                                effort=0,
                                moment=0,
                                power=0,
                                LeftCap=LeftCap,
                                RightCap=RightCap,
                                Gap_feedback = self.Gap_feedbackLog[-1],
                                Speed_V_feedback = self.Speed_V_feedbackLog[-1])
        else:
            while self.x1_log[-1] > 0:
                x1 = max(self.x1_log[-1] - self.speed_V0[-1] * self.time_step,0)
                x = max(self.x_log[-1] - self.speed_V0[-1] * self.time_step,self.length_log[-1])
                if x1 == 0:
                    LeftCap = 1
                current_temp -= temp_drop_per_ms
                current_time += self.time_step
                self._update_logs(time=round(current_time,2), 
                    gap=round(self.gap_log[-1],2), 
                    speed_V=round(self.speed_V[-1],2), 
                    temp=round(current_temp,2), 
                    pyrometr_1=round(self.TempV,2),
                    pyrometr_2=round(self.TempV,2), 
                    pos_x=round(x,2), 
                    pos_x1=round(x1,2), 
                    speed_V0=round(self.speed_V0[-1],2), 
                    speed_V1=round(self.speed_V1[-1],2), 
                    length=round(self.length_log[-1],2),
                    effort=0,
                    moment=0,
                    power=0,
                    LeftCap=LeftCap,
                    RightCap=RightCap,
                    Gap_feedback = self.Gap_feedbackLog[-1],
                    Speed_V_feedback = self.Speed_V_feedbackLog[-1])
                
        #3.Замедление рольгангов и валков до 0 скорости
        current_speed = self.speed_V[-1]
        current_V0 = self.speed_V0[-1]
        current_V1 = self.speed_V1[-1]
        while current_speed > 0 or current_V0 > 0 or current_V1 > 0:
            current_speed = max(current_speed - self.accel * self.time_step,0)
            current_V0 = max(current_V0 - self.accel * self.time_step,0)
            current_V1 = max(current_V1 - self.accel * self.time_step,0)
            if current_speed != self.V_Valk_Per:
                Speed_V_flag = 0
            current_temp -= temp_drop_per_ms
            current_time += self.time_step
            self._update_logs(time=round(current_time,2),
                              gap=round(self.gap_log[-1],2),
                              speed_V=round(current_speed,2),
                              temp=round(current_temp,2),
                              pyrometr_1=round(self.TempV,2),
                              pyrometr_2=round(self.TempV,2),
                              pos_x=round(self.x_log[-1],2),
                              pos_x1= round(self.x1_log[-1],2),
                              speed_V0=round(current_V0,2),
                              speed_V1=round(current_V1,2),
                              length=round(self.length_log[-1],2),
                              effort=0,
                              moment=0,
                              power=0,
                              LeftCap=self.LeftCap[-1],
                              RightCap=self.RightCap[-1],
                              Gap_feedback = self.Gap_feedbackLog[-1],
                              Speed_V_feedback = Speed_V_flag)
    pass

    # def alarm_stop(self):
    #     "Аварийный останов"
    #     while self.speed_V[-1] > 0 or self.speed_V0[-1] > 0 or self.speed_V1[-1] > 0 or self.CurrentS[-1] != self.StartS:
    #         current_speed = max(current_speed - self.accel * self.time_step,0)
    #         current_V0 = max(current_V0 - self.accel * self.time_step,0)
    #         current_V1 = max(current_V1 - self.accel * self.time_step,0)
    #         currentS = min(currentS + self.VS,self.StartS)       


def start(Num_of_revol_rolls,Roll_pos,Num_of_revol_0rollg,Num_of_revol_1rollg,Dir_of_rot_valk,Dir_of_rot_L_rolg,Mode,Dir_of_rot_R_rolg,Speed_of_diverg,Length_slab,Width_slab,Thikness_slab,Temperature_slab,Material_slab,Material_roll):
    # Параметры прокатки
    L = Length_slab  # начальная длина сляба, мм
    b = Width_slab   # ширина сляба, мм
    h_0 = Thikness_slab  # начальная толщина, мм
    StartTemp = Temperature_slab  # начальная температура, °C
    StartS = 200 # начальный раствор валков
    DV = 300   # диаметр валков, мм
    DR = 100  # диаметр рольгангов, мм
    MV = 'Steel'  # материал валков
    MS = 'Carbon Steel'  # материал сляба
    OutTemp = 28  # температура валков, °C
    PauseBIter = 5  # пауза между пропусками, с
    SteelGrade = 'Ст3сп' #Марка стали
    
    S = Roll_pos  #Расхождение валков, мм
    V0 = (2 * pi * DR/2 * Num_of_revol_0rollg) / 60  # начальная скорость(мм/с)
    V1 = (2 * pi * DR/2 * Num_of_revol_1rollg) / 60  # конечная скорость(мм/с) 
    V_Valk_Per =  (2 * pi * DV/2 * Num_of_revol_rolls) / 60 # Скорость валков (мм/c)
    Dir_of_rot_valk = Dir_of_rot_valk #Направление вращения валков
    Dir_of_rot_L_rolg = Dir_of_rot_L_rolg #Направление вращения левых рольгангов
    Mode = Mode #Отправка на частотник флага ручного режима
    Dir_of_rot_R_rolg = Dir_of_rot_R_rolg #Направление вращения правых рольгангов
    
    simulator = RollingMillSimulator(
        L=L,b=b,h_0=h_0,S=S,StartTemp=StartTemp,
        DV=DV,MV=MV,MS=MS,OutTemp=OutTemp,DR=DR,SteelGrade=SteelGrade,
        V0=V0,V1=V1,PauseBIter=PauseBIter,VS=Speed_of_diverg,Dir_of_rot = Dir_of_rot_valk,
        d1=2200.0,d2=2200.0,d=220.0, V_Valk_Per=V_Valk_Per,StartS=StartS,
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
    return {'Time':simulator.time_log,
            'Pyro1':simulator.temperature_log,
            'Pyro2':simulator.temperature_log,
            'Pressure':simulator.effort_log,
            'Gap':simulator.gap_log,
            'VRPM':simulator.speed_V,
            'V0RPM':simulator.speed_V0,
            'V1RPM':simulator.speed_V1,
            'StartCap':simulator.LeftCap,
            'EndCap':simulator.RightCap,
            'Moment':simulator.moment_log,
            'Power':simulator.power_log,
            'Gap_feedback':simulator.Gap_feedbackLog,
            'Speed_feedback':simulator.Speed_V_feedbackLog}

if __name__ == "__main__":
    start(Num_of_revol_rolls = 10,
          Roll_pos = 56,
          Num_of_revol_0rollg = 38,
          Num_of_revol_1rollg = 38,
          Dir_of_rot_valk = 0,
          Dir_of_rot_L_rolg = 0,
          Mode = 0,
          Dir_of_rot_R_rolg = 0,
          Speed_of_diverg = 100)
