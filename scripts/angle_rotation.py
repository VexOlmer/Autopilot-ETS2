import cv2
import numpy as np

# Загрузка изображения
img = cv2.imread('C:\Projects\Cursovik\example\minimap\minimap_6.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Определение диапазона красного цвета в HSV
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# Создание маски изображения только для красного цвета
mask = cv2.inRange(hsv, lower_red, upper_red)

# Нахождение контуров
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Нахождение самой длинной красной линии
max_line_length = 0
max_line_angle = 0

for contour in contours:
    (x, y), (w, h), angle = cv2.minAreaRect(contour)
    if w > max_line_length:
        max_line_length = w
        max_line_angle = angle

# Отображение найденной красной линии
cv2.drawContours(img, contours, -1, (0, 0, 255), 2)

# Вывод угла поворота найденной красной линии
print("Угол красной линии: ", max_line_angle)

# Отображение изображения с красной линией
cv2.imshow('Red Line', img)
cv2.waitKey(0)
cv2.destroyAllWindows()