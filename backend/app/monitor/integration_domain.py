"""匿名集成数值技术域；纯规则，旧 UTC 域保持原样。"""
from app.monitor.mapping_domain import identifier

from decimal import Decimal
import struct
from common.integration.envelope import source_time

def decimal_number(value, precision, scale, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ValueError("JSON number required")
    number = Decimal(value)
    if not number.is_finite() or number.copy_abs() >= Decimal(10) ** (precision-scale) or (nonnegative and number < 0):
        raise ValueError("number outside storage domain")
    digits = list(number.as_tuple().digits)
    exponent = number.as_tuple().exponent
    while digits and digits[-1] == 0:
        digits.pop(); exponent += 1
    if digits and exponent < -scale:
        raise ValueError("number exceeds storage scale")
    return Decimal(0) if number == 0 else number

def float_number(value, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ValueError("JSON number required")
    number = Decimal(value)
    if not number.is_finite() or number.copy_abs() > Decimal("3.4028234663852886e38") or (nonnegative and number < 0):
        raise ValueError("number outside FLOAT domain")
    try:
        stored = Decimal.from_float(struct.unpack("!f", struct.pack("!f", float(number)))[0])
    except (OverflowError, struct.error):
        raise ValueError("number outside FLOAT domain") from None
    if number != 0 and stored == 0:
        raise ValueError("FLOAT cannot preserve measurement")
    # Decimal.as_integer_ratio是精确整数，不受调用方context影响。
    # |F-N|*1e6 <= |N|，以及绝对误差 <= max(1e-6,|N|*1e-6)，交叉相乘无舍入。
    numerator,denominator=number.as_integer_ratio()
    stored_numerator,stored_denominator=stored.as_integer_ratio()
    delta=abs(stored_numerator*denominator-numerator*stored_denominator)
    if ((number!=0 and delta*1000000>abs(numerator)*stored_denominator)
            or delta*1000000>max(denominator,abs(numerator))*stored_denominator):
        raise ValueError("FLOAT cannot preserve measurement")
    return Decimal(0) if stored == 0 else stored

def integer_number(value, low=-2147483648, high=2147483647):
    number = decimal_number(value, 20, 0)
    if not low <= number <= high:
        raise ValueError("integer outside storage domain")
    return int(number)
