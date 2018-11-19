#!/usr/bin/python

import math
import pygame
from shadow import *
from pygame.locals import *
from pygame.math import Vector2
import state

polygons = [[Vector2(p) for p in poly] for poly in state.polygons]


screensize = 1000,1000 
white = (255,255,255)

pygame.init()
screen = pygame.display.set_mode(screensize)
pygame.display.set_caption('Python shadow test')

polysurf = pygame.Surface(screensize)
polysurf.fill((0, 0, 0))
# draw polys
for p in polygons :
    pygame.draw.polygon(polysurf, white, p, 0)

shadowmap = pygame.Surface(screensize, SRCALPHA)

#### Main loop ####
runme = True
clock = pygame.time.Clock()
counter = 0

newpoly = []

obstacles = Obstacles(polygons)

while runme:
    for event in pygame.event.get():
        if event.type == QUIT:
            runme = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                runme = False
            if event.key == K_RETURN:
                polygons.append(newpoly)
                pygame.draw.polygon(polysurf, white, newpoly, 0)
                newpoly = []
            if event.key == K_s:
                with open("polygons.py","w") as f:
                    f.write("polygons = ")
                    f.write(repr(polygons))

        if event.type == MOUSEBUTTONDOWN:
            point = pygame.mouse.get_pos()
            newpoly.append(point)
            

    screen.blit(polysurf, (0,0))
    light = pygame.mouse.get_pos()

    ### draw shadows
    shadowmap.fill((0, 0, 0, 0))

    shadowlist, edgelist = obstacles.shadows((light[0]-1500,light[1]-1500,3000,3000),light, debug=True)

    for s in shadowlist:
        pygame.draw.polygon(shadowmap, (0,0,255,255), s, 0)

    pygame.draw.circle(screen, (0,255,0), light, 10, 2) 
    screen.blit(shadowmap, (0,0))
    
    ### draw active debug edges
    for e in edgelist:
        pygame.draw.line(screen,(255,0,0), 
                (e[0][0] , e[0][1] ) , 
                (e[1][0] , e[1][1] ),3)

    # show newpoly
    if len(newpoly) > 0 : pp = newpoly[0]
    for p in newpoly:
        pygame.draw.line(screen,(255,0,0), pp,p)
        pp = p
        

    pygame.display.flip()
    clock.tick(50)
    counter+=1
    if not counter % 20 : print(clock.get_fps())

