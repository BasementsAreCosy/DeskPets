def roundToNearestBase(num, base):
    return round(num/base)*base

def sign(num):
    if num == 0:
        return 0
    return int(num/abs(num))