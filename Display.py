import pygame, sys, time
from state import polygons
from shadow import shadows
from pygame.locals import *
from math import sqrt
pygame.init()

size = width, height = (1000,800)
screen = pygame.display.set_mode(size)
black = 0, 0, 0 , 255
white = 255, 255, 255 , 255
grid=False
DM_mode=False
walls=False
feet=6

def ment_poly(l):
    with open("state.py","w") as f:
        f.write("polygons=")
        f.write(repr(l))
        f.write("\n")

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
##hanne=Sprite("Hanne","hanne.jpg", (feet*5,feet*5), (200,150), 0)
##lia=Sprite("Lia","lia.png", (feet*5,feet*5), (500,450), 0, 35)
##gallindram=Sprite("Gallindram","gallindram.png", (feet*5,feet*5), (600,550), 0)
##trench=Sprite("Trench","trench.jpg", (feet*5,feet*5), (100,150), 0)
characters=[travis]
dungeon = pygame.transform.scale(pygame.image.load("dungeon2.jpg"), size)

##sötetseg
basedarkness=pygame.Surface(size, SRCALPHA)
basedarkness.fill(black)
darkrect= basedarkness.get_rect()

##feny
light=pygame.Surface((60*feet,60*feet),SRCALPHA)
light.fill(white)
lightrect=light.get_rect()
fenycsokken=-round(feet/3)*2
for i in range(250,0,-10):
    pygame.draw.ellipse(light, (255,255,255,i), lightrect, 0)
    lightrect = lightrect.inflate(fenycsokken,fenycsokken)



clock=pygame.time.Clock()
##main loop
while 1:
    for onturn in characters:
        turn=True
        while turn:
            if DM_mode:
                pygame.display.set_caption("DM mode")
            else:
                pygame.display.set_caption("{}'s turn".format(onturn.nev))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my=pygame.mouse.get_pos()
                    if DM_mode:
                        if walls:
                            fal.append((mx,my))
                    else:
                        onturn.go_to(mx,my)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if DM_mode:
                            if walls:
                                polygons.append(fal)
                                fal=[]
                        else:
                            turn=False
                    if event.key==K_u:
                        if walls:
                            fal=fal[0:-1]
                    if event.key == K_F1:
                        grid= not grid
                    if event.key==K_F12:
                        DM_mode= not DM_mode
                        ment_poly(polygons)
                    if DM_mode and event.key==K_w:
                        walls=not walls
                        fal=[]
                        if walls==False:
                            ment_poly(polygons)
            screen.blit(dungeon, [0,0])
            darkness=basedarkness.copy()
            if grid:
                for gridx in range(0,width,5*feet):
                    pygame.draw.line(screen, black,(gridx,0),(gridx,height),3)
                    pygame.draw.line(screen, white,(gridx,0),(gridx,height))
                for gridy in range(0, height, 5*feet):
                    pygame.draw.line(screen, black,(0, gridy),(width,gridy),3)
                    pygame.draw.line(screen, white,(0, gridy),(width,gridy))
            for character in characters:
                character.rajzolas()
                light2=light.copy()
                pos=(character.x-lightrect.centerx,character.y-lightrect.centery)
                arnyek=shadows(polygons, (character.x,character.y))
                for shadow in arnyek:
                    ts=[(x-pos[0],y-pos[1]) for x,y in shadow]
                    pygame.draw.polygon(light2, black, ts)
                darkness.blit(light2,pos, None,BLEND_RGBA_MULT)
            if DM_mode:
                for wall in polygons:
                    pygame.draw.polygon(screen,(255,0,0),wall)
                if walls:
                    for i in  range(len(fal)-1):
                         pygame.draw.line(screen, (0,0,255),fal[i],fal[i+1],3)   
            else:
                screen.blit(darkness, (0,0))
            pygame.display.flip()
            clock.tick(30)
    for character in characters:
            character.movebase=character.speed