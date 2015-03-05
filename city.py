import random
from business import *
from residence import *
from occupation import *
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


def clamp(val, minimum, maximum):
    return max(minimum, min(val, maximum))


class City(object):
    """A city in which a gameplay instance takes place."""

    def __init__(self, gameState):
        """Initialize a City object."""
        self.game = gameState
        self.founded = gameState.year
        self.residents = set()
        self.departed = set()  # People who left the city (i.e., left the simulation)
        self.deceased = set()  # People who died in in the city
        self.companies = set()
        self.lots = set()
        self.tracts = set()
        self.dwelling_places = set()  # Both houses and apartment units (not complexes)
        self.houses = set()  # Convenience wrapper for C# land
        self.apartment_complexes = set()  # Convenience wrapper for C# land
        self.other_businesses = set()  # Convenience wrapper for C# land
        self.streets = set()
        self.blocks = set()
        self.generateLots(gameState.config)
        for lot in self.lots | self.tracts:
            lot.setNeighboringLots()
            lot.init_generate_address()
        self.paths = {}
        self.generatePaths()
        self.downtown = None
        highestDensity = -1
        for lot in self.lots:
            density =  self.tertiary_density(lot)
            if (density > highestDensity):
                highestDensity = density
                self.downtown = lot
        self.name = None  # Gets set by Game.establish_setting()
        # These get set when these businesses get established (by their __init__() magic methods)
        self.cemetery = None
        self.city_hall = None
        self.fire_station = None
        self.hospital = None
        self.police_station = None
        self.school = None
        self.university = None

    def dist_from_downtown(self,lot):
        
        return self.getDistFrom(lot,self.downtown)

    def generatePaths(self):
        for start in self.blocks:
            for goal in self.blocks:
                if (start == goal):
                     self.paths[(start,goal)] = 0
                else :
                    if ((start,goal) not in self.paths):
                        came_from, cost_so_far = City.a_star_search(start,goal)
                        current  = goal
                        count = 0
                        while (current != start):
                            current = came_from[current]
                            count += 1
                        self.paths[(start,goal)] =count
                        self.paths[(goal,start)] =count
                        
    def getDistFrom(self, lot1, lot2):
        minDist = float("inf")
        for block1 in lot1.blocks:
            for block2 in lot2.blocks:
                if self.paths[(block1,block2)] < minDist:
                    minDist = self.paths[(block1,block2)]
        return minDist

    def nearest_business_of_type(self, lot, business_type):
        """Return the Manhattan distance between this lot and the nearest company of the given type.

        @param business_type: The Class representing the type of company in question.
        """
        businesses_of_this_type = self.businesses_of_type(business_type)
        if businesses_of_this_type:
            return min(businesses_of_this_type, key=lambda b: self.getDistFrom(lot, b.lot))
        else:
            return None
        
    def dist_to_nearest_business_of_type(self, lot, business_type, exclusion):
        """Return the Manhattan distance between this lot and the nearest company of the given type.

        @param business_type: The Class representing the type of company in question.
        @param exclusion: A company who is being excluded from this determination because they
                          are the ones making the call to this method, as they try to decide where
                          to put their lot.
        """
        distances = [
            self.getDistFrom(lot, company.lot) for company in self.companies if isinstance(company, business_type)
            and company is not exclusion
        ]
        if distances:
            return max(99, min(distances))  # Elsewhere, a max of 99 is relied on
        else:
            return None

    def secondary_population(self, lot):
        """Return the total population of this lot and its neighbors."""
        secondary_population = 0
        for neighbor in set([lot]) | lot.neighboring_lots:
            secondary_population += neighbor.population
        return secondary_population

    def tertiary_population(self, lot):
        lots_already_considered = set()
        tertiary_population = 0
        for neighbor in set([lot]) | lot.neighboring_lots:
            if neighbor not in lots_already_considered:
                lots_already_considered.add(neighbor)
                tertiary_population += neighbor.population
                for neighbor_to_that_lot in neighbor.neighboring_lots:
                    if neighbor_to_that_lot not in lots_already_considered:
                        lots_already_considered.add(neighbor_to_that_lot)
                        tertiary_population += neighbor.population
        return tertiary_population
        
    def tertiary_density(self, lot):
        lots_already_considered = set()
        tertiary_density = 0
        for neighbor in set([lot]) | lot.neighboring_lots:
            if neighbor not in lots_already_considered:
                lots_already_considered.add(neighbor)
                tertiary_density += 1
                for neighbor_to_that_lot in neighbor.neighboring_lots:
                    if neighbor_to_that_lot not in lots_already_considered:
                        lots_already_considered.add(neighbor_to_that_lot)
                        tertiary_density += 1
        return tertiary_density
        
    def generateLots(self, configFile):
        
        loci = configFile.loci
        samples = configFile.samples
        size = configFile.size
        
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
            reifiedStreet = (Street(self, number, direction, startingBlock, endingBlock))
            self.streets.add(reifiedStreet)
            for ii in range(startingBlock, endingBlock+1):
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
                    connections[coord] = set()
                connections[coord].add(next)
                if (not next in connections):
                    connections[next] = set()
                connections[next].add(coord)
                

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

        totalCount = 0;
        corners = set()
        for block in blocks:
            ew = int(block[0]/2)+1
            ns = int(block[1]/2)+1 
            sizeOfBlock = int(block[2]/2)
            tract = None
            if (sizeOfBlock > 1):
                tract = Tract(self)
                self.tracts.add(tract)
            for ii in range(0,sizeOfBlock+1):
                
                insertOnce(Blocks,(ew,ns+ii,'NS'),Block( nsStreets[(ew,ns)], (ii+ns)*100,(ew,ns+ii))) 
                insertOnce(Numberings,(ew,ns+ii,'E'),Block.determine_house_numbering( (ii+ns)*100,'E', configFile))
                insertOnce(Blocks,(ew+ii,ns,'EW'),Block( ewStreets[(ew,ns)], (ii+ew)*100,(ew+ii,ns)))        
                insertOnce(Numberings,(ew+ii,ns,'N'),Block.determine_house_numbering( (ii+ew)*100,'N', configFile))
                insertOnce(Blocks,(ew+sizeOfBlock,ns+ii,'NS'),Block( nsStreets[(ew+sizeOfBlock,ns)], (ii+ns)*100,(ew+sizeOfBlock,ns+ii)))   
                insertOnce(Numberings,(ew+sizeOfBlock,ns+ii,'W'),Block.determine_house_numbering( (ii+ns)*100,'W', configFile))     
                insertOnce(Blocks,(ew+ii,ns+sizeOfBlock,'EW'),Block( ewStreets[(ew,ns+sizeOfBlock)], (ii+ew)*100,(ew+ii,ns+sizeOfBlock)))
                insertOnce(Numberings,(ew+ii,ns+sizeOfBlock,'S'),Block.determine_house_numbering( (ii+ew)*100,'S', configFile)) 
                if (tract != None):
                    tract.addBlock(Blocks[(ew,ns+ii,'NS')],Numberings[(ew,ns+ii,'E')][n_buildings_per_block],'E',0)
                    tract.addBlock( Blocks[(ew+ii,ns,'EW')],Numberings[(ew+ii,ns,'N')][n_buildings_per_block] ,'N',0)
                    if (ew+sizeOfBlock <= size/2):
                        tract.addBlock(Blocks[(ew+sizeOfBlock,ns+ii,'NS')],Numberings[(ew+sizeOfBlock,ns+ii,'W')][n_buildings_per_block],'W',0)
                    
                    if (ns+sizeOfBlock <= size/2):
                        tract.addBlock( Blocks[(ew+ii,ns+sizeOfBlock,'EW')],Numberings[(ew+ii,ns+sizeOfBlock,'S')][n_buildings_per_block],'S',0)
             
            neCorner = Lot(self)
            insertInto(lots,(ew,ns,'N'),(0,neCorner))
            insertInto(lots,(ew,ns,'E'),(0,neCorner))
            self.lots.add(neCorner)
            corners.add((ew,ns,'EW',ew,ns,'NS'))
            
            nwCorner = Lot(self)
            if (ew+sizeOfBlock <= size/2):
                insertInto(lots,(ew+sizeOfBlock-1,ns,'N'),(n_buildings_per_block-1,nwCorner))
            insertInto(lots,(ew+sizeOfBlock,ns,'W'),(0,nwCorner))            
            corners.add((ew+sizeOfBlock-1,ns,'EW',ew+sizeOfBlock,ns,'NS'))
            self.lots.add(nwCorner)
            
            seCorner = Lot(self)
            insertInto(lots,(ew,ns+sizeOfBlock,'S'),(0,seCorner))
            if (ns+sizeOfBlock <= size/2):
                insertInto(lots,(ew,ns+sizeOfBlock-1,'E'),(n_buildings_per_block-1,seCorner))
            self.lots.add(seCorner)
            corners.add((ew,ns+sizeOfBlock,'EW',ew,ns+sizeOfBlock-1,'NS'))
            
            swCorner = Lot(self)
            insertInto(lots,(ew+sizeOfBlock-1,ns+sizeOfBlock,'S'),(n_buildings_per_block-1,swCorner))  
            insertInto(lots,(ew+sizeOfBlock,ns+sizeOfBlock-1,'W'),(n_buildings_per_block-1,swCorner))    
            corners.add((ew+sizeOfBlock-1,ns+sizeOfBlock,'EW',ew+sizeOfBlock,ns+sizeOfBlock-1,'NS'))        
            self.lots.add(swCorner)
            
            for ii in range(1,sizeOfBlock*configFile.n_buildings_per_block-1): 
                blockNum = int(ii/2)
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew,ns+blockNum,'E'),(ii %n_buildings_per_block,lot))
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew+blockNum,ns,'N'),(ii %n_buildings_per_block,lot))
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew+sizeOfBlock,ns+blockNum,'W'),(ii %n_buildings_per_block,lot))
                lot = Lot(self)
                self.lots.add(lot)      
                insertInto(lots,(ew+blockNum,ns+sizeOfBlock,'S'),(ii %n_buildings_per_block,lot))  
        for block in lots:
            dir = 'NS' if block[2] == 'W' or block[2] == 'E' else 'EW'
            actualBlock = Blocks[(block[0],block[1],dir)]
            lotList = lots[block]
            
            for lot in lotList:
                lot[1].addBlock(actualBlock,Numberings[block][lot[0]],block[2],lot[0])
                actualBlock.lots.append(lot[1])
                
        for conn in connections: 
            for neighbor in connections[conn]:
                dx = neighbor[0] - conn[0]
                dy = neighbor[1] - conn[1]
                if dx != 0:
                    if (conn[0],conn[1],'EW') in Blocks and (neighbor[0],neighbor[1],'EW') in Blocks:
                        Blocks[(conn[0],conn[1],'EW')].addNeighbor(Blocks[(neighbor[0],neighbor[1],'EW')])
                if dy != 0:
                    if (conn[0],conn[1],'NS') in Blocks and (neighbor[0],neighbor[1],'NS') in Blocks:
                        Blocks[(conn[0],conn[1],'NS')].addNeighbor(Blocks[(neighbor[0],neighbor[1],'NS')])
        for corner in corners:
            Blocks[(corner[0],corner[1],corner[2])].addNeighbor(Blocks[(corner[3],corner[4],corner[5])])
            Blocks[(corner[3],corner[4],corner[5])].addNeighbor(Blocks[(corner[0],corner[1],corner[2])])
            
        for block in Blocks:
            self.blocks.add(Blocks[block])
        self.mayor = None  # Currently being set to city founder by CityHall.__init__()

    def temp_init_lots_and_tracts_for_testing(self):
        for i in xrange(256):
            meaningless_block = Block(city=self, x_coord=0, y_coord=0, ewstreet=None, nsstreet=None, number=i)
            Lot(block=meaningless_block, house_number=999)
        for j in xrange(6):
            meaningless_block = Block(city=self, x_coord=0, y_coord=0, ewstreet=None, nsstreet=None, number=j+256)
            Tract(block=meaningless_block, house_number=999)

    @property
    def pop(self):
        """Return the number of residents living in the city."""
        return len(self.residents)

    @property
    def population(self):
        """Return the number of residents living in the city."""
        return len(self.residents)

    @property
    def vacant_lots(self):
        """Return all vacant lots in the city."""
        vacant_lots = [lot for lot in self.lots if not lot.building]
        return vacant_lots

    @property
    def vacant_tracts(self):
        """Return all vacant tracts in the city."""
        vacant_tracts = [tract for tract in self.tracts if not tract.landmark]
        return vacant_tracts

    @property
    def vacant_homes(self):
        """Return all vacant homes in the city."""
        vacant_homes = [home for home in self.dwelling_places if not home.residents]
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
        return [resident for resident in self.residents if isinstance(resident.occupation, occupation)]

    def businesses_of_type(self, business_type):
        """Return all business in this city of the given type.

        @param business_type: A string of the Class name representing the type of business in question.
        """
        businesses_of_this_type = [
            company for company in self.companies if company.__class__.__name__ == business_type
        ]
        return businesses_of_this_type

    @staticmethod
    def heuristic(a, b):
        (x1, y1) = a.coords
        (x2, y2) = b.coords
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
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
                    priority = new_cost + City.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        return came_from, cost_so_far


class Street(object):
    """A street in a city."""

    def __init__(self, city, number, direction, startingBlock, endingBlock):
        """Initialize a Street object."""
        self.city = city
        self.number = number
        self.direction = direction  # Direction relative to the center of the city
        self.name = self.generate_name(number, direction)
        self.startingBlock = startingBlock
        self.endingBlock = endingBlock

    def generate_name(self, number, direction):
        """Generate a street name."""
        config = self.city.game.config
        number_to_ordinal = {
            1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th',
            6: '6th', 7: '7th', 8: '8th', 9: '9th'
        }
        if direction == 'E' or direction == 'W':
            street_type = 'Street'
            if random.random() < config.chance_street_gets_numbered_name:
                name = number_to_ordinal[number]
            else:
                if random.random() < 0.5:
                    name = Names.any_surname()
                else:
                    name = Names.a_place_name()
        else:
            street_type = 'Avenue'
            if random.random() < config.chance_avenue_gets_numbered_name:
                name = number_to_ordinal[number]
            else:
                if random.random() < 0.5:
                    name = Names.any_surname()
                else:
                    name = Names.a_place_name()
        # name = "{0} {1} {2}".format(name, street_type, direction)
        name = "{0} {1}".format(name, street_type)
        return name

    def __str__(self):
        """Return string representation."""
        return self.name


class Block(object):
    """A block on a street in a city."""

    def __init__(self, street, number,coords):
        """Initialize a Block object."""
        self.street = street
        self.number = number
        self.lots = []
        self.neighbors = []
        self.coords = coords

    def __str__(self):
        """Return string representation."""
        return "{0} block of {1}".format(self.number, str(self.street))

    @property
    def buildings(self):
        """Return all the buildings on this block."""
        return (lot.building for lot in self.lots if lot.building)

    @staticmethod
    def determine_house_numbering(block_number,sideOfStreet, config):
        """Devise an appropriate house numbering scheme given the number of buildings on the block."""
        n_buildings = config.n_buildings_per_block+1
        house_numbers = []
        house_number_increment = int(100.0 / n_buildings)
        evenOdd = 0 if  sideOfStreet == "E" or sideOfStreet == "N" else 1
        for i in xrange(n_buildings):
            base_house_number = (i * house_number_increment) - 1
            house_number = base_house_number + int(random.random() * house_number_increment)
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

    def __init__(self, city):
        """Initialize a Lot object."""
        self.city = city
        self.streets = []
        self.blocks = []
        self.sidesOfStreet = []
        self.house_numbers = []  # In the event a business/landmark is erected here, it inherits this
        self.building = None  # Will always be None for Tract
        self.landmark = None  # Will always be None for Lot
        self.positionsInBlock = []
        self.neighboring_lots = set()  # Gets set by City call to setNeighboringLots after all lots have been generated
        # These get set by init_generate_address(), which gets called by City
        self.address = None
        self.street_address_is_on = None
        self.block_address_is_on = None

    @property
    def population(self):
        """Return the number of people living/working on the lot."""
        if self.building:
            population = len(self.building.residents)
        else:
            population = 0
        return population

    def addBlock(self, block, number, sideOfStreet, positionInBlock):
        self.streets.append(block.street)
        self.blocks.append(block)
        self.sidesOfStreet.append(sideOfStreet)
        self.house_numbers.append(number)
        self.positionsInBlock.append(positionInBlock)

    def setNeighboringLots(self):
        neighboringLots = set()
        for block in self.blocks:
            for lot in block.lots:
                if lot is not self:
                    neighboringLots.add(lot)
        self.neighboring_lots = neighboringLots

    def init_generate_address(self):
        """Generate an address, given the lot building is on."""
        self.index_of_street_address_will_be_on = random.randint(0, len(self.streets)-1)
        house_number = self.house_numbers[self.index_of_street_address_will_be_on]
        house_number = int(house_number)
        street = self.streets[self.index_of_street_address_will_be_on]
        self.address = "{0} {1}".format(house_number, street.name)
        self.street_address_is_on = street
        self.block_address_is_on = self.blocks[self.index_of_street_address_will_be_on]


class Tract(Lot):
    """A tract of land on a block in a city, upon which parks and cemeteries are established."""

    def __init__(self, city):
        """Initialize a Lot object."""
        super(Tract, self).__init__(city)