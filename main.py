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
        for i in range(1):
            self.sprites.append(Pet(size=32))
        
        self.mousePressed = False
        self.heldSprite = None
        self.heldSpriteOffset = (0, 0)

        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateScr)
        self.updateTimer.start(200)

        #self.autosaveTimer = QTimer(self)
        #self.autosaveTimer.timeout.connect(self.save)
        #self.autosaveTimer.start(60000)
    
    def initUI(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint | # todo: change to bottom after development
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Make window click-through
        hwnd = self.winId().__int__()
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED # | win32con.WS_EX_TRANSPARENT
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
                sprite.draw(painter)
    
    def mousePressEvent(self, event):
        self.mousePressed = True
    
    def mouseMoveEvent(self, event):
        if self.mousePressed and self.heldSprite == None:
            for sprite in self.sprites:
                if hasattr(sprite, 'bed'):
                    if (sprite.bed.x <= event.x() <= sprite.bed.x + sprite.bed.size and 
                    sprite.bed.y <= event.y() <= sprite.bed.y + sprite.bed.size):
                        self.heldSprite = sprite.bed
                        self.heldSpriteOffset = (sprite.bed.x-event.x(), sprite.bed.y-event.y())
                        break
        elif self.mousePressed:
            self.heldSprite.position.setX(round(event.x()+self.heldSpriteOffset[0]))
            self.heldSprite.position.setY(round(event.y()+self.heldSpriteOffset[1]))
    
    def mouseReleaseEvent(self, event):
        self.mousePressed = False
        self.heldSprite = None
        for sprite in self.sprites:
            if (sprite.x <= event.x() <= sprite.x + sprite.size and 
                sprite.y <= event.y() <= sprite.y + sprite.size):
                sprite.onClick()
                break

class Sprite:
    def __init__(self, pos=(0, 0), image=None, size=32):
        self.image = utils.scaleImage(image, size)
        self.position = QPoint(round(pos[0]), round(pos[1]))
        self.size = size
    
    def update(self):
        pass

    def onClick(self):
        pass

    def draw(self, painter):
        if self.image != None:
            painter.drawPixmap(self.x, self.y, self.image)

    @property
    def x(self):
        return self.position.x()
    
    @property
    def y(self):
        return self.position.y()

class Pet(Sprite):
    def __init__(self, imageRes=32, size=128):
        super().__init__((random.randint(0, win32api.GetSystemMetrics(0)-size), random.randint(0, win32api.GetSystemMetrics(1)-size)))
        self.size = size
        self.imageRes = imageRes
        self.growthMultiplier = 1
        self.hunger = 100
        self.happiness = 100
        self.energy = 100
        self.targetPosition = None
        self.frame = 0
        self.attemptingSleep = False
        self.sleeping = False
        self.lastDirection = (2, 2)

        self.bed = Bed()

        self.spriteName = 'bear'
        self.idleImage = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_2_i_0.png', self.size)
        self.setImage()  # Set initial image
        
        self.particles = []
    
    def update(self):
        self.frame += 1
        self.size = min(128, self.size+self.growthMultiplier/432000)

        if not self.sleeping:
            self.energy -= 0.01
            self.hunger -= 0.01
            self.happiness -= 0.01

        if self.energy <= 0 and self.targetPosition == None:
            self.energy = 0
            self.attemptingSleep = True
            self.targetPosition = QPoint(self.bed.position)
            self.idleImage = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_1_s_0.png', self.size)
        elif not self.isMoving and not self.sleeping:
            if random.random() < 0.02:
                self.setNewTarget()
        elif self.targetPosition != None:
            # Move towards target position
            dx = self.targetPosition.x() - self.position.x()
            dy = self.targetPosition.y() - self.position.y()
            distance = math.sqrt(dx**2 + dy**2)

            if distance < 200 and not self.attemptingSleep:
                self.targetPosition = None
            elif distance < 20 and self.attemptingSleep:
                self.energy += 20
                self.position = self.targetPosition
                self.targetPosition = None
            else:
                self.position.setX(round(self.position.x() + utils.clamp(utils.invClamp(dx*0.05, 3), self.size/2)))
                self.position.setY(round(self.position.y() + utils.clamp(utils.invClamp(dy*0.05, 3), self.size/2)))
        
        if self.targetPosition == None:
            self.idleImage = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_{self.lastDirection[0]}_{self.lastDirection[1]}_i_0.png', self.size)
        
        if self.attemptingSleep and self.targetPosition == None and self.position == self.bed.position:
            self.attemptingSleep = False
            self.sleeping = True
        
        if self.sleeping:
            self.idleImage = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_1_s_{"0" if self.frame%10 != 0 else "1"}.png', self.size)
            self.energy += 0.1
            if self.energy >= 100:
                self.sleeping = False
                self.energy = 100
                self.setNewTarget()
        
        for particle in self.particles:
            if not particle.dead:
                particle.update()
            else:
                self.particles.remove(particle)
        
        self.bed.update()

        self.setImage()
    
    def setImage(self):
        if self.directionMatrix == None:
            self.image = self.idleImage
        else:
            self.image = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_{self.directionMatrix[0]}_{self.directionMatrix[1]}_a_{self.frame%2}.png', self.size)

    def setNewTarget(self):
        newPos = self.newPos
        self.targetPosition = QPoint(newPos[0], newPos[1])
    
    def onClick(self):
        self.happiness = min(100, self.happiness + 20)
        self.particles.append(Particle((self.x+self.size, self.y), f'sprites/heart_{random.randint(0, 3)}.png'))

    def draw(self, painter):
        if self.image != None:
            self.bed.draw(painter)
            painter.drawPixmap(self.x, self.y, self.image)
            for particle in self.particles:
                if not particle.dead:
                    particle.draw(painter)

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
    
    @property
    def newPos(self):
        return (random.randint(0, win32api.GetSystemMetrics(0) - round(self.size)), random.randint(0, win32api.GetSystemMetrics(1) - round(self.size)))



class Bed(Sprite):
    def __init__(self):
        super().__init__((random.randint(0, win32api.GetSystemMetrics(0)-128), win32api.GetSystemMetrics(1)-144), 'sprites/bed.png', 128)
        self.held = False
        self.speedByGravity = 0

    def update(self):
        if self.y == win32api.GetSystemMetrics(1)-144:
            self.speedByGravity = 0
        else:
            self.speedByGravity += 9.8
        
        self.position.setY(round(self.y+self.speedByGravity))
        
    @property
    def y(self):
        return min(self.position.y(), win32api.GetSystemMetrics(1)-144)


class Particle(Sprite):
    def __init__(self, pos=(0, 0), image=None):
        super().__init__(pos, image)
        self.waviness = random.randint(5, 10)
        self.speed = random.randint(2, 5)
        self.origin = QPoint(round(pos[0]), round(pos[1]))
    
    def update(self):
        self.position.setY(self.position.y()-self.speed)

    @property
    def x(self):
        return self.origin.x()+round(self.waviness*math.sin(self.y-self.origin.y()))
    
    @property
    def dead(self):
        return self.position.y() <= -32



def main():
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()