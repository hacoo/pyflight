#
# quat.py
#
# Author: Jim Fix
# MATH 385, Reed College, Fall 2015
#
# Version: 01.27.15a
#
# This defines the class of quaternion objects, class quat.
#

from constants import EPSILON
from geometry import vector
from math import sin, cos, sqrt, acos, pi
from OpenGL.GL import *

#
# Description of quaternion objects and their methods.
#
class quat:

    def __init__(self,real,imagv):
        """ Constructs a new quat instance from the following:
              re: the scalar value of the quaternion
              iv: the i,j,k components of the quaternion, as a vector.
        """
        self.re = real
        self.iv = imagv

    @classmethod
    def with_components(cls,qs):
        """ Constructs a new quat instance from [q0,q1,q2,q3]. """
        return quat(qs[0],vector.with_components(qs[1:]))

    @classmethod
    def of_vector(cls,v):
        """ Constructs a new quat instance from [q0,q1,q2,q3]. """
        return quat(0.0,v)

    @classmethod
    def for_rotation(cls,angle,around):
        """ Constructs a new quat instance corresponding to a rotation of
            3-space by an amount in radians given by angle.  The axis
            of rotation is given by the vector given by around.  
        """
        half_angle = angle / 2.0 
        axis = around.unit() 
        return quat(cos(half_angle),axis*sin(half_angle))

    def components(self):
        """ Object self as a Python list. """
        return [self.re] + self.iv.components()

    def as_rotation(self):
        """ The rotation represented by self, given as an angle around
            an vector serving as the Euler axis of rotation. 
        """
        qs = self.unit().components()
        half_theta = acos(qs[0])
        if half_theta < EPSILON:
            return (0.0,vector(1.0,0.0,0.0))
        else:
            return (2.0*half_theta,
                    vector.with_components(qs[1:])/sin(half_theta))

    def glRotate(self):
        """ Issues a glRotatef using the rotation of self. """
        theta,axis = self.as_rotation()
        glRotatef(theta*180.0/pi,axis[0],axis[1],axis[2])

    def as_matrix(self):
        """ Returns a column major 3x3 rotation matrix for self. """
        u = self*quat(0.0,vector(1.0,0.0,0.0))/self
        v = self*quat(0.0,vector(0.0,1.0,0.0))/self
        w = self*quat(0.0,vector(0.0,0.0,1.0))/self
        return [u.vector(),v.vector(),w.vector()]

    def rotate(self,v):
        """ Returns v rotated according to the rotation for self. """
        return (self*quat(0.0,v)/self).vector()

    def plus(self,other):
        """ Computes the sum of two quat objects, self and other. """
        return quat(self.re+other.re, self.iv+other.iv)

    def minus(self,other):
        """ Computes the difference of two quat objects, self and other. """
        return self.plus(other.neg())

    def times(self,other):
        """ Computes the product of two quat objects, self and other. """
        return quat(self.re*other.re-self.iv.dot(other.iv),
                    other.iv*self.re+self.iv*other.re+self.iv.cross(other.iv))

    def div(self,other):
        """ Computes the qivision of self by other. """
        return self.times(other.recip())

    def scale(self,amount):
        """ Returns a quat, same as self but scaled by the given amount. """
        return quat(self.re*amount, self.iv*amount)

    def neg(self,amount):
        """ Returns the additive inverse of self. """
        return quat(-self.re, self.iv.negate())

    def recip(self):
        """ Returns the multiplicative inverse of self. """
        return self.conj().scale(1.0/self.norm2())

    def scalar(self):
        """ Returns the scalar part of self. """
        return self.re

    def vector(self):
        """ Returns the i,j,k part of self. """
        return self.iv

    def conj(self):
        """ Returns the conjugate of self. """
        return quat(self.re,self.iv.neg())

    def norm2(self):
        """ Returns the squared norm of self. """
        return self.re*self.re + self.iv.dot(self.iv)

    def norm(self):
        """ Returns the norm of self. """
        return sqrt(self.norm2())

    def unit(self):
        """ Returns the versor of self. """
        return self.scale(1.0/self.norm())

    #
    # Special methods, hooks into Python syntax.
    #

    __add__ = plus    # Defines q1 + q2

    __sub__ = minus   # Defines q1 - q2

    __mul__ = times   # Defines q1 * q2

    __truediv__ = div # Defines q1 / q2

    __abs__ = norm    # Defines abs(q)

    __neg__ = neg     # Defines -q

    def __rmul__(self,scalar):
        """ Defines a * q """
        return self.scale(scalar)

    def __bool__(self):
        """ Defines if q: """
        return self.norm() > EPSILON

    def __str__(self):
        """ Defines str(p), as a+bi+cj+dk """ 

        def pm(value):
            if value < 0.0:
                return ""
            else:
                return "+"

        cs = self.components()
        s = ""
        s += str(cs[0])
        s += pm(cs[1])
        s += str(cs[1])
        s += "i"
        s += pm(cs[2])
        s += str(cs[2])
        s += "j"
        s += pm(cs[3])
        s += str(cs[3])
        s += "k"
        return s

    __repr__ = __str__ # Defines Python's presentation of a quat.

    def __getitem__(self,i):
        """ Defines q[i] """
        return self.components()[i]
