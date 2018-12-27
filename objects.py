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
        a=pygame.image.load(kep).convert_alpha()
        self.surface = pygame.transform.scale(a, (s,s))
        self.menusurface=pygame.transform.scale(a, (50,50))
        self.x, self.y= pos
    def rajzolas(self, surf, offset=(0,0)):
        w,h=self.surface.get_size()
        ox,oy=offset
        surf.blit(self.surface, [self.x-w/2-ox,self.y-h/2-oy])
    def menurajzolas(self, surf, pos=(0,0)):
        surf.blit(self.surface, pos)
    def copy(self):
        return copy(self)
    def state(self):
        return({'kep':self.kep, 'meret':self.meret, 'pos':self.pos})
    @property
    def pos(self): return (self.x, self.y)

class Character (Sprite):
    moving=True
    def __init__(self, nev="Unknown", direction=0, speed=30, maxhp=20, hp=20, stats=None, ac=10, **args):
        self.nev=nev
        self.direction=direction
        self.speed=speed
        self.movebase=self.speed
        self.egyseg_x, self.egyseg_y, self.mozog=0,0,0
        self.maxhp=maxhp
        self.hp=hp
        self.ac=ac
        if stats is None:
            self.stats={"STR":10,
                        "DEX":10,
                        "CON":10,
                        "INT":10,
                        "WIS":10,
                        "CHA":10}
        else:
            self.stats=stats
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
    def rajzolas(self,surf,offset=(0,0)):
        self.x+=self.egyseg_x
        self.y+=self.egyseg_y
        self.mozog+=-1
        if self.mozog==0:
            self.egyseg_x= self.egyseg_y=0
        Sprite.rajzolas(self, surf, offset)
    def state(self):
        st = {'nev':self.nev, 'direction':self.direction, 'speed':self.speed, "maxhp": self.maxhp, "hp":self.hp, "stats": self.stats}
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

class Selector(Sprite):
    def __init__(self, kep='selector.png'):
        self.surface = pygame.image.load(kep).convert_alpha()
        self.meret = 'M'
        self.go_to(0,0)
        self.counter = self.phase = 0
        self.visible = False
    def go_to(self,x,y):
        self.x, self.y = x,y
        self.visible = True
    def rajzolas(self, surf, offset):
        if not self.visible: return
        self.counter = (self.counter + 1) % 2
        w,h = self.surface.get_size()
        if self.counter == 0: self.phase = (self.phase + 1) % (w/h)
        ox,oy=offset
        surf.blit(self.surface, [self.x-h/2-ox,self.y-h/2-oy], pygame.Rect(h*self.phase,0,h,h))
