 def _simulate_approach_to_rolls(self):
        "Проход сляба к валкам"
        Gap_flag = self.Gap_feedbackLog[-1]
        Speed_V_flag = self.Speed_V_feedbackLog[-1]
        current_pos_x = self.x_log[-1]
        current_pos_x1 = self.x1_log[-1]
        current_time = self.time_log[-1] 
        CurrentS = self.gap_log[-1] 
        current_temp = self.temperature_log[-1]
        current_speed = self.speed_V[-1] 
        speed_V0 = self.speed_V0[-1] 
        speed_V1 = self.speed_V1[-1] 
        current_length = self.length_log[-1] 
        
        target_gap = self.S
        gap_change_per_ms = self.VS * self.time_step 
        time_gap = (abs(self.S - CurrentS)) / (self.VS)
        time_accel = ((self.V_Valk_Per) / (self.accel))
        time_accel_V0 = ((self.V0) / (self.accel))
        S1 = ((self.accel) * time_accel_V0**2)/2
        S2 = (self.d1 - self.L) - S1
        time_max_speed = (S2 / (self.V0))
        time_move = (time_accel_V0 + time_max_speed)
        total_time = time_gap + time_accel + time_move
        final_temp = current_temp - 50
        temp_drop_per_ms = ((current_temp - final_temp) / total_time) * self.time_step

        if self.Dir_of_rot == 0:
            target_SpeedV1 = round(self.V0 * (self.h_0 / self.h_1),2)
            self.V1 = target_SpeedV1
        else:
            target_speed_V0 = round(self.V1 * (self.h_0 / self.h_1),2)
            self.V0 = target_speed_V0
        # Фаза 1: Выставление зазора валков
        while CurrentS != target_gap:
            if current_pos_x == 0:
                Left_Cap = 1
            else:
                Left_Cap = 0
            if current_pos_x1 == self.d1+self.d2+self.d:
                cur_Right_Cap = 1
            else:
                cur_Right_Cap = 0
            CurrentS = min(CurrentS + gap_change_per_ms, target_gap) if CurrentS < target_gap else max(CurrentS - gap_change_per_ms, target_gap)
            if CurrentS == self.S:
                Gap_flag = 1
            else:
                Gap_flag = 0
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            Pyro1 = self.TempV + self.roughness(self.TempV,0.07)
            Pyro2 = self.TempV + self.roughness(self.TempV,0.07)
            current_time += self.time_step
            self._update_logs(time=round(current_time,2), 
                              gap=round(CurrentS,2), 
                              speed_V=0, 
                              temp=round(current_temp,2),
                              pyrometr_1=round(Pyro1,2),
                              pyrometr_2=round(Pyro2,2), 
                              pos_x=round(self.x_log[-1],2),
                              pos_x1=round(self.x1_log[-1]), 
                              speed_V0=round(speed_V0,2), 
                              speed_V1=round(speed_V1,2), 
                              length=round(current_length,2),
                              effort=0,
                              moment=0,
                              power=0,
                              LeftCap = Left_Cap,
                              RightCap = cur_Right_Cap,
                              Gap_feedback = Gap_flag,
                              Speed_V_feedback = Speed_V_flag) 

        # Фаза 2: Разгон валков
        while current_speed != self.V_Valk_Per:
            current_speed = min(current_speed + self.accel * self.time_step,self.V_Valk_Per) 
            current_time += self.time_step
            current_temp = max(current_temp - temp_drop_per_ms, final_temp)
            Pyro1 = self.TempV + self.roughness(self.TempV,0.07)
            Pyro2 = self.TempV + self.roughness(self.TempV,0.07)
            if current_speed == self.V_Valk_Per:
                Speed_V_flag = 1
            self._update_logs(time=round(current_time,2), 
                              gap=round(CurrentS,2), 
                              speed_V=round(current_speed,2), 
                              temp=round(current_temp,2), 
                              pyrometr_1=round(Pyro1,2), 
                              pyrometr_2=round(Pyro2,2),
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
            while current_pos_x1 != self.d1 + self.d/2:
                current_temp = max(current_temp - temp_drop_per_ms, final_temp)
                if current_pos_x > 0:
                    Left_Cap = 0
                speed_V0 = min(speed_V0 + self.accel * self.time_step, self.V0)
                speed_V1 = min(speed_V1 + self.accel * self.time_step, target_SpeedV1)
                current_pos_x = min(current_pos_x + speed_V0 * self.time_step, self.d1 + self.d/2 - self.length_log[-1]) 
                current_pos_x1 = min(current_pos_x1 + speed_V0 * self.time_step, self.d1 + self.d/2)
                if current_pos_x1 >= 2000 and current_pos_x <= 2000:
                    Pyro1 = current_temp
                else:
                    Pyro1 = self.TempV + self.roughness(self.TempV,0.07)
                Pyro2 = self.TempV + self.roughness(self.TempV,0.07)
                current_length = self.length_log[-1]
                current_time += self.time_step
                self._update_logs(time=round(current_time,2), 
                                gap=round(CurrentS,2), 
                                speed_V=round(current_speed,2), 
                                temp=round(current_temp,2), 
                                pyrometr_1=round(Pyro1,2),
                                pyrometr_2=round(Pyro2,2), 
                                pos_x=round(current_pos_x,2),
                                pos_x1=round(current_pos_x1,2), 
                                speed_V0=round(speed_V0,2), 
                                speed_V1=round(speed_V1,2), 
                                length=round(current_length,2),
                                effort=0,
                                moment=0,
                                power=0,
                                LeftCap=Left_Cap,
                                RightCap=self.RightCap[-1],
                                Gap_feedback = Gap_flag,
                                Speed_V_feedback = Speed_V_flag)
        else:
            while current_pos_x != self.d1 + self.d/2:
                current_temp = max(current_temp - temp_drop_per_ms, final_temp)
                if current_pos_x < self.d1+self.d2+self.d: 
                    cur_RightCap = 0
                speed_V0 = min(speed_V0 + self.accel * self.time_step, target_speed_V0)
                speed_V1 = min(speed_V1 + self.accel * self.time_step, self.V1)
                current_pos_x = max(current_pos_x - speed_V1 * self.time_step, self.d1 + self.d/2)
                current_pos_x1 = max(current_pos_x1 - speed_V1 * self.time_step, self.d1+self.d/2 + self.length_log[-1])
                if current_pos_x <= 2700 and current_pos_x1 >= 2700:
                    Pyro2 = current_temp
                else:
                    Pyro2 = self.TempV + self.roughness(self.TempV,0.07)
                Pyro1 = self.TempV + self.roughness(self.TempV,0.07)
                current_time += self.time_step
                self._update_logs(time=round(current_time,2), 
                                gap=round(CurrentS,2), 
                                speed_V=round(current_speed,2), 
                                temp=round(current_temp,2), 
                                pyrometr_1=round(Pyro1,2),
                                pyrometr_2=round(Pyro2,2), 
                                pos_x=round(current_pos_x,2),
                                pos_x1=round(current_pos_x1,2), 
                                speed_V0=round(speed_V0,2), 
                                speed_V1=round(speed_V1,2), 
                                length=round(current_length,2),
                                effort=0,
                                moment=0,
                                power=0,
                                LeftCap=self.LeftCap[-1],
                                RightCap=cur_RightCap,
                                Gap_feedback = Gap_flag,
                                Speed_V_feedback = Speed_V_flag)