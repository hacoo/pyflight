# Henry Cooney
# hacoo36@gmail.com
#
# landscape.py
# 21 April 2015
#
# Creates a landscape using OpenGL, for use in PyFlight. Creates bumpy
# height-mapped terrain. Based on a tutorial by Ben Humphrey (DigiBen)
# and Jeff Molofee (Nehe):
#http://nehe.gamedev.net/tutorial/beautiful_landscapes_by_means_of_height_mapping/16006/
#
# This class loads a .raw image file into 3d heightmapped terrain. 




from OpenGL.GL import *

from struct import *
from constants import *
from numpy import array, matrix, zeros

# landscape constants
    
MAP_SIZE = AREA_SIZE
IMAGE_SIZE = 256 # per side.
PIXELS = 256*256
HEIGHTMAP_RAW_MAX = 65535 # 16 bit heightmap
STEP_SIZE = MAP_SIZE / IMAGE_SIZE # How far apart each vertex is
HEIGHT_RATIO = 0.0020 # terrain scaling constant
RADIUS = MAP_SIZE // 2

# at 10000ft. This corresponds to max hill height of about 6000ft, but
# 0.003 seems to be a good scaling factor, creating nice, rolling hills
# the terrain is very "spread out", it seems lower than this.


class landscape:
    # Height mapped landscape class
   
    def __init__(self, filepath):
        """ Initialize the landscape, loading from file at FILEPATH """

        self.pixels = zeros(shape=(IMAGE_SIZE, IMAGE_SIZE))
        self.verts = []


        # Load the file
        self.loadRawFile(filepath)
        # Load the file infomation into 3d heightmap coordinates,
        # ready to be interpreted as a openGL quads:
        self.makeQuadsArray()
        
        

    def loadRawFile(self, filepath):
        """ Load a .raw heightmap into the matrix self.pixels """
        
        print("Loading " + filepath)
        f = open(filepath, "rb") # read byte mode

        byte = f.read(2)

        for i in range(IMAGE_SIZE):
            for ii in range(IMAGE_SIZE):
                byte = f.read(2)
                value=unpack('H', byte)
                self.pixels[i, ii] = value[0]
            
        print("Heightmap loaded.")
        print(self.pixels)
        print("MAX:")
        print(self.pixels.max())
        print("MIN:")
        print(self.pixels.min())
        

    def makeQuadsArray(self):
        """ Convert the 2d matrix of image pixels into an array
        of OpenGL coordinates, scaled to our map size. """ 

        # vertices will be added to the vertex array row
        # at a time. The terrain is centered at the origin, and
        # stretches across a MAP_SIZE sized area.

     

        #for i in range(125,126):
        for i in range(IMAGE_SIZE-1):
            for ii in range(IMAGE_SIZE-1):
                self.appendQuadCoords(i, ii)


        
        
    def appendQuadCoords(self, x, y):
        """ appends the quadrilateral coordinates for pixel at (x,y) to the
        vertex list """
        
        ycoord = RADIUS - y*STEP_SIZE
        xcoord = (-RADIUS) + x*STEP_SIZE
                    
        q1 = [xcoord, self.pixels[y][x]*HEIGHT_RATIO, ycoord]
        q2 = [xcoord+STEP_SIZE, self.pixels[y][x+1]*HEIGHT_RATIO, ycoord]
        q3 = [xcoord, self.pixels[y+1][x]*HEIGHT_RATIO, ycoord-STEP_SIZE]
        q4 = [xcoord+STEP_SIZE, self.pixels[y+1][x+1]*HEIGHT_RATIO, ycoord-STEP_SIZE]

        self.verts.extend(q1)
        self.verts.extend(q2)
        self.verts.extend(q3)
        self.verts.extend(q2)
        self.verts.extend(q3)
        self.verts.extend(q4)

    def draw(self):
        """ draws the landscape without using a buffer. Slow!! """

        glBegin(GL_TRIANGLES)

        for i in range(0, len(self.verts), 3):
            glVertex3f(self.verts[i], self.verts[i+1], self.verts[i+1])

        glEnd()

    def getVerts(self):
        """ Return the landscape vertices """
        return self.verts

        
        
        


    
            
            
            
            
            
            
                
                
        