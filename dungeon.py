import libtcodpy as libtcod
import math
import textwrap

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

#room info
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 10 

FOV_ALGO = 2 #FOV_SHADOW
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

WALL_CHAR = '#'
GROUND_CHAR  = '.'


color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(25, 25, 25)

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start out unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    #a rectangle on the map. used to characterize a room
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2)/2
        center_y = (self.y1 + self.y2)/2
        return (center_x, center_y)

    def intersect(self, other):
        #returns True if this rect intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    #this is a generic object: player, monster, item, stairs
    #always represented by a character on the screen
    def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self


    def move(self, dx, dy):

        if not is_blocked(self.x + dx, self.y + dy):
        #if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    def draw(self):
        #only draw if in field of view of player
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #set the color then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase char that represents this object
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_put_char_ex(con, self.x, self.y, GROUND_CHAR, libtcod.white, color_light_ground)

    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx1 = target_x - self.x
        dy1 = target_y - self.y
        #print str(target_x) + '/' + str(target_y) + '::' + str(self.x) + '/' + str(self.y)
        distance = get_distance(dx1, dy1)
        
        #normalize vector and round accordingly and convert to int
        dx = int(round(dx1 / distance))
        dy = int(round(dy1 / distance))

        #print str(dx) + '/' + str(dx1) + ', ' + str(dy) + '/' + str(dy) + ', ' + str(distance)
        if not self.move(dx, dy):
        #if monster didn't move. Try diagonal
            if dx1 != 0:
                dx = abs(dx1) / dx1
            elif target_x < self.x:
                dx = -1
            else:
                dx = 1

            if dy != 0:
                dy = abs(dy1) / dy1
            elif target_y < self.y:
                dy = -1
            else:
                dy = 1
            #print 'trying diagonal:' +str(dx) + ', ' + str(dy) + ', ' + str(distance)
            self.move(dx, dy)

    def distance_to(self, other):
        #return distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return get_distance(dx, dy)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they are in the same tile
        global objects
        objects.remove(self)
        objects.insert(0, self)

class Fighter:
    #combat-related properties and methods (monster, player, NPC, etc)
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power  
        self.death_function=death_function

    def take_damage(self, damage):
        #inflict dmg if possible
        if damage > 0:
            self.hp -= damage

        #check for death and call death_function (if set)
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

    def attack(self, target):
        #very simple formula for attack damage
        damage = self.power - target.fighter.defense

        if damage > 0:
            #make target take some damage
            message (self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' +str(damage) + ' HP.', libtcod.yellow)
            target.fighter.take_damage(damage)
        else:
            message (self.owner.name.capitalize() + ' attacks ' + target.name + ' but there is no effect.', libtcod.white)

class BasicMonster:
    #AI for basic monster
    def take_turn(self):
        #basic monsters can see you if you can see them
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            #move towards player if far enough away
            if flip_coin() and flip_coin() and flip_coin():
                 message ('The ' + self.owner.name + ' clears its throat!', monster.color)
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

                #close enough to attack (if the player is alive)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def create_room(room):
    global map
    #go through tiles in rect to make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
                map[x][y].blocked = False
                map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map

    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map

    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    global map, player
    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #get random width/height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #get random positions, but stay within map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        #check for intersection with this room
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #no intersections

            create_room(new_room)
            (new_x, new_y) = new_room.center()

            #add some contents to the room
            place_objects(new_room)

            if num_rooms == 0:
                #first room. start player here
                player.x = new_x
                player.y = new_y

            else:
                #for all other rooms, need to connect to previous room with a tunnel

                #get center coords of previous room
                (prev_x, prev_y) = rooms[num_rooms -1].center()

                #flip coin
                if flip_coin() == 1:
                    #move h then v
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #move v then h
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            
            #add to rooms list
            rooms.append(new_room)
            num_rooms +=1

def place_objects(room):
    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        #choose random spot for this monster
        x =  libtcod.random_get_int(0, room.x1, room.x2)
        y =  libtcod.random_get_int(0, room.y1, room.y2)

        if not is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) < 80: #80% chance for orcs
                #create orc
                fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'o', 'orcy', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
            else:
                #create a troll
                fighter_component = Fighter(hp=16, defense=1, power=4, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'TROLLY', libtcod.darker_green, blocks= True, fighter=fighter_component, ai=ai_component)

            objects.append(monster)

def get_distance(dx, dy):
    return math.sqrt(dx ** 2 + dy ** 2)

def render_all():
    global color_light_wall, color_dark_wall
    global color_light_ground, color_dark_ground
    global fov_recompute, fov_map

    if fov_recompute:
        #recompute FOV if needed (if player moved or something else happened)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #tile not visible
                    if wall:
                        color_wall_ground = color_dark_wall
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = color_dark_ground
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.grey
                else:
                    #tile is visible
                    map[x][y].explored = True
                    if wall:
                        color_wall_ground = color_light_wall
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = color_light_ground
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.white

                if map[x][y].explored:
                    libtcod.console_put_char_ex(con, x, y, char_wall_ground, fov_wall_ground, color_wall_ground)
                

    #draw all objects in the list
    for object in objects:
        if object != player:
            object.draw()
    #ensure we draw player last
    player.draw()

    #blit contents of con to root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #show player's stats via GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #show player stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #blit panel to root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def get_names_under_mouse():
    global mouse
    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #create list with the names of all objects at the mouse's coords and in FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
    
    names = ', '.join(names) #join names separated by commas
    return names.capitalize()


def handle_keys():
    global fov_recompute
    global key

    #for real-time, uncomment
    #key = libtcod.console_check_for_keypress()

    #for turn-based, uncomment
    #key = libtcod.console_wait_for_keypress(True)
    key_char = chr(key.c)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #ALT + ENTER: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit' #exit game

    if game_state == 'playing':
        #rest
        if key.vk == libtcod.KEY_KPDEC :
            player_resting()
        #movement keys
        elif key.vk == libtcod.KEY_UP or key_char == 'k' or key.vk == libtcod.KEY_KP8 :
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_DOWN or key_char == 'j' or key.vk == libtcod.KEY_KP2 :
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_LEFT or key_char == 'h' or key.vk == libtcod.KEY_KP4 :
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_RIGHT or key_char == 'l' or key.vk == libtcod.KEY_KP6 :
            player_move_or_attack(1, 0)

        #handle diagonal. 11 oclock -> clockwise
        elif key_char == 'y' or key.vk == libtcod.KEY_KP7 :
            player_move_or_attack(-1, -1)

        elif key_char == 'u' or key.vk == libtcod.KEY_KP9 :
            player_move_or_attack(1, -1)

        elif key_char == 'n' or key.vk == libtcod.KEY_KP3 :
            player_move_or_attack(1, 1)

        elif key_char == 'b' or key.vk == libtcod.KEY_KP1 :
            player_move_or_attack(-1, 1)

        else:
            return 'no_action'

def player_resting():
    player.fighter.hp += 2
    
def player_move_or_attack(dx, dy):
    global fov_recompute

    #the coords the player is moving-to/attacking
    x = player.x + dx
    y = player.y + dy

    #try to find attackable object there
    target = None
    for object in objects:
        if object.x == x and object.y == y and object.fighter:
            target = object
            break

    #attack if target found. else, move
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True

def flip_coin():
    return (libtcod.random_get_int(0,0,1))

def player_death(player):
    #the game has ended
    global game_state
    message ('YOU DIED! YOU SUCK!', libtcod.red)
    game_state = 'dead'

    #turn player into corpse
    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster):
    #transform into corpse
    #doesn't block, can't be attacked, cannot move
    message (monster.name.capitalize() + ' is DEAD!', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, exp, etc). first calc the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #lastly add text
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width/2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

def message(new_msg, color = libtcod.white):
    #split message if necessary
    #print new_msg
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the txt and the color
        game_msgs.append((line, color))

########################################################
#init and main loop
########################################################

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'DUNGEONEER!', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH,MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', 'Bobb', libtcod.white, blocks=True, fighter=fighter_component)

objects = [player]
game_msgs = []

make_map()

#create FOV map according to the generated map
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True
game_state = 'playing'
player_action = None

#mouse stuff
mouse = libtcod.Mouse()
key = libtcod.Key()

#WECOME
message('Welcome to Dungeoneer! Good Luck! Don\'t suck!', libtcod.blue)

#limit FPS


while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

    #render the screen
    render_all()

    libtcod.console_flush()

    #erase objects from old position, before they move
    for object in objects:
        object.clear()

    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == 'exit':
        break

    #give monsters a turn
    if game_state == 'playing' and player_action != 'no_action':
        for object in objects:
            if object.ai:
                object.ai.take_turn()
