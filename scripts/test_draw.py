import cv2 as cv

img = cv.imread(r"D:\Projects\Cursovik\test_images\lane_detection_test.png", cv.IMREAD_COLOR)

def draw_points(img, points, color):
    for (x,y) in points:
        if x < 0 or y < 0:
            continue
        img = cv.circle(img, (int(x), int(y)), 5, color, -1)
    return img

points = [
    [550, 670],
    [517, 581],
    [490, 523],
    [463, 451],
    [435, 400],
    [415, 358],
    [400, 338],
    [475, 485],
    [422, 375],
    [450, 427],
    [534, 637],
    [503, 549],

    [20, 420],
    [53, 409],
    [83, 399],
    [115, 385],
    [149, 372],
    [183, 360],
    [225, 343],

    [20, 590],
    [65, 552],
    [196, 450],
    [119, 514],
    [167, 474],
    [218, 429],
    [257, 393],
    [297, 359],
]

img = draw_points(img, points, (250, 255, 0))

cv.imshow('Lane detection', img)
cv.waitKey(0)
