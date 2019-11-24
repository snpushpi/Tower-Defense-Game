"""6.009 Fall 2019 Lab 9 -- 6.009 Zoo"""

from math import acos
# NO OTHER IMPORTS ALLOWED!

class Constants:
    """
    A collection of game-specific constants.

    You can experiment with tweaking these constants, but
    remember to revert the changes when running the test suite!
    """
    # width and height of keepers
    KEEPER_WIDTH = 30
    KEEPER_HEIGHT = 30

    # width and height of animals
    ANIMAL_WIDTH = 30
    ANIMAL_HEIGHT = 30

    # width and height of food
    FOOD_WIDTH = 10
    FOOD_HEIGHT = 10

    # width and height of rocks
    ROCK_WIDTH = 50
    ROCK_HEIGHT = 50

    # thickness of the path
    PATH_THICKNESS = 30

    TEXTURES = {
        'rock': '1f5ff',
        'animal': '1f418',
        'SpeedyZookeeper': '1f472',
        'ThriftyZookeeper': '1f46e',
        'CheeryZookeeper': '1f477',
        'food': '1f34e'
    }
    TEXTURE2 = {
       '1f5ff': 'rock',
       '1f418': 'animal',
       '1f472':'SpeedyZookeeper',
       '1f46e':'ThriftyZookeeper',
       '1f477':'CheeryZookeeper',
       '1f34e':'food'
       }

    FORMATION_INFO = {'SpeedyZookeeper':
                       {'price': 9,
                        'interval': 55,
                        'throw_speed_mag': 20},
                      'ThriftyZookeeper':
                       {'price': 7,
                        'interval': 45,
                        'throw_speed_mag': 7},
                      'CheeryZookeeper':
                       {'price': 10,
                        'interval': 35,
                        'throw_speed_mag': 2}}

class NotEnoughMoneyError(Exception):
    """A custom exception to be used when insufficient funds are available
    to hire new zookeepers. You may leave this class as is."""
    pass


################################################################################
################################################################################

class Game:
    def __init__(self, game_info):
        """Initializes the game.

        `game_info` is a dictionary formatted in the following manner:
          { 'width': The width of the game grid, in an integer (i.e. number of pixels).
            'height': The height of the game grid, in an integer (i.e. number of pixels).
            'rocks': The set of tuple rock coordinates.
            'path_corners': An ordered list of coordinate tuples. The first
                            coordinate is the starting point of the path, the
                            last point is the end point (both of which lie on
                            the edges of the gameboard), and the other points
                            are corner ("turning") points on the path.
            'money': The money balance with which the player begins.
            'spawn_interval': The interval (in timesteps) for spawning animals
                              to the game.
            'animal_speed': The magnitude of the speed at which the animals move
                            along the path, in units of grid distance traversed
                            per timestep.
            'num_allowed_unfed': The number of animals allowed to finish the
                                 path unfed before the player loses.
          }
        """
        
        self.game_info = game_info
        print('hi',self.game_info)
        self.status = 'ongoing'
        self.animals = []
        self.rocks = []
        self.foods =[]
        self.szookeeper=[]
        self.tzookeeper=[]
        self.czookeeper=[]
        self.timer = 0
        self.money = self.game_info['money']
        p = Path(self.game_info['path_corners'][0])
        self.path_obj_list = [p]
        self.path_list =[self.game_info['path_corners'][0]]
        for i in range(len(self.game_info['path_corners'])-1):
            if self.game_info['path_corners'][i][0]==self.game_info['path_corners'][i+1][0]:
                if self.game_info['path_corners'][i][1]>self.game_info['path_corners'][i+1][1]:
                    for j in range(self.game_info['path_corners'][i][1]+1,self.game_info['path_corners'][i+1][1]-1,-1):
                        self.path_list.append((self.game_info['path_corners'][i][0],j))
                        p = Path((self.game_info['path_corners'][i][0],j))
                        self.path_obj_list.append(p)
                else:
                    for j in range(self.game_info['path_corners'][i][1]+1,self.game_info['path_corners'][i+1][1]+1):
                        self.path_list.append((self.game_info['path_corners'][i][0],j))
                        p = Path((self.game_info['path_corners'][i][0],j))
                        self.path_obj_list.append(p)
            elif self.game_info['path_corners'][i][1]==self.game_info['path_corners'][i+1][1]:
                if self.game_info['path_corners'][i][0]>self.game_info['path_corners'][i+1][0]:
                    for j in range(self.game_info['path_corners'][i][0]+1,self.game_info['path_corners'][i+1][0]-1,-1):
                        self.path_list.append((j,self.game_info['path_corners'][i][1]))
                        p = Path((j,self.game_info['path_corners'][i][1]))
                        self.path_obj_list.append(p)
                else:
                    for j in range(self.game_info['path_corners'][i][1]+1,self.game_info['path_corners'][i+1][1]+1):
                        self.path_list.append((j,self.game_info['path_corners'][i][1]))
                        p = Path((j,self.game_info['path_corners'][i][1]))
                        self.path_obj_list.append(p)
        self.zookeeper_selected = False
        self.zookeeper_position_try = False
        self.zookeeper_aim_try = False
        self.zookeeper_type = None
        self.zookeeper_position_valid = False
        for elt in self.game_info['rocks']:
            r = Rocks(elt)
            self.rocks.append(r)
            
    def render(self):
        """Renders the game in a form that can be parsed by the UI.

        Returns a dictionary of the following form:
          { 'formations': A list of dictionaries in any order, each one
                          representing a formation. The list should contain 
                          the formations of all animals, zookeepers, rocks, 
                          and food. Each dictionary has the key/value pairs:
                             'loc': (x, y), 
                             'texture': texture, 
                             'size': (width, height)
                          where `(x, y)` is the center coordinate of the 
                          formation, `texture` is its texture, and `width` 
                          and `height` are its dimensions. Zookeeper
                          formations have an additional key, 'aim_dir',
                          which is None if the keeper has not been aimed, or a 
                          tuple `(aim_x, aim_y)` representing a unit vector 
                          pointing in the aimed direction.
            'money': The amount of money the player has available.
            'status': The current state of the game which can be 'ongoing' or 'defeat'.
            'num_allowed_remaining': The number of animals which are still
                                     allowed to exit the board before the game
                                     status is `'defeat'`.
          }
        """
        game_state_list = []
        for food in self.foods:
            food_dict = {'loc':food.loc,'texture':food.texture,'size':food.size}
            game_state_list.append(food_dict)
        for rock in self.rocks:
            rock_dict = {'loc':rock.loc,'texture':rock.texture,'size':rock.size}
            game_state_list.append(rock_dict)
        for animal in self.animals:
            animal_dict = {'loc':animal.loc,'texture':animal.texture,'size':animal.size}
            game_state_list.append(animal_dict)
        for keeper in self.szookeeper+self.tzookeeper+self.czookeeper:
            keeper_dict = {'loc':keeper.loc,'texture':keeper.texture,'size':keeper.size,'aim_dir':keeper.aim_dir}
            game_state_list.append(keeper_dict)
        render_dict = {}
        render_dict['formations']=game_state_list
        render_dict['money']=self.money
        render_dict['status']=self.status
        render_dict['num_allowed_remaining']=self.game_info['num_allowed_unfed']
        return render_dict
    def timestep(self, mouse=None):
        """Simulates the evolution of the game by one timestep.

        In this order:
            (0. Do not take any action if the player is already defeated.)
            1. Compute any changes in formation locations, then remove any
                off-board formations.
            2. Handle any food-animal collisions, and remove the fed animals
                and eaten food.
            3. Throw new food if possible.
            4. Spawn a new animal from the path's start if needed.
            5. Handle mouse input, which is the integer coordinate of a player's
               click, the string label of a particular zookeeper type, or `None`.
            6. Redeem one unit money per animal fed this timestep.
            7. Check for the losing condition to update the game status if needed.
        """
        def handle_mouse_input():
            #now we will handle mouse input, if it is a string, then user has selected a zookeeper, the the next click will determine the co-ordinate about where this zookeeper should be placed
            #if the player has enough money, we will check existing collisions and allow user to fix the location of zookeeper until the valid location is achieved.
            if isinstance(mouse,str):
                self.zookeeper_selected = True
                self.zookeeper_type = mouse                                                   
            if isinstance(mouse,tuple):
                if not self.zookeeper_position_valid:
                    self.zookeeper_position_try = True
                                                                    
            if self.zookeeper_position_try:
                if self.money>=Constants.FORMATION_INFO[self.zookeeper_type]['price']:#we have enough money to start, we will first create an instance of a zookeeper
                    
                    if self.zookeeper_type=='SpeedyZookeeper':
                        z = SpeedyZookeeper(mouse)
                    elif self.zookeeper_type=='ThriftyZookeeper':
                        z = ThriftyZookeeper(mouse)
                    elif self.zookeeper_type=='CheeryZookeeper':
                        z = CheeryZookeeper(mouse)
                    # we will now check whether it collides with any current object, if it does, we will reset our flag variable
                    # so that next time we give a mouse co-ordinate, we understand that this click is still for the placement of our zookeeper.
                    #In this way, when we will get a click which does not collide with any curent object,we will add that instance to our zookeeper
                    #instance list, we will reset some of our flag variables to be false, so next time when we get another tuple click , we understand that this
                    #is deciding aim_direction
                    for animal in self.animals:
                        if animal.intersect(z):                                   
                            return                                   
                    for rock in self.rocks:
                        if rock.intersect(z):
                            return
                    for path in self.path_obj_list:
                        if path.intersect(z):
                            return
                    for keeper in self.szookeeper:
                        if keeper.intersect(z):
                            return
                    for keeper in self.tzookeeper:
                        if keeper.intersect(z):
                            return
                    for keeper in self.czookeeper:
                        if keeper.intersect(z):
                            return
                    #it does not collide with anything, so a valid placement.
                    self.zookeeper_position_valid = True
                    self.zookeeper_position_try = False
                    self.zookeeper_selected = False
                    if self.zookeeper_type=='SpeedyZookeeper':
                        
                        self.szookeeper.append(z)
                        z.timer = self.timer
                    elif self.zookeeper_type=='ThriftyZookeeper':
                        self.tzookeeper.append(z)
                        z.timer = self.timer
                    elif self.zookeeper_type=='CheeryZookeeper':
                        self.czookeeper.append(z)
                        z.timer = self.timer
                            
                    self.zookeeper_type = None
                    self.money = self.money - z.throw_price
                else:
                    #we have to refix all the values since we are not taking that zookeeper.
                    self.zookeeper_selected = False
                    self.zookeeper_position_try = False
                    self.zookeeper_type = None
                    self.zookeeper_position_valid = False
                    raise NotEnoughMoneyError
            if self.zookeeper_position_valid:
                if z.loc is not mouse:
                    denom = ((mouse[0]-z.loc[0])**2+(mouse[1]-z.loc[1])**2)**(-0.5)
                    x_coordinate = (mouse[0]-z.loc[0])/denom
                    y_coordinate = (mouse[1]-z.loc[1])/denom
                    z.aim_dir =(x_coordinate,y_coordinate)
                    self.zookeeper_position_valid = False
        if self.status == 'ongoing':
            self.formation_location_change()
            self.food_animal_collision()
            self.check_throw_food()
            self.spawn_animal()
            handle_mouse_input()
            if self.money<0:
                self.game_status = 'defeat'
            self.timer+=1

    def formation_location_change(self):
        #we will update the formation locs, specially foods and animals location and will let them out if they are no longer on the board.
        #For animals, they will be vanished if they are out of the board or they intersect with a food
        # food will be vanished if they get out of the board or eaten by some animal
        all_animals = self.animals[:]
        all_foods = self.foods[:]
        for animal in self.animals:
            animal.move()
            if animal.move()==None:
                all_animals.remove(animal)
                self.game_info['num_allowed_unfed']=self.game_info['num_allowed_unfed']-1
        
        self.animals = all_animals[:]
        for food in self.foods:
            new_loc = food.move()
            if not((0<= new_loc[0]<=self.game_info['width']) and (0 <= new_loc[1]<= self.game_info['height'])):
                all_foods.remove(food)
        self.animals = all_animals[:]
        self.foods = all_foods[:]
    def food_animal_collision(self):
        all_animals = self.animals[:]
        all_foods = self.foods[:]
        flag = False
        for food in self.foods:
            for animal in self.animals:       
                if food.intersect(animal):
                    flag = True                                            
                    all_animals.remove(animal)
                    self.money+=1
            if flag == True:
                all_foods.remove(food)
        self.foods = all_foods[:]
        self.animals = all_animals[:]
    def check_throw_food(self):
        # we will check the timer to know whether we should throw new food                                                       
        for z in self.szookeeper:
            if z.timer% z.throw_interval == 0:
                for animal in self.animals:
                    if z.animal_sight(animal.loc):
                        f = SFood(z.loc)
                        self.foods.append(f)
        for z in self.tzookeeper:
            if z.timer% z.throw_interval == 0:
                for animal in self.animals:
                    if z.animal_sight(animal.loc):
                        f = TFood(z.loc)
                        self.foods.append(f)                                        
        for z in self.czookeeper:
            if z.timer% z.throw_interval == 0:
                for animal in self.animals:
                    if z.animal_sight(animal.loc):
                        f = CFood(z.loc)
                        self.foods.append(f)                                        
    def spawn_animal(self):
        # we will now spawn a new animal if needed , we will check the timer for that and then will create an animal instance
        if self.timer % (self.game_info['spawn_interval'])==0:
            a = Animals(self.path_list[0],self.game_info['animal_speed'])
    
class Formation():#intersection,movement
    def intersect(object1,object2):#two class instances as parameter, returns boolean value
        object1_ul =object1.loc[0]-(object1.size[0]//2),object1.loc[1]-(object1.size[1]//2)
        object1_ur =object1.loc[0]+(object1.size[0]//2),object1.loc[1]-(object1.size[1]//2)
        object1_bl =object1.loc[0]-(object1.size[0]//2),object1.loc[1]+(object1.size[1]//2)
        object1_br =object1.loc[0]+(object1.size[0]//2),object1.loc[1]+(object1.size[1]//2)
        object2_ul =object2.loc[0]-(object2.size[0]//2),object2.loc[1]-(object2.size[1]//2)
        object2_ur =object2.loc[0]+(object2.size[0]//2),object2.loc[1]-(object2.size[1]//2)
        object2_bl =object2.loc[0]-(object2.size[0]//2),object2.loc[1]+(object2.size[1]//2)
        object2_br =object2.loc[0]+(object2.size[0]//2),object2.loc[1]+(object2.size[1]//2)
        if object1_ul[0]<=object2_bl[0]<=object1_ur[0] and object1_ul[1]<=object2_bl[1]<=object1_bl[1]:
            return True 
        if object1_ul[0]<=object2_ul[0]<=object1_ur[0] and object1_ul[1]<=object2_ul[1]<=object1_bl[1]:
            return True
        if object1_ul[0]<=object2_ur[0]<=object1_ur[0] and object1_ul[1]<=object2_ur[1]<=object1_bl[1]:
            return True
        if object1_ul[0]<=object2_br[0]<=object1_ur[0] and object1_ul[1]<=object2_br[1]<=object1_bl[1]:
            return True
        return False
class Zookeeper(Formation):
    def __init__(self,loc):
        self.size = (Constants.KEEPER_WIDTH,Constants.KEEPER_HEIGHT)
        self.loc = loc
    def animal_sight(self,other_loc):
         
        '''returns boolean value whether a food object is in this keeper's sight'''
        vector1_mag = ((self.loc[0]-other_loc[0])**2+(self.loc[1]-other_loc[1])**2)**0.5
        vector2_mag = ((other_loc[0]-15-self.loc[0])**2+(other_loc[1]-15-self.loc[1])**2)**0.5
        vector3_mag = ((other_loc[0]+15-self.loc[0])**2+(other_loc[1]-15-self.loc[1])**2)**0.5
        upper_mag1 = (self.loc[0]-other_loc[0])*(other_loc[0]-15-self.loc[0])+ (self.loc[1]-other_loc[1])*(other_loc[1]-15-self.loc[1])
        upper_mag2 = (self.loc[0]-other_loc[0])*(other_loc[0]+15-self.loc[0])+(self.loc[1]-other_loc[1])*(other_loc[1]-15-self.loc[1])
        upper_mag3 = (other_loc[0]-15-self.loc[0])*(other_loc[0]+15-self.loc[0]) + (other_loc[1]-15-self.loc[1])*(other_loc[1]-15-self.loc[1])
        cos_1 = upper_mag1/(vector1_mag*vector2_mag)
        cos_2 = upper_mag2/(vector1_mag*vector3_mag)
        cos_3 = upper_mag3/vector2_mag*vector3_mag
        if cos_3+0.001 <= acos(cos_1)+acos(cos_2) <= cos_3+0.001:
            return True
        return False
class SpeedyZookeeper(Zookeeper):# will store everything a zookeeper does, including throwing food,aiming food, checking intersection,when the user choses a
                                #zookeeper, it will create a zookeeper instance. Then another mouse click will fix the aim direction and instantly it will start throwing food.
    def __init__(self,loc):
        Zookeeper.__init__(self,loc)
        self.size = (Constants.KEEPER_WIDTH,Constants.KEEPER_HEIGHT)
        self.texture = Constants.TEXTURES['SpeedyZookeeper']
        self.throw_interval=Constants.FORMATION_INFO['SpeedyZookeeper']['interval']
        self.throw_speed = Constants.FORMATION_INFO['SpeedyZookeeper']['throw_speed_mag']
        self.throw_price = Constants.FORMATION_INFO['SpeedyZookeeper']['price']
        self.timer = None
        self.aim_dir = None
class ThriftyZookeeper(Zookeeper):
    def __init__(self,loc):
        Zookeeper.__init__(self,loc)
        self.size = (Constants.KEEPER_WIDTH,Constants.KEEPER_HEIGHT)
        self.texture = Constants.TEXTURES['ThriftyZookeeper']
        self.throw_interval=Constants.FORMATION_INFO['ThriftyZookeeper']['interval']
        self.throw_speed = Constants.FORMATION_INFO['ThriftyZookeeper']['throw_speed_mag']
        self.throw_price = Constants.FORMATION_INFO['ThriftyZookeeper']['price']
        self.timer = None
        self.aim_dir = None
        
class CheeryZookeeper(Zookeeper):
    def __init__(self,loc):
        Zookeeper.__init__(self,loc)
        self.size = (Constants.KEEPER_WIDTH,Constants.KEEPER_HEIGHT)
        self.texture = Constants.TEXTURES['CheeryZookeeper']
        self.throw_interval=Constants.FORMATION_INFO['CheeryZookeeper']['interval']
        self.throw_speed = Constants.FORMATION_INFO['CheeryZookeeper']['throw_speed_mag']
        self.throw_price = Constants.FORMATION_INFO['CheeryZookeeper']['price']
        self.timer = None
        self.aim_dir = None
        
class SFood(SpeedyZookeeper):
    def __init__(self,loc):
        self.loc = loc
        self.size = (Constants.FOOD_WIDTH,Constants.FOOD_HEIGHT)
        self.texture = Constants.TEXTURES['food']
    def move(self):
        self.loc = (self.aim_dir[0]*self.throw_speed + self.aim_dir[1]*self.throw_speed)
        return self.loc
class TFood(ThriftyZookeeper):
    def __init__(self,loc):
        self.loc = loc
        self.size = (Constants.FOOD_WIDTH,Constants.FOOD_HEIGHT)
        self.texture = Constants.TEXTURES['food']
    def move(self):
        self.loc = (self.aim_dir[0]*self.throw_speed + self.aim_dir[1]*self.throw_speed)
        return self.loc
class CFood(CheeryZookeeper):
    def __init__(self,loc):
        self.loc = loc
        self.size = (Constants.FOOD_WIDTH,Constants.FOOD_HEIGHT)
        self.texture = Constants.TEXTURES['food']
    def move(self):
        self.loc = (self.aim_dir[0]*self.throw_speed + self.aim_dir[1]*self.throw_speed)
        return self.loc

class Rocks(Formation):
    def __init__(self,loc):
        self.loc = loc
        self.texture = Constants.TEXTURES['rock']
        self.size = (Constants.ROCK_WIDTH,Constants.ROCK_HEIGHT)
class Animals(Formation):
    def __init__(self,loc,animal_speed):
        self.loc = loc
        self.texture = Constants.TEXTURES['animal']
        self.size = (Constants.ANIMAL_WIDTH,Constants.ANIMAL_HEIGHT)
        self.animal_speed = animal_speed
    def move(self):
        flag = True
        for i in range(len(self.path_list)):
            if self.path_list[i]==self.loc:
                if i+self.animal_speed<len(self.path_list):
                    flag = False
                    self.loc = self.path_list[i+self.animal_speed]
                break
        if flag:
            self.loc = None
        return self.loc
class Path(Formation):
    def __init__(self,loc):
        self.loc = loc
        
        
    def intersect(self,other):
        self_ul =self.loc[0]-0.5,self.loc[1]-15
        self_ur =self.loc[0]+0.5,self.loc[1]-15
        self_bl =self.loc[0]-0.5,self.loc[1]+15
        self_br =self.loc[0]+0.5,self.loc[1]+15
        other_ul =other.loc[0]-0.5,other.loc[1]-15
        other_ur =other.loc[0]+0.5,other.loc[1]-15
        other_bl =other.loc[0]-0.5,other.loc[1]+15
        other_br =other.loc[0]+0.5,other.loc[1]+15
        if self_ul[0]<=other_bl[0]<=self_ur[0] and self_ul[1]<=other_bl[1]<=self_bl[1]:
            return True 
        if self_ul[0]<=other_ul[0]<=self_ur[0] and self_ul[1]<=other_ul[1]<=self_bl[1]:
            return True
        if self_ul[0]<=other_ur[0]<=self_ur[0] and self_ul[1]<=other_ur[1]<=self_bl[1]:
            return True
        if self_ul[0]<=other_br[0]<=self_ur[0] and self_ul[1]<=other_br[1]<=self_bl[1]:
            return True
        return False
        



################################################################################
################################################################################
# TODO: Add a Formation class and at least two additional classes here.





################################################################################
################################################################################



if __name__ == '__main__':
   pass
