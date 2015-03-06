from game import *
from city import *
from config import *
import pickle

if False:
    lots = pickle.load(open( "lots.dat", "rb" ))
    blocks = pickle.load(open( "blocks.dat", "rb" ))
    apartments = pickle.load(open( "apartments.dat", "rb" ))
    businesses = pickle.load(open( "businesses.dat", "rb" ))
    streets = pickle.load(open( "streets.dat", "rb" ))
    houses = pickle.load(open( "houses.dat", "rb" ))
else :
    lots = pickle.load(open( "Assets/StreamingAssets/lots.dat", "rb" ))
    blocks = pickle.load(open( "Assets/StreamingAssets/blocks.dat", "rb" ))

    apartments = pickle.load(open( "Assets/StreamingAssets/apartments.dat", "rb" ))
    businesses = pickle.load(open( "Assets/StreamingAssets/businesses.dat", "rb" ))
    streets = pickle.load(open( "Assets/StreamingAssets/streets.dat", "rb" ))
    houses = pickle.load(open( "Assets/StreamingAssets/houses.dat", "rb" ))