#constants.py

import pygame

#   Screen Size
window_width, window_height = 1000, 300
#window_width, window_height = 1920, 720
#gauge_window = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
gauge_window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption('Chevrolet K1500')

backGround_image = 'Images/splash2.png'
Icon_image = 'Images/speedometer.png'
Icon = pygame.image.load(Icon_image).convert()
pygame.display.set_icon(Icon)
backGround = pygame.image.load(backGround_image).convert()
backGround = pygame.transform.scale(backGround, (window_width, window_height))

#Temporary to cause indicators to display
indicator_row = 250
illumination_state = False
foglight_state = False
defog_state = False
highbeam_state = False
leftturn_state = False
rightturn_state = False
brakewarn_state = False
oillight_state = False
high4_state = False
mil_state = False
alt_state = False
glow_state = False
speed_status = 55
tach_status = 1700
fuel_status = 73
coolant_status = 198
voltage_status = 14.2
oil_status = 54


#   Colours
NEON_YELLOW = (236, 253, 147)   #   Speedo Colour
NEON_GREEN = (145, 213, 89)     #   Lower gauge colours, clock, odo etc
DARK_GREY = (9, 52, 50)         #   background of the digits (for the 7segment appearance)
GREEN = (0, 255, 0)
BLUE = (0, 175, 255)
AMBER = (255, 191, 0)
TEXTCOLOUR = (255, 255, 255)
TEXTCOLOUR_RED = (255, 0, 0)

#   Font Details
FONT_PATH = "fonts/DSEG7Classic-Bold.ttf"
FONT_LARGE = 90    #   Speedo size
FONT_MEDIUM = 55    #   Clock, MFA, Fuel size
FONT_SMALL = 25     #   Odo Size


#   Locations for gauge graphics, each has the same start XY but builds upon it, check images folder
RPM_XY = (585, 230)
#COOLANT_XY = (1481, 105)
#EGT_XY = (1599, 105)
OILPRESSURE_XY = (60, 25)
#BOOST_XY = (1822, 105)
#CLOCK_XY = (555, 620)
FUEL_XY = (925, 75)
#ODO_XY = (60, 644)
#ODO_L_XY = (395, 678)
#MFA_XY = (1435, 668)
#MFABG_XY = (1021, 563)
SPEEDO_XY = (570 , 55)
COOLANT_XY =(170, 215)
VOLTAGE_XY = (925, 215)
OIL_XY = (170, 75)
OIL_LABEL_XY = (60, 25)
COOLANT_LABEL_XY = (60, 162)
VOLTAGE_LABEL_XY = (835, 162)
FUEL_LABEL_XY = (815, 25)
SPEED_LABEL_XY = (560, 10)
TACH_LABEL_XY = (580, 240)





