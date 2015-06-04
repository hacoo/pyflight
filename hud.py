# Makes a hud for the airplane. The hud references an airplane object,
# and uses it to determine coordinates for drawing a 2D HUD. Use GLOrtho
# to draw the hud.

# The hud draws the following:
# Horizon line
# Flight-path marker (FPM)
# Airspeed (knots)
# Altitude (feet)
# AoA (degrees)
# VVI (ft/s)
# And debugging info...


from geometry import *
from quat import *
from airplane import *
from constants import *

from numpy import *
from math import sin, cos, sqrt
from quat import *


class hud:


    def __init__(s, plane):
        """ Creates a HUD for the airplane object plane """

        s.plane = plane
        s.P = None
        s.Nose = None
        s.Up = None
        s.airspeed = None
        s.altitude = None
        s.AoA = None
        s.warningsDisplayed = 0
        s.Displaying = False

        # Vertex arrays for each hud element
        s.horizon_verts = list(range(12))
        s.fpm_verts = list(range(36))
    
        s.getPlaneState()


    def getHorizon(s):
        """ Get the HUD's current vertex arrays. """
        return s.horizon_verts

    def getFPM(s):
        """ Get the current FPM vertices """
        return s.fpm_verts

    def getAltimeter(s):
        """ Gets the current altimeter reading, as a cstring, ready for display """
        output = str(round(s.altitude)) + " ft MSL"
        return output.encode('utf-8')

    def getAoA(s):
        """ Get displayable AoA """
        output = str(round(s.AoA)) + " deg."
        return output.encode('utf-8')

    def getAirspeed(s):
        """ Get displayable airspeed """
        output = str(round(s.airspeed)) + " kts"
        return output.encode('utf-8')

    def getVVI(s):
        """ Get the vertical velocity indicator """
        output = str(round(s.VVI)) + " ft/s V" 
        return output.encode('utf-8')

    def getDebug1(s):
        """ Gets the first debugger instrument """
        output = "Lift Force: " + str(round(s.debug1,2))
        return output.encode('utf-8')

    def getDebug2(s):
        """ Gets the first debugger instrument """
        output = "Drag Force: " + str(round(s.debug2,1))
        #output = "LVEC: " + str(s.debug2)
        return output.encode('utf-8')


    def getBitchinBetty(s):
        """ Returns the bitchin' betty string, basically a warning
        or whatever. Mostly for debugging. The warning will blink
        annoyingly. """

        # To implement blinking, the warning will be on for 30 frames,
        # then off for 30 frames

        output = ""
        
        if s.plane.warning == False:
            s.warningsDisplayed = 0
            s.Displaying = False
            return output.encode('utf-8')

        if (s.warningsDisplayed % 15 == 0):
            s.warningsDisplayed = 0
            # Flip the display status:
            s.Displaying = not(s.Displaying)
            
        s.warningsDisplayed += 1
        
        if(s.Displaying == True):
            output = "WARNING"
            
        return output.encode('utf-8')
            

                
        
    def getPlaneState(s):
        """ Gets the current state of the plane """

        s.P = s.plane.rigid.P
        s.x = vector(s.plane.rigid.P.x, s.plane.rigid.P.y, s.plane.rigid.P.z)
        s.Nose = s.plane.rigid.nose
        s.Up = s.plane.rigid.lift
        s.airspeed = s.plane.airspeed
        s.altitude = s.plane.altitude
        s.AoA = s.plane.AoA(s.plane.rigid)


    

    def update(s):
        """ Update the HUD based on current plane state """
        s.getPlaneState()
        s.horizon()
        s.FPM()
        s.instruments()
        
    def horizon(s):
        """ Gets coordinates for the current horizon line """

        # The horizon is normal to the lift vector and the nose.
        #c = s.Nose.cross(vector(0.0, 1.0, 0.0).unit()
        
        c = vector(s.Nose.dx, 0.0, s.Nose.dz)
        h = c.cross(vector(0.0, 1.0, 0.0))
        h = h.unit()
        # Get the points that we should actually draw:
        v = list(range(4))
        v[0] = s.P+(s.Nose + h.scale(0.07))
        v[1] = s.P+(s.Nose + h.scale(0.5))
        v[2] = s.P+(s.Nose + h.scale(-0.07))
        v[3] = s.P+(s.Nose + h.scale(-0.5))

        
        for i in range(4):
            z = v[i].components()
            for ii in range(3):
                s.horizon_verts[3*i+ii] = z[ii]

                
    def FPM(s):
        """ Gets coordinates for the current FPM. The FPM looks like a small
            winged diamond. """
            
        # The FMP is a just a marker of the velocity vector.
        
        center = s.P + s.plane.rigid.V.unit()
        temp = vector(s.Nose.dx, 0.0, s.Nose.dz)
        h = temp.cross(vector(0.0, 1.0, 0.0)).unit() # horizon vector
        #h = temp.cross(s.plane.rigid.lift).unit()
        up = vector(0.0, 1.0, 0.0) # vertical vector

        v = list(range(6))
        v[0] = center + up.scale(0.02)
        v[1] = center + h.scale(0.02)
        v[2] = center + up.scale(-0.02)
        v[3] = center + h.scale(-0.02)
        v[4] = center + h.scale(-0.04)
        v[5] = center + h.scale(0.04)
        
        # Make the diamond
        for i in range(4):
            z1 = v[i].components()
            z2 = v[(i+1) % 4].components()
            for ii in range(3):
                s.fpm_verts[6*i+ii] = z1[ii]
                s.fpm_verts[6*i+ii+3] = z2[ii]

        # Make the wingies
        v3 = v[3].components()
        v1 = v[1].components()
        v5 = v[5].components()
        v4 = v[4].components()
        
        for i in range(3):
            s.fpm_verts[24+i] = v3[i]
            s.fpm_verts[27+i] = v4[i]
            s.fpm_verts[30+i] = v1[i]
            s.fpm_verts[33+i] = v5[i]
                
        
    def instruments(s):
        """ Update all the instruments - altitude, airspeed, the debugger, etc.
        """
        s.airspeed = WUps2kts(s.airspeed)
        s.altitude = WU2ft(s.altitude)
        s.VVI = WU2ft(s.plane.rigid.V.dy) 
        s.debug1 = s.plane.lift(s.plane.rigid).norm()
        s.debug2 = s.plane.drag(s.plane.rigid).norm()
        
        
        
        

        
        

        
        
        
        

        