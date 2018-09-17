import pygame
from SwarmNode import SwarmNode, RandomVector2
from pygame.locals import *
from pygame import Vector2

import sys, math, random


pygame.init()
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode((640,640))
fontObj = pygame.font.Font('freesansbold.ttf', 16)


zoom = 200 # Pixels / meter
center = Vector2(0, 0)
collective = []
obstacles = [(Vector2(0,0), 0.5)]

for i in range(200):
    SwarmNode(collective, obstacles, position=RandomVector2(-1, 1))

dt = 0.001
drag = False
while True:
    screen.fill(pygame.Color(255, 255, 255))

    for obs in obstacles:
        w, h = screen.get_size()
        w /= 2
        h /= 2
        w -= center.x * zoom
        h -= center.y * zoom
        pos, r = obs
        pos *= zoom
        x = int(pos.x+w)
        y = int(pos.y+h)
        r = int(r*zoom)
        pygame.draw.circle(screen, pygame.Color(0,127,0),(x,y), r, 0)

    for node in collective:
        node.update(dt)
        node.draw(screen, center, zoom)

    msgSurf = fontObj.render("Nodes: %i, FPS: %i" % (len(collective), 1/dt), False, pygame.color.Color(0,0,0))
    msgRect = msgSurf.get_rect()
    msgRect.topleft = (5,5)
    screen.blit(msgSurf, msgRect)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 4:
                zoom = min(640, zoom+10)
            elif event.button == 5:
                zoom = max(0, zoom-10)
            elif event.button == 1:
                drag = True
                pygame.mouse.get_rel()
            elif event.button == 3:
                mousex, mousey = pygame.mouse.get_pos()
                x = ((mousex-320) / zoom)+center.x
                y = ((mousey-320) / zoom)+center.y
                SwarmNode(collective, obstacles, position=Vector2(x,y))
                print("New node at: (%i, %i)" % (x,y))
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                drag = False

        elif event.type == MOUSEMOTION:
            if drag:
                dx, dy = pygame.mouse.get_rel()
                center -= Vector2(dx, dy) * 0.01
    pygame.display.update()
    dt = fpsClock.tick(100)/1000
