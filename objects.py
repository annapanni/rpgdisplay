from state import feet
from copy import copy
import pygame
from math import sqrt

class Sprite():
    moving=False
    explorer=False
    def __init__(self, kep, meret, pos=(0,0)):
        a=pygame.image.load(kep)
        self.kep=pygame.transform.scale(a, meret)
        self.x, self.y= pos
    def rajzolas(self, surf):
        w,h=self.kep.get_size()
        surf.blit(self.kep, [self.x-w/2,self.y-h/2])
    def copy(self):
        return copy(self)

class Character (Sprite):
    moving=True
    def __init__(self, nev, kep, meret, pos=(0,0), direction=0, speed=30):
        self.nev=nev
        self.direction=direction
        self.speed=speed
        self.movebase=self.speed
        self.egyseg_x, self.egyseg_y, self.mozog=0,0,0
        Sprite.__init__(self, kep, meret, pos)
    def go_to(self, x,y):
        side1=abs(self.x-x)
        side2=abs(self.y-y)
        distance=sqrt(side1**2+side2**2)
        if distance<self.movebase*feet:
            self.mozog=round(distance/2)
            self.egyseg_x=(x-self.x)/(distance/2)
            self.egyseg_y=(y-self.y)/(distance/2)
            self.movebase+=-distance/feet
    def rajzolas(self,surf):
        self.x+=self.egyseg_x
        self.y+=self.egyseg_y
        self.mozog+=-1
        if self.mozog==0:
            self.egyseg_x= self.egyseg_y=0
        Sprite.rajzolas(self, surf)

class Player (Character):
    explorer=True
    def __init__(self, nev, kep, meret, pos=(0,0), direction=0, speed=30, sight="no"):
        self.sight=sight
        Character.__init__(self, nev, kep, meret, pos, direction, speed)

class Npc (Character):
    pass

hanne=Player("Hanne","hanne.jpg", (feet*5,feet*5), (200,150))
travis=Player("Travis","travis.png", (feet*5,feet*5), (400,300), sight="t")
lia=Player("Lia","lia.png", (feet*5,feet*5), (500,450), 0, 35, "dv")
gallindram=Player("Gallindram","gallindram.png", (feet*5,feet*5), (600,550), sight="dv")
trench=Player("Trench","trench.jpg", (feet*5,feet*5), (100,150), sight="dv")

orc=Npc( "Orc#1", "orc.png", (5*feet,5*feet), pos=(100,100))