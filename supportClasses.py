import utils
from PyQt5.QtCore import QPoint
import win32api
import random

class Sprite:
    def __init__(self, window=None, pos=(0, 0), image=None, size=32, holdable=False, updatesPerSecond=60):
        self.window = window
        self.held = False
        self.holdable = holdable
        self.updatesPerSecond = updatesPerSecond
        self.image = utils.scaleImage(image, size)
        self.position = QPoint(round(pos[0]), round(pos[1]))
        self.size = size
        self.children = []
    
    def getChildren(self):
        return self.children
    
    def update(self):
        pass

    def onClick(self):
        pass

    def draw(self, painter):
        if self.image != None:
            painter.drawPixmap(self.x, self.y, self.image)

    @property
    def dead(self):
        return False
    
    @property
    def updateSpeed(self):
        return self.updatesPerSecond
    
    @property
    def x(self):
        return self.position.x()
    
    @property
    def y(self):
        return self.position.y()

class grainGrid:
    def __init__(self):
        self.grains = {}
    
    def update(self):
        grainSize = 3
        for grain in self.list:
            dx, dy = 0, 0
            belowEmpty = not self.exists((grain[0], grain[1]+grainSize)) and 0 <= grain[1]+grainSize <= win32api.GetSystemMetrics(1)-49
            if belowEmpty:
                dy = grainSize
                
            if random.random() <= 0.2:
                leftExists = self.exists((grain[0]-grainSize, grain[1]+dy))
                rightExists = self.exists((grain[0]+grainSize, grain[1]+dy))
                if (leftExists or rightExists or belowEmpty) and grain[1] != win32api.GetSystemMetrics(1)-49:
                    left = random.random() <= 0.5
                    if left and not leftExists and 0 <= grain[0]-grainSize <= win32api.GetSystemMetrics(0):
                        dx = -grainSize
                    elif not left and not rightExists and 0 <= grain[0]+grainSize <= win32api.GetSystemMetrics(0):
                        dx = grainSize

            if dx != 0 or dy != 0:
                self.removeItem(grain)
                self.addItem((grain[0]+dx, grain[1]+dy, *grain[2:]))
    
    def addItem(self, item):
        self.grains[(item[0], item[1])] = list(item)
    
    def removeItem(self, item):
        self.grains.pop((item[0], item[1]))
    
    def exists(self, coord):
        return coord in self.grains

    @property
    def list(self):
        return list(self.grains.values())

    @property
    def set(self):
        return set(self.grains.keys())

