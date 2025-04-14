#!/usr/bin/python3
import paho.mqtt.client as mqtt

broker_url = "test.mosquitto.org"
broker_port = 1883

def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code Nu", rc)

def on_message(client, userdata, message):
   print("Message Recieved: is"+message.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_url, broker_port)
client.subscribe("sensor/temperature", qos=1)

#client.publish(topic="TestingTopic", payload="TestingPayload", qos=1, retain=False)

client.loop_forever()
