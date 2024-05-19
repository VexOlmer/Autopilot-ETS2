import cv2
import numpy as np


def angle_rotation_from_map(image_numpy):

    """
    
        Finding the turning angle of a route on the minimap.
        :param image_numpy: Cropped image of the route in numpy array format.
    
    """

    hsv = cv2.cvtColor(image_numpy, cv2.COLOR_RGB2HSV)

    # Defining the red color range in HSV
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])

    # Image mask including only red color
    mask = cv2.inRange(hsv, lower_red, upper_red)

    # Determining the contours of the longest red line
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_line_length = 0
    max_line_angle = 0

    for contour in contours:
        (x, y), (w, h), angle = cv2.minAreaRect(contour)
        if w > max_line_length:
            max_line_length = w
            max_line_angle = angle
    
    cv2.drawContours(image_numpy, contours, -1, (0, 0, 255), 2)
    print("Угол красной линии: ", max_line_angle)
    
    cv2.imshow('Red Line', mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return max_line_angle


image = cv2.imread('example/minimap/minimap_1.png')
angle_rotation_from_map(image)

# cv2.imshow('image', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()