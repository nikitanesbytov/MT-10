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
        self.x_log = [self.L]#Лог начальной координаты сляба
        self.x1_log = [0]
        self.pyrometr_1 = [self.TempV]#Лог пирометра перед валками
        self.pyrometr_2 = [self.TempV]#Лог пирометра после валков
        self.gap_log = [0]#Лог раствора валков(мм)
        self.speed_V = [0]#Лог скорости варщения валков(об/c)
        self.speed_V0 = [0]#Лог скорости вращения рольгангов до валков(об/c)
        self.speed_V1 = [0]#Лог скорости вращения рольгангов после валков(об/c)
        self.time_step = 0.1#Шаг времени
        #Лог - это ныншнее значение представленных ТПов
        
    def linear_interpolation(self,start, end, steps) -> float:
        "Линейная интерполяция, возвращающая шаг смещения величины"
        if steps <= 0:
            raise ValueError("Количество шагов должно быть положительным")
        step_size = (end - start) / steps
        return step_size
    
    def save_logs_to_file(self, filename="rolling_log.txt"):
        """Сохраняет логи в файл в виде отформатированной таблицы"""
        with open(filename, 'w') as f:
            col_widths = {
                'Time': 8,
                'Gap': 8,
                'Speed_V': 8,
                'Pyro1': 8,
                'Pyro2': 8,
                'Temp': 8,
                'Pos_x': 8,
                'Pos_x1': 8,
                'Speed_V0': 8,
                'Speed_V1': 8,
                'Length': 8
            }
            # Заголовки таблицы
            headers = [
                f"{'Time(s)':<{col_widths['Time']}}",
                f"{'Gap(mm)':<{col_widths['Gap']}}",
                f"{'Speed_V':<{col_widths['Speed_V']}}",
                f"{'Speed_V0':<{col_widths['Speed_V0']}}",
                f"{'Speed_V1':<{col_widths['Speed_V1']}}",
                f"{'Pyro1':<{col_widths['Pyro1']}}",
                f"{'Pyro2':<{col_widths['Pyro2']}}",
                f"{'Temp(C)':<{col_widths['Temp']}}",
                f"{'Pos_x(mm)':<{col_widths['Pos_x']}}",
                f"{'Pos_x1(mm)':<{col_widths['Pos_x1']}}",
                f"{'Length':<{col_widths['Length']}}"
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
                    f"{self.pyrometr_1[i]:<{col_widths['Pyro1']}.1f}",
                    f"{self.pyrometr_2[i]:<{col_widths['Pyro2']}.1f}",
                    f"{self.temperature_log[i]:<{col_widths['Temp']}.1f}",
                    f"{self.x_log[i]:<{col_widths['Pos_x']}.1f}",
                    f"{self.x1_log[i]:<{col_widths['Pos_x1']}.1f}",
                    f"{self.length_log[i]:<{col_widths['Length']}.1f}"
                ]
                f.write(" | ".join(row) + "\n")
    
    def _update_logs(self, time, gap, speed_V, temp, pyrometr_1,pyrometr_2, pos_x, pos_x1, speed_V0, speed_V1, length):
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

    def _simulate_approach_to_rolls(self, n):
        "Проход сляба к валкам (чистая версия без работы с файлами)"
        # Инициализация параметров
        current_pos_x = self.x_log[-1]
        current_pos_x1 = self.x1_log[-1]
        current_time = self.time_log[-1] if self.time_log else 0
        CurrentS = self.CurrentS[-1] 
        initial_temp = self.StartTemp if n == 0 else (self.temperature_log[-1] if self.temperature_log else self.StartTemp)
        current_temp = initial_temp
        target_gap = self.S[n]
        
        gap_change_per_ms = self.VS * self.time_step 
        start_time = self.time_log[-1]
        
       #Расчёт временных параметров (в секундах)
        time_gap = (abs(self.S[n] - CurrentS)) / (self.VS)
        time_accel = ((self.V_Valk_Per[n]) / (self.accel))
        time_accel_V0 = ((self.V0[n]) / (self.accel))
        S1 = ((self.accel) * time_accel_V0**2)/2
        S2 = (self.d1 - self.L) - S1
        time_max_speed = (S2 / (self.V0[n]))
        time_move = (time_accel_V0 + time_max_speed)
        total_time = time_gap + time_accel + time_move

        final_temp = initial_temp - 100
        temp_drop_per_ms = ((initial_temp - final_temp) / total_time) * self.time_step
        
        # Инициализация скоростей
        current_speed = self.speed_V[-1] if self.speed_V else 0
        speed_V0 = self.speed_V0[-1] if self.speed_V0 else 0
        speed_V1 = self.speed_V1[-1] if self.speed_V1 else 0
        current_length = self.length_log[-1] if self.length_log else 0
        
        # Фаза 1: Выставление зазора валков
        while CurrentS != target_gap:
            CurrentS = min(CurrentS + gap_change_per_ms, target_gap) if CurrentS < target_gap else max(CurrentS - gap_change_per_ms, target_gap)
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            self._update_logs(current_time, CurrentS, 0, current_temp,self.TempV,self.TempV, self.x_log[-1],0, speed_V0, speed_V1, current_length)

        # Фаза 2: Разгон валков
        while current_speed != V_Valk_Per[n]:
            current_speed = current_speed + self.accel * self.time_step
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            self._update_logs(current_time, CurrentS, current_speed, current_temp, self.TempV, self.TempV,self.x_log[-1],0, 0, 0, current_length)
        
        # Фаза 3: Движение сляба
        while  current_pos_x != self.d1:
            speed_V0 = min(speed_V0 + self.accel * self.time_step, self.V0[n])
            speed_V1 = min(speed_V1 + self.accel * self.time_step, self.V1[n])
            current_pos_x = min(current_pos_x + speed_V0 * self.time_step, self.d1)
            current_pos_x1 = min(current_pos_x1 + speed_V0 * self.time_step, self.d1-self.L)
            current_length = self.length_log[-1] if self.length_log else 0
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            self._update_logs(current_time, CurrentS, current_speed, current_temp, self.TempV,self.TempV, current_pos_x,current_pos_x1, speed_V0, speed_V1, current_length)
    
    def _simulate_rolling_pass(self,n):
        "Симуляция прохода сляба через валки"
        start_time = self.time_log[-1]
        current_time = self.time_log[-1]
        
        #1.Рассчет изменения длины
        h_0 = self.h_0 if n == 0 else self.height_log[-1]
        h_1 = self.S[n] 
        RelDef = self.RelDef(h_0,h_1)
        start_length = self.length_log[-1]
        FinalLength = self.FinalLength(h_0,h_1,self.L if n == 0 else self.length_log[-1])
        rolling_time = abs(((start_length + FinalLength)/2) / ((self.V0[n] + self.V1[n])/2))
        def_for_sek = self.linear_interpolation(start_length,FinalLength,rolling_time) #Изменение длины за секунду
        
        #2.Рассчет усилия,момента и мощности и проверка этих показателей с максимальными
        ContactArcLen = self.ContactArcLen(self.DV,self.S[n])
        DefResistance = self.DefResistance(RelDef,ContactArcLen,self.speed_V[-1],)
        AvrgPressure = self.AvrgPressure(DefResistance,ContactArcLen,h_0,h_1)
        Effort = self.Effort(ContactArcLen,AvrgPressure,self.b)
        Moment = self.Moment(ContactArcLen,h_0,h_1,Effort)
        Power = self.Power(Moment,self.speed_V[n]*2*pi)
        
        #3.Рассчет падения температуры от пластической деформации и контакта с валками
        TempDrDConRoll = self.TempDrDConRoll(self.DV,h_0,h_1)
        TempDrPlDeform = self.TempDrPlDeform(RelDef,h_0,h_1)
        GenTempDrop = self.GenTemp(self.temperature_log[-1],TempDrDConRoll,TempDrPlDeform,TempDrBPass=0) 
            

        pass


    # def simulate_process(self):
    #     #Запуск симуляции   
        
    # def _simulate_exit_from_rolls(self):
    #     #1.Доход сляба до конечного концевика

    #     #2.Замедление рольгангов и валков до 0 скорости

    #     #3.Рассчет падения температуры

    # def _simulate_pause_between_passes(self):
    #     #1.Выдержка паузы и падение температуры во время этой паузы

if __name__ == "__main__":
    # Параметры прокатки
    L = 200  # начальная длина сляба, мм
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
    V0 = [36, 10, 0.7, 0.7, 0.7]  # начальная скорость(мм/с)
    V1 = [36, 10, 0.7, 0.7, 0.7]  # конечная скорость(мм/с)
    PauseBIter = 5  # пауза между пропусками, с
    V_Valk_Per = [36, 0.7, 0.7, 0.7, 0.7] # установка скоростей валков для каждого пропуска (мм/с)
    SteelGrade = "Ст3сп" #Марка стали
   
    simulator = RollingMillSimulator(
        L=L,b=b,h_0=h_0,S=S,StartTemp=StartTemp,
        DV=DV,MV=MV,MS=MS,OutTemp=OutTemp,DR=DR,SteelGrade=SteelGrade,
        n=n, V0=V0,V1=V1,PauseBIter=PauseBIter,
        d1=1500,d2=1500,V_Valk_Per=V_Valk_Per,StartS=StartS,
    )

    # Запуск симуляции
    simulator._simulate_approach_to_rolls(0)
    # simulator._simulate_rolling_pass(0) 
    
    #Создание лога
    simulator.save_logs_to_file("my_logs.txt")