import pygame, sys, time
from pygame.locals import *
from math import sqrt
pygame.init()

size = width, height = (1000,800)
screen = pygame.display.set_mode(size)
black = 0, 0, 0 , 255
white = 255, 255, 255 , 255
feet=6

class Sprite():
    def __init__(self, nev, kep, meret, pos=(0,0), direction=0, speed=30):
        self.nev=nev
        self.kep=pygame.transform.scale(pygame.image.load(kep), meret)
        self.x, self.y= pos
        self.direction=direction
        self.speed=speed
        self.movebase=self.speed
        self.egyseg_x, self.egyseg_y, self.mozog=0,0,0
    def go_to(self, x,y):
        side1=abs(self.x-x)
        side2=abs(self.y-y)
        distance=sqrt(side1**2+side2**2)
        if distance<self.movebase*feet:
            self.mozog=round(distance/2)
            self.egyseg_x=(x-self.x)/(distance/2)
            self.egyseg_y=(y-self.y)/(distance/2)
            self.movebase+=-distance/feet
    def rajzolas(self):
        self.x+=self.egyseg_x
        self.y+=self.egyseg_y
        self.mozog+=-1
        if self.mozog==0:
            self.egyseg_x= self.egyseg_y=0
        w,h=self.kep.get_size()
        screen.blit(self.kep, [self.x-w/2,self.y-h/2])

##karakterek, hatter
travis=Sprite("Travis","travis.png", (feet*5,feet*5), (400,300), 0)
hanne=Sprite("Hanne","hanne.jpg", (feet*5,feet*5), (200,150), 0)
lia=Sprite("Lia","lia.png", (feet*5,feet*5), (500,450), 0, 35)
characters=[hanne,travis,lia]
dungeon = pygame.transform.scale(pygame.image.load("dungeon.jpg"), size)

##sötetseg
basedarkness=pygame.Surface(size, SRCALPHA)
basedarkness.fill(black)
darkrect= basedarkness.get_rect()

##feny
light=pygame.Surface((60*feet,60*feet),SRCALPHA)
light.fill(white)
lightrect=light.get_rect()
for i in range(250,0,-10):
    pygame.draw.ellipse(light, (255,255,255,i), lightrect, 0)
    lightrect = lightrect.inflate(-8,-8)



clock=pygame.time.Clock()
##main loop
while 1:
    for onturn in characters:
        pygame.display.set_caption("{}'s turn".format(onturn.nev))
        turn=True
        while turn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my=pygame.mouse.get_pos()
                    onturn.go_to(mx,my)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        turn=False
            screen.blit(dungeon, [0,0])
            darkness=basedarkness.copy()
            for character in characters:
                character.rajzolas()
                darkness.blit(light,(character.x-lightrect.centerx,character.y-lightrect.centery), None,BLEND_RGBA_MULT)
            screen.blit(darkness, (0,0))
            pygame.display.flip()
            clock.tick(30)
    for character in characters:
            character.movebase=character.speed