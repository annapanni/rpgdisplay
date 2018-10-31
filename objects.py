from state import feet
from copy import copy
import pygame
from math import sqrt

class Sprite():
    size = {'S':3, 'M':5, 'L': 10, 'H': 15}
    moving=False
    explorer=False
    def __init__(self, kep='default.png', meret='M', pos=(0,0)):
        self.meret = meret
        s = feet*self.size[meret]
        self.kep=kep
        a=pygame.image.load(kep)
        self.surface = pygame.transform.scale(a, (s,s))
        self.x, self.y= pos
    def rajzolas(self, surf):
        w,h=self.surface.get_size()
        surf.blit(self.surface, [self.x-w/2,self.y-h/2])
    def copy(self):
        return copy(self)
    def state(self):
        return({'kep':self.kep, 'meret':self.meret, 'pos':self.pos})
    @property
    def pos(self): return (self.x, self.y)

class Character (Sprite):
    moving=True
    def __init__(self, nev="Unknown", direction=0, speed=30, **args):
        self.nev=nev
        self.direction=direction
        self.speed=speed
        self.movebase=self.speed
        self.egyseg_x, self.egyseg_y, self.mozog=0,0,0
        Sprite.__init__(self, **args)
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
    def state(self):
        st = {'nev':self.nev, 'direction':self.direction, 'speed':self.speed}
        st.update(super().state())
        return st

class Player (Character):
    explorer=True
    def __init__(self, sight="no", **args):
        self.sight=sight
        Character.__init__(self, **args)
    def __repr__(self):
        return("Player({})".format(self.nev))
    def state(self):
        st = super().state()
        st.update({'sight':self.sight})
        return st


class Npc (Character):
    pass

