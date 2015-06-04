

EPSILON = 1.0e-8
AREA_SIZE = 2048 # How long a side of the  area is, in OpenGL "units"
SCALE = 100 # how many openGL units per mile
AREA_MILES = AREA_SIZE/SCALE  # How long a side of the area is, in nautical miles

FRAMES_PER_SECOND = 60 # roughly - it's actual 58.8
MS_PER_FRAME = 17 
DELAY = 0.017 # Number of seconds in between frames
FEET_PER_MILE = 6076
AREA_FEET = AREA_MILES * FEET_PER_MILE
GRAVITY = 32.2 # gravity acceleration value

TIMESTEP = 0.017 # Timestep, used for integration (same as frame delay for now)