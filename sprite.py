import utils
from PyQt5.QtCore import QPoint

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
    def x(self):
        return self.position.x()
    
    @property
    def y(self):
        return self.position.y()