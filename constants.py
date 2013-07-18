#standard imports
import libtcodpy as libtcod


MAIN_MENU_BKG = 'menu_background.png'
STATE_PLAYING = 'playing'
STATE_NOACTION = 'no_action'
STATE_DEAD = 'dead'

CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 40

#GUI rendering
BAR_WIDTH = 20
PANEL_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

#combat log
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

#items
MAX_NUM_ITEMS = 30
INVENTORY_WIDTH = 50

#spell info
HEAL_AMOUNT = 50
LIGHTNING_DAMAGE = 25
LIGHTNING_RANGE = 5
FIREBALL_DAMAGE = 25
FIREBALL_RADIUS = 3
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8

#room info
ROOM_MAX_SIZE = 15
ROOM_MIN_SIZE = 4
MAX_ROOMS = 40

FOV_ALGO = 2 #FOV_SHADOW
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

#WALL_CHAR = '#'
#GROUND_CHAR  = '.'

#dice
D6=[1,6]
D4=[1,4]
D8=[1,8]
D10=[1,10]

#player
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

COLOR_DARK_WALL = libtcod.Color(0, 0, 100)
COLOR_LIGHT_WALL = libtcod.Color(130, 110, 50)
COLOR_DARK_GROUND = libtcod.Color(50, 50, 150)
COLOR_LIGHT_GROUND = libtcod.Color(25, 25, 25)

AUTOEQUIP = True #need to add a game options class/structure