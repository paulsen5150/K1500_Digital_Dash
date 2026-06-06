import time
import json

import board
import busio
import adafruit_pcf8574
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# ---------- Hardware configuration ----------

# CircuitPython busio.I2C argument order is SCL, SDA.
I2C_SCL = board.IO9
I2C_SDA = board.IO8

PCF1_ADDRESS = 0x20
PCF2_ADDRESS = 0x21
ADS_ADDRESS = 0x48

ADS_ECT_CHANNEL = 0
ADS_OIL_PRESSURE_CHANNEL = 1
ADS_FUEL_LEVEL_CHANNEL = 2

# Update intervals in seconds.
ONE_HZ_INTERVAL = 1.0
TEN_HZ_INTERVAL = 0.1
TWENTY_HZ_INTERVAL = 0.05


# ---------- Sender calibration ----------

SUPPLY_VOLTAGE = 3.3
PULLUP_RESISTOR = 250.0

MAX_SENDER_RESISTANCE = 90.0
MAX_PSI = 80.0

# Replace this with a real ECT sender calibration table or curve.
DEFAULT_ECT_F = 180.0


# ---------- I2C devices ----------

i2c = busio.I2C(I2C_SCL, I2C_SDA)

pcf1 = adafruit_pcf8574.PCF8574(i2c, address=PCF1_ADDRESS)
pcf2 = adafruit_pcf8574.PCF8574(i2c, address=PCF2_ADDRESS)

ads = ADS.ADS1115(i2c, address=ADS_ADDRESS)
ect_raw_v = AnalogIn(ads, ADS_ECT_CHANNEL)
oil_pressure_raw_v = AnalogIn(ads, ADS_OIL_PRESSURE_CHANNEL)
fuel_level_raw_v = AnalogIn(ads, ADS_FUEL_LEVEL_CHANNEL)


# ---------- Digital input map ----------

warning_light_inputs = {
    # Update these names/pins to match the real harness.
    "left_signal": pcf1.get_pin(0),
    "brakewarn": pcf2.get_pin(7),
}

for input_pin in warning_light_inputs.values():
    input_pin.switch_to_input()


dash_state = {
    "fuel_percent": 0,
    "oil_psi": 0,
    "ECT": 0,
    "speed": 0.0,
    "tach": 0,
    "odometer": 153000,
    "left_signal": False,
    "right_signal": False,
    "milwarn": False,
    "illumination": False,
    "foglight": False,
    "high4": False,
    "brakewarn": False,
    "oilwarn": False,
    "altwarn": False,
    "highbeam": False,
}


def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value


def voltage_to_resistance(vout):
    if vout <= 0:
        return 0.0

    if vout >= SUPPLY_VOLTAGE:
        return MAX_SENDER_RESISTANCE

    return (vout * PULLUP_RESISTOR) / (SUPPLY_VOLTAGE - vout)


def resistance_to_percent(rsensor):
    percent = 100.0 * (1.0 - (rsensor / MAX_SENDER_RESISTANCE))
    return clamp(percent, 0.0, 100.0)


def resistance_to_psi(rsensor):
    psi = MAX_PSI * (1.0 - (rsensor / MAX_SENDER_RESISTANCE))
    return clamp(psi, 0.0, MAX_PSI)


def resistance_to_ect_f(rsensor):
    # Placeholder until the ECT sender resistance/temp curve is known.
    return DEFAULT_ECT_F


def read_speed():
    # Later this would be captured by the ESP32.
    return 70.6


def read_rpm():
    # Later this would be captured by the ESP32.
    return 2800


def read_ect():
    resistance = voltage_to_resistance(ect_raw_v.voltage)
    return resistance_to_ect_f(resistance)


def read_fuel():
    resistance = voltage_to_resistance(fuel_level_raw_v.voltage)
    return resistance_to_percent(resistance)


def read_oil_pressure():
    resistance = voltage_to_resistance(oil_pressure_raw_v.voltage)
    return resistance_to_psi(resistance)


def read_warning_lights():
    lights = {}

    for name, input_pin in warning_light_inputs.items():
        lights[name] = bool(input_pin.value)

    return lights


def update_warning_lights():
    lights = read_warning_lights()

    for name, value in lights.items():
        dash_state[name] = value


def send_dash_state():
    print(json.dumps(dash_state))


last_fuel_time = 0
last_oil_time = 0
last_light_time = 0
last_send_time = 0
last_ect_time = 0
last_mph_time = 0
last_tach_time = 0


while True:
    now = time.monotonic()

    if now - last_fuel_time >= ONE_HZ_INTERVAL:
        last_fuel_time = now
        dash_state["fuel_percent"] = read_fuel()

    if now - last_oil_time >= TEN_HZ_INTERVAL:
        last_oil_time = now
        dash_state["oil_psi"] = read_oil_pressure()

    if now - last_mph_time >= TEN_HZ_INTERVAL:
        last_mph_time = now
        dash_state["speed"] = read_speed()

    if now - last_tach_time >= TEN_HZ_INTERVAL:
        last_tach_time = now
        dash_state["tach"] = read_rpm()

    if now - last_ect_time >= TEN_HZ_INTERVAL:
        last_ect_time = now
        dash_state["ECT"] = read_ect()

    if now - last_light_time >= TWENTY_HZ_INTERVAL:
        last_light_time = now
        update_warning_lights()

    if now - last_send_time >= TEN_HZ_INTERVAL:
        last_send_time = now
        send_dash_state()

    time.sleep(0.001)
