import libtcodpy as libtcod
import curses
from gamestuff import *
import data
import entitydata
import time
import math


def isgameover():
    if data.GRAPHICSMODE == 'libtcod': 
        return libtcod.console_is_window_closed()
    elif data.GRAPHICSMODE == 'curses':
        return False
    else:
        print('Error in isgameover. wrong GRAPHICSMODE')

class World(object):
    def __init__(self, nwidth, nheight, alivechar, deadchar,char_option, rndgen):
        
        self.nwidth = nwidth
        self.nheight = nheight 
        self.alive = alivechar
        self.dead = deadchar
        self.char_option = char_option
        self.population =[]
        self.generation = 0
        self.rndgen = rndgen
        
        if data.GRAPHICSMODE == 'libtcod':
            self.con = libtcod.console_new(self.nwidth,self.nheight)
        elif data.GRAPHICSMODE == 'curses':
            self.con =  curses.newwin(self.nheight, self.nwidth)
        else:
            print('ERROR in world _init_. GRAPHICSMODE incorrect')

        self.init_world()

    def init_world(self):
        self.generation = 0
        self.population = [[ flip_coin(self.rndgen)
        for yy in range(self.nheight) ]
            for xx in range(self.nwidth) ]

    def check_stable(self):
        MAX_POP = 125
        num_unstable=0
        for yy in range(self.nheight):
            for xx in range(self.nwidth):
                if self.population[xx][yy] > 2 and self.population[xx][yy] <=MAX_POP:
                    num_unstable+=1

        if num_unstable < 5 and self.generation >500:
            self.init_world()    

    def get_world(self):
        if data.GRAPHICSMODE == 'libtcod':
            libtcod.console_clear(self.con)
        elif data.GRAPHICSMODE == 'curses':
            self.con.clear()
        else:
            print('ERROR in get_world(). GRAPHICSMODE incorrect')

        for yy in range(self.nheight):        
            for xx in range(self.nwidth):
                #my_color=self.random_color()
                my_color = self.get_color(self.population[xx][yy])
                if data.GRAPHICSMODE == 'libtcod':
                    libtcod.console_set_default_foreground(self.con, my_color)
                    libtcod.console_print_ex(self.con, xx, yy, libtcod.BKGND_NONE, libtcod.LEFT, self.get_entity(self.population[xx][yy], self.char_option))
                elif data.GRAPHICSMODE == 'curses':
                    try:
                        self.con.addstr(yy, xx, self.get_entity(self.population[xx][yy], self.char_option), curses.color_pair(my_color))
                    except curses.error:
                        pass
                else:
                    print('Error in get_world. wrong GRAPHICSMODE')
        return self.con

    def get_entity(self, entity, option):
        Max_ASCII = 125
        ASCII_offset = 23

        if option is 'symbol':

            if entity == 0:
                return ' '
            elif entity < 10:
                return '.'
            elif entity >=10 and entity < 20:
                return ','
            elif entity >=20 and entity < 30:
                return '_'
            elif entity >=30 and entity < 40:
                return '-'
            elif entity >=40 and entity < 50:
                return '|'
            elif entity >=50 and entity < 60:
                return '+'
            elif entity >=60 and entity < 70:
                return 'x'
            elif entity >=70 and entity < 80:
                return '='
            elif entity >=80 and entity < 90:
                return '#'
            elif entity >=90 and entity < 100:
                return 'o'
            else:
                return '@'
        elif option is 'ascii':
            if entity == 0:
                thechar = ' '
            elif entity < 10:
                thechar = entity
            elif entity >=10 and entity <= Max_ASCII - ASCII_offset:
                thechar =  chr(entity + ASCII_offset)
            else:
                thechar = chr(Max_ASCII + 1)

            return str(thechar)

    def update(self):
        self.generation+=1
        new_population = []
        new_population = [[ 0
            for yy in range(self.nheight) ]
                for xx in range(self.nwidth) ]

        for yy in range(self.nheight):        
            for xx in range(self.nwidth):    

                if self.isalive(self.population[xx][yy]):
                    state = self.alive
                else:
                    state = self.dead

                num_neighbors = self.neighbors(xx,yy)
                #print str(xx) + '/' + str(yy) + ':' + str(state) + '\t' + str(num_neighbors)
                if state == self.alive:
                    #check rules 1 & 3 (rule 2, nothing happens)
                    if num_neighbors <2 or num_neighbors >3:
                        #rule 1: #neighbors < 2, alive->dead
                        #rule 3: #neighbors = 4, alive->dead
                        new_population[xx][yy] = 0
                        #print '!!! DEATH !!!'
                    else:
                        new_population[xx][yy] = self.population[xx][yy]+1
                        #print 'STAYIN ALIVE!'
                else: #dead
                    #check rule 4
                    if num_neighbors == 3:
                        #rule 4: #neighbors = 3 alive, dead->alive
                        new_population[xx][yy] = self.population[xx][yy]+1
                        #print '??? BACK FROM DEATH ???'

        self.population = new_population
            
    def get_color(self, code):
        if data.GRAPHICSMODE == 'libtcod':
	    rr = 8
	    gg = 8 + code*2
	    bb = 8

	    if gg > 255:
	        rr = 128
	        gg = 255
	        bb = 128

	    return libtcod.Color(rr,gg,bb)
        elif data.GRAPHICSMODE == 'curses':
            fg = round(code/16) 
            if fg <=0:
                fg = 1
            if fg >=8:
                fg = 7
            return int(fg)   

        else: 
            print('error in get_color. Wrong GRAPHICSMODE')
       
    def random_color(self):
        rr = libtcod.random_get_int(0,0,255)
        gg = libtcod.random_get_int(0,0,255)
        bb = libtcod.random_get_int(0,0,255)
        return libtcod.Color(rr,gg,bb)

    def isalive(self,entity):
        if entity > 0:
            return True
        else:
            return False

    def neighbors(self, xx,yy):
        num_neighbors=0

        if xx != 0: #not far left
            if self.isalive(self.population[xx-1][yy]):
                num_neighbors+=1

        if xx !=self.nwidth-1: #not far right
            if self.isalive(self.population[xx+1][yy]):
                num_neighbors+=1            

        if yy != 0: #not far bottom
            if self.isalive(self.population[xx][yy-1]):
                num_neighbors+=1

        if yy != self.nheight-1: #not far top
            if self.isalive(self.population[xx][yy+1]):
                num_neighbors+=1

        if xx != 0 and yy != 0: #not bottom left
            if self.isalive(self.population[xx-1][yy-1]):
                num_neighbors+=1

        if xx != 0 and yy != self.nheight-1: #not top left
            if self.isalive(self.population[xx-1][yy+1]):
                num_neighbors+=1

        if xx != self.nwidth-1 and yy != 0: #not bottom right
            if self.isalive(self.population[xx+1][yy-1]):
                num_neighbors+=1

        if xx != self.nwidth-1 and yy != self.nheight-1: #not top right
            if self.isalive(self.population[xx+1][yy+1]):
                num_neighbors+=1

        return num_neighbors



    def __str__(self):
        ret=''
        for yy in range(self.nheight):    
            ret= ret + '|'        
            for xx in range(self.nwidth):
                ret= ret + str(self.population[xx][yy])
            ret= ret + '|\n'
        return(ret)

def main(stdscr):
    for col in range(1,7):
        curses.init_pair(col, col, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
    
    class keypress(object):
        pass
    
    #create world
    nwidth = 200 
    nheight = 60
    alivechar = '+'
    deadchar = ' '
    char_option = 'ascii'
    speed = .1
    inc = 0.01

    #key vars. TODO put this in a module or something
    if data.GRAPHICSMODE == 'libtcod':
        keypress.ESC  = libtcod.KEY_ESCAPE
        keypress.TAB  = libtcod.KEY_TAB
        keypress.UP   = libtcod.KEY_UP
        keypress.DOWN = libtcod.KEY_DOWN
        keypress.RIGHT= libtcod.KEY_RIGHT
        keypress.LEFT = libtcod.KEY_LEFT
    elif data.GRAPHICSMODE == 'curses':
        keypress.ESC  = 27
        keypress.TAB  = ord('\t')
        keypress.UP   = curses.KEY_UP
        keypress.DOWN = curses.KEY_DOWN
        keypress.RIGHT= curses.KEY_RIGHT
        keypress.LEFT = curses.KEY_LEFT
    else:
        print('Error in key-set. wrong GRAPHICSMODE')


    # default generator
    default = libtcod.random_get_instance()
    # another random generator
    my_random = libtcod.random_new()
    # a random generator with a specific seed
    my_determinist_random = libtcod.random_new_from_seed(0xdeadbeef)

    world = World(nwidth,nheight, alivechar, deadchar, char_option, my_determinist_random)

    if data.GRAPHICSMODE == 'libtcod':
        libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 12)
        libtcod.console_init_root(nwidth, nheight, 'johnstein\'s Game of RogueLife!', False, libtcod.RENDERER_SDL)
        libtcod.sys_set_fps(30)

        libtcod.console_map_ascii_codes_to_font(256   , 32, 0, 5)  #map all characters in 1st row
        libtcod.console_map_ascii_codes_to_font(256+32, 32, 0, 6)  #map all characters in 2nd row

        mouse = libtcod.Mouse()
        key = libtcod.Key()  
    elif data.GRAPHICSMODE == 'curses':
        world.con.nodelay(1)
        world.con.keypad(1)
        print('cursing!')
    else:
        print('Error in setup. wrong GRAPHICSMODE')

    #initialize population

    #enter game loop and check for user input
    while not isgameover():
        if data.GRAPHICSMODE == 'libtcod':
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            thekey = key.vk
        elif data.GRAPHICSMODE == 'curses':
            thekey = world.con.getch()
        else:
            print('Error in isgameover(). wrong GRAPHICSMODE')
    
#TODO add some enums here or find ones that work
        if thekey == keypress.TAB:
            world.init_world()
        elif thekey == keypress.UP:
            speed-=inc
        elif thekey ==keypress.DOWN:
            speed+=inc
        elif thekey == keypress.RIGHT:
            inc+=.01
        elif thekey ==keypress.LEFT:
            inc-=.01
        elif thekey == keypress.ESC:
                break             

        if speed <0:
            speed = .001
        #display world
        if data.GRAPHICSMODE == 'libtcod':
            con_world = world.get_world()
            libtcod.console_blit(con_world, 0, 0, nwidth, nheight, 0, 0, 0)
            libtcod.console_flush()
        elif data.GRAPHICSMODE == 'curses':
            world.con = world.get_world()
            world.con.refresh()

        #waitkey = libtcod.console_wait_for_keypress(True)
        
        #check rules and create new population
        #replace old population with new one
        time.sleep(speed)
        world.update()
        world.check_stable()

if __name__ == '__main__':
    if data.GRAPHICSMODE == 'libtcod':
        main()
    elif data.GRAPHICSMODE == 'curses':
        curses.wrapper(main)
    else:
        print('Error in __name__. wrong GRAPHICSMODE')
