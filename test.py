# -*- coding: utf-8 -*-
"""
Исправленный расчет с правильной физикой
"""

# Исходные данные
H_in = 200    # Начальная толщина, мм
H_out = 20    # Конечная толщина, мм
L_in = 5      # Начальная длина, м
V_roll = 2    # Скорость валков, м/с
V_in = 1.9    # Скорость подачи, м/с

# Расчет
mu = H_in / H_out
L_out_theoretical = L_in * mu
S = 1.05 + 0.05 * (mu - 1)
V_out = S * V_roll

print(f"Теоретическая конечная длина: {L_out_theoretical:.1f} м")
print(f"Скорость выхода: {V_out:.2f} м/с")
print("-" * 65)

# Инициализация в правильной системе координат
time = 0
front_pos = 0    # Передний торец на линии валков
rear_pos = -L_in # Задний торец до валков
is_complete = False

print("Время(с) | Передний(м) | Задний(м) | Длина(м) | Состояние")
print("-" * 65)

# Симуляция
while time < 20:  # Ограничим время для демонстрации
    
    # Определяем состояние
    if rear_pos < 0:
        state = "До валков"
    else:
        state = "После валков"
        is_complete = True
    
    # Текущая длина
    current_length = front_pos - rear_pos if not is_complete else L_out_theoretical
    
    print(f"{time:6.1f}  | {front_pos:9.2f}  | {rear_pos:9.2f}  | {current_length:7.2f}  | {state}")
    
    # Двигаем передний торец (всегда вперед)
    front_pos += V_out
    
    # Двигаем задний торец
    if not is_complete:
        if rear_pos < 0:
            # Задний торец еще ДО валков
            rear_pos += V_in
        else:
            # Задний торец только что вышел из валков
            # Устанавливаем правильное положение
            rear_pos = front_pos - L_out_theoretical
            is_complete = True
    else:
        # После полного выхода - оба торца движутся с V_out
        rear_pos += V_out
    
    time += 1

print(f"\nТеоретическая длина: {L_out_theoretical:.2f} м")