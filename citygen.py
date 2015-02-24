import pyqtree
from random import gauss,randrange
from city import *

def clamp(val,minimum,maximum):
    return max(minimum,min(val,maximum))
loci = 3
samples = 32
size = 16

lociLocations = []
for ii in range(loci):
    lociLocations.append([gauss(size/2.0,size/6.0), gauss(size/2.0,size/6.0)])

    
tree = pyqtree.Index(bbox=[0,0,16,16])

for ii in range(samples):
    center = lociLocations[randrange(len(lociLocations))]
    point = [clamp(gauss(center[0],size/6.0),0,size-1),clamp(gauss(center[1],size/6.0),0,size-1)]
    point.append(point[0]+1)
    point.append(point[1]+1)
    #print(point)
    tree.insert(point,point)

nsstreets = {}
ewstreets = {}
blocks = []
lots = []
tracts =[]
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
        #print(node.center[0]-node.width*0.5,node.center[1]-node.width*0.5)
    for child in node.children:
        traverseTree(child)
    
traverseTree(tree)
nsEnd = []
ewEnd = []
streets = []

for ii in range(0,18,2):
    for jj in range(0,18,2):
        street = (ii,jj)
        if street in nsstreets:
            start = street
            end = nsstreets[start]
            while end in nsstreets:
                end = nsstreets[end]
            if (end not in nsEnd):
                nsEnd.append(end)             
                streets.append([start, end])
        if street in ewstreets:
            start = street
            end = ewstreets[start]
            while end in ewstreets:
                end = ewstreets[end]
            if (end not in ewEnd):
                ewEnd.append(end)             
                streets.append([start, end])

str = "b = ["
for street in streets:
    str += "[{},{}];[{},{}];[nan,nan];".format(street[0][0],street[0][1],street[1][0],street[1][1])
str += "]" 
print(str)  
str = "a = ["
for loot in lots:
    str += "[{},{}];[nan,nan];".format(loot[0],loot[1])
str += "]"

print(str)       
print("plot(a(:,1),a(:,2),'bx',b(:,1),b(:,2),'b')")