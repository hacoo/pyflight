# Implements the airplane as a rigid body. Airplane.py handles the forces
# acting on the airplane, this module computes the actual effect of those
# forces on the plane's position and rotation.
#
# I used the following sources to figure this out:
#
# David Baraff - Phyically Based Modeling: Rigid Body Simulation
# http://www.pixar.com/companyinfo/research/pbm2001/pdf/notesg.pdf
#
# Glenn Fielder - Rotation and Inertial Tensors
# http://gafferongames.com/virtual-go/rotation-and-inertia-tensors/
# (AWESOME article!)

from geometry import *
from quat import *
from airplane import *
from constants import *

from numpy import *
from math import sin, cos, sqrt
from quat import *

class rigidBody:

    # A rigid body (specifically, the pyflight airplane!)
    instances = []

    def __init__(s, x, M, v):
        """ Initialize the plane, at point x, and with mass M, velocity
        vector v """

        s.P = x # The center position
        s.left = vector(-1.0, 0.0, 0.0) # the left wing
        s.right = vector(1.0, 0.0, 0.0) # the right wing
        s.tail = vector(0.0, 0.0, -1.0) # the tail
        s.nose = vector(0.0, 0.0, 1.0) # the nose
        s.up = vector(0.0, 1.0, 0.0) # up vector

        # The vectors below are the ROTATED vectors
        # (call rotateVectors() to update them)
        s.l = vector(-1.0, 0.0, 0.25) # the left wing
        s.r = vector(1.0, 0.0, 0.25) # the right wing
        s.t = vector(0.0, 0.0, -1.0) # the tail
        s.n = vector(0.0, 0.0, 1.0) # the nose
        s.lift = vector(0.0, 1.0, 0.0) # The lift vector

        s.acc = vector(0.0, 0.0, 0.0)
        s.omega = matrix([0, 0, 0]) # represents rotational velocity
        


        s.M = M # total mass of the plane

        s.PForces = [] # Forces acting on plane overall -
        # these will move the plane around linearly

        # Each part of the plane has its own list of forces.
        # These will constribute to the plane's rotation.
        # Gravity acts on everything, so it's allllways there
        s.lForces = [] # left wing forces
        s.rForces = [] # right wing forces
        s.nForces = [] # nose forces
        s.tForces = [] # forces on the tail

        
        s.pointForces = {} # Point force dictionary -
        # allows you to get forces lists by name
        s.pointForces['left'] = s.lForces
        s.pointForces['right'] = s.rForces
        s.pointForces['nose'] = s.nForces
        s.pointForces['tail'] = s.tForces
        s.pointForces['l'] = s.lForces
        s.pointForces['r'] = s.rForces
        s.pointForces['n'] = s.nForces
        s.pointForces['t'] = s.tForces

        s.I = matrix([[0.177721, 0.0, 0.0],
                      [0.0, 0.304776, 0.0],
                      [0.0, 0.0, 0.177721]]) * 100
        
        # This is the inertial tensor.
        # It represents the plane's distribution of mass.
        # Currently, it assumes the plane is a uniform disk shape; obviously
        # this could be improved!
        s.Iinv = linalg.inv(s.I)
        
        # The state of the airplane:

        # Rotation matrix
        s.q = quat(0.0, vector(1.0, 0.0, 0.0)) # Rotation quaternion
        s.R = matrix([[1.0, 0.0, 0.0],
                      [0.0, 1.0, 0.0],
                      [0.0, 0.0, 1.0]]) # The airplane starts out straight+level
        s.RDot = matrix([[0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0]]) # Rate of change of rot. matrix

        s.V = v # starting velocity vector
        s.AV = vector(0.0, 0.0, 0.0) # starting angular velocity
        s.LM = v.scale(s.M) # the linear momentum
        s.AM = vector(0.0, 0.0, 0.0) # the angular momentum

        rigidBody.instances.append(s)

        

    @classmethod
    def updateAll(cls):
        """ Update the positions, velocities, etc for each part """
        
        for c in cls.instances:
            c.updatePositionsEuler()
            #c.updatePosition()
            
    def computeForce(s):
        """ Get the total force acting on the body """ 

        fv = vector(0.0, 0.0, 0.0) # Overall force vector
        
        for f in s.PForces:
            # Determine if the force is a vector or a function,
            # and act appropriately:
            if hasattr(f, '__call__') == True:
                fv = fv + f(s)
            else:
                fv = fv + f

        # Forces on ALL parts of the object contribute to overall force vector
        for f in s.lForces:
            if hasattr(f, '__call__') == True:
                fv = fv + f(s)
            else:
                fv = fv + f 

        for f in s.rForces:
            if hasattr(f, '__call__') == True:
                fv = fv + f(s)
            else:
                fv = fv + f

        for f in s.nForces:
            if hasattr(f, '__call__') == True:
                fv = fv + f(s)
            else:
                fv = fv + f

        for f in s.tForces:
            if hasattr(f, '__call__') == True:
                fv = fv + f(s)
            else:
                fv = fv + f

        
        return fv.scale(TIMESTEP)

    def computeTorque(s):
        """ get the total torque vector on the object. """

        tv = vector(0.0, 0.0, 0.0)

        # Get the torques for eachpart:
        xt = vector(s.P.x, s.P.y, s.P.z) # This vector represents the current displace
        #ment
        
        for f in s.lForces:
            if hasattr(f, '__call__') == True:
                tv = tv + ((s.left).cross(f(s))) 
            else:
                tv = tv + ((s.left).cross(f))

        for f in s.rForces:
            if hasattr(f, '__call__') == True:
                tv = tv + ((s.right).cross(f(s))) 
            else:
                tv = tv + ((s.right).cross(f))

        for f in s.nForces:
            if hasattr(f, '__call__') == True:
                tv = tv + ((s.nose).cross(f(s))) 
            else:
                tv = tv + ((s.nose).cross(f))

        for f in s.tForces:
            if hasattr(f, '__call__') == True:
                tv = tv + ((s.tail).cross(f(s))) 
            else:
                tv = tv + ((s.tail).cross(f)) 
        
        # Add a rotational damping factor:
        tv += s.AM.scale(-0.1)
        return tv.scale(TIMESTEP)
            

    def updateMomentum(s):
        """ Update momentum based on current forces """
        
        s.LM += s.computeForce()
        s.AM += s.computeTorque()


    def updateVelocity(s):
        """ Use the current momentum to compute velocity """
        s.updateMomentum()
        s.V = s.LM.scale(1/s.M)

        s.omega = s.Iinv * s.AM.np_vector()
        s.RDot = star(s.omega) * s.R # Rate of change of rotation
#        s.q = s.q*quat(0.0, npArray2Vector(s.omega)).scale(1/2)
#        s.q.glRotate()

    def updateI(s):
        """ Update the inerial tensor to reflect the current orientation """

        s.I = s.R * s.I * transpose(s.R)
        s.Iinv = linalg.inv(s.I)
                                

    
    def updatePosition(s):
        """ Compute the updated position of the plane, based on velocity
        this frame. Uses RK4 """


        yn = s.P # Starting position
        ynR = s.R # starting rotation
        
        s.updateVelocity() # updates linear and angular velocity
        k1 = s.V.scale(TIMESTEP)
        k1R = s.RDot * TIMESTEP
        
        s.P = yn + k1.scale(1/2)
        s.R = ynR + k1R * (1/2)
        s.rotateVectors()
        s.updateVelocity()
        k2 = s.V.scale(TIMESTEP)
        k2R = s.RDot * TIMESTEP

        s.P = yn + k2.scale(1/2)
        s.R = ynR + k2R * (1/2)
        s.rotateVectors()
        s.updateVelocity()
        k3 = s.V.scale(TIMESTEP)
        k3R = s.RDot * TIMESTEP

        s.P = yn + k3
        s.R = ynR + k3R
        s.rotateVectors()
        s.updateVelocity()
        k4 = s.V.scale(TIMESTEP)
        k4R = s.RDot * TIMESTEP

        s.P = yn + k1.scale(1/6) + k2.scale(1/3) \
                + k3.scale(1/3) + k4.scale(1/6)
        
        s.R = ynR + k1R*(1/6) + k2R*(1/3) + k3R*(1/3) + k4R*(1/6)
        s.rotateVectors()


    def resetR(s):
        """ Resets the rotation matrix, so that the object's
        current orientation is now the "default" orientation. """
        
        s.R = matrix([[1, 0, 0],
                      [0, 1, 0],
                      [0, 0, 1]])

        s.left = s.l
        s.right = s.r
        s.nose = s.n
        s.tail = s.t
        s.up = s.lift

    def addForce(s, f):
        """ Adds a force to this object's force list. Forces are either
        functions returning vectors or just vectors. """

        s.PForces.append(f)

    def addPointForce(s, f, p):
        """ Adds a force to this object, acting at a particular point.
        'p' argument speficies which point, i.e., nose, tail, etc. """

        s.pointForces[p].append(f)

    def rotateVectors(s):
        """ Rotate all the vectors to reflect the current orientation.
        Also updates the inertial tensor. """
        s.l = npArray2Vector(s.R*s.left.np_vector()).unit()
        s.r = npArray2Vector(s.R*s.right.np_vector()).unit()
        s.t = npArray2Vector(s.R*s.tail.np_vector()).unit()
        s.n = npArray2Vector(s.R*s.nose.np_vector()).unit()
        s.lift = npArray2Vector(s.R*s.up.np_vector()).unit()
        s.updateI()
        s.resetR()

        
    def liftTest(s, obj):
        return s.lift
        
    def updatePositionsEuler(s):
        """ Updates positions and rotation, using crappy euler integration
        """

        s.updateVelocity()
        s.rotateVectors()

        s.P += s.V.scale(TIMESTEP)
        s.R = s.R + s.RDot*TIMESTEP

