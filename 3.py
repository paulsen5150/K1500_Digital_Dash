#! /usr/bin/python3
# VERSION 0.3 Adding MQTT polling and adding OBD support
# kate: indent-pasted-text false; indent-width 4;
# import pygame module
import pygame
import random
from constants3 import *
from functions3 import *
import paho.mqtt.client as mqttClient
import obd
import time

#backGround = pygame.image.load('Images/splash2.png')
#backGround = pygame.transform.scale(backGround, (window_width, window_height))
# Initializing OBD
#connection = obd.OBD("/dev/pts/1")
connection = obd.Async("/dev/pts/1")

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
coolant = DigitalGauge(coolant_status, 'Temperature', COOLANT_XY, digital_font, fontObj, COOLANT_LABEL_XY)
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

######
#       MQTT Connection Function
######


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker with on_connect")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else: print("Connection failed")


def on_message(client, userdata, message):
     print("made it here wiht on_message")
     #print(message.topic + " on_message " + message.payload.decode())


######
#       ENGINE TOPIC MQTT
######
#def on_message(digi, obj, message):
#def on_message_coolant(digi, obj, message):
def on_message_coolant(message):
	#print(message)
	global coolant_status
	if not message.is_null():
		coolant_status = str(int((message.value.magnitude * 1.8) + 32)) # NEED TO CONVERT TO Fahrenheit °F = (°C × 1.8) + 32
		#coolant.draw(coolant_status)
		#print(coolant_status)

def on_message_speed(message):
	global speed_status
	if not message.is_null():
		speed_status = str(int(message.value.magnitude * .621371)) # IN MPH
    #oil.draw(oil_status)

def on_message_rpm(message):
	global tach_status
	if not message.is_null():
		tach_status = str(int(message.value.magnitude))
    #oil.draw(oil_status)

def on_message_voltage(message):
	global voltage_status
	if not message.is_null():
		voltage_status = str(float(message.value.magnitude))
    #voltage.draw(voltage_status)
	#print(voltage_status)

def on_message_mil(message):
	global mil_state
#	mil_state = message.value.MIL
	#print(mil_state)

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

#   MQTT Variables
# broker_address = "test.mosquitto.org"  # Broker address
# port = 1883  # Broker port
# client = mqttClient.Client()  # create new instance
# #print(client.on_message)
# client.on_connect = on_connect  # attach function to callback
# #client.on_message = on_message  # attach function to callback
# client.connect(broker_address, port=port)  # connect to broker
# client.subscribe("sensor/temperature")
# #client.loop_forever()
# client.loop_start()  # start the loop


	###################
    # OBS Call Backs
	###################
connection.watch(obd.commands.SPEED, callback=on_message_speed)
connection.watch(obd.commands.RPM, callback=on_message_rpm)
connection.watch(obd.commands.COOLANT_TEMP, callback=on_message_coolant)
connection.watch(obd.commands.ELM_VOLTAGE, callback=on_message_voltage)
connection.watch(obd.commands.STATUS, callback=on_message_mil)
connection.start()

# Keep game running till running is true
while running:
    
    #   MQTT Call backs... putting values in from topics
    
	#print(client.on_message)
	## client.message_callback_add('sensor/temperature', on_message_coolant)
	## Above line not need.  Coolant temprature comes from OBD
	#client.message_callback_add('sensor/temperature', on_message_oil)

	#client.message_callback('sensor/Temperature#')
	#client.subscribe("sensor/temperature")
	#client.on_message()
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
					gauge_windoww = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
					#gauge_windoww = pygame.display.set_mode((1920, 720), pygame.FULLSCREEN)
				else:
					gauge_windoww = pygame.display.set_mode((window_width, window_height))
					#gauge_windoww = pygame.display.set_mode((1920, 720))
			if event.key == pygame.K_q:
				running = False
                
#	gauge_window.blit(backGround, (0, 0))

	
	draw_gauge_panel()
	pygame.display.update()
