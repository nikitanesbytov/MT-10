def AvrgPressure(LK, h_average, sigma) -> float:
    """Среднее давление на валки"""
    if ((LK/h_average) <= 2):
        n_frict = 1 + (LK/h_average)/6
    elif (((LK/h_average) > 2) and ((LK/h_average) <= 4)):
        n_frict = 1 + (LK/h_average)/5
    elif ((LK/h_average) > 4):
        n_frict = 1 + (LK/h_average)/4

    n_zone = (LK / h_average) ** -0.4

    P = 1.15 * n_frict * n_zone * sigma #sigma - сопротивление деформации
    return P

# LK - длина дуги контакта
# h_average - средняя толщина сляба
# sigma - сопротивление деформации
# n_frict - коэффициент, учитывающий влияние внешнего трения (n')
# n_zone - коэффициент, учитывающий влияние внешних зон (n'')
# P - срднее давление на валки