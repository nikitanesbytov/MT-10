from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.client import ModbusTcpClient
import threading
import time
import struct
from datetime import datetime


class ModbusServer:
    def __init__(self):     
        total_registers = 31
        initial_values = [0] * total_registers
        self.hr_data_combined = ModbusSequentialDataBlock(1, initial_values)
        store = ModbusSlaveContext(hr=self.hr_data_combined)
        self.context = ModbusServerContext(slaves=store, single=True)
        self.stop_monitoring = False
        counter = 0

    
    def run_server(self):
        """Запуск Modbus сервера"""    
        try:
            StartTcpServer(context=self.context, address=("127.0.0.1", 55000))
        except Exception as e:
            self.log_message(f"Ошибка сервера: {e}")
        finally:
            self.stop_monitoring = True

    def read_plc_registers_directly(self):
        """
        Чтение регистров напрямую из datastore сервера
        """
        value = self.context[0].getValues(3,8,1)
        return value[-1]

    def monitor_registers(self):
        """Мониторинг регистров без создания клиента"""
        
        while not self.stop_monitoring:
            self.log_message("----------------------")
            
            register = self.read_plc_registers_directly()
            arr = self.bits(register)
            start = arr[3]
            if start == 1:
                if arr[0] == 1 and self.counter == 0:
                    self.Test1()
                    self.counter = 1
                if arr[1] == 1 and self.counter == 1:
                    self.Test2()
                    self.counter = 2
                if arr[2] == 1 and self.counter == 2:
                    self.Test3()
                    self.counter = 3
            if start == 0:
                self.counter = 0

            self.log_message("----------------------")
            
            time.sleep(1)
    
    def bits(self, register_value):

        bit_5 = (register_value >> 5) & 1 
        bit_6 = (register_value >> 6) & 1  
        bit_7 = (register_value >> 7) & 1 
        bit_4 =  (register_value >> 4) & 1
        return (bit_5,bit_6,bit_7,bit_4)

    def Test1(self):
        self.log_message('1')
        

    def Test2(self):
        self.log_message('2')

    def Test3(self):
        self.log_message('3')

        
    def log_message(self, message):
        """Запись сообщения в консоль"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] {message}")
    def stop_server(self):
        """Остановка сервера"""
        self.stop_monitoring = True


def main():
    server = ModbusServer()   
    
    monitor_thread = threading.Thread(target=server.monitor_registers, daemon=True)
    monitor_thread.start()
    
    try:
        server.run_server()
    except KeyboardInterrupt:
        server.log_message("Сервер остановлен пользователем")
        server.stop_server()


if __name__ == "__main__":
    main()