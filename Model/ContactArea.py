def ContactArea(b_0, b_1, LK) -> float:
    """Площадь контакта"""
    b_average = (b_0 + b_1) / 2
    F = b_average * LK
    return F