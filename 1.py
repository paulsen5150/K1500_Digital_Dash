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
speed = DigitalGauge(speed_status,'MPH', SPEEDO_XY, font_speedunits, fontObj, SPEED_LABEL_XY)

# Displaying a window of height 
# 500 and width 400
# gauge_window = pygame.display.set_mode((window_width, window_height)) #Moved to constants.py library

# Here we set name or title of our
# pygame window
#pygame.display.set_caption('Chevrolet K1500') #Moved to constants.py library

# Here we load the image we want to 
# use

#Icon = pygame.image.load('gfglogo.png')

# We use set_icon to set new icon
#pygame.display.set_icon(Icon)

#   Creating the list for the indicator gauges
indicator_images = []
resize_scaleXY = (48 , 35) 
for i in range(10):
    image = pygame.image.load(("indicators/ind" + str(i) + ".png")).convert()
    image_small = pygame.transform.scale(image, resize_scaleXY)
    indicator_images.append(image_small)

def draw_indicators():
    '''
    The area where I blit or draw the indicators/idiot lights and turn signals/low fuel etc.
    '''
    
    if illumination_state == True:
        gauge_window.blit(indicator_images[0], (40, indicator_row))
    if foglight_state == True:
        gauge_window.blit(indicator_images[1], (108, indicator_row))
    if defog_state == True:
        gauge_window.blit(indicator_images[2], (176, indicator_row))
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
    if glow_state == True:
        gauge_window.blit(indicator_images[9], (912, indicator_row))

def draw_speedometer_text():
    ''' Speedometer Font Testing '''
    global speed_status
    global font_speedunits
    speedtext = font_speedunits.render(str(speed_status), True, AMBER)#NEON_YELLOW)
    text_rect = speedtext.get_rect()
    text_rect.midright = SPEEDO_XY
    gauge_window.blit(speedtext, text_rect)
    textSufaceObj = fontObj.render('MPH', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (560, 10))

def draw_tach_text():
    ''' Tachometer Font Testing '''
    global tach_status
    global font_tachunits
    tachtext = font_tachunits.render(str(tach_status), True, AMBER)#NEON_YELLOW)
    text_rect = tachtext.get_rect()
    text_rect.midright = RPM_XY
    gauge_window.blit(tachtext, text_rect)
    textSufaceObj = fontObj.render('RPM', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (580, 240))

def draw_fuel_text():
    #global digital_font
    #digital_fuel = fuel_status
    #fuel_text = digital_font.render(str(int(digital_fuel)), True, GREEN) #NEON_GREEN)
    fuel_text = digital_font.render(str(int(fuel_status)), True, GREEN) #NEON_GREEN)
    text_rect = fuel_text.get_rect()
    text_rect.midright = FUEL_XY
    gauge_window.blit(fuel_text, text_rect)
    textSufaceObj = fontObj.render('Fuel Level', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (815, 25))
    #Debuging 
    # print("text_rect", text_rect)
    # print("text_rect.midright", text_rect.midright)
    
    
def draw_coolant_text():
    #global digital_font
    digital_coolant = coolant_status
    coolant_text = digital_font.render(str(int(digital_coolant)), True, GREEN) #NEON_GREEN)
    text_rect = coolant_text.get_rect()
    text_rect.midright = COOLANT_XY
    gauge_window.blit(coolant_text, text_rect)
    textSufaceObj = fontObj.render('Temprature', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (60, 162))
    
def draw_voltage_text():
    #global digital_font
    digital_voltage = voltage_status
    voltage_text = digital_font.render(str(float(digital_voltage)), True, GREEN) #NEON_GREEN)
    text_rect = voltage_text.get_rect()
    text_rect.midright = VOLTAGE_XY
    gauge_window.blit(voltage_text, text_rect)
    textSufaceObj = fontObj.render('Battery', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (835, 162))

def draw_oil_text():
    #global digital_font
    digital_oil = oil_status
    oil_text = digital_font.render(str(int(digital_oil)), True, GREEN) #NEON_GREEN)
    text_rect = oil_text.get_rect()
    text_rect.midright = OIL_XY
    gauge_window.blit(oil_text, text_rect)
    textSufaceObj = fontObj.render('Oil Pressure', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, OILPRESSURE_XY)

def draw_labels():
    # set up Fonts
    # fontObj = pygame.font.Font(None, 32)
    # fontObj2 = pygame.font.Font(None, 50)
    
    # textSufaceObj = fontObj.render('Oil Pressure', True, TEXTCOLOUR, None)
    # gauge_window.blit(textSufaceObj, (60, 25))
    
    # textSufaceObj = fontObj.render('Temprature', True, TEXTCOLOUR, None)
    # gauge_window.blit(textSufaceObj, (60, 162))
 
    # textSufaceObj = fontObj.render('Fuel Level', True, TEXTCOLOUR, None)
    # gauge_window.blit(textSufaceObj, (815, 25))
    
    # textSufaceObj = fontObj.render('Battery', True, TEXTCOLOUR, None)
    # gauge_window.blit(textSufaceObj, (835, 162))
    
    # textSufaceObj = fontObj.render('MPH', True, TEXTCOLOUR, None)
    # gauge_window.blit(textSufaceObj, (560, 10))
    
    # textSufaceObj = fontObj.render('RPM', True, TEXTCOLOUR, None)
    # gauge_window.blit(textSufaceObj, (580, 240))
 
    textSufaceObj = fontObj2.render('%', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (920, 45))
 
    textSufaceObj = fontObj.render('P R N D 3 2 1', True, TEXTCOLOUR, None)
    gauge_window.blit(textSufaceObj, (440, 265))
 
    textSufaceObj = fontObj.render('D', True, TEXTCOLOUR_RED, None)
    gauge_window.blit(textSufaceObj, (506, 265))
 
 
def draw_gauge_panel():
    gauge_window.blit(backGround, (0, 0))
#    rpm.show(gauge_window)
#    coolant.show(gauge_window)
    draw_coolant_text()
#    boost.show(gauge_window)
#    oilpressure.show(gauge_window)
#    egt.show(gauge_window)
#    mileage()
    draw_indicators()
#    draw_clock()
#    draw_mfa()
    draw_fuel_text()
#    draw_speedometer_text()
    draw_tach_text()
    draw_voltage_text()
#    draw_oil_text()
    draw_labels()
    oil.draw()
    speed.draw()


    #   To highlight the fuel reserve indicator (factory is at 7 litres
'''   if fuel_status <= 7:
        gauge_window.blit(fuelresOn, (1795, 616))
    else:
        gauge_window.blit(fuelresOff, (1795, 616))
'''

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
			if event.key == pygame.K_3: defog_state = not defog_state
			if event.key == pygame.K_4: highbeam_state = not highbeam_state
			if event.key == pygame.K_5: leftturn_state = not leftturn_state
			if event.key == pygame.K_6: rightturn_state = not rightturn_state
			if event.key == pygame.K_7: brakewarn_state = not brakewarn_state
			if event.key == pygame.K_8: oillight_state = not oillight_state
			if event.key == pygame.K_9: alt_state = not alt_state
			if event.key == pygame.K_0: glow_state = not glow_state
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
