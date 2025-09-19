from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import threading
import time
import struct
from datetime import datetime
from RollingMillSimulator import start
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QGroupBox,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QColor

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

class ModbusServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server = ModbusServerWithMonitoring(self)
        self.init_ui()
        self.start_server()

    def init_ui(self):
        self.setWindowTitle("Modbus Server - Rolling Mill Simulator")
        self.setGeometry(100, 100, 1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Левая панель - таблицы значений
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)

        # Таблица входных переменных
        input_group = QGroupBox("Входные переменные (Write)")
        input_layout = QVBoxLayout()
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(2)
        self.input_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.input_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        input_layout.addWidget(self.input_table)
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)

        # Таблица выходных переменных
        output_group = QGroupBox("Выходные переменные (Read)")
        output_layout = QVBoxLayout()
        self.output_table = QTableWidget()
        self.output_table.setColumnCount(2)
        self.output_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.output_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        output_layout.addWidget(self.output_table)
        output_group.setLayout(output_layout)
        left_layout.addWidget(output_group)

        # Правая панель - управление и логи
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Панель управления
        control_group = QGroupBox("Управление")
        control_layout = QVBoxLayout()
        
        self.start_button = QPushButton("СТАРТ симуляции")
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.start_button.clicked.connect(self.start_simulation)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("СТОП сервер")
        self.stop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.stop_button.clicked.connect(self.stop_server)
        control_layout.addWidget(self.stop_button)

        # Статус
        self.status_label = QLabel("Статус: Сервер запущен на localhost:55000")
        self.status_label.setStyleSheet("QLabel { background-color: #e3f2fd; padding: 5px; border: 1px solid #90caf9; }")
        control_layout.addWidget(self.status_label)

        control_group.setLayout(control_layout)
        right_layout.addWidget(control_group)

        # Панель логов
        log_group = QGroupBox("Логи симуляции")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        self.log_text.setMaximumHeight(300)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)

        # Добавляем панели в основной layout
        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 1)

        # Таймер для обновления значений
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # Обновление каждые 100мс

        # Инициализируем таблицы
        self.init_tables()

    def init_tables(self):
        # Входные переменные
        input_vars = [
            'Num_of_revol_rolls', 'Roll_pos', 'Num_of_revol_0rollg',
            'Num_of_revol_1rollg', 'Speed_of_diverg'
        ]
        self.input_table.setRowCount(len(input_vars))
        for i, var in enumerate(input_vars):
            self.input_table.setItem(i, 0, QTableWidgetItem(var))
            self.input_table.setItem(i, 1, QTableWidgetItem("0.000000"))

        # Выходные переменные
        output_vars = [
            'Pyro1', 'Pyro2', 'Pressure', 'Gap', 'VRPM', 
            'V0RPM', 'V1RPM', 'Moment', 'Power'
        ]
        self.output_table.setRowCount(len(output_vars))
        for i, var in enumerate(output_vars):
            self.output_table.setItem(i, 0, QTableWidgetItem(var))
            self.output_table.setItem(i, 1, QTableWidgetItem("0.000000"))

    def update_display(self):
        """Обновление значений в таблицах"""
        data = self.server.update_variables()
        if data:
            # Обновляем входные переменные
            for i, (var_name, value) in enumerate(data['input_vars'].items()):
                if i < self.input_table.rowCount():
                    item = self.input_table.item(i, 1)
                    if item:
                        item.setText(f"{value:.6f}")

            # Обновляем выходные переменные
            for i, (var_name, value) in enumerate(data['output_vars'].items()):
                if i < self.output_table.rowCount():
                    item = self.output_table.item(i, 1)
                    if item:
                        item.setText(f"{value:.6f}")

    def start_simulation(self):
        """Запуск симуляции"""
        self.start_button.setEnabled(False)
        self.status_label.setText("Статус: Запуск симуляции...")
        self.server.start_logging()  # Включаем запись логов
        self.server.start_simulator_from_registers()
        
        # Через 5 секунд после завершения выключаем логи
        QTimer.singleShot(5000, self.stop_logging)

    def stop_logging(self):
        """Остановка записи логов"""
        self.server.stop_logging()
        self.status_label.setText("Статус: Симуляция завершена, логи сохранены")
        self.start_button.setEnabled(True)

    def start_server(self):
        self.server_thread = threading.Thread(target=self.server.run_server, daemon=True)
        self.server_thread.start()

    def stop_server(self):
        self.server.stop_monitoring = True
        self.status_label.setText("Статус: Сервер останавливается...")
        QTimer.singleShot(2000, self.close)

    def closeEvent(self, event):
        self.server.stop_monitoring = True
        event.accept()

class ModbusServerWithMonitoring:
    def __init__(self, gui):
        total_registers = 30
        initial_values = [0] * total_registers
        self.hr_data_combined = ModbusSequentialDataBlock(1, initial_values)
        store = ModbusSlaveContext(hr=self.hr_data_combined)
        self.context = ModbusServerContext(slaves=store, single=True)
        self.stop_monitoring = False
        self.gui = gui
        self.logging_enabled = False
        self.log_file = None

    def start_logging(self):
        """Включение записи логов в файл"""
        self.logging_enabled = True
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = open(f"simulation_log_{timestamp}.txt", "w", encoding="utf-8")
        self.log_message("=== НАЧАЛО СИМУЛЯЦИИ ===")

    def stop_logging(self):
        """Выключение записи логов в файл"""
        self.logging_enabled = False
        if self.log_file:
            self.log_message("=== КОНЕЦ СИМУЛЯЦИИ ===")
            self.log_file.close()
            self.log_file = None

    def log_message(self, message):
        """Запись сообщения в GUI и файл (если включено)"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        log_line = f"[{timestamp}] {message}"
        
        # Всегда в GUI
        if hasattr(self.gui, 'log_text'):
            self.gui.log_text.append(log_line)
            cursor = self.gui.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.gui.log_text.setTextCursor(cursor)

        # В файл только если включено логирование
        if self.logging_enabled and self.log_file:
            self.log_file.write(log_line + "\n")
            self.log_file.flush()

    def update_variables(self):
        try:
            current_values = self.hr_data_combined.getValues(1, 30)
            
            input_vars = {
                'Num_of_revol_rolls': regs_to_float(current_values[0], current_values[1]),
                'Roll_pos': regs_to_float(current_values[2], current_values[3]),
                'Num_of_revol_0rollg': regs_to_float(current_values[4], current_values[5]),
                'Num_of_revol_1rollg': regs_to_float(current_values[6], current_values[7]),
                'Speed_of_diverg': regs_to_float(current_values[9], current_values[10])
            }
            
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
            }
            
            return {'input_vars': input_vars, 'output_vars': output_vars}
            
        except Exception as e:
            self.log_message(f"Ошибка обновления: {e}")
            return None

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
        if sim_data.get('StartCap'):
            flags |= 0x01
        if sim_data.get('EndCap'):
            flags |= 0x02
        if sim_data.get('Gap_feedback'):
            flags |= 0x04
        if sim_data.get('Speed_feedback'):
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
        
        # Поддерживаем последние значения 5 секунд
        end_time = time.time() + 5
        while not self.stop_monitoring and time.time() < end_time:
            self.update_simulation_registers(sim_result, last_idx)
            time.sleep(0.1)

    def start_simulator_from_registers(self):
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
                Speed_of_diverg=Speed_of_diverg
            ),
            daemon=True
        ).start()

    def run_server(self):
        self.log_message("Modbus сервер запущен на localhost:55000")
        try:
            StartTcpServer(context=self.context, address=("localhost", 55000))
        except Exception as e:
            self.log_message(f"Ошибка сервера: {e}")
        finally:
            self.stop_monitoring = True

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ModbusServerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()