def _simulate_approach_to_rolls(self, n, filename="rolling_log.txt"):
    """Симуляция подхода сляба к валкам с линейным падением температуры."""
    
    # Начальные параметры
    initial_temp = self.StartTemp if n == 0 else self.temp_after_prev_pass
    final_temp = initial_temp - 50  # Пример: падение на 50°C за весь процесс
    
    # Рассчитываем общее время всех процессов
    time_gap = abs(self.S[n] - self.CurrentS) / self.VS  # Время выставления зазора
    time_accel = self.V_Valk_Per[n] / self.accel        # Время разгона валков
    time_move = self.d1 / (self.V0[n] * 1000)           # Время движения сляба
    total_time = time_gap + time_accel + time_move
    
    # Шаг падения температуры в °C/сек (линейная интерполяция)
    temp_drop_per_sec = (initial_temp - final_temp) / total_time

    # Открываем файл для записи
    with open(filename, 'w') as f:
        f.write("Time(s)\tGap(mm)\tSpeed(rpm)\tTemp(C)\tPosition(mm)\n")
        
        current_time = 0
        CurrentS = self.CurrentS
        current_temp = initial_temp
        current_speed = 0
        current_pos = 0

        # 1. Процесс выставления валков
        while abs(CurrentS - self.S[n]) > 0.1:
            # Обновляем зазор
            if CurrentS < self.S[n]:
                CurrentS = min(CurrentS + self.VS, self.S[n])
            else:
                CurrentS = max(CurrentS - self.VS, self.S[n])
            
            # Падение температуры (линейное)
            current_temp = initial_temp - (temp_drop_per_sec * current_time)
            
            # Запись в лог
            f.write(f"{current_time:.1f}\t{CurrentS:.1f}\t0\t{current_temp:.1f}\t0\n")
            current_time += 1

        # 2. Процесс разгона валков
        while current_speed < self.V_Valk_Per[n]:
            current_speed = min(current_speed + self.accel, self.V_Valk_Per[n])
            
            # Падение температуры (продолжаем линейное)
            current_temp = initial_temp - (temp_drop_per_sec * current_time)
            
            f.write(f"{current_time:.1f}\t{CurrentS:.1f}\t{current_speed:.1f}\t{current_temp:.1f}\t0\n")
            current_time += 1

        # 3. Процесс движения сляба
        while current_pos < self.d1:
            current_pos = min(current_pos + (self.V0[n] * 1000), self.d1)
            
            # Падение температуры (финальная часть)
            current_temp = initial_temp - (temp_drop_per_sec * current_time)
            
            f.write(f"{current_time:.1f}\t{CurrentS:.1f}\t{current_speed:.1f}\t{current_temp:.1f}\t{current_pos:.1f}\n")
            current_time += 1

    pass