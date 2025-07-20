def RelDef(h_0, h_1) -> float:
    """Относительная деформация"""
    RelDef = (h_0 - h_1) / h_0
    return RelDef