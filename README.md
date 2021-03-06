# pyflight
pyflight

Pyflight is a simple physics-based flight simulator, written in Python. Graphics are implemented
with PyOpenGL, and user input / windowing uses Freeglut. 

Pyflight has been tested on Linux Mint Debian 3.11.8. I'm working to test  / make
it compatible with other systems, but for now, Linux is the only supported OS.

![alt tag](https://raw.githubusercontent.com/hacoo/pyflight/master/screenshots/pyflight.png)

To run pyflight:

> git clone https://github.com/hacoo/pyflight.git
> cd pyflight/
> python3.3 pyflight.py
- Use the mouse to control the plane
- For much more detailed game instructions, see Instructions.odp

Pyflight requires Python (tested with version 3.3), numpy, OpenGL, PyOpenGL, and Freeglut.

Python: https://www.python.org/
Numpy: http://www.numpy.org/
OpenGL: https://www.opengl.org/wiki/Getting_Started
PyOpenGL: http://pyopengl.sourceforge.net/
Freeglut: http://freeglut.sourceforge.net/docs/install.php

To install on Ubuntu Linux:
> sudo apt-get install freeglut3-dev
> pip3 install numpy pyopengl
 
This *SHOULD* get everything, but I haven't tested it yet on a clean stock system 
(so it might miss something).
 
To run Pyflight on Mac OS X, you will need to install Freeglut, which I have not figured out
how to do (since I don't own a Mac). If you get it working on Mac, let me know!

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

