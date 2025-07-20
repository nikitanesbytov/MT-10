from Stan import Stan
from RelDef import RelDef
from TempDrDMove import TempDrDMove
from TempDrDR import TempDrDR
from DefResistance import DefResistance
from TorEffPow import TorrEffPow
from CapCondition import CapCondition
from FricCoef import FricCoef
from AvrgPressure import AvrgPressure
from ContactArcLen import ContactArcLen
from ContactArea import ContactArea
from AbsWidening import AbsWidening


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
# Конечная длина
# Центрирование 


if __name__ == "__main__":
    Process = Stan(Size=10, StartTemp="25C")
    