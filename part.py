# Implements airplane parts - of which there are 5, the nose (N), tail (T),
# left wing (L), right wing (R), and pilot (P) (the pilot is the center of
# the airplane).
#
# Each individual part has location, velocity, acceleration, forces acting
# on it, and mass. It's airplane's job to set the forces acting on each
# part, then the part determines its position in the next timestep.
#
# Also implements the constraint class, a simple object that specifies
# a part to constrain to and a distance.

from geometry import *


class part:

    instances = []

    def __init__(s, pos, vel, mass):
        """ Initialize the part """

        s.pos = pos # the part's location point
        s.vel = vel
        s.mass = mass
        s.acc = vector(0.0, 0.0, 0.0) # the current acceleration
        s.forces = [] # list of forces acting on the part
        # Each force is a FUNCION.
        s.constraints = [] # List of constraint objects. Each constrait
        # is another part and a distance.

        part.instances.append(s)



    @classmethod
    def update(cls):
        """ Update the positions, velocities, etc for each part """
        
        for c in cls.instances:
            c.computeAcc()
            c.updateVelocity()
            c.updatePosition()
    
    def computeAcc(s):
        """ Compute the acceleration of the plane at this timestep
        based on the forces acting on it. Forces are assumed to be
        in lbf. """

        massinverse = 1/s.mass
        fv = vector(0.0, 0.0, 0.0) # Force vector
        
        for f in s.forces:
            fv += f().scale(massinverse)
        for c in s.constraints:
            fv += c.force()

            
        s.acc = fv


    def updateVelocity(s):
        """ Compute the velocity vector of the plane, based
        on acceleration this frame. Uses RK4"""

        k1 = s.acc.scale(1/60)
        yn = s.vel
        
        # Now, update velocity with k1, and recompute acceleration
        s.vel += k1.scale(1/2) # This velocity will be discarded
        s.computeAcc()
        k2 = s.acc.scale(1/60)

        s.vel = yn + k2.scale(1/2)
        s.computeAcc()
        k3 = s.acc.scale(1/60)

        # Finally, get k4:
        s.vel = yn + k3
        s.computeAcc()
        k4 = s.acc.scale(1/60)

        # Compute final acceleration value
        s.vel = yn + k1.scale(1/6) + k2.scale(1/3) \
                + k3.scale(1/3) + k4.scale(1/6)
        

                        

        
        
        

    def updatePosition(s):
        """ Compute the updated position of the plane, based on velocity
        this frame. Uses RK4 """
        
        k1 = s.vel.scale(1/60)
        yn = s.pos

        s.pos += k1.scale(1/2)
        s.updateVelocity()
        k2 = s.vel.scale(1/60)

        s.pos = yn + k2.scale(1/2)
        s.updateVelocity()
        k3 = s.vel.scale(1/60)

        s.pos = yn + k3
        s.updateVelocity()
        k4 = s.vel.scale(1/60)

        s.pos = yn + k1.scale(1/6) + k2.scale(1/3) \
                + k3.scale(1/3) + k4.scale(1/6)
    
    def minus(s, other):
        """ Return the vector result of substracting two part positions. """
        return s.pos.minus(other.pos)


    __sub__ = minus
    

class constraint:
    # Constraints are ridgid connections between two parts, of some length.
    # Constraints are one-directional (i.e. you should have one going
    # in each direction).
    # A constrait is modeled as a very stiff spring between objects.

    def __init__(s, this, other, l):
        """ Create a constrait between part 'this' and another
        part 'other', forcing them to maintaing distance l. """
        s.other = other
        s.this = this
        s.l = l

    def force(s):
        """ Generates the force of this constraint """

        v = s.other.pos - s.this.pos
        lv = v.norm() # actual distance between the objects
        
        diff = lv - s.l
        return v.unit().scale(diff/5) # this is the force to apply
        # to "this". It's actually not very large (because constraints don't
        # take mass into account)
        
     

    