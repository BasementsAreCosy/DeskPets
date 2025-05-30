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



class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resolution = 128
        self.hunger = 100
        self.happiness = 100
        self.energy = 100
        self.position = QPoint(100, 100)
        self.targetPosition = None
        self.frame = 0
        self.sleeping = False
        
        self.initUI()

        self.spriteName = 'bear'
        self.petImage = None  # Initialize petImage
        self.idleImage = QPixmap(f'{self.spriteName}x{self.resolution}/{self.spriteName}_1_2_a_0.png')
        self.setPetImage()  # Set initial image

        self.bedImage = QPixmap('sprites/bed.png')

        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updatePet)
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
    
    def updatePet(self):
        self.frame += 1

        if not self.sleeping:
            self.energy -= 2
            self.hunger -= 0.01
            self.happiness -= 0.01

        self.setPetImage()
        if self.energy <= 0 and self.targetPosition == None:
            self.sleeping = True
            self.targetPosition = QPoint(100, win32api.GetSystemMetrics(1) - 144)
            self.idleImage = QPixmap(f'{self.spriteName}x{self.resolution}/{self.spriteName}_1_2_a_0.png')
        elif not self.isMoving and not self.sleeping:
            if random.random() < 0.1:
                self.targetPosition = QPoint(random.randint(100, win32api.GetSystemMetrics(0) - 100), random.randint(100, win32api.GetSystemMetrics(1) - 100))
        else:
            # Move towards target position
            dx = self.targetPosition.x() - self.position.x()
            dy = self.targetPosition.y() - self.position.y()
            distance = math.sqrt(dx**2 + dy**2)

            if distance < 200 and not self.sleeping:
                self.targetPosition = None
            else:
                self.position.setX(self.position.x() + max(min(dx * 0.05, self.resolution/2), -self.resolution/2))
                self.position.setY(self.position.y() + max(min(dy * 0.05, self.resolution/2), -self.resolution/2))
                self.update()  # Update the window to redraw the pet at new position
        
        if self.sleeping:
            self.energy += 0.01
            if self.energy >= 100:
                self.sleeping = False
                self.energy = 100
    
    def setPetImage(self):
        if self.directionMatrix == None:
            self.petImage = self.idleImage
        else:
            self.petImage = QPixmap(f'{self.spriteName}x{self.resolution}/{self.spriteName}_{self.directionMatrix[0]}_{self.directionMatrix[1]}_a_{self.frame%2}.png')
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)

        if self.bedImage:
            painter.drawPixmap(100, win32api.GetSystemMetrics(1) - 144, self.bedImage)
            
        if self.petImage:
            painter.drawPixmap(self.position.x(), self.position.y(), self.petImage)

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
        
        return direction_map[direction]
    
    @property
    def isMoving(self):
        if self.targetPosition == None:
            return False
        return self.position != self.targetPosition





def main():
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()