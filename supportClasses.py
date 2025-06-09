import utils
from PyQt5.QtCore import QPoint
import win32api
import random

class Sprite:
    def __init__(self, pos=(0, 0), image=None, size=32, holdable=False, updatesPerSecond=60):
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
        self.map = {}
    
    def update(self):
        print(len(self.map))
        for grain in self.list:
            dx, dy = 0, 0
            if not grain[2]:
                belowEmpty = not self.exists((grain[0], grain[1]+1)) and 0 <= grain[1]+1 <= win32api.GetSystemMetrics(1)-49
                if belowEmpty:
                    dy = 1
                    
                if random.random() <= 0.05:
                    leftExists = self.exists((grain[0]-1, grain[1]))
                    rightExists = self.exists((grain[0]+1, grain[1]))
                    if leftExists or rightExists or belowEmpty:
                        left = random.random() <= 0.5
                        if left and not leftExists and 0 <= grain[0]-1 <= win32api.GetSystemMetrics(0):
                            dx = -1
                        elif not left and not rightExists and 0 <= grain[0]+1 <= win32api.GetSystemMetrics(0):
                            dx = 1

                # todo: 
                # Grid checks:
                # # X #
                #   #
                # if side and down happen at once, bottom left/right gets overridden

                '''
                if dx != 0 or dy != 0:
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            if self.exists((grain[0]+x, grain[1]+y)):
                                self.map[(grain[0]+x, grain[1]+y)][2] = False
                elif leftExists and rightExists and not belowEmpty:''' # todo: trapped bool to reduce lag

                self.removeItem(grain)
                self.addItem((grain[0]+dx, grain[1]+dy, True, *grain[3:]))
        self.resetFlags()
    
    def addItem(self, item):
        self.map[(item[0], item[1])] = item
    
    def removeItem(self, item):
        self.map.pop((item[0], item[1]))
    
    def resetFlags(self, flag=False):
        for key in list(self.map.keys()):
            item = self.map[key]
            self.map[key] = (item[0], item[1], flag, *item[3:])
    
    def exists(self, coord):
        return coord in self.map

    @property
    def list(self):
        return list(self.map.values())

    @property
    def set(self):
        return set(self.map.keys())

