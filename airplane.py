# Implements the pyflight airplane. Control inputs should come from pyflight.py
# (the openGL/GLUT module), this module is responsible for computing the plane
# next position and direction.
#
# The airplane class is responsible for figuring out what forces act on the
# plane. Actual simulation is accomplished by the rigidBody class.


import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
#from scene import vertex, edge, face, scene
from random import random
from math import sin, cos, acos, asin, pi, sqrt, exp
from ctypes import *


from units import *
from part import *
from rigidbody import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *


class airplane:
    
    def __init__(s):
        """ Initialize the plane, at 10000 feet going 150kts. """

        # Parameters related to airplane's position
        # All parameters are in feet.

        # Some starting parameters
        s.altitude = ft2WU(12000) # in ft
        s.airspeed = kts2WUps(200) # in kts
        s.AngleOfAttack = 0.0 # in degrees
        
        s.Pilot = point(0.0, s.altitude, 0.0)
        s.Nose = s.Pilot + vector(0.0, 0.0, 1.0)
        s.Up = s.Pilot + vector(0.0, 1.0, 0.0)
        s.velocity = vector(0.0, 0.0, 1.0).scale(s.airspeed)


        ### OK. Init the rigid body.
        # The rigid body is the plane itself - it handles forces
        # incoming from this object and comptues the plane's new position.
        s.rigid = rigidBody(s.Pilot, 100, s.velocity)

        # Add forces to it:
        s.rigid.addForce(s.thrust)
        s.rigid.addForce(s.drag)
        s.rigid.addForce(s.gravity(s.rigid))
        s.rigid.addPointForce(s.leftWing, 'left')
        s.rigid.addPointForce(s.rightWing, 'right')
        s.rigid.addPointForce(s.elevator, 'tail')
        s.rigid.addPointForce(s.rudder, 'tail')
        s.rigid.addPointForce(s.stabilizer, 'tail')
        s.warning = False # whether or not to flash the warning lamp
        
        # Control parameters
        s.x = 0.0 # The mouse/joystick x coord (-0.5 to 0.5)
        s.y = 0.0 # Mouse/joystick y coord (-0.5 to 0.5)
        s.r = 0.0 # Keyboard rudder control (-0.5 or 0.5)

    def inputStick(s, x, y):
        """ Sets the current position of the "stick" --
        mouse or joystick """
        s.x = x
        s.y = y

    def inputRudder(s, rudder_input):
        """ Sets the current rudder input """
        s.r = rudder_input
        
    def fly(s):
        """ Update the airplane's position, direction """
        # Tell the rigid body to go for it
        s.warning = False # reset the warning
        rigidBody.updateAll()

        s.airspeed = s.rigid.V.norm()
        s.Nose = s.rigid.P + s.rigid.n.unit() 
        s.Pilot = s.rigid.P
        s.Up = s.rigid.lift.unit()
        s.AngleOfAttack = s.AoA(s.rigid)
        s.altitude = s.rigid.P.y


    def thrust(s, obj):
        """ Compute the current thrust force vector in world units
        per frame, on the rigid body obj. """
        #return vector(0.0, 0.0, 0.0)
        return obj.n.scale(ft2WU(2000))


    def drag(s, obj):
        """ Compute current drag vector, return it """
        # Drag always goes in the opposite direction of velocity.
        # It's related to the CoD and the velocity squared.

        v = obj.V
        dragCoefficient = s.CoD(obj)
        magnitude = WUps2kts(v.norm()) # knots per hour
        magnitude = magnitude * 6076/3600 # converts to ft/s
        p = 0.001 # Air density (lbm/ft^3)
        return(v.scale(-1/2 * p * dragCoefficient * magnitude**2))
        
    
        

    def Airflow(s, obj):
        """ Compute the current airflow, i.e., how much air is going
        over the wings. Airflow is the component of velocity that
        is parallel to the nose-tail axis. """
        
        return obj.V.projOnto(obj.n)

        
    def AoA(s, obj):
        """ Computes the current angle of attack, in degrees. AoA is the
        angle between where the plane is pointed, and where it's actually
        going. """

        # Check if AoA should be negative. AoA is negative
        # when the angle between the flight vector and the lift vector
        # is less than 90 deg.
        
        if (obj.V.angleBetween(obj.lift) < pi/2):
            return -((obj.n.angleBetween(obj.V)) * (180/pi))

        return (obj.n.angleBetween(obj.V)) * (180/pi)

        
    def CoL(s, obj):
        """ Computes the coefficient of lift for this airfoil. CoL
        is a function of angle of attack. """
        
        # CoL is different for every airfoil. I decided to create a plausible
        # airfoil by combining two logistic functions. The wing should
        # generate good lift between around 10 and 22 degrees, after 22 deg,
        # there is a rapid dropoff in lift. The CoL never goes below
        # 0.3, so the plane can always be controlled somewhat.
        
        aoa = s.AoA(obj)
        if aoa > 30:
            #warning! you're about to stall!
            s.warning = True
        
        if aoa <= -8.3 or aoa >= 36.88:
            return 0.3 # the wing is completely stalled. You still get a little
            # lift.

        if aoa <= 22.87:
            # We are in the ascending part of curve:
            return 1.0 / (1.0 + exp(-0.20 * (aoa + 4.0)))

        # otherwise, we are in the descending part of the curve (the
        # wing is starting to stall)
        return 1.0 - (1.0 / (1.0 + exp(-0.45 * (aoa - 35))))


    def CoD(s, obj):
        """ Computes the coefficient of drag, a function of AoA. """
        aoa = s.AoA(obj)
        if aoa > 31.5 or aoa < -31.5:
            return 1.0 # maximum CoD reached
        # CoD is related to AoA quadratically
        return 0.0005 * aoa**2



    def lift(s, obj):
        """ Compute the current lift magnitude, return it.
        Lift is a function of airflow and coefficient of lift """

        # Lift just multiplies CoL by airflow and by another constant.
        # Use the constant to adjust how much lift the plane gets.
        # A heavier plane will need more lift, etc.
        
        liftCoefficient = s.CoL(obj) 
        speedCoefficient = s.airspeedMultiplier(obj)
        z = 70 # Adjust this coefficient to get the
        # right amount of lift (represents wing area and air density)
        
        return obj.lift.scale(speedCoefficient*liftCoefficient*z)
        


    def airspeedMultiplier(s, obj):
        """ Returns the airspeed multiplier. Airspeed should increase
        lift quadratically, but I'm modeling it as a sigmoidal relationship-
        so the plane shouldn't get much extra lift about 350kts. """

        speed = WUps2kts(obj.V.norm())
        return 2.25 / (1 + exp(-0.024 * (speed - 212)))
        
    def getP(s):
        """ Returns the position, scaled to world units """
        return point(s.P.x*s, s.P.y*s, s.P.z*s)


    def rightWing(s, obj):
        """ Models the right wing. The right wing has lift; its lift
        is scaled by the control input (allowing the plane to roll) """

        lift = s.lift(obj)/2
        return lift.scale(s.x+1)
        #return s.rigid.lift.scale(-s.lift(obj) * (-s.x + 1))


    
    def leftWing(s, obj):
        """ Models the left wing. The left wing has lift; its lift
        is scaled by the control input (allowing the plane to roll) """

        lift = s.lift(obj)/2 # Two wings so divide by 2
        return lift.scale(-s.x + 1)
        

    def elevator(s, obj):
        """ A very simple elevator. """
        return s.lift(s.rigid).scale(-s.y/2)

    def rudder(s, obj):
        """ A very simple rudder """
        lift = s.lift(obj)
        return lift.cross(obj.n).scale(s.r*0.15)

    def stabilizer(s, obj):
        """ Airplanes are designed to be stable. This represents a well
        designed airplane's tendency to fly straight, exerting a 
        force that brings the nose in line with the direction of flight.
        I don't know how realistic this is, but adding this force
        makes the plane feel more like a real airplane, and makes it
        easier to control. """
        
        offsetVector = obj.n + obj.V.unit().scale(-1) # Difference between nose
        # and actual direction

        return offsetVector.scale(s.CoL(obj)*2)

        
    def gravity(s, obj):
        """ Gets the gravity vector """
        return vector(0.0, -(ft2WU(32.2))*obj.M, 0.0)

    def getViewpoint(s):
        """ Return the current viewing parameters - pilot position,
        nose position, and up vector """
        return s.Pilot, s.Nose, s.Up