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

class ModbusServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modbus Server Monitor")
        self.root.geometry("1000x700")
        self.server = ModbusServerWithMonitoring(self.update_gui)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        title_label = ttk.Label(main_frame, text="Modbus Server Monitor", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        info_frame = ttk.LabelFrame(main_frame, text="Server Info", padding="5")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(info_frame, text="Address: localhost:55000").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="Write registers: 1-11 (11 registers)").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="Read registers: 12-34 (23 registers)").grid(row=2, column=0, sticky=tk.W)
        real_frame = ttk.LabelFrame(main_frame, text="REAL Variables", padding="5")
        real_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))
        self.real_vars = {}
        real_labels = [
            ("var1 (registers 1-2):", "var1"),
            ("var2 (registers 3-4):", "var2"),
            ("var3 (registers 5-6):", "var3"),
            ("var4 (registers 7-8):", "var4"),
            ("var5 (registers 9-10):", "var5")
        ]
        for i, (label_text, var_name) in enumerate(real_labels):
            ttk.Label(real_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            value_label = ttk.Label(real_frame, text="0.000000", foreground="blue", font=("Arial", 10))
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2)
            self.real_vars[var_name] = value_label
        bits_frame = ttk.LabelFrame(main_frame, text="Bit Flags (Register 8)", padding="5")
        bits_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))
        self.bit_vars = []
        bit_labels = ["Bit 0", "Bit 1", "Bit 2", "Bit 3"]
        for i, label_text in enumerate(bit_labels):
            ttk.Label(bits_frame, text=label_text + ":").grid(row=i, column=0, sticky=tk.W, pady=2)
            value_label = ttk.Label(bits_frame, text="False", foreground="red", font=("Arial", 10))
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2)
            self.bit_vars.append(value_label)
        write_frame = ttk.LabelFrame(main_frame, text="Write Registers (1-11)", padding="5")
        write_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))
        self.write_vars = []
        for i in range(11):
            ttk.Label(write_frame, text=f"Reg {i+1}:").grid(row=i//6, column=(i%6)*2, sticky=tk.W, pady=1)
            value_label = ttk.Label(write_frame, text="0", foreground="green", font=("Arial", 9))
            value_label.grid(row=i//6, column=(i%6)*2+1, sticky=tk.W, pady=1, padx=(5, 10))
            self.write_vars.append(value_label)
        read_frame = ttk.LabelFrame(main_frame, text="Read Registers (12-34)", padding="5")
        read_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))
        self.read_vars = []
        for i in range(23):
            ttk.Label(read_frame, text=f"Reg {i+12}:").grid(row=i//6, column=(i%6)*2, sticky=tk.W, pady=1)
            value_label = ttk.Label(read_frame, text="0", foreground="purple", font=("Arial", 9))
            value_label.grid(row=i//6, column=(i%6)*2+1, sticky=tk.W, pady=1, padx=(5, 10))
            self.read_vars.append(value_label)
        log_frame = ttk.LabelFrame(main_frame, text="Event Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.config(state=tk.DISABLED)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Simulator", command=self.start_simulator).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.exit_app).pack(side=tk.LEFT, padx=5)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def update_gui(self, data):
        def update():
            for var_name, value in data['real_vars'].items():
                self.real_vars[var_name].config(text=f"{value:.6f}")
            for i, value in enumerate(data['bit_flags']):
                color = "green" if value else "red"
                text = "True" if value else "False"
                self.bit_vars[i].config(text=text, foreground=color)
            for i, value in enumerate(data['write_registers']):
                self.write_vars[i].config(text=str(value))
            for i, value in enumerate(data['read_registers']):
                self.read_vars[i].config(text=str(value))
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
        # Преобразуем регистры в нужные типы
        def regs_to_float(r1, r2):
            try:
                b1 = (r1 >> 8) & 0xFF
                b2 = r1 & 0xFF
                b3 = (r2 >> 8) & 0xFF
                b4 = r2 & 0xFF
                return struct.unpack('>f', bytes([b1, b2, b3, b4]))[0]
            except:
                return 0.0
        Num_of_revol_rolls = int(regs_to_float(regs[0], regs[1]))
        Roll_pos = int(regs_to_float(regs[2], regs[3]))
        Num_of_revol_0rollg = int(regs_to_float(regs[4], regs[5]))
        Num_of_revol_1rollg = int(regs_to_float(regs[6], regs[7]))
        # Биты для булевых параметров
        reg8 = regs[7]
        Dir_of_rot = bool(reg8 & 0x0001)
        Dir_of_rot_rolg = bool(reg8 & 0x0002)
        Mode = bool(reg8 & 0x0004)
        Dir_of_rot_valk = bool(reg8 & 0x0008)
        Speed_of_diverg = int(regs_to_float(regs[9], regs[10]))
        # Запуск симулятора
        start(
            Num_of_revol_rolls=Num_of_revol_rolls,
            Roll_pos=Roll_pos,
            Num_of_revol_0rollg=Num_of_revol_0rollg,
            Num_of_revol_1rollg=Num_of_revol_1rollg,
            Dir_of_rot=Dir_of_rot,
            Dir_of_rot_rolg=Dir_of_rot_rolg,
            Mode=Mode,
            Dir_of_rot_valk=Dir_of_rot_valk,
            Speed_of_diverg=Speed_of_diverg
        )
        # Лог
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "[{}] Simulator started with values from registers\n".format(datetime.now().strftime("%H:%M:%S")))
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
        self.real_vars = {'var1': 0.0, 'var2': 0.0, 'var3': 0.0, 'var4': 0.0, 'var5': 0.0}
        self.bit_flags = [False, False, False, False]
        self.update_callback = update_callback

    def registers_to_float(self, reg1, reg2):
        try:
            byte1 = (reg1 >> 8) & 0xFF
            byte2 = reg1 & 0xFF
            byte3 = (reg2 >> 8) & 0xFF
            byte4 = reg2 & 0xFF
            return struct.unpack('>f', bytes([byte1, byte2, byte3, byte4]))[0]
        except:
            return 0.0

    def update_variables(self):
        try:
            current_values = self.hr_data_combined.getValues(1, 11)
            self.real_vars['var1'] = self.registers_to_float(current_values[0], current_values[1])
            self.real_vars['var2'] = self.registers_to_float(current_values[2], current_values[3])
            self.real_vars['var3'] = self.registers_to_float(current_values[4], current_values[5])
            self.real_vars['var4'] = self.registers_to_float(current_values[6], current_values[7])
            self.real_vars['var5'] = self.registers_to_float(current_values[9], current_values[10])
            reg8_value = current_values[7]
            self.bit_flags[0] = bool(reg8_value & 0x0001)
            self.bit_flags[1] = bool(reg8_value & 0x0002)
            self.bit_flags[2] = bool(reg8_value & 0x0004)
            self.bit_flags[3] = bool(reg8_value & 0x0008)
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False

    def monitor_registers(self):
        while not self.stop_monitoring:
            try:
                all_values = self.hr_data_combined.getValues(1, 34)
                write_values = all_values[:11]
                read_values = all_values[11:34]
                if self.update_variables():
                    data = {
                        'real_vars': self.real_vars,
                        'bit_flags': self.bit_flags,
                        'write_registers': write_values,
                        'read_registers': read_values
                    }
                    self.update_callback(data)
                time.sleep(2)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)

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
