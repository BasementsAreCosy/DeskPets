##### My Libs #####
import sprite
import utils

##### Other Libs #####
import uuid
import time
import sys
import json
import math
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter
import win32gui
import win32con
import win32api
from pathlib import Path


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        if Path('petData.json').exists():
            try:
                with open('petData.json', 'r') as f:
                    spriteData = dict(json.load(f))
            except:
                pass
        else:
            with open('petData.json', 'w') as f:
                json.dump({}, f)
                spriteData = {}

        self.sprites = []
        for key in spriteData.keys():
            self.sprites.append(Pet(ID=key, size=spriteData[key]['size'], hunger=spriteData[key]['hunger'], happiness=spriteData[key]['happiness'], energy=spriteData[key]['energy'], offlineTime=time.time()-spriteData[key]['lastSave']))
        
        if self.sprites == []:
            self.sprites.append(Pet())
            self.sprites.append(Pet())
            self.sprites.append(Pet())
            self.sprites.append(Pet())
            self.sprites.append(Pet())

        self.mousePressed = False
        self.heldSprite = None
        self.heldSpriteOffset = (0, 0)

        self.frame = 0
        self.FPS = 120
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateScr)
        self.updateTimer.start(1000//self.FPS)

        self.autosaveTimer = QTimer(self)
        self.autosaveTimer.timeout.connect(self.save)
        self.autosaveTimer.start(10000)
    
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
    
    def save(self):
        petDict = {}
        for pet in self.sprites:
            petDict[pet.ID] = {}
            petDict[pet.ID]['size'] = pet.size
            petDict[pet.ID]['hunger'] = pet.hunger
            petDict[pet.ID]['happiness'] = pet.happiness
            petDict[pet.ID]['energy'] = pet.energy
            petDict[pet.ID]['lastSave'] = time.time()
        with open('petData.json', 'w') as f:
            jsonObj = json.dumps(petDict, indent=4)
            f.write(jsonObj)
    
    def updateScr(self):
        self.frame += 1
        for sprite in self.sprites:
            for child in sprite.children:
                if self.frame%max(1, self.FPS//child.updatesPerSecond) == 0:
                    child.update()
            if self.frame%max(1, self.FPS//sprite.updatesPerSecond) == 0:
                sprite.update()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)

        for sprite in self.sprites:
            for child in sprite.children: # todo: intro layers for foreground/background objs
                child.draw(painter)
            sprite.draw(painter)
    
    def mousePressEvent(self, event):
        self.mousePressed = True
    
    def mouseMoveEvent(self, event):
        if self.mousePressed and self.heldSprite == None:
            for sprite in self.sprites:
                if sprite.holdable:
                    if (sprite.x <= event.x() <= sprite.x + sprite.size and 
                        sprite.y <= event.y() <= sprite.y + sprite.size):
                        self.heldSprite = sprite
                        sprite.held = True
                        self.heldSpriteOffset = (sprite.x-event.x(), sprite.y-event.y())
                        break
                for child in sprite.children:
                    if child.holdable:
                        if (child.x <= event.x() <= child.x + child.size and 
                            child.y <= event.y() <= child.y + child.size):
                            self.heldSprite = child
                            child.held = True
                            self.heldSpriteOffset = (child.x-event.x(), child.y-event.y())
                            break
        elif self.mousePressed:
            self.heldSprite.position.setX(round(event.x()+self.heldSpriteOffset[0]))
            self.heldSprite.position.setY(round(event.y()+self.heldSpriteOffset[1]))
    
    def mouseReleaseEvent(self, event):
        self.mousePressed = False
        if self.heldSprite != None:
            self.heldSprite.held = False
        self.heldSprite = None
        for sprite in self.sprites:
            if (sprite.x <= event.x() <= sprite.x + sprite.size and 
                sprite.y <= event.y() <= sprite.y + sprite.size):
                sprite.onClick()
                break
            for child in sprite.children:
                if (child.x <= event.x() <= child.x + child.size and 
                    child.y <= event.y() <= child.y + child.size):
                    child.onClick()
                    break

class Pet(sprite.Sprite):
    def __init__(self, ID=None, pos=(0, 0), image=None, imageRes=32, size=32, hunger=100, happiness=100, energy=100, updatesPerSecond=60, offlineTime=0):
        self.size = size
        super().__init__(self.newPos, image, size, updatesPerSecond)

        if ID == None:
            self.ID = uuid.uuid4().hex
        else:
            self.ID = ID
        
        self.imageRes = imageRes

        self.growthMultiplier = 1
        self.hungerMultiplier = 1
        self.happinessMultiplier = 1
        self.energyMultiplier = 1

        self.size = min(128, size+offlineTime*5*self.growthMultiplier/432000)
        self.hunger = max(0, hunger-0.01*self.hungerMultiplier*offlineTime*5)
        self.happiness = max(0, happiness-0.01*self.happinessMultiplier*offlineTime*5)
        self.energy = max(0, energy-0.01*self.energyMultiplier*offlineTime*5)

        self.targetPosition = None
        self.updatesSinceBoot = 0
        self.attemptingSleep = False
        self.sleeping = False
        self.lastDirection = (2, 2)

        self.spriteName = 'bear'
        self.idleImage = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_2_i_0.png', self.size)
        self.setImage()  # Set initial image

        self.children = [Bed()]
    
    def update(self):
        self.updatesSinceBoot += 1
        if self.happiness != 0:
            self.size = min(128, self.size+self.growthMultiplier/432000)

        if not self.sleeping:
            self.energy = max(0, self.energy-0.01*self.energyMultiplier)
            self.hunger = max(0, self.hunger-0.01*self.hungerMultiplier)
            self.happiness = max(0, self.happiness-0.01*self.happinessMultiplier)

        if self.energy == 0:
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
                self.position = self.targetPosition
                self.targetPosition = None
            else:
                self.position.setX(round(self.position.x() + utils.clamp(utils.invClamp(dx*0.05, 3), self.size/2)))
                self.position.setY(round(self.position.y() + utils.clamp(utils.invClamp(dy*0.05, 3), self.size/2)))
        
        if self.targetPosition == None:
            self.idleImage = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_{self.lastDirection[0]}_{self.lastDirection[1]}_i_0.png', self.size)
        
        if self.attemptingSleep and self.position == self.bed.position:
            self.attemptingSleep = False
            self.sleeping = True
        
        if self.sleeping:
            self.idleImage = utils.scaleImage(f'{self.spriteName}x{self.imageRes}/{self.spriteName}_1_1_s_{"0" if self.updatesSinceBoot%10 != 0 else "1"}.png', self.size)
            self.energy += 0.1
            if self.energy >= 100:
                self.sleeping = False
                self.energy = 100
                self.setNewTarget()
        
        for child in self.children:
            if child.dead:
                self.children.remove(child)

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
        self.setNewTarget()
        self.happiness = min(100, self.happiness + 20)
        self.children.append(Particle((self.x+self.size, self.y), f'sprites/heart_{random.randint(0, 3)}.png'))
    
    def draw(self, painter):
        if self.image != None:
            painter.drawPixmap(self.x, self.y, self.image)
    
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

    @property
    def speed(self):
        return (1-(self.size/128))
    

class Bed(sprite.Sprite):
    def __init__(self):
        super().__init__(pos=(random.randint(0, win32api.GetSystemMetrics(0)-128), win32api.GetSystemMetrics(1)-144), image='sprites/bed.png', size=128, holdable=True, updatesPerSecond=60)
        self.speedByGravity = 0

    def update(self):
        if self.y == win32api.GetSystemMetrics(1)-144 or self.held:
            self.speedByGravity = 0
        else:
            self.speedByGravity += 9.8/self.updatesPerSecond
        
        self.position.setY(round(self.y+self.speedByGravity))
        
    @property
    def y(self):
        return min(self.position.y(), win32api.GetSystemMetrics(1)-144)

class Particle(sprite.Sprite):
    def __init__(self, pos=(0, 0), image=None):
        super().__init__(pos=pos, image=image)
        self.waviness = random.randint(50, 100)
        self.speed = random.randint(2, 5)
        self.origin = QPoint(round(pos[0]), round(pos[1]))
    
    def update(self):
        self.position.setY(round(self.position.y()-max(1, self.speed/self.updatesPerSecond)))

    @property
    def x(self):
        return self.origin.x()+round(self.waviness*math.sin((self.y-self.origin.y())/self.updatesPerSecond))
    
    @property
    def dead(self):
        return self.position.y() <= -32