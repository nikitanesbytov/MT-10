from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import threading
import time
import struct
from datetime import datetime
import psycopg2
from RollingMillSimulator import start
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

    def run_simulation_and_update(self, **kwargs):
        self.log_message("Запуск симуляции...")
        sim_result = start(**kwargs)
        steps = len(sim_result['Pyro1'])
        
        self.log_message(f"Симуляция запущена, шагов: {steps}")
        
        for i in range(steps):
            if self.stop_monitoring:
                break
            self.update_simulation_registers(sim_result, i)
            time.sleep(0.1)
        
        last_idx = steps - 1
        self.log_message("Симуляция завершена, поддержание последних значений")
        
        end_time = time.time() + 5
        while not self.stop_monitoring and time.time() < end_time:
            self.update_simulation_registers(sim_result, last_idx)
            time.sleep(0.1)

    def start_simulator_from_registers(self):
        """Запуск симуляции на основе текущих значений регистров"""
        cur.execute("SELECT * FROM slabs ORDER BY id DESC LIMIT 1")
        last_row = cur.fetchone()
        id, Length_slab, Width_slab, Thikness_slab, Temperature_slab, Material_slab, Diametr_roll,Material_roll = last_row
        regs = self.hr_data_combined.getValues(1, 11)
        
        Num_of_revol_rolls = regs_to_float(regs[0], regs[1])
        Roll_pos = regs_to_float(regs[2], regs[3])
        Num_of_revol_0rollg = regs_to_float(regs[4], regs[5])
        Num_of_revol_1rollg = regs_to_float(regs[6], regs[7])
        Speed_of_diverg = regs_to_float(regs[9], regs[10])
        
        reg8 = regs[8]
        Dir_of_rot_valk = bool(reg8 & 0x01)
        Dir_of_rot_L_rolg = bool(reg8 & 0x02)
        Mode = bool(reg8 & 0x04)
        Dir_of_rot_R_rolg = bool(reg8 & 0x08)
        Start = bool(reg8 & 0x10)
        
        self.log_message(f"Параметры симуляции:")
        self.log_message(f"  Num_of_revol_rolls: {Num_of_revol_rolls}")
        self.log_message(f"  Roll_pos: {Roll_pos}")
        self.log_message(f"  Num_of_revol_0rollg: {Num_of_revol_0rollg}")
        self.log_message(f"  Num_of_revol_1rollg: {Num_of_revol_1rollg}")
        self.log_message(f"  Speed_of_diverg: {Speed_of_diverg}")
        self.log_message(f"  Dir_of_rot_valk: {Dir_of_rot_valk}")
        self.log_message(f"  Dir_of_rot_L_rolg: {Dir_of_rot_L_rolg}")
        self.log_message(f"  Dir_of_rot_R_rolg: {Dir_of_rot_R_rolg}")
        self.log_message(f"  Mode: {Mode}")
        self.log_message(f"  Start: {Start}")
        
        threading.Thread(
            target=self.run_simulation_and_update,
            kwargs=dict(
                Num_of_revol_rolls=Num_of_revol_rolls,
                Roll_pos=Roll_pos,
                Num_of_revol_0rollg=Num_of_revol_0rollg,
                Num_of_revol_1rollg=Num_of_revol_1rollg,
                Dir_of_rot_valk=Dir_of_rot_valk,
                Dir_of_rot_L_rolg=Dir_of_rot_L_rolg,
                Dir_of_rot_R_rolg=Dir_of_rot_R_rolg,
                Mode=Mode,
                Speed_of_diverg=Speed_of_diverg,
                Length_slab = Length_slab,
                Width_slab = Width_slab,
                Thikness_slab = Thikness_slab,
                Temperature_slab= Temperature_slab,
                Material_slab = Material_slab,
                Material_roll = Material_roll
            ),
            daemon=True
        ).start()

    def run_server(self):
        """Запуск Modbus сервера"""
        self.log_message("Modbus сервер запущен на localhost:55000")
        self.log_message("Для запуска симуляции установите бит Start (0x10) в регистре 8")
        
        try:
            StartTcpServer(context=self.context, address=("localhost", 55000))
        except Exception as e:
            self.log_message(f"Ошибка сервера: {e}")
        finally:
            self.stop_monitoring = True

def monitor_registers(server):
    """Мониторинг регистров для автоматического запуска симуляции"""
    last_start_state = False
    
    while not server.stop_monitoring:
        try:
            regs = server.hr_data_combined.getValues(1, 11)
            reg8 = regs[8]
            current_start_state = bool(reg8 & 0x10)
            
            if current_start_state and not last_start_state:
                server.log_message("Обнаружен запуск симуляции по биту Start")
                server.start_simulator_from_registers()
            
            last_start_state = current_start_state
            time.sleep(0.1) 
            
        except Exception as e:
            server.log_message(f"Ошибка мониторинга: {e}")
            time.sleep(1)

def main():
    server = ModbusServer()
    
    monitor_thread = threading.Thread(target=monitor_registers, args=(server,), daemon=True)
    monitor_thread.start()
    
    server.run_server()

if __name__ == "__main__":
    main()