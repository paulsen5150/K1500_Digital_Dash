#! /usr/bin/python3
# VERSION 0.2 Compacted code using classes
# kate: indent-pasted-text false; indent-width 4;
# import pygame module
import pygame
import random
from constants import *
from functions import *

#backGround = pygame.image.load('Images/splash2.png')
#backGround = pygame.transform.scale(backGround, (window_width, window_height))

# initializing imported module
pygame.init()

# Font Information
odo_font = pygame.font.Font(FONT_PATH, FONT_SMALL)
digital_font = pygame.font.Font(FONT_PATH, FONT_MEDIUM)
font_speedunits = pygame.font.Font(FONT_PATH, FONT_LARGE)
font_tachunits = pygame.font.Font(FONT_PATH, FONT_MEDIUM)
fontObj = pygame.font.Font(None, 32)
fontObj2 = pygame.font.Font(None, 50)

#Object initializing
oil = DigitalGauge(oil_status, 'Oil Pressure', OIL_XY, digital_font, fontObj, OIL_LABEL_XY)
voltage = DigitalGauge(voltage_status, 'Battery', VOLTAGE_XY, digital_font, fontObj, VOLTAGE_LABEL_XY)
coolant = DigitalGauge(coolant_status, 'Temprature', COOLANT_XY, digital_font, fontObj, COOLANT_LABEL_XY)
fuel = DigitalGauge(fuel_status, 'Fuel Level', FUEL_XY, digital_font, fontObj, FUEL_LABEL_XY)
speed = DigitalGauge(speed_status,'MPH', SPEEDO_XY, font_speedunits, fontObj, SPEED_LABEL_XY, AMBER)
tach = DigitalGauge(tach_status,'RPM', RPM_XY, font_tachunits, fontObj, TACH_LABEL_XY, AMBER)

#   Creating the list for the indicator gauges
# indicator_images = []
# resize_scaleXY = (48 , 35) 
# for i in range(10):
#     image = pygame.image.load(("indicators/ind" + str(i) + ".png")).convert()
#     image_small = pygame.transform.scale(image, resize_scaleXY)
#     indicator_images.append(image_small)

#   Creating the list for the indicator gauges
indicator_images = []
resize_scaleXY = (48 , 35) 
for i in range(10):
    image = pygame.image.load(("indicators/ind" + str(i) + ".png")).convert()
    image = pygame.transform.scale(image, resize_scaleXY)
    indicator_images.append(image)

def draw_indicators():
    '''
    The area where I blit or draw the indicators/idiot lights and turn signals/low fuel etc.
    '''
    
    if illumination_state == True:
        gauge_window.blit(indicator_images[0], (40, indicator_row))
    if foglight_state == True:
        gauge_window.blit(indicator_images[1], (108, indicator_row))
    if high4_state == True:
        gauge_window.blit(indicator_images[2], (176, indicator_row))
    # if defog_state == True:
    #     gauge_window.blit(indicator_images[2], (176, indicator_row))
    if highbeam_state == True:
        gauge_window.blit(indicator_images[3], (244, indicator_row))
    if leftturn_state == True:
        #gauge_window.blit(indicator_images[4], (312, indicator_row))
        gauge_window.blit(indicator_images[4], (335, 85))
    if rightturn_state == True:
        #gauge_window.blit(indicator_images[5], (640, indicator_row))
        gauge_window.blit(indicator_images[5], (610, 85))
    if brakewarn_state == True:
        gauge_window.blit(indicator_images[6], (708, indicator_row))
    if oillight_state == True:
        gauge_window.blit(indicator_images[7], (776, indicator_row))
    if alt_state == True:
        gauge_window.blit(indicator_images[8], (844, indicator_row))
    if mil_state == True:
        gauge_window.blit(indicator_images[9], (912, indicator_row))# if glow_state == True:
    #     gauge_window.blit(indicator_images[9], (912, indicator_row))

def draw_labels():
    textSufaceObj = fontObj2.render('%', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (920, 45))
 
    textSufaceObj = fontObj.render('P R N D 3 2 1', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (440, 265))
 
    textSufaceObj = fontObj.render('D', True, TEXTCOLOUR_RED, None)
    gauge_window.blit(textSufaceObj, (506, 265))
 
 
def draw_gauge_panel():
    gauge_window.blit(backGround, (0, 0))
#    mileage()
#    draw_clock()
    draw_indicators()
#    draw_speedometer_text()
#    draw_tach_text()
    draw_labels()
    oil.draw(oil_status)
    voltage.draw(voltage_status)
    coolant.draw(coolant_status)
    fuel.draw(fuel_status)
    tach.draw(tach_status)
    speed.draw(speed_status)

# Creating a bool value which checks if 
# game is running
running = True
fullscreen = False

# Keep game running till running is true
while running:
	
	# Check for event if user has pushed 
	# any event in queue
	for event in pygame.event.get():
		# If event is of type quit then set 
		# running bool to false
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_1: illumination_state = not illumination_state
			if event.key == pygame.K_2: foglight_state = not foglight_state
			# if event.key == pygame.K_3: defog_state = not defog_state
			if event.key == pygame.K_3: high4_state = not high4_state
			if event.key == pygame.K_4: highbeam_state = not highbeam_state
			if event.key == pygame.K_5: leftturn_state = not leftturn_state
			if event.key == pygame.K_6: rightturn_state = not rightturn_state
			if event.key == pygame.K_7: brakewarn_state = not brakewarn_state
			if event.key == pygame.K_8: oillight_state = not oillight_state
			if event.key == pygame.K_9: alt_state = not alt_state
			# if event.key == pygame.K_0: glow_state = not glow_state
			if event.key == pygame.K_0: mil_state = not mil_state
			if event.key == pygame.K_F11:
				fullscreen = not fullscreen
				if fullscreen:
					gauge_windoww = pygame.display.set_mode((1000, 300), pygame.FULLSCREEN)
					#gauge_windoww = pygame.display.set_mode((1920, 720), pygame.FULLSCREEN)
				else:
					gauge_windoww = pygame.display.set_mode((1000, 300))
					#gauge_windoww = pygame.display.set_mode((1920, 720))
			if event.key == pygame.K_q:
				running = False
                
#	gauge_window.blit(backGround, (0, 0))
	draw_gauge_panel()
	pygame.display.update()
