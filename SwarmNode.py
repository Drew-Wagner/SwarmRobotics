import pygame
from pygame.locals import *
from pygame import Vector2
import math, sys, random

def RandomVector2(minimum, maximum):
    return pygame.Vector2(random.uniform(minimum, maximum), random.uniform(minimum, maximum))


STATE_TO_COLOR = {
    0: pygame.Color(0,0,0),
    1: pygame.Color(255,0,0),
    2: pygame.Color(0,0,255)
}

NODE_RADIUS = 0.1 # In Meters
NODE_DIAMETER = NODE_RADIUS*2
CROWDING_DISTANCE = NODE_RADIUS*5
MAX_SPEED = 3*NODE_RADIUS  # in Meters / second
MAX_NEIGHBOURS = 5
MAX_VIEW_DIST = 10*NODE_DIAMETER
ANGRY = 5
LONELY = 1


class SwarmNode(object):

    def __init__(self, collective, obstacles, position=Vector2(0,0)):
        self.collective = collective
        self.obstacles = obstacles
        self.position = position
        self.velocity = RandomVector2(-MAX_SPEED, MAX_SPEED)
        self.state = 0

        self.neighbours = []
        self.collective.append(self)

    def set_position(self, new_position):
        self.position = new_position

    def move(self, offset):
        self.position += offset

    def set_velocity(self, new_velocity):
        self.velocity = new_velocity

    def find_neighbours(self):
        collective_by_distance = sorted(
            [(node, (node.position-self.position).normalize(), self.position.distance_to(node.position)) \
                                         for node in self.collective if node is not self and self.position.distance_to(node.position) < MAX_VIEW_DIST],
            key=lambda x: x[2])
        if len(collective_by_distance) > MAX_NEIGHBOURS:
            self.neighbours = collective_by_distance[:MAX_NEIGHBOURS]
        else:
            self.neighbours = collective_by_distance

    def draw(self, surf, center, zoom):
        w, h = surf.get_size()
        w /= 2
        h /= 2
        w -= center.x*zoom
        h -= center.y*zoom
        pygame.draw.circle(surf, STATE_TO_COLOR[self.state], (int((self.position.x*zoom)+w), int(self.position.y*zoom+h)), int(NODE_RADIUS*zoom), int(0.05*zoom))

    def update(self, dt):
        self.find_neighbours()
        # Local logic goes here
        if len(self.neighbours) > 0:
            new_vel = Vector2(0, 0)
            crowding = 0
            for node, dir, dist in self.neighbours:
                d = dist-CROWDING_DISTANCE
                if d < 0:
                    crowding += 1
                if crowding >= ANGRY:
                    self.state = 1
                elif crowding > LONELY:
                    self.state = 0
                else:
                    self.state = 2
                if node.state == 2:
                    new_vel += 3*abs(d)*dir
                elif node.state == 1:
                    new_vel += -5*abs(d)*dir
                else:
                    new_vel += d*dir

            self.velocity = new_vel.normalize()*MAX_SPEED
        else:
            self.state = 2
            if random.randint(0, 100) == 0:
                self.velocity = RandomVector2(-MAX_SPEED, MAX_SPEED)

        # Move according to velocity
        self.move(dt * self.velocity)

        # Check collisions
        for obs in self.obstacles:
            dir = (obs[0] - self.position)
            dist = dir.length()
            dir = dir.normalize()
            if dist < NODE_RADIUS+obs[1]:
                self.move(-dir*((NODE_RADIUS+obs[1])-dist))

        for node in self.collective:
            if node is not self:
                dir = (node.position - self.position)
                dist = dir.length()
                dir = dir.normalize()
                if dist < NODE_DIAMETER:
                    self.move(-dir*(NODE_DIAMETER-dist))
