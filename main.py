##### My Libs #####
import utils

##### Other Libs #####
import sys
import math
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor
import win32gui
import win32con
import win32api
from PIL import Image, ImageDraw



class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()


        self.sprites = []
        for i in range(10):
            self.sprites.append(Pet(resolution=random.randint(100, 150)))

        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateScr)
        self.updateTimer.start(200)

        #self.autosaveTimer = QTimer(self)
        #self.autosaveTimer.timeout.connect(self.save)
        #self.autosaveTimer.start(60000)
    
    def initUI(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Make window click-through
        hwnd = self.winId().__int__()
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        )
        
        # Set window size to be full screen
        self.setGeometry(0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
        self.show()
    
    def updateScr(self):
        for sprite in self.sprites:
            sprite.update()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)

        for sprite in self.sprites:
            if sprite.image:
                painter.drawPixmap(sprite.bed.x, sprite.bed.y, sprite.bed.image)
                painter.drawPixmap(sprite.x, sprite.y, sprite.image)

class Sprite:
    def __init__(self, pos=(0, 0)):
        self.image = None
        self.position = QPoint(pos[0], pos[1])
    
    def update(self):
        pass

    @property
    def x(self):
        return self.position.x()
    
    @property
    def y(self):
        return self.position.y()

class Pet(Sprite):
    def __init__(self, imageRes=32, resolution=128):
        super().__init__((random.randint(0, win32api.GetSystemMetrics(0)-resolution), random.randint(0, win32api.GetSystemMetrics(1)-resolution)))
        self.resolution = resolution
        self.imageRes = imageRes
        self.hunger = 100
        self.happiness = 100
        self.energy = 100
        self.targetPosition = None
        self.frame = 0
        self.sleeping = False
        self.lastDirection = (2, 2)

        self.bed = Bed()

        self.spriteName = 'bear'
        self.idleImage = QPixmap(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_2_i_0.png').scaled(self.resolution, self.resolution)
        self.setImage()  # Set initial image
    
    def update(self):
        self.frame += 1

        if not self.sleeping:
            self.energy -= 2
            self.hunger -= 0.01
            self.happiness -= 0.01

        if self.energy <= 0 and self.targetPosition == None:
            self.sleeping = True
            self.targetPosition = QPoint(self.bed.position)
            self.idleImage = QPixmap(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_1_s_0.png').scaled(self.resolution, self.resolution)
        elif not self.isMoving and not self.sleeping:
            if random.random() < 0.02:
                self.targetPosition = QPoint(random.randint(0, win32api.GetSystemMetrics(0) - self.resolution), random.randint(0, win32api.GetSystemMetrics(1) - self.resolution))
        elif self.targetPosition != None:
            # Move towards target position
            dx = self.targetPosition.x() - self.position.x()
            dy = self.targetPosition.y() - self.position.y()
            distance = math.sqrt(dx**2 + dy**2)

            if distance < 200 and not self.sleeping:
                self.targetPosition = None
            elif distance < 20 and self.sleeping:
                self.position = self.targetPosition
                self.targetPosition = None
            else:
                self.position.setX(round(self.position.x() + utils.clamp(utils.invClamp(dx*0.05, 3), self.resolution/2)))
                self.position.setY(round(self.position.y() + utils.clamp(utils.invClamp(dy*0.05, 3), self.resolution/2)))
        
        if self.targetPosition == None:
            self.idleImage = QPixmap(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_{self.lastDirection[0]}_{self.lastDirection[1]}_i_0.png').scaled(self.resolution, self.resolution)
        
        if self.sleeping and self.targetPosition == None:
            self.idleImage = QPixmap(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_1_s_{"0" if self.frame%10 != 0 else "1"}.png').scaled(self.resolution, self.resolution)
            self.energy += 1
            if self.energy >= 100:
                self.sleeping = False
                self.energy = 100
                self.targetPosition = QPoint(random.randint(0, win32api.GetSystemMetrics(0) - self.resolution), random.randint(0, win32api.GetSystemMetrics(1) - self.resolution))
        
        self.setImage()
    
    def setImage(self):
        if self.directionMatrix == None:
            self.image = self.idleImage
        else:
            self.image = QPixmap(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_{self.directionMatrix[0]}_{self.directionMatrix[1]}_a_{self.frame%2}.png').scaled(self.resolution, self.resolution)
    
    @property
    def directionVector(self):
        return None if self.targetPosition == None else (self.targetPosition.x()-self.position.x(), self.targetPosition.y()-self.position.y())

    @property
    def directionMatrix(self):
        if self.targetPosition == None:
            return None
        theta = math.atan2(self.directionVector[1], self.directionVector[0])
        # Convert angle to 0-360 degrees
        degrees = math.degrees(theta) % 360
        
        # Map to 8 directions (0,0) to (2,2)
        # Each direction is 45 degrees
        # 0: right, 1: bottom-right, 2: bottom, 3: bottom-left, 4: left, 5: top-left, 6: top, 7: top-right
        direction = round(degrees / 45) % 8
        
        # Explicit mapping of directions to coordinates
        direction_map = {
            0: (2, 1),  # right
            1: (2, 2),  # bottom-right
            2: (1, 2),  # bottom
            3: (0, 2),  # bottom-left
            4: (0, 1),  # left
            5: (0, 0),  # top-left
            6: (1, 0),  # top
            7: (2, 0)   # top-right
        }
        
        self.lastDirection = direction_map[direction]
        return direction_map[direction]
    
    @property
    def isMoving(self):
        if self.targetPosition == None:
            return False
        return self.position != self.targetPosition


class Bed(Sprite):
    def __init__(self):
        super().__init__((random.randint(0, win32api.GetSystemMetrics(0)-128), win32api.GetSystemMetrics(1)-144))
        self.image = QPixmap('sprites/bed.png')



def main():
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()