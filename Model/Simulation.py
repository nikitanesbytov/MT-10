from Stan import Stan
from Methods.RelDef import RelDef
from Methods.TempDrBPass import TempDrBPass
from Methods.TempDrPlDeform import TempDrPlDeform
from Methods.TempDrDConRoll import TempDrDConRoll
from Methods.GenTemp import GenTemp
from Methods.DefResistance import DefResistance
from Model.Methods.MFP import TorrEffPow
from Methods.CapCondition import CapCondition
from Methods.FricCoef import FricCoef
from Methods.AvrgPressure import AvrgPressure
from Methods.ContactArcLen import ContactArcLen
from Methods.ContactArea import ContactArea
from Methods.AbsWidening import AbsWidening


Stan.RelDef = RelDef #1 - Относитенльная деформация
Stan.TempDrBPass = TempDrBPass #2 - Падение температуры между пропусками
Stan.TempDrPlDeform = TempDrPlDeform #3 - Падение температуры вследствие пластической дфеормации
Stan.TempDrDConRoll = TempDrDConRoll #4 - Падение температуры вследствие контакта с валками  
Stan.GenTemp = GenTemp #5 - Общая температура
Stan.DefResistance = DefResistance #6 - Сопротивление деформации
Stan.MFP = MFP #7 - Расчет момента, усилие, мощности, проверка
Stan.CapCondition = CapCondition #8 - Условие захвата
Stan.FricCoef = FricCoef #9 - Коэффициент трения
Stan.AvrgPressure = AvrgPressure #10 - Среднее давление на валки
Stan.ContactArcLen = ContactArcLen #11 - Длина дуги контакта
Stan.ContactArea = ContactArea #12 - Площадь поверхности контакта
Stan.AbsWidening = AbsWidening #13 - Абсолютное уширение
# Конечная длина
# Центрирование 


if __name__ == "__main__":
    Process = Stan()
    