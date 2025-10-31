from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import threading
import time
import struct
from datetime import datetime
import psycopg2
import RollingMillSimulator
import sys

conn = psycopg2.connect(
    host="localhost",
    database="test_bd_1",  
    user="postgres",          
    password="postgres",      
    port="5432"
)

cur = conn.cursor()

def float_to_regs(value):
    """Преобразует float в два WORD регистра (big-endian)"""
    b = struct.pack('>f', float(value))
    return [int.from_bytes(b[:2], 'big'), int.from_bytes(b[2:], 'big')]

def regs_to_float(reg1, reg2):
    """Преобразует два WORD регистра обратно в float (big-endian)"""
    try:
        b1 = (reg1 >> 8) & 0xFF
        b2 = reg1 & 0xFF
        b3 = (reg2 >> 8) & 0xFF
        b4 = reg2 & 0xFF
        return struct.unpack('>f', bytes([b1, b2, b3, b4]))[0]
    except:
        return 0.0

class ModbusServer:
    def __init__(self):
        total_registers = 31
        initial_values = [0] * total_registers
        self.hr_data_combined = ModbusSequentialDataBlock(1, initial_values)
        store = ModbusSlaveContext(hr=self.hr_data_combined)
        self.context = ModbusServerContext(slaves=store, single=True)
        self.stop_monitoring = False
        self.simulation_running = False
        self.simulator = None
        self.initialized = False
        self.current_step = 0  # 0 - ready for Gap_Valk, 1 - ready for Accel_Valk, 2 - ready for Approaching
        self.writing_to_registers = False
        self.step_complete = False
        self.current_data = None

        # Try to initialize immediately
        try:
            self.start_init_from_registers()
            if self.initialized:
                self.log_message("Модель успешно инициализирована при запуске")
        except Exception as e:
            self.log_message(f"Ошибка автоматической инициализации: {e}")

    def log_message(self, message):
        """Запись сообщения в консоль"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] {message}")

    def update_simulation_registers(self, sim_data, idx):
        keys = [
            'Pyro1', 'Pyro2', 'Pressure', 'Gap', 'VRPM', 'V0RPM', 'V1RPM',
            'Moment', 'Power'
        ]
        regs = []
        for k in keys:
            v = sim_data[k][idx] if isinstance(sim_data[k], list) else sim_data[k]
            regs.extend(float_to_regs(v))
        
        flags = 0
        StartCap_val = sim_data['StartCap'][idx] if isinstance(sim_data['StartCap'], list) else sim_data['StartCap']
        EndCap_val = sim_data['EndCap'][idx] if isinstance(sim_data['EndCap'], list) else sim_data['EndCap']
        Gap_feedback_val = sim_data['Gap_feedback'][idx] if isinstance(sim_data['Gap_feedback'], list) else sim_data['Gap_feedback']
        Speed_feedback_val = sim_data['Speed_feedback'][idx] if isinstance(sim_data['Speed_feedback'], list) else sim_data['Speed_feedback']
        
        if StartCap_val:
            flags |= 0x01
        if EndCap_val:
            flags |= 0x02
        if Gap_feedback_val:
            flags |= 0x04
        if Speed_feedback_val:
            flags |= 0x08
        
        self.hr_data_combined.setValues(12, regs)  
        self.hr_data_combined.setValues(30, [flags])  

        # После записи в регистры:
        with open("serv.txt", "a") as f:
            f.write(f"Step {idx}: ")
            for k in keys:
                v = sim_data[k][idx] if isinstance(sim_data[k], list) else sim_data[k]
                f.write(f"{k}={v} ")
            f.write("\n")

    def run_simulation_and_update(self, **kwargs):
        self.simulation_running = True
        self.log_message("Запуск симуляции...")
        from RollingMillSimulator import RollingMillSimulator  # Импортируем здесь, чтобы избежать циклических импортов

        # 1. Инициализация прокатки из SQL
        simulator = RollingMillSimulator(
            L=0, b=0, h_0=0, S=0, StartTemp=0,
            DV=0, MV=0, MS=0, OutTemp=0, DR=0, SteelGrade=0,
            V0=0, V1=0, VS=0, Dir_of_rot=0,
            d1=0, d2=0, d=0, V_Valk_Per=0, StartS=0
        )
        kwargs['Material_slab'] = kwargs['Material_slab'].replace(' ', '')
        simulator.Init(
            Length_slab=kwargs['Length_slab'],
            Width_slab=kwargs['Width_slab'],
            Thikness_slab=kwargs['Thikness_slab'],
            Temperature_slab=kwargs['Temperature_slab'],
            Material_slab=kwargs['Material_slab'],
            Diametr_roll=kwargs.get('Diametr_roll', 300),
            Material_roll=kwargs['Material_roll']
        )

        # Логируем уставки для Iteration
        self.log_message("Параметры Iteration:")
        for k in [
            'Num_of_revol_rolls', 'Roll_pos', 'Num_of_revol_0rollg', 'Num_of_revol_1rollg',
            'Speed_of_diverg', 'Dir_of_rot_valk', 'Dir_of_rot_L_rolg', 'Mode', 'Dir_of_rot_R_rolg'
        ]:
            self.log_message(f"  {k}: {kwargs[k]}")

        # 2. Запуск симуляции по данным из регистров
        sim_result = simulator.Iteration(
            Num_of_revol_rolls=kwargs['Num_of_revol_rolls'],
            Roll_pos=kwargs['Roll_pos'],
            Num_of_revol_0rollg=kwargs['Num_of_revol_0rollg'],
            Num_of_revol_1rollg=kwargs['Num_of_revol_1rollg'],
            Speed_of_diverg=kwargs['Speed_of_diverg'],
            Dir_of_rot_valk=kwargs['Dir_of_rot_valk'],
            Dir_of_rot_L_rolg=kwargs['Dir_of_rot_L_rolg'],
            Mode=kwargs['Mode'],
            Dir_of_rot_R_rolg=kwargs['Dir_of_rot_R_rolg']
        )
        steps = len(sim_result['Pyro1'])
        self.log_message(f"Симуляция запущена, шагов: {steps}")

        for i in range(steps):
            if self.stop_monitoring:
                break
            self.update_simulation_registers(sim_result, i)
            time.sleep(0.1)

        self.log_message("Симуляция завершена")
        self.simulation_running = False  # Сразу освобождаем сервер для новых команд

    def start_simulator_from_registers(self):
        """Запуск симуляции на основе текущих значений регистров"""
        if self.simulation_running:
            self.log_message("Симуляция уже выполняется, новый запуск невозможен!")
            return

        if not self.initialized:
            self.log_message("Модель не инициализирована! Сначала выполните Init.")
            return

        regs = self.hr_data_combined.getValues(1, 11)
        reg8 = regs[8]

        # Новая карта битов для reg8
        Dir_of_rot_valk = bool(reg8 & 0x01)       
        Dir_of_rot_rolg = bool(reg8 & 0x02)       
        Mode = bool(reg8 & 0x04)                  # бит 2
        Alarm = bool(reg8 & 0x08)                 # бит 3
        Start = bool(reg8 & 0x10)                 # бит 4
        Start_Gap = bool(reg8 & 0x20)             # бит 5
        Start_Accel = bool(reg8 & 0x40)           # бит 6
        Start_Roll = bool(reg8 & 0x80)            # бит 7

        # Получаем остальные параметры
        Num_of_revol_rolls = regs_to_float(regs[0], regs[1])
        Roll_pos = regs_to_float(regs[2], regs[3])
        Num_of_revol_0rollg = regs_to_float(regs[4], regs[5])
        Num_of_revol_1rollg = regs_to_float(regs[6], regs[7])
        Speed_of_diverg = regs_to_float(regs[9], regs[10])


        # Проверка и выполнение Gap_Valk
        if Start_Gap:
            if Roll_pos <= 0:
                self.log_message("Ошибка: не установлено значение Roll_pos")
                return
 
            self.log_message("Выполняется Gap_Valk...",Roll_pos)
            self.simulator._Gap_Valk_(Roll_pos=Roll_pos, Dir_of_rot_valk=Dir_of_rot_valk)
            self.update_simulation_registers_from_simulator()
            self.simulator.save_logs_to_file("serv.txt")
            self.log_message("Выполнился Gap_Valk...")
            return  # Выходим и ждем следующего вызова
            
        # Проверка и выполнение Accel_Valk    
        if Start_Accel:
            if Num_of_revol_rolls <= 0:
                self.log_message("Ошибка: не установлено значение Num_of_revol_rolls")
                return
            if not self.simulator.Gap_feedbackLog[-1]:
                self.log_message("Ошибка: Gap_Valk не завершил работу")
                return
                
            self.log_message("Выполняется Accel_Valk...")
            self.simulator._Accel_Valk_(Num_of_revol_rolls, Dir_of_rot_rolg, Dir_of_rot_rolg)
            self.update_simulation_registers_from_simulator()
            self.simulator.save_logs_to_file("serv.txt")
            self.log_message("Выполнился Accel_Valk...")
            return  # Выходим и ждем следующего вызова
            
        # Проверка и выполнение Approaching_to_Roll    
        if Start_Roll:
            if Num_of_revol_0rollg <= 0 or Num_of_revol_1rollg <= 0:
                self.log_message("Ошибка: не установлены скорости рольгангов")
                return
            if not self.simulator.Speed_V_feedbackLog[-1]:
                self.log_message("Ошибка: Accel_Valk не завершил работу")
                return
                
            self.log_message("Выполняется Approaching_to_Roll...")
            sim_result = self.simulator._Approching_to_Roll_(
                Dir_of_rot_valk,
                Num_of_revol_0rollg,
                Num_of_revol_1rollg,
                Dir_of_rot_rolg,
                Dir_of_rot_rolg
            )
            
            if sim_result:
                pyrometr_1, pyrometr_2, power_log, gap_log, speed_V, speed_V0, speed_V1, \
                moment_log, effort_log, LeftCap, RightCap, Gap_feedback, Speed_feedback = sim_result
                
                sim_data = {
                    'Pyro1': pyrometr_1[-1],
                    'Pyro2': pyrometr_2[-1],
                    'Power': power_log[-1],
                    'Gap': gap_log[-1],
                    'VRPM': speed_V[-1],
                    'V0RPM': speed_V0[-1],
                    'V1RPM': speed_V1[-1],
                    'Moment': moment_log[-1],
                    'Pressure': effort_log[-1],
                    'StartCap': LeftCap[-1],
                    'EndCap': RightCap[-1],
                    'Gap_feedback': Gap_feedback[-1],
                    'Speed_feedback': Speed_feedback[-1]
                }
                self.update_simulation_registers(sim_data, -1)
            return 

    def update_simulation_registers_from_simulator(self):
        """Вспомогательный метод для обновления регистров текущими значениями симулятора"""
        sim_data = {
            'Pyro1': self.simulator.pyrometr_1[-1],
            'Pyro2': self.simulator.pyrometr_2[-1],
            'Power': self.simulator.power_log[-1],
            'Gap': self.simulator.gap_log[-1],
            'VRPM': self.simulator.speed_V[-1],
            'V0RPM': self.simulator.speed_V0[-1],
            'V1RPM': self.simulator.speed_V1[-1],
            'Moment': self.simulator.moment_log[-1],
            'Pressure': self.simulator.effort_log[-1],
            'StartCap': self.simulator.LeftCap[-1],
            'EndCap': self.simulator.RightCap[-1],
            'Gap_feedback': self.simulator.Gap_feedbackLog[-1],
            'Speed_feedback': self.simulator.Speed_V_feedbackLog[-1]
        }
        self.update_simulation_registers(sim_data, -1)

    def start_init_from_registers(self):
        """Инициализация (Init) прокатки из БД по биту и сохранение симулятора в self.simulator"""
        if self.simulation_running:
            self.log_message("Сейчас выполняется симуляция — Init не запускается.")
            return

        try:
            cur.execute("SELECT * FROM slabs ORDER BY id DESC LIMIT 1")
            last_row = cur.fetchone()
            if not last_row:
                self.log_message("Нет записей в таблице slabs для Init.")
                return
            id, Length_slab, Width_slab, Thikness_slab, Temperature_slab, Material_slab, Diametr_roll, Material_roll = last_row

            # Создаём экземпляр симулятора и выполняем Init с данными из БД
            from RollingMillSimulator import RollingMillSimulator
            sim = RollingMillSimulator(
                L=0,b=0,h_0=0,S=0,StartTemp=0,RightStopCap=0,
                DV=0,MV=0,MS=0,OutTemp=0,DR=0,SteelGrade=0,
                V0=0,V1=0,VS=0,Dir_of_rot=0,LeftStopCap=0,
                d1=0,d2=0,d=0, V_Valk_Per=0,StartS=0
            )
            ms_clean = (Material_slab or "").replace(' ', '')
            sim.Init(
                Length_slab=Length_slab,
                Width_slab=Width_slab,
                Thikness_slab=Thikness_slab,
                Temperature_slab=Temperature_slab,
                Material_slab=ms_clean,
                Diametr_roll=Diametr_roll,
                Material_roll=Material_roll
            )

            # Сохраняем симулятор в сервере — для возможного дальнейшего использования
            self.simulator = sim
            self.initialized = True

            # Логируем уставки Init
            self.log_message("Выполнен Init с параметрами из БД:")
            for name, val in [
                ("Length_slab", Length_slab),
                ("Width_slab", Width_slab),
                ("Thikness_slab", Thikness_slab),
                ("Temperature_slab", Temperature_slab),
                ("Material_slab", ms_clean),
                ("Diametr_roll", Diametr_roll),
                ("Material_roll", Material_roll),
            ]:
                self.log_message(f"  {name}: {val}")

        except Exception as e:
            self.log_message(f"Ошибка Init из БД: {e}")

    def run_server(self):
        """Запуск Modbus сервера"""
        self.log_message("Modbus сервер запущен на :55000")
        self.log_message("Для запуска симуляции установите бит Start (0x10) в регистре 8")
        
        try:
            StartTcpServer(context=self.context, address=("192.168.0.99", 55000))
        except Exception as e:
            self.log_message(f"Ошибка сервера: {e}")
        finally:
            self.stop_monitoring = True

def write_data_to_registers(server):
    """Постепенно записывает значения из current_data в регистры 12-30"""
    if not server.current_data:
        return

    # Определяем длину лога (например, по Pyro1)
    steps = len(server.current_data['Pyro1'])
    if not hasattr(server, 'write_idx'):
        server.write_idx = 0

    if server.write_idx < steps:
        server.update_simulation_registers(server.current_data, server.write_idx)
        server.write_idx += 1
    else:
        # После окончания лога можно либо держать последнее значение, либо ничего не делать
        pass

def monitor_registers(server):
    while not server.stop_monitoring:
        try:
            # Если идёт запись — только пишем в регистры, команды не проверяем!
            if server.writing_to_registers:
                write_data_to_registers(server)
                flags = server.hr_data_combined.getValues(30, 1)[0]
                if server.current_step == 0 and (flags & 0x04):  # Gap_feedback
                    server.writing_to_registers = False
                    server.current_step = 1
                    server.write_idx = 0
                elif server.current_step == 1 and (flags & 0x08):  # Speed_feedback
                    server.writing_to_registers = False
                    server.current_step = 2
                    server.write_idx = 0
                elif server.current_step in (2, 3, 4) and server.write_idx >= server.current_steps_total:
                    server.writing_to_registers = False
                    server.current_step += 1
                    server.write_idx = 0
                time.sleep(0.1)
                continue

            # Только если НЕ идёт запись — проверяем команды ПЛК:
            regs = server.hr_data_combined.getValues(1, 31)
            reg8 = regs[8]

            Start_Gap = bool(reg8 & 0x20)
            Start_Accel = bool(reg8 & 0x40)
            Start_Roll = bool(reg8 & 0x80)

            if server.current_step == 0 and Start_Gap:
                Roll_pos = regs_to_float(regs[2], regs[3])
                Dir_of_rot_valk = bool(reg8 & 0x01)
                server.log_message(f"Запуск Gap_Valk... {Roll_pos}")
                sim_result = server.simulator._Gap_Valk_(Roll_pos, Dir_of_rot_valk)
                server.current_data = sim_result
                server.current_steps_total = len(sim_result['Pyro1'])
                server.write_idx = 0
                server.writing_to_registers = True

            elif server.current_step == 1 and Start_Accel:
                Num_of_revol_rolls = regs_to_float(regs[0], regs[1])
                Dir_of_rot_rolg = bool(reg8 & 0x02)
                server.log_message("Запуск Accel_Valk...")
                sim_result = server.simulator._Accel_Valk_(Num_of_revol_rolls, Dir_of_rot_rolg, Dir_of_rot_rolg)
                server.current_data = sim_result
                server.current_steps_total = len(sim_result['Pyro1'])
                server.write_idx = 0
                server.writing_to_registers = True

            elif server.current_step == 2 and Start_Roll:
                Num_of_revol_0rollg = regs_to_float(regs[4], regs[5])
                Num_of_revol_1rollg = regs_to_float(regs[6], regs[7])
                Dir_of_rot_valk = bool(reg8 & 0x01)
                Dir_of_rot_rolg = bool(reg8 & 0x02)
                server.log_message("Запуск Approaching_to_Roll...")
                sim_result = server.simulator._Approching_to_Roll_(
                    Dir_of_rot_valk,
                    Num_of_revol_0rollg,
                    Num_of_revol_1rollg,
                    Dir_of_rot_rolg,
                    Dir_of_rot_rolg
                )
                server.current_data = sim_result
                server.current_steps_total = len(sim_result['Pyro1'])
                server.write_idx = 0
                server.writing_to_registers = True

            elif server.current_step == 3:
                server.log_message("Запуск simulate_rolling_pass...")
                sim_result = server.simulator._simulate_rolling_pass()
                server.current_data = sim_result
                server.current_steps_total = len(sim_result['Pyro1'])
                server.write_idx = 0
                server.writing_to_registers = True

            elif server.current_step == 4:
                server.log_message("Запуск simulate_exit_from_rolls...")
                sim_result = server.simulator._simulate_exit_from_rolls()
                server.current_data = sim_result
                server.current_steps_total = len(sim_result['Pyro1'])
                server.write_idx = 0
                server.writing_to_registers = True

            elif server.current_step > 4:
                # Ждём, пока все управляющие биты будут сброшены (Start_Gap, Start_Accel, Start_Roll)
                if not (Start_Gap or Start_Accel or Start_Roll):
                    server.current_step = 0
                # Если хотя бы один бит поднят — ничего не делаем, ждём сброса

            time.sleep(0.1)
        except Exception as e:
            server.log_message(f"Ошибка мониторинга: {e}")
            server.writing_to_registers = False
            server.write_idx = 0
            time.sleep(1)

def main():
    server = ModbusServer()
    
    monitor_thread = threading.Thread(target=monitor_registers, args=(server,), daemon=True)
    monitor_thread.start()
    
    server.run_server()

if __name__ == "__main__":
    main()