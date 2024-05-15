"""



"""


import os
import sys
from PIL import Image
from cv2 import cv

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.screen import ScreenUtils, LocalScreenGrab

# Select game screen
box = ScreenUtils.select_screen_area()

# Grab selected area
local_grab = LocalScreenGrab(box)
arr = local_grab.grab()
arr = arr.reshape(box.numpy_shape)

# Show image
image = Image.fromarray(arr, 'RGB')
image.show()