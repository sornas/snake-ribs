import sys
import math

from ribs import *
from dataclasses import dataclass

# Asset dictionary for holding all your assets.
assets = {}
shots = []

def vec_len(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2)

def clamp(val, low, high):
    return min(max(val, low), high)

@dataclass
class Shot:
    centerx = 0
    centery = 0
    width = 5
    height = 5
    
    velocity = (0, 0)
    owner = None # shooter's id()

def update_shot(shot, delta):
    shot.centerx += shot.velocity[0] * delta
    shot.centery += shot.velocity[1] * delta
    return True

def draw_shot(shot):
    window = pg.display.get_surface()
    pg.draw.rect(window, pg.Color(30, 30, 100), (shot.centerx - shot.width / 2,
                                                 shot.centery - shot.height / 2,
                                                 shot.width,
                                                 shot.height))

@dataclass
class Player:
    centerx = 0
    centery = 0
    width = 20
    height = 20
    min_width = 1
    min_height = 1
    gesmol_speeed = 0.5
    small = False

    velocity = (0, 0)

    walk_acc = 1000.0
    max_speed = 250
    slow_down = 4
    shot_speed = 100

def update_player(player, delta):
    dx, dy = (0, 0)
    if key_down("a"):
        dx -= 1
    if key_down("d"):
        dx += 1
    if key_down("w"):
        dy -= 1
    if key_down("s"):
        dy += 1

    player.velocity = (player.velocity[0] + (dx * player.walk_acc * delta),
                       player.velocity[1] + (dy * player.walk_acc * delta))

    # y u tuple :(
    # ** delta ?
    player.velocity = (player.velocity[0] + player.velocity[0] * -player.slow_down * delta,
                       player.velocity[1] + player.velocity[1] * -player.slow_down * delta)

    if (speed := vec_len(player.velocity)) > player.max_speed:
        player.velocity = ((player.velocity[0] * (player.max_speed / speed)),
                           (player.velocity[1] * (player.max_speed / speed)))

    player.centerx += player.velocity[0] * delta
    player.centery += player.velocity[1] * delta

    if not player.small and key_down(" "):
        player.small = True

    if key_down("c"):
        # shoot
        player_speed = vec_len(player.velocity)
        if player_speed != 0:
            shot = Shot()
            shot.centerx = player.centerx
            shot.centery = player.centery
            shot.owner = id(player)
            shot.velocity = (player.velocity[0] * (player.shot_speed / player_speed),
                             player.velocity[1] * (player.shot_speed / player_speed))
            shots.append(shot)


    if player.small and player.width > player.min_width:
        player.width -= player.gesmol_speeed
    if player.small and player.height > player.min_height:
        player.height -= player.gesmol_speeed

def draw_player(player):
    window = pg.display.get_surface()
    pg.draw.rect(window, pg.Color(100, 30, 30), (player.centerx - player.width / 2,
                                                 player.centery - player.height / 2,
                                                 player.width,
                                                 player.height))

# square
LEVEL = \
"""
##########
#        #
#        #
#        #
# S      #
#      S #
#        #
#        #
#        #
##########
"""

def parse_level(level_string):
    GRID_SIZE = 40

    walls = []
    starts = []

    level_lines = level_string.strip().split("\n")
    for tile_y, line in enumerate(level_lines):
        y = tile_y * GRID_SIZE
        for tile_x, c in enumerate(line):
            x = tile_x * GRID_SIZE
            r = pg.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if c == "#":
                # It's a wall
                walls.append(r)
            elif c == "S":
                # It's the start
                starts.append((x, y))

    return walls, starts


def init():
    """ A function for loading all your assets.
        (Audio assets can at their earliest be loaded here.)
    """
    # Load images here
    assets["teapot"] = pg.image.load("teapot.png")

    # Load sounds here
    assets["plong"] = pg.mixer.Sound("plong.wav")


def update():
    """The program starts here"""
    # Initialization (only runs on start/restart)
    player = Player()

    walls, start = parse_level(LEVEL)
    player.centerx = start[0][0]
    player.centery = start[0][1]

    # Main update loop
    while True:
        update_player(player, delta())

        to_remove = []
        for shot in shots:
            if not update_shot(shot, delta()):
                to_remove.append(shot)
        for shot in to_remove:
            shots.remove(shot)


        draw_player(player)
        for shot in shots:
            draw_shot(shot)

        for wall in walls:
            window = pg.display.get_surface()
            pg.draw.rect(window, pg.Color(100, 100, 100), wall)

            player.velocity, wall_vel, overlap = solve_rect_overlap(player,
                                                                    wall,
                                                                    player.velocity,
                                                                    mass_b=0,
                                                                    bounce=0.1)

        # Main loop ends here, put your code above this line
        yield


# This has to be at the bottom, because of python reasons.
if __name__ == "__main__":
   start_game(init, update)
