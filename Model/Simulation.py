from Stan import Stan
from Methods.RelDef import RelDef
from Methods.TempDrDMove import TempDrDMove
from Methods.TempDrDR import TempDrDR
from Methods.DefResistance import DefResistance
from Methods.TorEffPow import TorrEffPow
from Methods.CapCondition import CapCondition
from Methods.FricCoef import FricCoef
from Methods.AvrgPressure import AvrgPressure
from Methods.ContactArcLen import ContactArcLen
from Methods.ContactArea import ContactArea
from Methods.AbsWidening import AbsWidening


Stan.RelDef = RelDef #1 - Относитенльная деформация
Stan.TempDrDMove = TempDrDMove #2 - Падение температуры во время движения
Stan.TempDrDR = TempDrDR #3 - Падение температуры во время прокатки
Stan.DefResistance = DefResistance #4 - Сопротивление деформации
Stan.TorrEffPow = TorrEffPow #5 - Расчет момента, усилие, мощности, проверка
Stan.CapCondition = CapCondition #6 - Условие захвата
Stan.FricCoef = FricCoef #7 - Коэффициент трения
Stan.AvrgPressure = AvrgPressure #8 - Среднее давление на валки
Stan.ContactArcLen = ContactArcLen #9 - Длина дуги контакта
Stan.ContactArea = ContactArea #10 - Площадь поверхности контакта
Stan.AbsWidening = AbsWidening #11 - Абсолютное уширение
Stan.AbsWidening = AbsWidening #11 - Абсолютное уширение
# Конечная длина
# Центрирование 


if __name__ == "__main__":
    Process = Stan()
    