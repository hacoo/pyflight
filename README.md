# pyflight
pyflight

Pyflight is a simple flight simulator, written in Python. Graphics are implemented
with PyOpenGL, and user input / windowing uses Freeglut. 

Pyflight has been tested on Linux Mint Debian 3.11.8. I'm working to test  / make
it compatible with other systems, but for now, Linux is the only supported OS.

To run pyflight:

- clone the repository
- cd pyflight/
- python3.3 pyflight.py
- Use the mouse to control the plane
- For much more detailed game instructions, see Instructions.odp

Pyflight requires Python (tested with version 3.3), numpy, OpenGL, PyOpenGL, and Freeglut.

Python: https://www.python.org/
Numpy: http://www.numpy.org/
OpenGL: https://www.opengl.org/wiki/Getting_Started
PyOpenGL: http://pyopengl.sourceforge.net/
Freeglut: http://freeglut.sourceforge.net/docs/install.php

This is an intimidating list, but hopefully you can easily install these using apt and / or pip. So, 
on Ubuntu/Debian Linux flavors, try:

sudo apt-get install python3.3 python3-pip python3-opengl freeglut3 python3-numpy

If you'd rather use Pip, first install Python 3, pip, and Freeglut, then:

sudo pip3 install numpy
sudo pip3 install pyopengl

On my system (Linux Mint 17.2) all the required packages were easily available through 
standard apt repositories. 

To run Pyflight on Mac OS X, you will need to install Freeglut, which I have not figured out
how to do (since I don't own a Mac). If you get it working on Mac, let me know!

WHAT'S IN THIS REPOSITORY:
16i_stonehenge.raw - the terrain map file. This is from originally from the 1998 video
game, Starsiege:Tribes.
CoLCurve2.jpg - A graph of the Coefficient of Lift curve. .fig files are MATLAB files
Instructions.odp - OpenOffice presentation of game instructions

CODE: 
airplane.py - Handles the forces acting on the airplane (including user controls)
constants.py - Constant definitions
geometry.py - Implements point and vector objects (Written by Jim Fix)
hud.py - Implements the HUD.
landscape.py - Loads the landscape from a file and draws it.
part.py - old mass-spring simulation, not used (rigid body phsics used instead)
pyflight.py - viewer module, responible for actualy OpenGL calls (adapted from code written by Jim Fix)
quat.py - Implements quaternions (Written by Jim Fix)
ridigbody.py - Implements a rigid-body simulation, this computes the actual effect of forces on the airplane.
units.py - Simple unit conversion functions.


THANK YOU TO: 
Jim Fix - http://people.reed.edu/~jimfix/ - Jim Fix taught Computer Graphics class that I wrote this 
program for. He wrote geometry.py and quat.py, and much of the OpenGL viewer code
was adapted from his work.

Jeff Molofee (nehe) - http://nehe.gamedev.net/tutorial/beautiful_landscapes_by_means_of_height_mapping/16006/
Greate tutorial on constructing a 3D landscape from a heightmap.

David Baraff - Physically Based Modeling: Rigid Body Simulation
http://www.pixar.com/companyinfo/research/pbm2001/pdf/notesg.pdf
In-depth explaination of rigid-body simulation

Glenn Fielder - Rotation and Inertial Tensors
http://gafferongames.com/virtual-go/rotation-and-inertia-tensors/
Fantastic article on the pratical implementation of rigid-body physics.

Happy flying!

