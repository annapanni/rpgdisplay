from objects import *
from state import tokens, polygons, feet, dungeon, bckgr_music, enemies
import pygame, sys, time
from shadow import Obstacles
from pygame.locals import *
from copy import copy
pygame.init()

font = pygame.font.SysFont("comicsansms", 72)
font_small = pygame.font.SysFont("comicsansms", 24)

size = width, height = (1280,1024)
window = pygame.Rect(0,0,width,height)
formsize=(350,200)
menusize=size
scroll_step = 20*feet
screen = pygame.display.set_mode(size)
black = 0, 0, 0 , 255
white = 255, 255, 255 , 255
global_state= {"grid":False,
                "DM_mode":False,
                "walls":False,
                "enemy":False,
                "dead":False,
                "move":False,
                "turn": False}
to_move=None
fal=[]
chosen_enemy=(Npc(nev="Enemy#0", kep= 'enemy.png'))
keyboard={}

### Load tokens ###
cross=pygame.image.load("cross.png")
cross=pygame.transform.scale(cross, (6*feet, 6*feet))
sprites = []
enemylist=[]
for cs, state in tokens:
   tokenclass = globals()[cs] 
   sprites.append(tokenclass(**state))
for cs, state in enemies:
   tokenclass = globals()[cs] 
   enemylist.append(tokenclass(**state))
   
### Load Dungeon map ####
background = pygame.image.load(dungeon)
### Load walls ###
obstacles=Obstacles(polygons)

####Keyboard dict decorator###
def onkey (key, modes=["DM_mode", "Player_mode"]):
    def return_fnc(fnc):
        global keyboard
        for i in modes:
            if key not in keyboard.keys():
                keyboard[key]={}
            keyboard[key].update({i: fnc})
        return fnc
    return return_fnc


###Keyboard Functions###
@onkey(K_s)
def save_state():
    global polygons, sprites
    with open("state.py","w") as f:
        f.write("dungeon='{}'\n".format(dungeon))
        f.write("bckgr_music={}\n".format(bckgr_music))
        f.write("feet={}\n".format(feet))
        f.write("polygons={}\n".format(polygons))
        f.write("tokens=[\n")
        for s in sprites:
            f.write("('{}',{}),\n".format(type(s).__name__,s.state()))
        f.write("]\n")
        f.write("enemies=[\n")
        for s in enemylist:
            f.write("('{}',{}),\n".format(type(s).__name__,s.state()))
        f.write("]\n")

@onkey(K_w, modes=["DM_mode"])
def wall_drawer():  
    global fal, global_state
    global_state["walls"]= not global_state["walls"]
    fal=[]
    if global_state["walls"]==False:
        save_state()
        
@onkey(K_u, modes=["DM_mode"])
def undo_walls():
    global fal
    if global_state["walls"]:
        fal=fal[0:-1]

@onkey(K_SPACE, modes=["DM_mode"])
def add_walls():
    global fal
    if global_state["DM_mode"]:
        if global_state["walls"] and len(fal)>1:
            polygons.append(fal)
            fal=[]

@onkey(K_SPACE, modes=["Player_mode"])
def endturn():
    global global_state
    global_state["turn"]=False

@onkey(K_RETURN)
def endround():
    for sprite in sprites:
        if sprite.moving:
            sprite.movebase=sprite.speed

@onkey(K_t)
def add_torch():
    global onturn
    if onturn.sight=="no":
        onturn.sight="t"
    elif onturn.sight=="t":
        onturn.sight="no"

@onkey(K_UP)
def scroll_up():
    global window
    if window.y >= scroll_step: window.y -= scroll_step
@onkey(K_DOWN)
def scroll_down():
    global window
    window.y += scroll_step
@onkey(K_RIGHT)
def scroll_right():
    global window
    window.x += scroll_step
@onkey(K_LEFT)
def scroll_left():
    global window
    if window.x >= scroll_step: window.x -= scroll_step


def switch(var):
    def return_fnc():
        global global_state
        global_state[var]=not global_state[var]
    return return_fnc

onkey(K_F1)(switch("grid"))
onkey(K_m)(switch("move"))
onkey(K_d)(switch("dead"))

@onkey(K_F12)
def DM_mode():
    switch("DM_mode")()
    save_state()

def play_music(var):
    def return_fnc():
        try:
            pygame.mixer.music.load(bckgr_music[var])
            pygame.mixer.music.play(-1)
        except pygame.error:
            print ("nincs ilyen zene")
    return return_fnc
        
onkey(K_1)(play_music(0))
onkey(K_2)(play_music(1))
onkey(K_3)(play_music(2))
    
@onkey(K_TAB)
def enemy_menu():
    screen.blit(menu, [0,0])
    counter=0
    for oszlop in range(int(height/70)):
        for sor in range(int(width/70)):
            if counter==len(enemylist):
                break
            enemylist[counter].menurajzolas(screen, (sor*70, oszlop*70))
            enemylist[counter].x, enemylist[counter].y= sor*70+25, oszlop*70+25
            text = font_small.render((enemylist[counter].nev[0:7]), True, black)
            blit2screen(text,(sor*70, oszlop*70+50))
            counter+=1
        if counter==len(enemylist):
                break
        counter+=1
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my=pygame.mouse.get_pos()
                selected=select(enemylist, mx,my)
                if selected is not None:
                    global chosen_enemy
                    chosen_enemy=selected
                    global_state["enemy"]=True
                    return                
@onkey(K_ESCAPE)
def escape_enemy():
    global global_state
    global_state["enemy"]=False

##selector function
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

##Kiiro negyzet (form)
form=pygame.Surface(formsize)
form.fill(white)

##enemy-menu
menu=pygame.Surface(menusize)
menu.fill(white)

selector = Selector()
clock=pygame.time.Clock()

##main loop
while 1:
    for onturn in sprites:
        if onturn.moving:
            global_state["turn"]=True
            while global_state["turn"]:
                if global_state["DM_mode"]:
                    pygame.display.set_caption("DM mode")
                else:
                    pygame.display.set_caption("{}'s turn".format(onturn.nev))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        smx,smy=pygame.mouse.get_pos()
                        mx,my = smx+window.x, smy+window.y
                        if pygame.mouse.get_pressed()[2]:
                            selected=select(sprites, mx,my)
                            if selected is not None:
                                keys=pygame.key.get_pressed()
                                change=-1
                                if keys[K_LCTRL] or keys[K_RCTRL]:
                                    change=-10
                                if keys[K_LSHIFT] or keys[K_RSHIFT]:
                                    change=change*-1
                                selected.hp+=change   
                        else:
                            if global_state["DM_mode"]:
                                if global_state["walls"]:
                                    fal.append((mx,my))
                            if global_state["dead"]:
                                selected=select(sprites, mx,my)
                                if selected is not None:
                                    sprites.remove(selected)
                                    global_state["dead"]=False
                            elif global_state["move"]==True:
                                selected=select(sprites,mx,my)
                                if selected is not None:
                                    selector.go_to(selected.x,selected.y)
                                    to_move=selected
                                elif to_move is not None:
                                    to_move.x=mx
                                    to_move.y=my
                                    to_move=None
                                    global_state["move"]=False
                                    selector.visible = False
                            elif global_state["enemy"]:
                                e=copy(chosen_enemy)
                                e.x,e.y=mx,my
                                sprites.append(e)
                            else:
                                selected=select(sprites,mx,my)
                                if selected is not None:
                                    onturn=selected
                                else:
                                    onturn.go_to(mx,my)   
                    if event.type == pygame.KEYDOWN:
                        for key in keyboard.keys():
                            if key==event.key:
                                if global_state["DM_mode"]:
                                    mode="DM_mode"
                                else:
                                    mode="Player_mode"
                                if mode in keyboard[key].keys():
                                    keyboard[key][mode]()           
                            
        ##            Dungeon
                screen.blit(background, [0,0], window)
                darkness=basedarkness.copy()
        ##            Grid
                if global_state["grid"]:
                    for gridx in range(0,width,5*feet):
                        pygame.draw.line(screen, black,(gridx,0),(gridx,height),3)
                        pygame.draw.line(screen, white,(gridx,0),(gridx,height))
                    for gridy in range(0, height, 5*feet):
                        pygame.draw.line(screen, black,(0, gridy),(width,gridy),3)
                        pygame.draw.line(screen, white,(0, gridy),(width,gridy))
        ##            Movevbase-circle        
                if global_state["DM_mode"]==False:
                    mb=round(onturn.movebase*feet)
                    mb_circle=pygame.Surface((mb*2,mb*2),SRCALPHA)
                    pygame.draw.circle(mb_circle, (200,255,200,150), (mb,mb), mb)
                    blit2screen(mb_circle, (onturn.x-mb,onturn.y-mb))
        ##            Characters + light
                for sprite in sprites:
                    sprite.rajzolas(screen,(window.x,window.y))
                    if sprite.hp <= 0:
                        screen.blit(cross, (sprite.x-2.5*feet, sprite.y-3*feet))
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
                        arnyekok = obstacles.shadows(window, (sprite.x,sprite.y))
                        for shadow in arnyekok:
                            ts=[(x-pos[0],y-pos[1]) for x,y in shadow]
                            pygame.draw.polygon(light2, black, ts)
                        darkness.blit(light2,pos,None, BLEND_RGBA_MULT)
        ##            Walls/Darkness
                if global_state["DM_mode"]:
                    for wall in polygons:
                        tr_wall=[(x-window.x,y-window.y) for x,y in wall]
                        pygame.draw.polygon(screen,(0,255,0),tr_wall,1)
                    if global_state["walls"]:
                        for i in  range(len(fal)-1):
                            (x1,y1),(x2,y2) = fal[i], fal[i+1]
                            pygame.draw.line(screen, (0,0,255),(x1-window.x, y1-window.y),(x2-window.x,y2-window.y),3)   
                else:
                    screen.blit(darkness, (0,0), window)
        ##            Movebase-counter
                if global_state["DM_mode"]==False:
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
##                Stats kiiro négyzet (form)
                mx,my=pygame.mouse.get_pos()
                selected=select(sprites, mx,my)
                if selected is not None:
                    screen.blit(form, [mx,my])
                    text = font.render((selected.nev), True, black)
                    screen.blit(text, [mx+20, my+20])
                    to_render=["STR: "+ str(selected.stats["STR"]), "DEX: " + str(selected.stats["DEX"]), "CON: " +str(selected.stats["CON"])]
                    for key, value in enumerate(to_render):
                        text = font_small.render((str(value)), True, black)
                        screen.blit(text, [mx+20, my+30*(key+1)+50])
                    to_render=["INT: "+ str(selected.stats["INT"]), "WIS: " + str(selected.stats["WIS"]), "CHA: " +str(selected.stats["CHA"])]
                    for key, value in enumerate(to_render):
                        text = font_small.render((str(value)), True, black)
                        screen.blit(text, [mx+120, my+30*(key+1)+50])
                    text=font_small.render(("Hp: "+ str(selected.hp)), True, black)
                    screen.blit(text, [mx+220, my+80])
                    text=font_small.render(("AC: "+ str(selected.ac)), True, black)
                    screen.blit(text, [mx+220, my+110])
                    
                pygame.display.flip()
                clock.tick(30)
    for sprite in sprites:
        if sprite.moving:
            sprite.movebase=sprite.speed
