from random import random
#from business import *
#from residence import *
#from occupation import *
# from landmark import *
import pyqtree
from random import gauss,randrange
from corpora import Names
from config import Config
import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

def clamp(val,minimum,maximum):
    return max(minimum,min(val,maximum))
    
class City(object):
    """A city in which a gameplay instance takes place."""

    def __init__(self, game):
        """Initialize a City object."""
        self.game = game
        self.founded = game.config.year_city_gets_founded
        self.residents = set()
        self.departed = set()  # People who left the city (i.e., left the simulation)
        self.deceased = set()  # People who died in in the city
        self.companies = set()
        self.lots = set()
        self.tracts = set()
        self.dwelling_places = set()  # Both houses and apartment units (not complexes)
        self.streets = set()
        self.blocks = set()
        self.generateLots(game.config)
        self.paths = {}
        self.generatePaths()
        
    def generatePaths(self):
        for start in blocks:
            for goal in blocks:
                if (start != goal):
                    if ((start,goal) not in paths):
                        came_from, cost_so_far = a_star_search(start,goal)
                        paths[(start,goal)] = came_from
                        paths[(goal,start)] = came_from
    def generateLots(self,configFile):
        
        loci =  configFile.loci
        samples = configFile.samples
        size =configFile.size
        
        lociLocations = []
        for ii in range(loci):
            lociLocations.append([gauss(size/2.0,size/6.0), gauss(size/2.0,size/6.0)])
            
        tree = pyqtree.Index(bbox=[0,0,size,size])

        for ii in range(samples):
            center = lociLocations[randrange(len(lociLocations))]
            point = [clamp(gauss(center[0],size/6.0),0,size-1),clamp(gauss(center[1],size/6.0),0,size-1)]
            point.append(point[0]+1)
            point.append(point[1]+1)
            tree.insert(point,point)
            
        nsstreets = {}
        ewstreets = {}
        blocks = []
        lots = []
        tracts =[]
            
        nsEnd = []
        ewEnd = []
        streets = []
        
        def traverseTree(node):
            if (len(node.children)==0 and node.width != 1):
                w =int( node.center[0]-node.width*0.5)
                e =int( node.center[0]+node.width*0.5)
                n =int( node.center[1]-node.width*0.5)
                s =int( node.center[1]+node.width*0.5)
                blocks.append((w,n,node.width))
                for xx in range(w,e):
                    lots.append((xx+0.5,n+0.5))
                    lots.append((xx+0.5,s-0.5))
                for xx in range(n+1,s-1):
                    lots.append((w+0.5,xx+0.5))
                    lots.append((e-0.5,xx+0.5))
                if (node.width > 2):
                    tracts.append([w+1,n+1,node.width-2])
                nsstreets[ (w,n)] = (w,s)
                nsstreets[ (e,n)] = (e,s)
                ewstreets[ (w,n)] = (e,n)
                ewstreets[ (w,s)] = (e,s)
                
            for child in node.children:
                traverseTree(child)
        
        traverseTree(tree)
        for ii in range(0,size+2,2):
            for jj in range(0,size+2,2):
                street = (ii,jj)
                if street in nsstreets:
                    start = street
                    end = nsstreets[start]
                    while end in nsstreets:
                        end = nsstreets[end]
                    if (end not in nsEnd):
                        nsEnd.append(end)             
                        streets.append(['ns',start, end])
                if street in ewstreets:
                    start = street
                    end = ewstreets[start]
                    while end in ewstreets:
                        end = ewstreets[end]
                    if (end not in ewEnd):
                        ewEnd.append(end)             
                        streets.append(['ew',start, end])

         
        
        nsStreets = {}
        ewStreets = {}
        connections = {}
        for street in streets:
            number = int(street[1][0]/2 if street[0] == "ns" else street[1][1]/2)+1
            direction = ""
            startingBlock = 0
            endingBlock = 0
            if (street[0] == "ns"):
                direction = ("N" if number < size/4 else "S")
                startingBlock =  street[1][1]
                endingBlock =  street[2][1]

            if (street[0] == "ew"):
                direction =( "E" if number < size/4 else "W")
                startingBlock =  street[1][0]
                endingBlock =  street[2][0]

            startingBlock = int(startingBlock/2)+1
            endingBlock = int(endingBlock/2)+1
            reifiedStreet = (Street(city,number, direction,startingBlock,endingBlock))
            self.streets.add(reifiedStreet)
            for ii in range(startingBlock,endingBlock+1):
                if (street[0] == "ns"):
                    nsStreets[(number,ii)] = reifiedStreet
                else:
                    ewStreets[(ii,number)] = reifiedStreet
            for ii in range(startingBlock,endingBlock):
                coord = None
                next = None
                if (street[0] == "ns"):
                    coord = (number,ii)
                    next = (number,ii+1)
                else:
                    coord = (ii,number)
                    next = (ii+1,number)
                if (not coord in connections):
                    connections[coord] = []
                connections[coord].append(next)
                if (not next in connections):
                    connections[next] = []
                connections[next].append(coord)

        def insertInto(dict,key,value):
            if (not key in dict):
                dict[key] = []
            dict[key].append(value)
            
        def insertOnce(dict,key,value):
            if (not key in dict):
                dict[key] = value
                
        lots = {}
        Blocks = {}
        Numberings = {}
        n_buildings_per_block = Config().n_buildings_per_block


        for block in blocks:
            ew = int(block[0]/2)+1
            ns = int(block[1]/2)+1 
            sizeOfBlock = int(block[2]/2)
            tract = None
            if (sizeOfBlock > 1):
                tract = Tract()
            
            for ii in range(0,sizeOfBlock+1):
                Blocks[(ew,ns+ii,'NS')] =Block( nsStreets[(ew,ns)], (ii+ns)*100,(ew,ns+ii)) 
                insertOnce(Numberings,(ew,ns+ii,'W'),Block.determine_house_numbering( (ii+ns)*100,'W', Config()))
                Blocks[(ew+ii,ns,'EW')] =Block( ewStreets[(ew,ns)], (ii+ew)*100,(ew+ii,ns))        
                insertOnce(Numberings,(ew+ii,ns,'S'),Block.determine_house_numbering( (ii+ew)*100,'S', Config()))
                Blocks[(ew+sizeOfBlock,ns+ii,'NS')] =Block( nsStreets[(ew+sizeOfBlock,ns)], (ii+ns)*100,(ew+sizeOfBlock,ns+ii))   
                insertOnce(Numberings,(ew+sizeOfBlock,ns+ii,'E'),Block.determine_house_numbering( (ii+ns)*100,'E', Config()))     
                Blocks[(ew+ii,ns+sizeOfBlock,'EW')] =Block( ewStreets[(ew,ns+sizeOfBlock)], (ii+ew)*100,(ew+ii,ns+sizeOfBlock))
                insertOnce(Numberings,(ew+ii,ns+sizeOfBlock,'N'),Block.determine_house_numbering( (ii+ew)*100,'N', Config())) 
                if (tract != None):
                    tract.addBlock(Blocks[(ew,ns+ii,'NS')],None)
                    tract.addBlock( Blocks[(ew+ii,ns,'EW')],None )
                    tract.addBlock(Blocks[(ew+sizeOfBlock,ns+ii,'NS')],None)
                    tract.addBlock( Blocks[(ew+ii,ns+sizeOfBlock,'EW')],None)
             
            neCorner = Lot()
            insertInto(lots,(ew,ns,'S'),(0,neCorner))
            insertInto(lots,(ew,ns,'W'),(0,neCorner))
            
            nwCorner = Lot()
            insertInto(lots,(ew+sizeOfBlock,ns,'S'),(0,nwCorner))
            insertInto(lots,(ew+sizeOfBlock,ns,'E'),(n_buildings_per_block-1,nwCorner))
            
            seCorner = Lot()
            insertInto(lots,(ew,ns+sizeOfBlock,'N'),(n_buildings_per_block-1,seCorner))
            insertInto(lots,(ew,ns+sizeOfBlock,'W'),(0,seCorner))
            
            swCorner = Lot()
            insertInto(lots,(ew+sizeOfBlock,ns+sizeOfBlock,'N'),(n_buildings_per_block-1,swCorner))
            insertInto(lots,(ew+sizeOfBlock,ns+sizeOfBlock,'E'),(n_buildings_per_block-1,swCorner))
            
            for ii in range(1,sizeOfBlock*Config().n_buildings_per_block):   
                blockNum = int(ii/2)
                insertInto(lots,(ew,ns+blockNum,'W'),(ii %n_buildings_per_block, Lot()))
                insertInto(lots,(ew+blockNum,ns,'S'),(ii %n_buildings_per_block, Lot()))
                insertInto(lots,(ew+sizeOfBlock,ns+blockNum,'E'),(ii %n_buildings_per_block, Lot()))
                insertInto(lots,(ew+blockNum,ns+sizeOfBlock,'N'),(ii %n_buildings_per_block, Lot()))        
                
        for block in lots:
            dir = 'NS' if block[2] == 'W' or block[2] == 'E' else 'EW'
            actualBlock = Blocks[(block[0],block[1],dir)]
            lotList = lots[block]
            for lot in lotList:
                lot[1].addBlock(actualBlock,Numberings[block][lot[0]])
                actualBlock.lots.append(lot[1])


        for conn in connections: 
            for neighbor in connections[conn]:
                dx = neighbor[0] - conn[0]
                dy = neighbor[1] - conn[1]
                if dx != 0:
                    Blocks[(conn[0],conn[1],'EW')].addNeighbor(Blocks[(neighbor[0],neighbor[1],'EW')])
                if dy != 0:
                    Blocks[(conn[0],conn[1],'NS')].addNeighbor(Blocks[(neighbor[0],neighbor[1],'NS')])
        for block in Blocks:
            self.blocks.add(block)

    @property
    def vacant_lots(self):
        """Return all vacant lots in the city."""
        vacant_lots = (lot for lot in self.lots if not lot.building)
        return vacant_lots

    @property
    def vacant_homes(self):
        """Return all vacant homes in the city."""
        vacant_homes = (home for home in self.dwelling_places if not home.residents)
        return vacant_homes

    @property
    def all_time_residents(self):
        """Return everyone who has at one time lived in the city."""
        return self.residents | self.deceased | self.departed

    @property
    def unemployed(self):
        """Return unemployed (mostly young) people, excluding retirees."""
        unemployed_people = set()
        for resident in self.residents:
            if not resident.occupation and not resident.retired:
                if resident.age >= self.game.config.age_people_start_working:
                    unemployed_people.add(resident)
        return unemployed_people

    def workers_of_trade(self, occupation):
        """Return all population in the city who practice to given occupation.

        @param occupation: The class pertaining to the occupation in question.
        """
        return (resident for resident in self.residents if isinstance(resident.occupation, occupation))
    def heuristic(a, b):
        (x1, y1) = a.coords
        (x2, y2) = b.coords
        return abs(x1 - x2) + abs(y1 - y2)

    def a_star_search(start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == goal:
                break
            
            for next in current.neighbors:
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        return came_from, cost_so_far

class Street(object):
    """A street in a city."""

    def __init__(self, city, number, direction,startingBlock,endingBlock):
        """Initialize a Street object."""
        #self.game = city.game
        self.city = city
        self.type = type
        self.number = number
        self.direction = direction  # Direction relative to the center of the city
        self.name = self.generate_name(number, direction)
        self.startingBlock = startingBlock
        self.endingBlock = endingBlock

    @staticmethod
    def generate_name(number, direction):
        """Generate a street name."""
        number_to_ordinal = {
            1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th',9:'9th'
        }
        if random() < 0.13:
            name = Names.any_surname()
        else:
            name = number_to_ordinal[number]
        if direction == 'E' or direction == 'W':
            street_type = 'Street'
        else:
            street_type = 'Avenue'
        name = "{} {} {}".format(name, street_type, direction)
        return name

    def __str__(self):
        """Return string representation."""
        return self.name


class Block(object):
    """A block on a street in a city."""

    def __init__(self,street, number,coords):
        """Initialize a Block object."""
        # self.game = street.city.game
        # self.city = street.city
        self.street = street
        self.number = number
        self.lots = []
        self.neighbors = []
        self.coords = coords
    def __str__(self):
        """Return string representation."""
        return "{} block of {}".format(self.number, str(self.street))
    
    @property
    def buildings(self):
        """Return all the buildings on this block."""
        return (lot.building for lot in self.lots if lot.building)

    @staticmethod
    def determine_house_numbering(block_number,sideOfStreet, config):
        """Devise an appropriate house numbering scheme given the number of buildings on the block."""
        n_buildings = config.n_buildings_per_block
        house_numbers = []
        house_number_increment = 100.0 / n_buildings
        evenOdd = 0 if  sideOfStreet == "E" or sideOfStreet == "N" else 1
        for i in xrange(n_buildings):
            base_house_number = (i * house_number_increment) - 1
            house_number = base_house_number + int(random() * house_number_increment)
            if house_number % 2 == (1-evenOdd):  
                house_number += 1
            if house_number < 1+evenOdd:
                house_number = 1+evenOdd
            elif house_number > 98+evenOdd:
                house_number = 98+evenOdd
            house_number += block_number
            house_numbers.append(house_number)
        return house_numbers
    def addNeighbor(self,other):
        self.neighbors.append(other)

class Lot(object):
    """A lot on a block in a city, upon which buildings and houses get erected."""

    def __init__(self):
        """Initialize a Lot object."""
        #self.game = block.city.game
       # self.city = block.city
        self.streets = []
        self.blocks = []
        self.house_numbers = []  # In the event a business/landmark is erected here, it inherits this
        self.building = None  # Will always be None for Tract
        self.landmark = None  # Will always be None for Lot
        self._init_add_to_city_plan()
        #self.neighboring_lots = self._init_get_neighboring_lots()
    def addBlock(self,block,number):
        self.streets.append(block.street)
        self.blocks.append(block)
        self.house_numbers.append(number)
    def _init_add_to_city_plan(self):
        """Add self to the city plan."""
        #self.city.lots.add(self)

    def _init_get_neighboring_lots(self):
        """Collect all lots that neighbor this lot."""
        neighboring_lots = set()
        return neighboring_lots

    @property
    def population(self):
        """Return the number of people living/working on the lot."""
        return len(self.building.residents)

    @property
    def secondary_population(self):
        """Return the total population of this lot and its neighbors."""
        secondary_population = 0
        for lot in {self} | self.neighboring_lots:
            secondary_population += lot.population
        return secondary_population

    @property
    def tertiary_population(self):
        """Return the total population of this lot and its neighbors and its neighbors' neighbors."""
        lots_already_considered = set()
        tertiary_population = 0
        for lot in {self} | self.neighboring_lots:
            if lot not in lots_already_considered:
                lots_already_considered |= lot
                tertiary_population += lot.population
                for neighbor_to_that_lot in lot.neighboring_lots:
                    if neighbor_to_that_lot not in lots_already_considered:
                        tertiary_population += lot.population
        return tertiary_population

    @property
    def dist_from_downtown(self):
        """Return the Manhattan distance between this lot and the center of downtown."""
        dist = -1
        return dist

    def get_dist_to(self, lot_or_tract):
        """Return the Manhattan distance between this lot and some lot or tract."""
        dist = -1
        return dist

    def dist_to_nearest_company_of_type(self, company_type):
        """Return the Manhattan distance between this lot and the nearest company of the given type."""
        distances = (
            self.get_dist_to(company.lot) for company in self.city.companies if isinstance(company, company_type)
        )
        if distances:
            return min(distances)
        else:
            return None


class Tract(Lot):
    """A tract of land on a block in a city, upon which parks and cemeteries are established."""

    def __init__(self):
        """Initialize a Lot object."""
        super(Tract, self).__init__()

    def _init_add_to_city_plan(self):
        """Add self to the city plan."""
        #self.city.tracts.add(self)
