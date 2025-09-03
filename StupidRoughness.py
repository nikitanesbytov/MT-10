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