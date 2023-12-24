#Importing Libraries
import cv2
import matplotlib.pyplot as plt
import numpy as np

class LaneLines():
    
    lane_image = None
    
    def __init__(self, image):
        self.lane_image = np.copy(image)
    
    def canny(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        canny = cv2.Canny(blur, 50, 150)
        
        return canny

    def region_of_interest(self, image):
        height = image.shape[0]
        width = image.shape[1]
        mask = np.zeros_like(image)
        triangle = np.array([[(290, height), (570,270), (1000,height)]], np.int32)
        cv2.fillPoly(mask, triangle, 255)
        masked_image = cv2.bitwise_and(image, mask)
        
        return masked_image
    
    # Find Coordinates of the Lines
    def make_points(self, image, line):
        slope, intercept = line
        y1 = int(image.shape[0])
        y2 = int(y1*3/5)
        x1 = int((y1-intercept)/slope)
        x2 = int((y2-intercept)/slope)
        return [[x1, y1, x2, y2]]
    
    # Obtain Single Lines for Both Left and Right
    def average_slope_intercept(self, image, lines):
        left_fit = []
        right_fit = []
        if lines is None:
            return None
        for line in lines:
            for x1, y1, x2, y2 in line:
                fit = np.polyfit((x1,x2), (y1,y2), 1)
                slope = fit[0]
                intercept = fit[1]
                if slope < 0:
                    left_fit.append((slope,intercept))
                else:
                    right_fit.append((slope,intercept))
        left_fit_average = np.average(left_fit, axis = 0)
        right_fit_average = np.average(right_fit, axis = 0)
        left_line = self.make_points(image, left_fit_average)
        right_line = self.make_points(image, right_fit_average)
        averaged_lines = [left_line, right_line]
        
        return averaged_lines
    
    def display_lines(self, image,lines):
        line_image = np.zeros_like(image)
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),10)
                    
        return line_image
    
    def find_lane_lines(self):
        canny_image = self.canny(self.lane_image)
        
        cropped_canny = self.region_of_interest(canny_image)
        lines = cv2.HoughLinesP(cropped_canny, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=5)
        
        averaged_lines = self.average_slope_intercept(self.lane_image, lines)
        line_image = self.display_lines(self.lane_image, averaged_lines)
        final_image = cv2.addWeighted(self.lane_image, 0.8, line_image, 1, 0)
        
        return final_image


# image = cv2.imread('./test_images/1.png')
# lane_image = np.copy(image)

# lane_lines = LaneLines(lane_image)
# final_image = lane_lines.find_lane_lines()

# cv2.imshow("Result", final_image)
# cv2.waitKey(0)

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    #channel_count = img.shape[2]
    match_mask_color = 255
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_the_lines(img, lines):
    img = np.copy(img)
    blank_image = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(blank_image, (x1,y1), (x2,y2), (0, 255, 0), thickness=10)

    img = cv2.addWeighted(img, 0.8, blank_image, 1, 0.0)
    return img


def process(image):
    height = image.shape[0]
    width = image.shape[1]
    region_of_interest_vertices = [
        (0, height),
        (width/2, height/2),
        (width, height)
    ]
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    canny_image = cv2.Canny(gray_image, 100, 120)
    cropped_image = region_of_interest(canny_image,
                    np.array([region_of_interest_vertices], np.int32))
    lines = cv2.HoughLinesP(cropped_image,
                            rho=2,
                            theta=np.pi/180,
                            threshold=200,
                            lines=np.array([]),
                            minLineLength=40,
                            maxLineGap=100)
    if type(lines) != type(None):
        image_with_lines = draw_the_lines(image, lines)
        return image_with_lines
    else:
        return image
  
# image = cv2.imread('./test_images/2.jpg')

# image = process(image)
# cv2.imshow('result', image)
# cv2.waitKey(0)