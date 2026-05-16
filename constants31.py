#constants31.py
#Version 3.1 May 2026

import pygame

#   Screen Size
window_width, window_height = 1000, 300
#window_width, window_height = 1920, 720
#gauge_window = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
gauge_window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
#test_window = pygame.display.set_mode((400, 400)) #TEMPORARY TRYOUT
#pygame.display.set_caption('Chevrolet K1500')
pygame.display.set_caption('K.I.T.T.')

backGround_image = 'Images/splash2.png'
Icon_image = 'Images/speedometer.png'
Icon = pygame.image.load(Icon_image).convert()
pygame.display.set_icon(Icon)
backGround = pygame.image.load(backGround_image).convert()
backGround = pygame.transform.scale(backGround, (window_width, window_height))

#Temporary to cause indicators to display

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
speed_status = 0
tach_status = 0
fuel_status = 0
coolant_status = 0
voltage_status = 0
oil_status = 0


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
#RPM_XY = (585, 230)
RPM_XY = (window_width / 2, window_height * .77)
#COOLANT_XY = (1481, 105)
#EGT_XY = (1599, 105)
#OILPRESSURE_XY = (60, 25)
#OILPRESSURE_XY = (0, 25)
#BOOST_XY = (1822, 105)
#CLOCK_XY = (555, 620)
#FUEL_XY = (925, 75)
FUEL_XY = (window_width*.925, window_height * .25)
#ODO_XY = (60, 644)
#ODO_L_XY = (395, 678)
#MFA_XY = (1435, 668)
#MFABG_XY = (1021, 563)
#SPEEDO_XY = (570 , 55)
SPEEDO_XY = (window_width*.5 , window_height * .18) 
COOLANT_XY =(105, 215)
#COOLANT_XY =(window_width*.17, window_height * .72)
#VOLTAGE_XY = (925, 215)
VOLTAGE_XY = (window_width*.925, window_height * .72)
#OIL_XY = (125, 75)
OIL_XY = (window_width*.105, window_height * .25)
OIL_LABEL_XY = (40, 25)
#COOLANT_LABEL_XY = (40, 162)
COOLANT_LABEL_XY = (window_width * .04, window_height * .54)
#VOLTAGE_LABEL_XY = (835, 162)
VOLTAGE_LABEL_XY = (window_width * .834, window_height * .54)
#FUEL_LABEL_XY = (815, 25)
FUEL_LABEL_XY = (815, 25)
#SPEED_LABEL_XY = (560, 10)
SPEED_LABEL_XY = (560, 10)
#TACH_LABEL_XY = (580, 240)
TACH_LABEL_XY = (window_width * .57, window_height * .8)
#indicator_row = 250
indicator_row = window_height * .83




