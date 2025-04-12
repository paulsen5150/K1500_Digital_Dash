#test.py
from functions import *
import pygame
from constants import *

pygame.init()

digital_font = pygame.font.Font(FONT_PATH, FONT_MEDIUM)
fontObj = pygame.font.Font(None, 32)
oil = DigitalGauge(44, 'Oil Pressure', OIL_XY, digital_font, fontObj)

# print (oil.status)
# print (oil.textColor)
# print (oil.label)
# print (oil.labelTextcolor)
# print(oil.position)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    oil.draw()
    pygame.display.update()

