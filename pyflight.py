# Henry Cooney
# hacoo36@gmail.com
#
# pyflight.py
# 21 April 2015
#
# PyopenGL flight simulator - viewer / interaction module
#
# This file contains the basic "engine" for PyFlight, a simple PyOpenGL
# flight simulator. This module is responsible for most OpenGl interaction,
# it processes user input, and executes the OpenGL draw loop.
#
# Basically, it is a very simple engine that allows the player to move
#x around an environment.
#
# Running this module in python (python3.3 pyflight.py) will start the simulator.
#
# Much of this code was based on work from the following sources:
# Jim Fix - scene.py
# http://cs.lmu.edu/~ray/notes/flightsimulator/ -- An OpenGL Flight Simulator

import sys
from math import sin, cos, acos, asin, pi, sqrt

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from OpenGL.GLU import *
from ctypes import *

from geometry import point, vector, ORIGIN
from quat import quat
from controls import *
from landscape import *

from constants import *
from airplane import *
from hud import *
from time import *



# global variables

width = 512 # window h
height = 512 # widow w
radius = 1.0 # window "radius" - how large things appear

xStart = 0
yStart = 0
trackball = quat.for_rotation(0.0,vector(1.0,0.0,0.0))
land = None
vertex_buffer = None
horizone_vertex_buffer = None
vertices = []

forward = 0.0
right = 0.0
up = 0.0

plane = airplane()
phud = hud(plane) # player's HUD

mouse_x = 0.0
mouse_y = 0.0
rudder = 0.0


# Main draw function

def draw():
    """ draw the scene """
    global land, vertices, vertex_buffer, forward, right, up, height, width
    
    
    # Clear the rendering information.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)    

    # Clear the transformation stack.
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    trackball.glRotate()
    #s = 1
    #glScalef(s, s, s)
    # Get the plane's position to set view
    Pilot, Nose, Up = plane.getViewpoint()
    horizon_verts = phud.getHorizon()
    fpm_verts = phud.getFPM()
    gluLookAt(Pilot.x, Pilot.y, Pilot.z, Nose.x, Nose.y, Nose.z, Up.dx, Up.dy, Up.dz)
    # Load VBOs
    #glBindBuffer(GL_ARRAY_BUFFER, vertices)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE ) # wireframe mode
    
    # Draw the terrain
    glColor3f(0.8, 0.4, 1.0)
    glLineWidth(1.0)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glDisableVertexAttribArray(0)
    
    # Now, draw the HUD:
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glColor3f(0.0, 1.0, 0.0)
    for i in range(4):
        glVertex3f(horizon_verts[3*i], horizon_verts[3*i+1], horizon_verts[3*i+2])

    for i in range(12):
        glVertex3f(fpm_verts[3*i], fpm_verts[3*i+1], fpm_verts[3*i+2])
                   
    glEnd()
    glPopMatrix()

    # Draw the text parts of the HUD:
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    
    glLoadIdentity()
    glOrtho(0.0, width, height, 0.0, -1.0, 1.0)
    
    #glMatrixMode(GL_MODELVIEW)
    #glLoadIdentity()

    # Altimeter
    glRasterPos(width*(2/3), height*(5/12), 1.0)
    glutBitmapString(GLUT_BITMAP_9_BY_15, phud.getAltimeter())

    #Airspeed indicator
    glRasterPos(width*(1/6), height*(5/12), 1.0)
    glutBitmapString(GLUT_BITMAP_9_BY_15, phud.getAirspeed())

    
    #AoA Indicator
    glRasterPos(width*(9/12), height*(7/12), 1.0)
    glutBitmapString(GLUT_BITMAP_9_BY_15, phud.getAoA())

    #VVI
    glRasterPos(width*(9/12), height*(8/12), 1.0)
    glutBitmapString(GLUT_BITMAP_9_BY_15, phud.getVVI())

    #The bitchin betty!
    glColor3f(1.0, 0.0, 0.0)
    glRasterPos(width*(5/12), height*(4/12), 1.0)
    glutBitmapString(GLUT_BITMAP_HELVETICA_18, phud.getBitchinBetty())

    # Debuggers
    glColor3f(0.0, 1.0, 0.0)
    glRasterPos(width*(1/6), height*(7/12), 1.0)
    glutBitmapString(GLUT_BITMAP_9_BY_15, phud.getDebug1())
    glRasterPos(width*(1/6), height*(8/12), 1.0)
    glutBitmapString(GLUT_BITMAP_9_BY_15, phud.getDebug2())

        
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glFlush()
    
    glutSwapBuffers()

def timer(val):
    """ Pauses the scene and renders at 60 fps if possible """
    global rudder
    
    glutPostRedisplay()
    # update the plane's position and get it
    plane.inputStick(mouse_x, mouse_y)
    plane.inputRudder(rudder)
    plane.fly()
    phud.update()
    glutTimerFunc(MS_PER_FRAME, timer, 0)
    

# Control callback functions

def resize(w, h):
    """ Register a window resize by changing the viewport.  """
    global width, height, scale, vertex_buffer

    r = radius
    glViewport(0, 0, w, h)
    width = w
    height = h
    scale = 2.0 * r/w
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, width/height, 0.001,  2500.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def mouse_controller(x, y):
    """ Gets mouse position, turns mouse into artificial joystick """
    global mouse_x, mouse_y

    # Mouse coordinates are in pixels, so normalize them to a -0.5 to 0.5 scale.
    mouse_x = x/width - 0.5
    mouse_y = y/height - 0.5
    #print("X: " + str(mouse_x) + " Y: " + str(mouse_y))
    
    
        
def mouse(button, state, x, y):
    global xStart, yStart, trackball
    xStart = (x - width/2) * scale
    yStart = (height/2 - y) * scale

    if glutGetModifiers() == GLUT_ACTIVE_SHIFT and state == GLUT_DOWN:
        minus_z = trackball.recip().rotate(vector(0.0,0.0,-1.0))
        click = trackball.recip().rotate(vector(xStart,yStart,2.0))
        
    glutPostRedisplay()


        
        
def motion(x, y):
    global trackball, xStart, yStart
    xNow = (x - width/2) * scale
    yNow = (height/2 - y) * scale
    change = point(xNow,yNow,0.0) - point(xStart,yStart,0.0)
    axis = vector(-change.dy,change.dx,0.0)
    sin_angle = change.norm()/radius
    sin_angle = max(min(sin_angle,1.0),-1.0) # clip
    angle = asin(sin_angle)
    trackball = quat.for_rotation(angle,axis) * trackball
    xStart,yStart = xNow, yNow

    glutPostRedisplay()


    
def keyboard(key, x, y):
    """ Handle a "normal" keypress. """
    global forward, right, up, rudder

    stepsize = 5.0
    # Handle ESC key.
    if key == b'\033':	
        # "\033" is the Escape key
        sys.exit(1)

    if key == b'w':
        # move forward
        forward = forward + stepsize
        #glutPostRedisplay()

    if key == b's':
        # move backward
        forward = forward - stepsize
        #glutPostRedisplay()


    if key == b'a':
        rudder = -0.5
    
    if key == b'd':
        rudder = 0.5

        
def release(key, x, y):
    """ Handles releasing a key """
    global rudder
    
    if key == b'a':
        rudder = 0.0

    if key == b'd':
        rudder = 0.0


def init():
    """ Initializes objects used in the scene. """
    global land, vertex_buffer, vertices, vertex_buffer, horizon_vertex_buffer

    land = landscape('landscapes/16i__stonehenge.raw')
    vertices = land.getVerts()
    #vertices = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    # Add landscape to vertex buffer

    glEnableClientState(GL_VERTEX_ARRAY)


    vertex_buffer = glGenBuffers(1)
    horizon_vertex_buffer = glGenBuffers(1)
    
    glBindBuffer (GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData (GL_ARRAY_BUFFER, len(vertices)*4, 
                  (c_float*len(vertices))(*vertices), GL_STATIC_DRAW)



    
def main(argc, argv):
    """ Sets up GL and GLUT """
    global width, height

    # initialize the window
    clock()
    glutInit(argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowPosition(0, 20)
    glutInitWindowSize(width, height)
    glutCreateWindow( 'pyfly - Press ESC to quit' )
    

    # register input functions
    glutDisplayFunc(draw)
    glutReshapeFunc(resize)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(release)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutPassiveMotionFunc(mouse_controller)
    glutTimerFunc(100, timer, 0) # Start timer func after 100 ms

    # initialize my classes
    init() 

    glEnable(GL_DEPTH_TEST)

    glutMainLoop()
    glutPostRedisplay()

    
if __name__ == '__main__': main(len(sys.argv), sys.argv)



