from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import threading
import time
import random
import struct
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from RollingMillSimulator import start

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

class ModbusServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modbus Server Monitor")
        self.root.geometry("1200x800")
        self.server = ModbusServerWithMonitoring(self.update_gui)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Modbus Server Monitor", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        info_frame = ttk.LabelFrame(main_frame, text="Server Info", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(info_frame, text="Address: localhost:55000").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="Write registers: 0-10 (11 registers)").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="Read registers: 11-33 (23 registers)").grid(row=2, column=0, sticky=tk.W)
        
        # Фрейм для входных REAL переменных (из write регистров)
        input_frame = ttk.LabelFrame(main_frame, text="Input REAL Variables (Write Registers)", padding="5")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))
        
        self.input_vars = {}
        input_labels = [
            ("Num_of_revol_rolls (reg 1-2):", "Num_of_revol_rolls"),
            ("Roll_pos (reg 3-4):", "Roll_pos"),
            ("Num_of_revol_0rollg (reg 5-6):", "Num_of_revol_0rollg"),
            ("Num_of_revol_1rollg (reg 7-8):", "Num_of_revol_1rollg"),
            ("Speed_of_diverg (reg 9-10):", "Speed_of_diverg")
        ]
        
        for i, (label_text, var_name) in enumerate(input_labels):
            ttk.Label(input_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            value_label = ttk.Label(input_frame, text="0.000000", foreground="blue", font=("Arial", 10))
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
            self.input_vars[var_name] = value_label
        
        # Фрейм для битовых флагов
        bits_frame = ttk.LabelFrame(main_frame, text="Bit Flags (Register 8)", padding="5")
        bits_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))
        
        self.bit_vars = {}
        bit_labels = [
            ("Bit 0 - Dir_of_rot:", "Dir_of_rot"),
            ("Bit 1 - Dir_of_rot_rolg:", "Dir_of_rot_rolg"),
            ("Bit 2 - Mode:", "Mode"),
            ("Bit 3 - Dir_of_rot_valk:", "Dir_of_rot_valk")
        ]
        
        for i, (label_text, var_name) in enumerate(bit_labels):
            ttk.Label(bits_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            value_label = ttk.Label(bits_frame, text="False", foreground="red", font=("Arial", 10))
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
            self.bit_vars[var_name] = value_label
        
        # Фрейм для выходных REAL переменных (из read регистров)
        output_frame = ttk.LabelFrame(main_frame, text="Output REAL Variables (Read Registers)", padding="5")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.output_vars = {}
        output_labels = [
            ("Pyro1 (reg 12-13):", "Pyro1"),
            ("Pyro2 (reg 14-15):", "Pyro2"),
            ("Pressure (reg 16-17):", "Pressure"),
            ("Gap (reg 18-19):", "Gap"),
            ("VRPM (reg 20-21):", "VRPM"),
            ("V0RPM (reg 22-23):", "V0RPM"),
            ("V1RPM (reg 24-25):", "V1RPM"),
            ("Moment (reg 26-27):", "Moment"),
            ("Power (reg 28-29):", "Power"),
            ("Gap_feedback (reg 30-31):", "Gap_feedback"),
            ("Speed_feedback (reg 32-33):", "Speed_feedback")
        ]
        
        for i, (label_text, var_name) in enumerate(output_labels):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(output_frame, text=label_text).grid(row=row, column=col, sticky=tk.W, pady=2, padx=(10, 5))
            value_label = ttk.Label(output_frame, text="0.000000", foreground="green", font=("Arial", 10))
            value_label.grid(row=row, column=col+1, sticky=tk.W, pady=2, padx=(5, 10))
            self.output_vars[var_name] = value_label
        
        # Фрейм для статусных флагов
        status_frame = ttk.LabelFrame(main_frame, text="Status Flags (Register 34)", padding="5")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_vars = {}
        status_labels = [
            ("StartCap (Bit 0):", "StartCap"),
            ("EndCap (Bit 1):", "EndCap")
        ]
        
        for i, (label_text, var_name) in enumerate(status_labels):
            ttk.Label(status_frame, text=label_text).grid(row=0, column=i*2, sticky=tk.W, pady=2, padx=(10, 5))
            value_label = ttk.Label(status_frame, text="False", foreground="purple", font=("Arial", 10))
            value_label.grid(row=0, column=i*2+1, sticky=tk.W, pady=2, padx=(5, 10))
            self.status_vars[var_name] = value_label
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Event Log", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.config(state=tk.DISABLED)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Simulator", command=self.start_simulator).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.exit_app).pack(side=tk.LEFT, padx=5)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def update_gui(self, data):
        def update():
            # Обновляем входные REAL переменные
            for var_name, value in data['input_vars'].items():
                self.input_vars[var_name].config(text=f"{value:.6f}")
            
            # Обновляем битовые флаги
            for var_name, value in data['bit_flags'].items():
                color = "green" if value else "red"
                text = "True" if value else "False"
                self.bit_vars[var_name].config(text=text, foreground=color)
            
            # Обновляем выходные REAL переменные
            for var_name, value in data['output_vars'].items():
                self.output_vars[var_name].config(text=f"{value:.6f}")
            
            # Обновляем статусные флаги
            for var_name, value in data['status_flags'].items():
                color = "green" if value else "red"
                text = "True" if value else "False"
                self.status_vars[var_name].config(text=text, foreground=color)
            
            # Логирование
            self.log_text.config(state=tk.NORMAL)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        self.root.after(0, update)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def exit_app(self):
        self.server.stop_monitoring = True
        self.root.quit()
        self.root.destroy()

    def start_simulator(self):
        """Взять значения из регистров и запустить симулятор"""
        regs = self.server.hr_data_combined.getValues(1, 11)
        
        # Получаем значения REAL переменных
        Num_of_revol_rolls = regs_to_float(regs[0], regs[1])
        Roll_pos = regs_to_float(regs[2], regs[3])
        Num_of_revol_0rollg = regs_to_float(regs[4], regs[5])
        Num_of_revol_1rollg = regs_to_float(regs[6], regs[7])
        Speed_of_diverg = regs_to_float(regs[9], regs[10])
        
        # Получаем битовые флаги
        reg8 = regs[7]
        Dir_of_rot = bool(reg8 & 0x0001)
        Dir_of_rot_rolg = bool(reg8 & 0x0002)
        Mode = bool(reg8 & 0x0004)
        Dir_of_rot_valk = bool(reg8 & 0x0008)
        
        # Запуск симуляции в отдельном потоке
        threading.Thread(
            target=self.server.run_simulation_and_update,
            kwargs=dict(
                Num_of_revol_rolls=Num_of_revol_rolls,
                Roll_pos=Roll_pos,
                Num_of_revol_0rollg=Num_of_revol_0rollg,
                Num_of_revol_1rollg=Num_of_revol_1rollg,
                Dir_of_rot=Dir_of_rot,
                Dir_of_rot_rolg=Dir_of_rot_rolg,
                Mode=Mode,
                Dir_of_rot_valk=Dir_of_rot_valk,
                Speed_of_diverg=Speed_of_diverg
            ),
            daemon=True
        ).start()
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Simulator started\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

class ModbusServerWithMonitoring:
    def __init__(self, update_callback):
        total_registers = 34
        initial_values = [0] * 11 + [random.randint(0, 1000) for _ in range(23)]
        self.hr_data_combined = ModbusSequentialDataBlock(1, initial_values)
        store = ModbusSlaveContext(hr=self.hr_data_combined)
        self.context = ModbusServerContext(slaves=store, single=True)
        self.stop_monitoring = False
        self.update_callback = update_callback

    def update_variables(self):
        try:
            current_values = self.hr_data_combined.getValues(1, 34)
            
            # Входные REAL переменные (write регистры 1-10)
            input_vars = {
                'Num_of_revol_rolls': regs_to_float(current_values[0], current_values[1]),
                'Roll_pos': regs_to_float(current_values[2], current_values[3]),
                'Num_of_revol_0rollg': regs_to_float(current_values[4], current_values[5]),
                'Num_of_revol_1rollg': regs_to_float(current_values[6], current_values[7]),
                'Speed_of_diverg': regs_to_float(current_values[9], current_values[10])
            }
            
            # Битовые флаги (регистр 8)
            reg8_value = current_values[7]
            bit_flags = {
                'Dir_of_rot': bool(reg8_value & 0x0001),
                'Dir_of_rot_rolg': bool(reg8_value & 0x0002),
                'Mode': bool(reg8_value & 0x0004),
                'Dir_of_rot_valk': bool(reg8_value & 0x0008)
            }
            
            # Выходные REAL переменные (read регистры 12-33)
            output_vars = {
                'Pyro1': regs_to_float(current_values[11], current_values[12]),
                'Pyro2': regs_to_float(current_values[13], current_values[14]),
                'Pressure': regs_to_float(current_values[15], current_values[16]),
                'Gap': regs_to_float(current_values[17], current_values[18]),
                'VRPM': regs_to_float(current_values[19], current_values[20]),
                'V0RPM': regs_to_float(current_values[21], current_values[22]),
                'V1RPM': regs_to_float(current_values[23], current_values[24]),
                'Moment': regs_to_float(current_values[25], current_values[26]),
                'Power': regs_to_float(current_values[27], current_values[28]),
                'Gap_feedback': regs_to_float(current_values[29], current_values[30]),
                'Speed_feedback': regs_to_float(current_values[31], current_values[32])
            }
            
            # Статусные флаги (регистр 34)
            reg34_value = current_values[33] if len(current_values) > 33 else 0
            status_flags = {
                'StartCap': bool(reg34_value & 0x01),
                'EndCap': bool(reg34_value & 0x02)
            }
            
            return {
                'input_vars': input_vars,
                'bit_flags': bit_flags,
                'output_vars': output_vars,
                'status_flags': status_flags
            }
            
        except Exception as e:
            print(f"Update error: {e}")
            return None

    def update_simulation_registers(self, sim_data, idx):
        # Порядок ключей как в return start, кроме 'Time'
        keys = [
            'Pyro1', 'Pyro2', 'Pressure', 'Gap', 'VRPM', 'V0RPM', 'V1RPM',
            'Moment', 'Power', 'Gap_feedback', 'Speed_feedback'
        ]
        regs = []
        for k in keys:
            v = sim_data[k][idx] if isinstance(sim_data[k], list) else sim_data[k]
            regs.extend(float_to_regs(v))
        
        # Булевые флаги в 1 регистр (регистр 34)
        flags = 0
        if sim_data.get('StartCap', False):
            flags |= 0x01
        if sim_data.get('EndCap', False):
            flags |= 0x02
        
        # Запись в регистры 12-34 (23 регистра)
        self.hr_data_combined.setValues(12, regs)
        self.hr_data_combined.setValues(34, [flags])

    def run_simulation_and_update(self, **kwargs):
        sim_result = start(**kwargs)
        steps = len(sim_result['Pyro1'])
        for i in range(steps):
            if self.stop_monitoring:
                break
            self.update_simulation_registers(sim_result, i)
            time.sleep(0.1)

    def monitor_registers(self):
        while not self.stop_monitoring:
            try:
                data = self.update_variables()
                if data:
                    self.update_callback(data)
                time.sleep(0.1)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(0.1)

    def run_server(self):
        monitor_thread = threading.Thread(target=self.monitor_registers, daemon=True)
        monitor_thread.start()
        print("Starting Modbus server...")
        try:
            StartTcpServer(context=self.context, address=("localhost", 55000))
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop_monitoring = True

def run_server():
    root = tk.Tk()
    app = ModbusServerGUI(root)
    server_thread = threading.Thread(target=app.server.run_server, daemon=True)
    server_thread.start()
    root.mainloop()

if __name__ == "__main__":
    run_server()