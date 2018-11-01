from objects import *
from state import tokens, polygons, feet, dungeon
import pygame, sys, time
from shadow import shadows
from pygame.locals import *
pygame.init()

font = pygame.font.SysFont("comicsansms", 72)
font_small = pygame.font.SysFont("comicsansms", 24)

size = width, height = (1280,1024)
window = pygame.Rect(0,0,width,height)
scroll_step = 20*feet
screen = pygame.display.set_mode(size)
black = 0, 0, 0 , 255
white = 255, 255, 255 , 255
grid=False
DM_mode=False
walls=False
enemy=False
enemynumber=0
dead=False
move=False

### Load tokens ###
sprites = []
for cs, state in tokens:
   tokenclass = globals()[cs] 
   sprites.append(tokenclass(**state))

### Load Dungeon map ####
background = pygame.image.load(dungeon)

def save_state(poligons, sprites):
    with open("state.py","w") as f:
        f.write("dungeon='{}'\n".format(dungeon))
        f.write("feet={}\n".format(feet))
        f.write("polygons={}\n".format(poligons))
        f.write("tokens=[\n")
        for s in sprites:
            f.write("('{}',{}),\n".format(type(s).__name__,s.state()))
        f.write("]\n")

def select(sprites, mx,my):
    susp=None
    susp_num=2.5*feet
    for sprite in sprites:
        side1=abs(sprite.x-mx)
        side2=abs(sprite.y-my)
        distance=sqrt(side1**2+side2**2)
        if distance<susp_num:
            susp=sprite
            susp_num=distance
    return susp

def blit2screen(what, where, *arg, **darg):
    screen.blit(what,(where[0]-window.x, where[1]-window.y), *arg, **darg)


##sötetseg
basedarkness=pygame.Surface(background.get_size(), SRCALPHA)
basedarkness.fill(black)

##feny
def light (rect):
    temprect=rect.copy()
    light=pygame.Surface((rect.width, rect.height),SRCALPHA)
    light.fill(white)
    fenycsokken=-round(rect.width/100)*2
    for i in range(250,0,-10):
        pygame.draw.ellipse(light, (255,255,255,i), temprect, 0)
        temprect= temprect.inflate(fenycsokken,fenycsokken)
    return light

lightrect_dv=Rect(0,0,120*feet,120*feet)
lightrect_t=Rect(0,0,60*feet,60*feet)
light_dv=light(lightrect_dv)
light_t=light(lightrect_t)

selector = Selector()

clock=pygame.time.Clock()
##main loop
while 1:
    for onturn in sprites:
        if onturn.moving:
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
                        smx,smy=pygame.mouse.get_pos()
                        mx,my = smx+window.x, smy+window.y
                        if DM_mode:
                            if walls:
                                fal.append((mx,my))
                        if dead:
                            selected=select(sprites, mx,my)
                            if selected is not None:
                                sprites.remove(selected)
                                dead=False
                        elif move==True:
                            selected=select(sprites,mx,my)
                            if selected is not None:
                                selector.go_to(selected.x,selected.y)
                                move=selected
                        elif move !=False:
                                move.x=mx
                                move.y=my
                                move=False
                                selector.visible = False
                        elif enemy:
                            enemynumber+=1
                            nmi = Npc(nev="nmi"+str(enemynumber), kep="orc.png", meret='M', pos=(mx,my))
                            sprites.append(nmi)
                            enemy=False
                        else:
                            onturn.go_to(mx,my)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if DM_mode:
                                if walls and len(fal)>1:
                                    polygons.append(fal)
                                    fal=[]
                            else:
                                turn=False
                        if event.key == K_F1:
                            grid= not grid
                        if event.key == K_s: # savegame
                            save_state(polygons,sprites)
                        if event.key==K_F12:
                            DM_mode= not DM_mode
                            save_state(polygons,sprites)
                        if DM_mode:
                            if event.key==K_w:
                                walls=not walls
                                fal=[]
                                if walls==False:
                                    save_state(polygons,sprites)
                            if event.key==K_u:
                                if walls:
                                    fal=fal[0:-1] 
                        if event.key==K_t:
                            if onturn.sight=="no":
                                onturn.sight="t"
                            elif onturn.sight=="t":
                                onturn.sight="no"
                        if event.key==K_e:
                            enemy=not enemy
                        if event.key==K_d:
                            dead=not dead
                        if event.key==K_m:
                            move=not move
                        if event.key==K_UP:
                            if window.y >= scroll_step: window.y -= scroll_step
                        if event.key==K_DOWN:
                            window.y += scroll_step
                        if event.key==K_LEFT:
                            if window.x >= scroll_step: window.x -= scroll_step
                        if event.key==K_RIGHT:
                            window.x += scroll_step
        ##            Dungeon
                screen.blit(background, [0,0], window)
                darkness=basedarkness.copy()
        ##            Grid
                if grid:
                    for gridx in range(0,width,5*feet):
                        pygame.draw.line(screen, black,(gridx,0),(gridx,height),3)
                        pygame.draw.line(screen, white,(gridx,0),(gridx,height))
                    for gridy in range(0, height, 5*feet):
                        pygame.draw.line(screen, black,(0, gridy),(width,gridy),3)
                        pygame.draw.line(screen, white,(0, gridy),(width,gridy))
        ##            Movevbase-circle        
                if DM_mode==False:
                    mb=round(onturn.movebase*feet)
                    mb_circle=pygame.Surface((mb*2,mb*2),SRCALPHA)
                    pygame.draw.circle(mb_circle, (200,255,200,150), (mb,mb), mb)
                    blit2screen(mb_circle, (onturn.x-mb,onturn.y-mb))
        ##            Characters + light
                for sprite in sprites:
                    sprite.rajzolas(screen,(window.x,window.y))
                    if sprite.moving:
                        text = font_small.render((sprite.nev), True, (0,150,255))
                        blit2screen(text,(sprite.x+2*feet, sprite.y+2*feet))
                    if sprite.explorer:
                        if sprite.sight=="dv":
                            light=light_dv
                            lightrect=lightrect_dv
                        elif sprite.sight=="t":
                            light=light_t
                            lightrect=lightrect_t
                        else:
                            continue
                        light2=light.copy()
                        pos=(sprite.x-lightrect.centerx,sprite.y-lightrect.centery)
                        arnyek=shadows(polygons, (sprite.x,sprite.y), 1000)
                        for shadow in arnyek:
                            ts=[(x-pos[0],y-pos[1]) for x,y in shadow]
                            pygame.draw.polygon(light2, black, ts)
                        darkness.blit(light2,pos,None, BLEND_RGBA_MULT)
        ##            Walls/Darkness
                if DM_mode:
                    for wall in polygons:
                        tr_wall=[(x-window.x,y-window.y) for x,y in wall]
                        pygame.draw.polygon(screen,(0,255,0),tr_wall,1)
                    if walls:
                        for i in  range(len(fal)-1):
                            (x1,y1),(x2,y2) = fal[i], fal[i+1]
                            pygame.draw.line(screen, (0,0,255),(x1-window.x, y1-window.y),(x2-window.x,y2-window.y),3)   
                else:
                    screen.blit(darkness, (0,0), window)
        ##            Movebase-counter
                if DM_mode==False:
                    smx,smy=pygame.mouse.get_pos()
                    mx,my=smx-window.x,smy-window.y
                    side1=abs(onturn.x-mx)
                    side2=abs(onturn.y-my)
                    distance=sqrt(side1**2+side2**2)
                    maradek=onturn.movebase-distance/feet
                    if maradek>=0:
                        text = font.render(str(round(maradek)), True, (0,255,0))
                    else:
                        text = font.render(str(round(maradek)), True, (255,0,0))
                    screen.blit(text,(15,10))
                selector.rajzolas(screen,(window.x, window.y))
                pygame.display.flip()
                clock.tick(30)
    for sprite in sprites:
        if sprite.moving:
            sprite.movebase=sprite.speed
