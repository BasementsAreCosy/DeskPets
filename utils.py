from PyQt5.QtGui import QPixmap

def roundToNearestBase(num, base):
    return round(num/base)*base

def sign(num):
    if num == 0:
        return 0
    return int(num/abs(num))

def clamp(num, bound):
    return max(min(num, bound), -bound)

def invClamp(num, bound):
    return max(abs(num), bound) * sign(num)

def scaleImage(imagePath, size):
    return QPixmap(imagePath).scaled(round(size), round(size))