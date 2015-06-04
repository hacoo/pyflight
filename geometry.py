#
# geometry.py
#
# Author: Jim Fix
# MATH 385, Reed College, Fall 2015
#
# Version: 01.27.15a
#
# This defines three names: 
#
#    point: a class of locations in 3-space
#    vector: a class of offsets between points within 3-space
#    ORIGIN: a point at the origin 
#
# The two classes/datatypes are designed based on Chapter 3 of
# "Coordinate-Free Geometric Programming" (UW-CSE TR-89-09-16)
# by Tony DeRose.
#

from random import random
from math import sqrt, pi, sin, cos, acos
from constants import EPSILON
from OpenGL.GL import *
from numpy import *



#
# Description of 3-D point objects and their methods.
#
class point:

    def __init__(self,_x,_y,_z):
        """ Construct a new point instance from its coordinates. """
        self.x = _x
        self.y = _y
        self.z = _z

    @classmethod
    def with_components(cls,cs):
        """ Construct a point from a Python list. """ 
        return point(cs[0],cs[1],cs[2])

    def components(self):
        """ Object self as a Python list. """
        return [self.x,self.y,self.z]

    def glVertex3(self):
        """ Issues a glVertex3f call with the coordinates of self. """
        glVertex3f(self[0],self[1],self[2])

    def plus(self,offset):
        """ Computes a point-vector sum, yielding a new point. """
        return point(self.x+offset.dx,self.y+offset.dy,self.z+offset.dz)

    def minus(self,other):
        """ Computes point-point subtraction, yielding a vector. """
        return vector(self.x-other.x,self.y-other.y,self.z-other.z)

    def dist2(self,other):
        """ Computes the squared distance between self and other. """
        return (self-other).norm2()

    def dist(self,other):
        """ Computes the distance between self and other. """
        return (self-other).norm()

    def combo(self,scalar,other):
        """ Computes the affine combination of self with other. """
        return self.plus(other.minus(self).scale(scalar))

    def combos(self,scalars,others):
        """ Computes the affine combination of self with other. """
        P = self
        for i in range(min(len(scalars),len(others))):
            P = P + scalars[i] * (others[i] - self)
        return P

    def max(self,other):
        return point(max(self.x,other.x),max(self.y,other.y),max(self.z,other.z))

    def min(self,other):
        return point(min(self.x,other.x),min(self.y,other.y),min(self.z,other.z))

    def scale(self, scalar):
        """ Scales all coordinates of the point by scalar and returns. Has
        no meaning as a geometric operation! Primarily used for loop subdivision
        """

        return point(scalar*self.x, scalar*self.y, scalar*self.z)

    def np_point(self):
        """ returns this vector as a numpy array """
        return array([self.x, self.y, self.z])

    #
    # Special methods, hooks into Python syntax.
    #

    __add__ = plus  # Defines p + v

    __sub__ = minus # Defines p1 - p2

    def __bool__(self): 
        """ Defines if p: """
        return self.dist(ORIGIN) > EPSILON

    def __str__(self):
        """ Defines str(p), as homogeneous coordinates. """
        return str(self.components()+[1.0])+"^T"

    __repr__ = __str__ # Defines Python's presentation of a point.

    def __getitem__(self,i):
        """ Defines p[i] """
        return (self.components())[i]


#
# Description of 3-D vector objects and their methods.
#
class vector:

    def __init__(self,_dx,_dy,_dz):
        """ Construct a new vector instance. """
        self.dx = _dx
        self.dy = _dy
        self.dz = _dz

    @classmethod
    def with_components(cls,cs):
        """ Construct a vector from a Python list. """
        return vector(cs[0],cs[1],cs[2])

    @classmethod
    def random_unit(cls):
        """ Construct a random unit vector """

        #
        # This method is adapted from 
        #    http://mathworld.wolfram.com/SpherePointPicking.html
        #
        phi = random() * pi * 2.0
        theta = acos(2.0 * random() - 1.0)
        return vector(sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta))

    def components(self):
        """ Object self as a Python list. """
        return [self.dx,self.dy,self.dz]

    def plus(self,other):
        """ Sum of self and other. """
        return vector(self.dx+other.dx,self.dy+other.dy,self.dz+other.dz)

    def minus(self,other):
        """ Vector that results from subtracting other from self. """
        return self.plus(other.neg())

    def scale(self,scalar):
        """ Same vector as self, but scaled by the given value. """
        return vector(scalar*self.dx,scalar*self.dy,scalar*self.dz)

    def neg(self):
        """ Additive inverse of self. """
        return self.scale(-1.0)

    def dot(self,other):
        """ Dot product of self with other. """
        return self.dx*other.dx+self.dy*other.dy+self.dz*other.dz

    def cross(self,other):
        """ Cross product of self with other. """
        return vector(self.dy*other.dz-self.dz*other.dy,
                      self.dz*other.dx-self.dx*other.dz,
                      self.dx*other.dy-self.dy*other.dx)

    def norm2(self):
        """ Length of self, squared. """
        return self.dot(self)

    def norm(self):
        """ Length of self. """
        return sqrt(self.norm2())

    def unit(self):
        """ Unit vector in the same direction as self. """
        n = self.norm()
        if n < EPSILON:
            return vector(1.0,0.0,0.0)
        else:
            return self.scale(1.0/n)

    def projOnto(self, other):
        """ Returns the vector result of projecting this vector onto Other """
        return other.unit().scale(self.dot(other)/(other.norm()))

    def np_vector(self):
        """ Return this vector as a numpy array """
        return array([[self.dx], [self.dy], [self.dz]])

    def star(self):
        """ Generates the "star" operation matrix for this vector. See
        http://www.pixar.com/companyinfo/research/pbm2001/pdf/notesg.pdf
        -- see page G8 for an explaination of this. Basically, this
        matrix is used for getting the cross product of a vector with each
        column of a matrix. """

        return matrix[[0, -self.dz, self.dy],
                      [self.dz, 0 -self.dx],
                      [-self.dy, self.dx, 0]]

    def angleBetween(self, other):
        """ Gets the angle between this vector and another, in radians """
        nself = self.norm()
        nother = other.norm()
        if nself < EPSILON or nother < EPSILON:
            return 0.0 # zero length vector - angle not defined
        return acos((self.dot(other)) / (nself*nother))

        


    #
    # Special methods, hooks into Python syntax.
    #

    __abs__ = norm  # Defines abs(v).

    __add__ = plus  # Defines v1 + v2

    __sub__ = minus # Defines v1 - v2

    __neg__ = neg   # Defines -v

    __mul__ = scale # Defines v * a

    def __truediv__(self,scalar):
        """ Defines v / a """
        return self.scale(1.0/scalar)

    def __rmul__(self,scalar):
        """ Defines a * v """
        return self.scale(scalar)

    def __bool__(self):
        """ Defines if v: """
        return self.norm() > EPSILON

    def __str__(self):
        """ Defines str(v) """
        return str(self.components()+[0.0])+"^T"

    __repr__ = __str__ # Defines the interpreter's presentation.

    def __getitem__(self,i):
        """ Defines v[i] """
        return (self.components())[i]

# 
# The point at the origin.
#
ORIGIN = point(0.0, 0.0, 0.0)

