from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import threading
import time
import struct
from datetime import datetime
import psycopg2

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
        self.current_step = 0  # 0 - ready for Gap_Valk, 1 - ready for Accel_Valk, 2 - ready for Approaching, 3 - ready for Rolling
        self.counter = 0
        self.counter2 = 0
        self.nex_idx = 0

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
        current_time = sim_data['Time'][idx] if 'Time' in sim_data else idx
        self.log_message(f"Запись в регистры: время симуляции = {current_time}с, шаг = {idx}")
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

        # После записи в регистры - улучшенное логирование в файл
        with open("serv.txt", "a") as f:
            f.write(f"=== Step {idx} (Time: {current_time}s) ===\n")
            for k in keys:
                v = sim_data[k][idx] if isinstance(sim_data[k], list) else sim_data[k]
                f.write(f"  {k}: {v}\n")
            f.write(f"  Flags: StartCap={StartCap_val}, EndCap={EndCap_val}, Gap_feedback={Gap_feedback_val}, Speed_feedback={Speed_feedback_val}\n")
            f.write("\n")

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

    def run_server(self,IP,port):
        """Запуск Modbus сервера"""
        self.log_message(f"Modbus сервер запущен на {IP}:{port}")
        try:
            StartTcpServer(context=self.context, address=(IP, port))
        except Exception as e:
            self.log_message(f"Ошибка сервера: {e}")
        finally:
            self.stop_monitoring = True

    def write_simulation_data_to_registers(self, sim_data):
        total_steps = len(sim_data['Time']) 

        # Инициализация переменных для управления временем
        write_start_time = time.time()
        
        while self.nex_idx != total_steps:      
            self._write_single_step_to_registers(sim_data, self.nex_idx)
            time.sleep(0.1)
            self.nex_idx += 1
        
        # Завершение записи
        if not self.stop_monitoring and self.nex_idx >= total_steps - 1:
            total_time = time.time() - write_start_time
            self.log_message(f" Запись данных завершена! Всего шагов: {total_steps}, время: {total_time:.1f}с")
            self.log_message(f" Переход к следующему этапу. Текущий счетчик: {self.counter}")

    
    def _write_single_step_to_registers(self, sim_data, idx):
        """Записывает данные одного шага симуляции в регистры"""
        current_time = sim_data['Time'][idx] 
        
        # Подготавливаем данные для регистров 12-29
        keys = [
            'Pyro1', 'Pyro2', 'Pressure', 'Gap', 'VRPM', 'V0RPM', 'V1RPM',
            'Moment', 'Power'
        ]
        regs = []
        for k in keys:
            v = sim_data[k][idx] if isinstance(sim_data[k], list) else sim_data[k]
            regs.extend(float_to_regs(v))
        
        # Записываем в регистры 12-29
        self.hr_data_combined.setValues(12, regs)  
        
        # Подготавливаем флаги для регистра 30
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
        
        # Записываем флаги в регистр 30
        self.hr_data_combined.setValues(30, [flags])
        
        # КОМПАКТНОЕ ЛОГИРОВАНИЕ В ФАЙЛ
        with open("serv.txt", "a") as f:
            # Шапка с временем и номером шага
            f.write(f"T{current_time:6.1f}s S{idx:4d} | ")
            
            # Основные параметры в компактном формате
            params = []
            for k in keys:
                v = sim_data[k][idx] if isinstance(sim_data[k], list) else sim_data[k]
                if k in ['Pyro1', 'Pyro2', 'Pressure']:
                    params.append(f"{k[:3]}:{v:6.1f}")
                elif k in ['Gap', 'VRPM', 'V0RPM', 'V1RPM']:
                    params.append(f"{k[:3]}:{v:6.1f}")
                elif k in ['Moment', 'Power']:
                    params.append(f"{k[:1]}:{v:6.1f}")
            
            f.write(" ".join(params))
            f.write(" | ")
            
            # Флаги в компактном формате
            flags_str = []
            if StartCap_val: flags_str.append("LCap")
            if EndCap_val: flags_str.append("RCap") 
            if Gap_feedback_val: flags_str.append("Gap")
            if Speed_feedback_val: flags_str.append("Speed")
            
            f.write("F:" + ("".join(flags_str) if flags_str else "---"))
            f.write("\n")
        
    def monitor_registers(self):
        while not self.stop_monitoring:
            # Читаем регистры
            regs = self.hr_data_combined.getValues(1, 31)
            reg8 = regs[8]
            
            # Обнаружение фронтов
            Start = bool(reg8 & 0x10)
            Start_Gap = bool(reg8 & 0x20)
            Start_Accel = bool(reg8 & 0x40)
            Start_Roll = bool(reg8 & 0x80)
            
            if Start:
                if Start_Gap and self.counter == 0 and self.counter2 < 2:
                    Roll_pos = regs_to_float(regs[2], regs[3])
                    Dir_of_rot_valk = bool(reg8 & 0x01)
                    self.log_message("ЗАПУСК Gap_Valk...")
                    self.log_message(f"Параметры: Roll_pos={Roll_pos}, Dir_of_rot_valk={Dir_of_rot_valk}")
                    sim_result = self.simulator._Gap_Valk_(Roll_pos, Dir_of_rot_valk)
                    self.write_simulation_data_to_registers(sim_result)
                    self.log_message(f"Завершено")
                    self.counter = 1
                    self.counter2 += 1
                    self.flag = 0

                if Start_Accel and self.counter == 1 and self.counter2 < 2:
                    Num_of_revol_rolls = regs_to_float(regs[0], regs[1])
                    Dir_of_rot_rolg = bool(reg8 & 0x02)
                    self.log_message("ЗАПУСК Accel_Valk...")
                    self.log_message(f"Параметры: Num_of_revol_rolls={Num_of_revol_rolls}")
                    sim_result = self.simulator._Accel_Valk_(Num_of_revol_rolls, Dir_of_rot_rolg, Dir_of_rot_rolg)
                    self.write_simulation_data_to_registers(sim_result)
                    self.log_message(f"Завершено")
                    self.counter = 2
                    self.counter2 += 1
                    self.flag = 0

                if Start_Roll and self.counter == 2 and self.counter2 <= 2:
                    Num_of_revol_0rollg = regs_to_float(regs[4], regs[5])
                    Num_of_revol_1rollg = regs_to_float(regs[6], regs[7])
                    Dir_of_rot_valk = bool(reg8 & 0x01)
                    Dir_of_rot_rolg = bool(reg8 & 0x02)
                    self.log_message("ЗАПУСК Approaching_to_Roll...")
                    sim_result = self.simulator._Approching_to_Roll_(
                        Dir_of_rot_valk,
                        Num_of_revol_0rollg,
                        Num_of_revol_1rollg,
                        Dir_of_rot_rolg,
                        Dir_of_rot_rolg
                    )
                    self.write_simulation_data_to_registers(sim_result)
                    self.flag = 0

                    sim_result = self.simulator._simulate_rolling_pass()
                    self.write_simulation_data_to_registers(sim_result)
                    self.flag = 0
                    
                    sim_result = self.simulator._simulate_exit_from_rolls()
                    self.write_simulation_data_to_registers(sim_result)
                    self.flag = 0
                    self.counter2 += 1
                    self.log_message(f"Завершено")
            if Start == 0:
                self.counter = 0
                self.counter2 = 0
            time.sleep(0.1)

    # def monitoring_alarm(self):
    #     while not self.stop_monitoring:
    #         reg8 = self.hr_data_combined.getValues(9, 1)[0] 
    #         alarm = bool(reg8 & 0x08)
    #         if alarm 

def main():

    server = ModbusServer()
    
    # Очищаем файл лога при запуске с компактной шапкой
    with open("serv.txt", "w") as f:
        f.write(f"=== ЛОГ СЕРВЕРА {datetime.now().strftime('%d.%m %H:%M')} ===\n")
        f.write("Формат: Время Шаг | Параметры | Флаги\n")
        f.write("Параметры: Py1 Py2 Pre Gap VRPM V0R V1R M P\n")
        f.write("Флаги: SC=StartCap EC=EndCap GF=GapFeedback SF=SpeedFeedback\n")
        f.write("-" * 80 + "\n")
    
    monitor_thread = threading.Thread(target=server.monitor_registers, args=(), daemon=True)
    monitor_thread.start()
    
    server.run_server("10.77.100.52",55000)

if __name__ == "__main__":
    main()