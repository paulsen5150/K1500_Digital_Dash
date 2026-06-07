"""
Reads the interface board and display a graphical output on 2inch lcd

ESP32-S3 CircuitPython instrument cluster for the K1500/KITT interface.

This version keeps the hardware setup from ESP32_KITT_Display/code.py, but the
default page is a landscape digital instrument cluster with speed, RPM, analog
gauges, warning lamps, PRNDL, and an integer-backed odometer.

This WiFi version also starts an ESP32 access point and HTTP server so a laptop
can connect directly and read the live dash state.
"""
import gc
import json
import os
import time

import board
import busio
import digitalio
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_st7789
import fourwire

try:
    import socketpool
    import wifi
    from adafruit_httpserver import JSONResponse, Request, Response, Server
    WIFI_IMPORT_ERROR = None
except Exception as exc:
    socketpool = None
    wifi = None
    JSONResponse = None
    Request = None
    Response = None
    Server = None
    WIFI_IMPORT_ERROR = str(exc)


# Hardware configuration
I2C_SCL = board.IO9
I2C_SDA = board.IO8

PCF_INDICATOR_ADDRESS = 0x20
PCF_WARNING_ADDRESS = 0x21
ADS_ADDRESS = 0x48

TFT_SCK = board.IO12
TFT_MOSI = board.IO11
TFT_CS = board.IO10
TFT_DC = board.IO13
TFT_RST = board.IO14
TFT_BL = board.IO21
TFT_WIDTH = 320
TFT_HEIGHT = 240
TFT_ROTATION = 90

PAGE_BUTTON_PIN = board.IO17
VSS_PIN = board.IO15
TACH_PIN = board.IO16

#COMMENTED OUT FOR DEBUGGING 06/06/2026
#REVERTED TO ORIGINAL 06/07/2026
PCF_POLL_INTERVAL = 0.05
ADS_POLL_INTERVAL = 0.2
PULSE_POLL_INTERVAL = 0.001
DISPLAY_INTERVAL = 0.1
TEXT_DISPLAY_INTERVAL = 0.5
SERIAL_INTERVAL = 1.0

BUTTON_DEBOUNCE = 0.05
FREQUENCY_WINDOW = 1.0
STALE_PULSE_SECONDS = 2.0
ENGINE_OFF_TACH_STALE_SECONDS = 5.0

#TIMING CHANGED FOR DEBUGGING 06/06/2026
#REVERTED TO ORIGINAL 06/07/2026
# SERIAL_INTERVAL = 10.0
# DISPLAY_INTERVAL = 0.5
# TEXT_DISPLAY_INTERVAL = 1.0
# PCF_POLL_INTERVAL = 0.2
# ADS_POLL_INTERVAL = 0.5
# PULSE_POLL_INTERVAL = 0.01

DASH_AP_SSID = os.getenv("DASH_AP_SSID") or "K1500_Dash"
DASH_AP_PASSWORD = os.getenv("DASH_AP_PASSWORD") or "k1500dash"
DASH_AP_CHANNEL = int(os.getenv("DASH_AP_CHANNEL") or 6)
DASH_HTTP_PORT = int(os.getenv("DASH_HTTP_PORT") or 5000)


# Calibration placeholders. Adjust these after road/bench testing.
VSS_PULSES_PER_MILE = 4000
VSS_PULSES_PER_TENTH_MILE = 400
TACH_PULSES_PER_REV = 2.0

ODOMETER_FILE = "/odometer.json"
ODOMETER_START_TENTHS = 2530000
ODOMETER_START_REMAINDER_PULSES = 0
ODOMETER_SAVE_INTERVAL_SECONDS = 60.0

SUPPLY_VOLTAGE = 3.3
SENDER_PULLUP_OHMS = 250.0
MAX_SENDER_OHMS = 90.0
MAX_OIL_PSI = 80.0
MAX_COOLANT_F = 260.0

GM_ECT_TABLE = (
    (-40.0, 100700.0),
    (-22.0, 52700.0),
    (-4.0, 28680.0),
    (14.0, 16180.0),
    (32.0, 9420.0),
    (50.0, 5670.0),
    (68.0, 3520.0),
    (86.0, 2238.0),
    (104.0, 1459.0),
    (122.0, 973.0),
    (140.0, 667.0),
    (158.0, 467.0),
    (176.0, 332.0),
    (194.0, 241.0),
    (212.0, 177.0),
)

LOW_FUEL_PERCENT = 12.5
LOW_OIL_PSI = 5.0
HIGH_COOLANT_F = 230.0


COLOR_BG = 0x000000
COLOR_DIM = 0x303030
COLOR_TEXT = 0xE8E8E8
COLOR_MUTED = 0x808080
COLOR_GREEN = 0x00FF66
COLOR_AMBER = 0xFFAA00
COLOR_RED = 0xFF2020
COLOR_BLUE = 0x2080FF


INDICATOR_SIGNALS = (
    {"name": "HiBeam", "bit": 0, "active_high": False},
    {"name": "L Turn", "bit": 1, "active_high": False},
    {"name": "R Turn", "bit": 2, "active_high": False},
    {"name": "SeatBelts", "bit": 3, "active_high": False},
    {"name": "PRNDL P", "bit": 4, "active_high": True},
    {"name": "PRNDL C", "bit": 5, "active_high": True},
    {"name": "PRNDL B", "bit": 6, "active_high": True},
    {"name": "PRNDL A", "bit": 7, "active_high": True},
)

WARNING_SIGNALS = (
    {"name": "ABS", "bit": 0, "active_high": False},
    {"name": "ALT", "bit": 1, "active_high": False},
    {"name": "AirBag", "bit": 2, "active_high": False},
    {"name": "DRL", "bit": 3, "active_high": False},
    {"name": "MIL", "bit": 4, "active_high": False},
    {"name": "ParkBrake", "bit": 5, "active_high": False},
    {"name": "Spare1", "bit": 6, "active_high": False},
    {"name": "Spare2", "bit": 7, "active_high": False},
)

ADS_CHANNELS = (
    {"name": "ECT", "channel": 0},
    {"name": "OilPres", "channel": 1},
    {"name": "Fuel", "channel": 2},
    {"name": "ADS3", "channel": 3},
)

PRNDL_TABLE = {
    (False, True, True, False): "P",
    (False, False, True, True): "R",
    (True, False, True, False): "N",
    (True, False, False, True): "OD",
    (False, False, False, False): "3",
    (False, True, False, True): "2",
    (True, True, False, False): "1",
}


class NullDisplay:
    def show(self, group):
        pass

    @property
    def root_group(self):
        return None

    @root_group.setter
    def root_group(self, group):
        pass


def pin_name(pin):
    return str(pin).split(".")[-1]


def init_i2c():
    i2c_bus = busio.I2C(I2C_SCL, I2C_SDA)
    while not i2c_bus.try_lock():
        time.sleep(0.01)
    try:
        found = tuple(i2c_bus.scan())
    finally:
        i2c_bus.unlock()
    return i2c_bus, found


class DirectPCF8574:
    def __init__(self, i2c_bus, address):
        self.i2c_bus = i2c_bus
        self.address = address
        self._buffer = bytearray(1)
        self._last_value = 0xFF
        self.write_byte(0xFF)

    def _lock(self):
        start = time.monotonic()
        while not self.i2c_bus.try_lock():
            if time.monotonic() - start > 0.25:
                raise RuntimeError("I2C lock timeout")
            time.sleep(0.001)

    def write_byte(self, value):
        self._lock()
        try:
            self.i2c_bus.writeto(self.address, bytes((value & 0xFF,)))
        finally:
            self.i2c_bus.unlock()

    def read_byte(self):
        self._lock()
        try:
            self.i2c_bus.readfrom_into(self.address, self._buffer)
        finally:
            self.i2c_bus.unlock()
        self._last_value = self._buffer[0]
        return self._last_value


def init_pcf(i2c_bus, address):
    try:
        return DirectPCF8574(i2c_bus, address), None
    except Exception as exc:
        return None, str(exc)


def init_ads(i2c_bus):
    try:
        ads = ADS.ADS1115(i2c_bus, address=ADS_ADDRESS)
        inputs = {}
        for channel in ADS_CHANNELS:
            inputs[channel["name"]] = AnalogIn(ads, channel["channel"])
        return ads, inputs, None
    except Exception as exc:
        return None, {}, str(exc)


def init_display():
    try:
        displayio.release_displays()
        spi = busio.SPI(TFT_SCK, MOSI=TFT_MOSI)
        display_bus = fourwire.FourWire(
#        display_bus = displayio.FourWire(
            spi,
            command=TFT_DC,
            chip_select=TFT_CS,
            reset=TFT_RST,
        )
        display = adafruit_st7789.ST7789(
            display_bus,
            width=TFT_WIDTH,
            height=TFT_HEIGHT,
            rotation=TFT_ROTATION,
        )
        backlight = digitalio.DigitalInOut(TFT_BL)
        backlight.direction = digitalio.Direction.OUTPUT
        backlight.value = True
        return display, backlight, None
    except Exception as exc:
        print("Display init failed:", exc)
        return NullDisplay(), None, str(exc)


def make_input(pin):
    dio = digitalio.DigitalInOut(pin)
    dio.direction = digitalio.Direction.INPUT
    dio.pull = digitalio.Pull.UP
    return dio


def read_bit(raw_value, bit):
    if raw_value is None:
        return None
    return bool(raw_value & (1 << bit))


def decode_signal(raw, active_high):
    if raw is None:
        return None
    return raw if active_high else not raw


def read_signal_group(pcf, configs):
    if pcf is None:
        raw_value = None
    else:
        try:
            raw_value = pcf.read_byte()
        except Exception:
            raw_value = None
    values = {}
    for config in configs:
        raw = read_bit(raw_value, config["bit"])
        values[config["name"]] = {
            "raw": raw,
            "active": decode_signal(raw, config["active_high"]),
        }
    return values


def clamp(value, low, high):
    return min(max(value, low), high)


def voltage_to_resistance(voltage):
    if voltage <= 0.0:
        return 0.0
    if voltage >= SUPPLY_VOLTAGE:
        return MAX_SENDER_OHMS
    return (voltage * SENDER_PULLUP_OHMS) / (SUPPLY_VOLTAGE - voltage)


def resistance_to_percent(resistance):
    return clamp(100.0 * (resistance / MAX_SENDER_OHMS), 0.0, 100.0)


def resistance_to_oil_psi(resistance):
    return clamp(MAX_OIL_PSI * (resistance / MAX_SENDER_OHMS), 0.0, MAX_OIL_PSI)


def resistance_to_coolant_f(resistance):
    if resistance >= GM_ECT_TABLE[0][1]:
        return GM_ECT_TABLE[0][0]
    if resistance <= GM_ECT_TABLE[-1][1]:
        return GM_ECT_TABLE[-1][0]
    for index in range(len(GM_ECT_TABLE) - 1):
        low_temp, high_resistance = GM_ECT_TABLE[index]
        high_temp, low_resistance = GM_ECT_TABLE[index + 1]
        if high_resistance >= resistance >= low_resistance:
            span = high_resistance - low_resistance
            position = (high_resistance - resistance) / span
            return low_temp + position * (high_temp - low_temp)
    return None


def read_ads_channels(ads_inputs):
    values = {}
    for channel in ADS_CHANNELS:
        name = channel["name"]
        analog = ads_inputs.get(name)
        if analog is None:
            values[name] = {
                "raw": None,
                "voltage": None,
                "resistance": None,
                "converted": None,
            }
            continue
        try:
            voltage = analog.voltage
            resistance = voltage_to_resistance(voltage)
            converted = None
            if name == "Fuel":
                converted = resistance_to_percent(resistance)
            elif name == "OilPres":
                converted = resistance_to_oil_psi(resistance)
            elif name == "ECT":
                converted = resistance_to_coolant_f(resistance)
            values[name] = {
                "raw": analog.value,
                "voltage": voltage,
                "resistance": resistance,
                "converted": converted,
            }
        except Exception:
            values[name] = {
                "raw": None,
                "voltage": None,
                "resistance": None,
                "converted": None,
            }
    return values


def prndl_state(indicators):
    a = indicators["PRNDL A"]["active"]
    b = indicators["PRNDL B"]["active"]
    c = indicators["PRNDL C"]["active"]
    p = indicators["PRNDL P"]["active"]
    if None in (a, b, c, p):
        return "NO DATA"
    return PRNDL_TABLE.get((a, b, c, p), "INVALID")


class PulseCounter:
    def __init__(self, input_pin, name):
        self.input_pin = input_pin
        self.name = name
        self.last_raw = input_pin.value
        self.count = 0
        self.window_count = 0
        self.frequency = 0.0
        self.last_edge_time = None
        self.last_window_time = time.monotonic()

    def update(self, now):
        edge_count = 0
        raw = self.input_pin.value
        if self.last_raw and not raw:
            self.count += 1
            self.window_count += 1
            edge_count = 1
            self.last_edge_time = now
        self.last_raw = raw

        elapsed = now - self.last_window_time
        if elapsed >= FREQUENCY_WINDOW:
            self.frequency = self.window_count / elapsed
            self.window_count = 0
            self.last_window_time = now
        return edge_count

    def snapshot(self, now, stale_seconds=STALE_PULSE_SECONDS):
        if self.last_edge_time is None:
            age = None
            stale = True
        else:
            age = now - self.last_edge_time
            stale = age > stale_seconds
        return {
            "count": self.count,
            "frequency_hz": self.frequency,
            "last_edge_age": age,
            "stale": stale,
        }


class Odometer:
    def __init__(self):
        self.tenths = ODOMETER_START_TENTHS
        self.remainder_pulses = ODOMETER_START_REMAINDER_PULSES
        self.load_ok = False
        self.save_ok = False
        self.last_error = None
        self.last_save_time = 0.0
        self.dirty = False
        self.load()

    def load(self):
        try:
            with open(ODOMETER_FILE, "r") as file_obj:
                data = json.loads(file_obj.read())
            tenths = int(data.get("tenths", ODOMETER_START_TENTHS))
            remainder = int(data.get("remainder_pulses", ODOMETER_START_REMAINDER_PULSES))
            if tenths < 0 or remainder < 0:
                raise ValueError("negative odometer value")
            self.tenths = tenths
            self.remainder_pulses = remainder
            self.normalize()
            self.load_ok = True
            self.last_error = None
        except Exception as exc:
            self.tenths = ODOMETER_START_TENTHS
            self.remainder_pulses = ODOMETER_START_REMAINDER_PULSES
            self.normalize()
            self.load_ok = False
            self.last_error = str(exc)

    def normalize(self):
        while self.remainder_pulses >= VSS_PULSES_PER_TENTH_MILE:
            self.tenths += 1
            self.remainder_pulses -= VSS_PULSES_PER_TENTH_MILE

    def add_pulses(self, pulse_count):
        if pulse_count <= 0:
            return
        self.remainder_pulses += int(pulse_count)
        self.normalize()
        self.dirty = True

    def miles(self):
        return self.tenths / 10.0

    def formatted(self):
        return "{:07.1f}".format(self.miles())

    def save(self, now):
        try:
            data = {
                "tenths": int(self.tenths),
                "remainder_pulses": int(self.remainder_pulses),
            }
            with open(ODOMETER_FILE, "w") as file_obj:
                file_obj.write(json.dumps(data))
            self.save_ok = True
            self.last_error = None
            self.last_save_time = now
            self.dirty = False
        except Exception as exc:
            self.save_ok = False
            self.last_error = str(exc)

    def maybe_periodic_save(self, now, running):
        if not running or not self.dirty:
            return
        if now - self.last_save_time >= ODOMETER_SAVE_INTERVAL_SECONDS:
            self.save(now)

    def snapshot(self):
        return {
            "tenths": self.tenths,
            "remainder_pulses": self.remainder_pulses,
            "miles": self.miles(),
            "load_ok": self.load_ok,
            "save_ok": self.save_ok,
            "last_error": self.last_error,
        }


def bool_text(value):
    if value is None:
        return "--"
    return "HI" if value else "LO"


def active_text(value):
    if value is None:
        return "--"
    return "ON" if value else "off"


def fmt_float(value, places=2):
    if value is None:
        return "--"
    return ("{:." + str(places) + "f}").format(value)


def fmt_int(value):
    if value is None:
        return "--"
    return str(int(value))


def make_label(text, x, y, color=COLOR_TEXT, scale=1):
    return label.Label(terminalio.FONT, text=text, color=color, x=x, y=y, scale=scale)


class TextPage:
    def __init__(self):
        self.group = displayio.Group()
        self.lines = []
        for index in range(14):
            text = make_label("", 4, 9 + index * 17, COLOR_GREEN, 1)
            self.group.append(text)
            self.lines.append(text)

    def set_lines(self, lines):
        for index, text_line in enumerate(self.lines):
            next_text = lines[index] if index < len(lines) else ""
            if text_line.text != next_text:
                text_line.text = next_text


class ClusterPage:
    def __init__(self):
        self.group = displayio.Group()
        self.lamps = {}
        self.group.append(make_label("MPH", 42, 16, COLOR_MUTED, 1))
        self.speed = make_label("000", 18, 63, COLOR_TEXT, 5)
        self.group.append(self.speed)
        self.group.append(make_label("RPM", 210, 16, COLOR_MUTED, 1))
        self.rpm = make_label("0000", 182, 63, COLOR_TEXT, 4)
        self.group.append(self.rpm)

        self.fuel = make_label("FUEL --%", 13, 132, COLOR_GREEN, 1)
        self.temp = make_label("TEMP ---F", 116, 132, COLOR_GREEN, 1)
        self.oil = make_label("OIL -- PSI", 218, 132, COLOR_GREEN, 1)
        self.prndl = make_label("PRNDL --", 13, 153, COLOR_TEXT, 1)
        self.odo = make_label("ODO 000000.0", 107, 228, COLOR_TEXT, 1)
        self.group.append(self.fuel)
        self.group.append(self.temp)
        self.group.append(self.oil)
        self.group.append(self.prndl)
        self.group.append(self.odo)

        self.add_lamp("L", 10, 178, COLOR_GREEN)
        self.add_lamp("HIGH", 31, 178, COLOR_BLUE)
        self.add_lamp("R", 65, 178, COLOR_GREEN)
        self.add_lamp("BELT", 87, 178, COLOR_RED)
        self.add_lamp("ABS", 123, 178, COLOR_AMBER)
        self.add_lamp("ALT", 153, 178, COLOR_RED)
        self.add_lamp("AIR", 184, 178, COLOR_RED)
        self.add_lamp("DRL", 214, 178, COLOR_GREEN)
        self.add_lamp("MIL", 244, 178, COLOR_AMBER)
        self.add_lamp("BRK", 275, 178, COLOR_RED)

        self.add_lamp("S1", 10, 204, COLOR_AMBER)
        self.add_lamp("S2", 32, 204, COLOR_AMBER)
        self.add_lamp("LOWF", 64, 204, COLOR_AMBER)
        self.add_lamp("OIL", 106, 204, COLOR_RED)
        self.add_lamp("TEMP", 141, 204, COLOR_RED)
        self.add_lamp("VSS", 184, 204, COLOR_AMBER)
        self.add_lamp("TACH", 220, 204, COLOR_AMBER)

    def add_lamp(self, name, x, y, on_color):
        lamp = make_label(name, x, y, COLOR_DIM, 1)
        self.lamps[name] = {"label": lamp, "on_color": on_color}
        self.group.append(lamp)

    def set_lamp(self, name, active):
        lamp = self.lamps[name]
        lamp["label"].color = lamp["on_color"] if active else COLOR_DIM

    def update(self, state):
        speed = state["cluster"]["speed_mph"]
        rpm = state["cluster"]["rpm"]
        fuel = state["cluster"]["fuel_percent"]
        oil = state["cluster"]["oil_psi"]
        temp = state["cluster"]["coolant_f"]
        warnings = state["derived_warnings"]

        self.speed.text = "{:03d}".format(int(clamp(speed, 0, 999)))
        self.rpm.text = "{:04d}".format(int(clamp(rpm, 0, 9999)))
        self.fuel.text = "FUEL {}%".format(fmt_int(fuel))
        self.fuel.color = COLOR_AMBER if warnings["low_fuel"] else COLOR_GREEN
        self.temp.text = "TEMP {}F".format(fmt_int(temp))
        self.temp.color = COLOR_RED if warnings["high_coolant"] else COLOR_GREEN
        self.oil.text = "OIL {} PSI".format(fmt_int(oil))
        self.oil.color = COLOR_RED if warnings["low_oil"] else COLOR_GREEN
        self.prndl.text = "PRNDL {}".format(state["prndl"])
        self.odo.text = "ODO {}".format(state["odometer"]["display"])

        self.set_lamp("L", state["indicators"]["L Turn"]["active"])
        self.set_lamp("HIGH", state["indicators"]["HiBeam"]["active"])
        self.set_lamp("R", state["indicators"]["R Turn"]["active"])
        self.set_lamp("BELT", state["indicators"]["SeatBelts"]["active"])
        self.set_lamp("ABS", state["warnings"]["ABS"]["active"])
        self.set_lamp("ALT", state["warnings"]["ALT"]["active"])
        self.set_lamp("AIR", state["warnings"]["AirBag"]["active"])
        self.set_lamp("MIL", state["warnings"]["MIL"]["active"])
        self.set_lamp("BRK", state["warnings"]["ParkBrake"]["active"])
        self.set_lamp("DRL", state["warnings"]["DRL"]["active"])
        self.set_lamp("S1", state["warnings"]["Spare1"]["active"])
        self.set_lamp("S2", state["warnings"]["Spare2"]["active"])
        self.set_lamp("LOWF", warnings["low_fuel"])
        self.set_lamp("OIL", warnings["low_oil"])
        self.set_lamp("TEMP", warnings["high_coolant"])
        self.set_lamp("VSS", warnings["stale_vss"])
        self.set_lamp("TACH", warnings["stale_tach"])


class DisplayController:
    def __init__(self, display):
        self.display = display
        self.cluster = ClusterPage()
        self.text = TextPage()
        self.current_group = None
        self.show_group(self.cluster.group)

    def show_group(self, group):
        if group == self.current_group:
            return
        gc.collect()
        try:
            self.display.root_group = group
        except AttributeError:
            self.display.show(group)
        self.current_group = group

    def update(self, state):
        if state["page"] == 0:
            self.show_group(self.cluster.group)
            self.cluster.update(state)
        else:
            self.show_group(self.text.group)
            self.text.set_lines(PAGES[state["page"]](state))


def speed_from_frequency(frequency_hz):
    return frequency_hz * 3600.0 / VSS_PULSES_PER_MILE


def rpm_from_frequency(frequency_hz):
    return frequency_hz * 60.0 / TACH_PULSES_PER_REV


def derived_warning_state(state):
    cluster = state["cluster"]
    pulses = state["pulses"]
    return {
        "low_fuel": cluster["fuel_percent"] is not None and cluster["fuel_percent"] <= LOW_FUEL_PERCENT,
        "low_oil": cluster["oil_psi"] is not None and cluster["oil_psi"] <= LOW_OIL_PSI,
        "high_coolant": cluster["coolant_f"] is not None and cluster["coolant_f"] >= HIGH_COOLANT_F,
        "stale_vss": pulses["VSS"]["stale"],
        "stale_tach": pulses["Tach"]["stale"],
    }


def page_indicators(state):
    lines = ["Indicators / Warnings", ""]
    for name in ("HiBeam", "L Turn", "R Turn", "SeatBelts"):
        item = state["indicators"][name]
        lines.append("{} {:>3} raw {}".format(name, active_text(item["active"]), bool_text(item["raw"])))
    lines.append("")
    for name in ("ABS", "ALT", "AirBag", "DRL", "MIL", "ParkBrake"):
        item = state["warnings"][name]
        lines.append("{} {:>3} raw {}".format(name, active_text(item["active"]), bool_text(item["raw"])))
    return lines


def page_analog(state):
    lines = ["ADS1115 Analog", ""]
    for name in ("ECT", "OilPres", "Fuel", "ADS3"):
        item = state["analog"][name]
        lines.append(name)
        lines.append(" raw {} V {}".format(item["raw"] if item["raw"] is not None else "--", fmt_float(item["voltage"], 3)))
        if name == "Fuel":
            lines.append(" fuel {}%".format(fmt_float(item["converted"], 1)))
        elif name == "OilPres":
            lines.append(" oil {} psi".format(fmt_float(item["converted"], 1)))
        elif name == "ECT":
            lines.append(" temp {}F".format(fmt_float(item["converted"], 1)))
        else:
            lines.append(" ohms {}".format(fmt_float(item["resistance"], 1)))
    return lines


def page_pulses(state):
    vss = state["pulses"]["VSS"]
    tach = state["pulses"]["Tach"]
    odo = state["odometer"]
    return [
        "VSS / Tach / Odometer",
        "",
        "MPH {}".format(fmt_float(state["cluster"]["speed_mph"], 1)),
        "VSS count {}".format(vss["count"]),
        "VSS freq {} Hz".format(fmt_float(vss["frequency_hz"], 2)),
        "VSS stale {}".format("YES" if vss["stale"] else "no"),
        "",
        "RPM {}".format(fmt_int(state["cluster"]["rpm"])),
        "Tach count {}".format(tach["count"]),
        "Tach freq {} Hz".format(fmt_float(tach["frequency_hz"], 2)),
        "Tach stale {}".format("YES" if tach["stale"] else "no"),
        "",
        "ODO tenths {}".format(odo["tenths"]),
        "ODO rem pulses {}".format(odo["remainder_pulses"]),
    ]


def page_system(state):
    devices = ["0x{:02X}".format(item) for item in state["i2c_found"]]
    wifi_state = state["wifi"]
    wifi_status = "OK" if wifi_state["ok"] else "ERR"
    wifi_url = wifi_state["url"] if wifi_state["url"] else "--"
    return [
        "System",
        "",
        "I2C {}".format(" ".join(devices) if devices else "none"),
        "PCF20 {}".format("OK" if state["pcf_indicator_ok"] else "missing"),
        "PCF21 {}".format("OK" if state["pcf_warning_ok"] else "missing"),
        "ADS48 {}".format("OK" if state["ads_ok"] else "missing"),
        "Display {}".format("OK" if state["display_ok"] else "fallback"),
        "ODO load {}".format("OK" if state["odometer"]["load_ok"] else "default"),
        "ODO save {}".format("OK" if state["odometer"]["save_ok"] else "--"),
        "WiFi {} {}".format(wifi_status, wifi_state["ssid"]),
        "HTTP {}".format(wifi_url),
        "Button {}".format(pin_name(PAGE_BUTTON_PIN)),
        "Page {}/{}".format(state["page"] + 1, len(PAGES)),
        "Loop {} Hz".format(fmt_float(state["loop_hz"], 1)),
    ]


PAGES = (None, page_indicators, page_analog, page_pulses, page_system)


def snapshot_for_serial(state):
    return {
        "page": state["page"],
        "prndl": state["prndl"],
        "cluster": state["cluster"],
        "derived_warnings": state["derived_warnings"],
        "odometer": state["odometer"],
        "indicators": state["indicators"],
        "warnings": state["warnings"],
        "analog": state["analog"],
        "pulses": state["pulses"],
        "wifi": state["wifi"],
        "i2c_found": state["i2c_found"],
        "loop_hz": state["loop_hz"],
    }


def wifi_status_template(ok=False, error=None, ip=None, url=None):
    return {
        "ok": ok,
        "ssid": DASH_AP_SSID,
        "channel": DASH_AP_CHANNEL,
        "port": DASH_HTTP_PORT,
        "ip": ip,
        "url": url,
        "requests": 0,
        "last_error": error,
    }


DASHBOARD_HTML = """<!doctype html><html><head><meta name=viewport content=width=device-width,initial-scale=1><title>K1500 Dash</title><style>
body{margin:0;background:#070707;color:#e8e8e8;font:16px system-ui,sans-serif}main{max-width:760px;margin:auto;padding:12px}h1{font-size:22px;margin:0 0 10px}.s{color:#888;font-size:13px}.g{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.t{border:1px solid #303030;border-radius:6px;padding:10px;background:#111}.l{color:#888;font-size:12px}.v{font-size:34px;font-weight:700}.w{grid-column:span 3}.lamps{display:grid;grid-template-columns:repeat(9,1fr);gap:6px}.lamp{border:1px solid #303030;border-radius:5px;padding:7px 3px;background:#151515;color:#4a4a4a;text-align:center;font-size:12px;font-weight:700}.on.gn{color:#00ff66;border-color:#00a846}.on.bl{color:#4ca0ff;border-color:#2060b0}.on.am{color:#ffaa00;border-color:#b87800}.on.rd{color:#ff3030;border-color:#a82020}@media(max-width:520px){.g{grid-template-columns:1fr}.w{grid-column:span 1}.lamps{grid-template-columns:repeat(4,1fr)}}
</style></head><body><main><h1>K1500 Dash</h1><div class=s id=s>connecting</div><section class=g>
<div class=t><div class=l>MPH</div><div class=v id=mph>--</div></div><div class=t><div class=l>RPM</div><div class=v id=rpm>--</div></div><div class=t><div class=l>PRNDL</div><div class=v id=prndl>--</div></div>
<div class=t><div class=l>Fuel</div><div class=v id=fuel>--</div></div><div class=t><div class=l>Oil</div><div class=v id=oil>--</div></div><div class=t><div class=l>Temp</div><div class=v id=temp>--</div></div>
<div class="t w"><div class=l>Odometer</div><div class=v id=odo>--</div></div><div class="t w"><div class=l>Idiot Lights</div><div class=lamps>
<div class="lamp gn" id=ll>L</div><div class="lamp bl" id=lh>HIGH</div><div class="lamp gn" id=lr>R</div><div class="lamp rd" id=lb>BELT</div><div class="lamp am" id=la>ABS</div><div class="lamp rd" id=lt>ALT</div><div class="lamp rd" id=li>AIR</div><div class="lamp gn" id=ld>DRL</div><div class="lamp am" id=lm>MIL</div><div class="lamp rd" id=lk>BRK</div><div class="lamp am" id=l1>S1</div><div class="lamp am" id=l2>S2</div><div class="lamp am" id=lf>LOWF</div><div class="lamp rd" id=lo>OIL</div><div class="lamp rd" id=lc>TEMP</div><div class="lamp am" id=lv>VSS</div><div class="lamp am" id=lx>TACH</div>
</div></div></section></main><script>
function f(v,u){return v==null?"--":Math.round(v)+(u||"")}function a(g,n){return g&&g[n]&&g[n].active===true}function l(i,o){document.getElementById(i).classList.toggle("on",!!o)}
async function r(){try{let d=await(await fetch("/data.json",{cache:"no-store"})).json(),w=d.derived_warnings||{};mph.textContent=f(d.cluster.speed_mph);rpm.textContent=f(d.cluster.rpm);prndl.textContent=d.prndl||"--";fuel.textContent=f(d.cluster.fuel_percent,"%");oil.textContent=f(d.cluster.oil_psi," psi");temp.textContent=f(d.cluster.coolant_f," F");odo.textContent=d.odometer.display||"--";l("ll",a(d.indicators,"L Turn"));l("lh",a(d.indicators,"HiBeam"));l("lr",a(d.indicators,"R Turn"));l("lb",a(d.indicators,"SeatBelts"));l("la",a(d.warnings,"ABS"));l("lt",a(d.warnings,"ALT"));l("li",a(d.warnings,"AirBag"));l("ld",a(d.warnings,"DRL"));l("lm",a(d.warnings,"MIL"));l("lk",a(d.warnings,"ParkBrake"));l("l1",a(d.warnings,"Spare1"));l("l2",a(d.warnings,"Spare2"));l("lf",w.low_fuel);l("lo",w.low_oil);l("lc",w.high_coolant);l("lv",w.stale_vss);l("lx",w.stale_tach);s.textContent="updated "+new Date().toLocaleTimeString()}catch(e){s.textContent="offline"}}
r();setInterval(r,2000);
</script></body></html>"""

#CHANGED FROM setInterval(r,1000) to setInterval(r,2000) FOR DEBUGGING 006/06/2026

class WiFiTelemetry:
    def __init__(self):
        self.server = None
        self.pool = None
        self.status = wifi_status_template(error=WIFI_IMPORT_ERROR)

    def start(self):
        if WIFI_IMPORT_ERROR:
            print("WiFi import failed:", WIFI_IMPORT_ERROR)
            return self.status
        try:
            wifi.radio.start_ap(
                ssid=DASH_AP_SSID,
                password=DASH_AP_PASSWORD,
                channel=DASH_AP_CHANNEL,
            )
            ip = str(wifi.radio.ipv4_address_ap)
            self.pool = socketpool.SocketPool(wifi.radio)
            self.server = Server(self.pool, debug=False)

            @self.server.route("/")
            def base(request: Request):
                self.status["requests"] += 1
                gc.collect()
                return Response(request, DASHBOARD_HTML, content_type="text/html")

            @self.server.route("/data.json")
            def data(request: Request):
                self.status["requests"] += 1
#                gc.collect()#COMMENTED OUT FOR DEBUGGING 06/06/2026
#                return JSONResponse(request, snapshot_for_serial(state))#COMMENTED OUT FOR DEBUGGING 06/06/2026
                return JSONResponse(request, snapshot_for_wifi(state))#ADDED FOR DEBUGGING 06/06/2026

            @self.server.route("/health.json")
            def health(request: Request):
                self.status["requests"] += 1
                gc.collect()
                return JSONResponse(
                    request,
                    {
                        "wifi": self.status,
                        "uptime": time.monotonic(),
                        "loop_hz": state["loop_hz"],
                    },
                )

            self.server.start(ip, port=DASH_HTTP_PORT)
            self.status = wifi_status_template(
                ok=True,
                ip=ip,
                url="http://{}:{}/".format(ip, DASH_HTTP_PORT),
            )
            print("WiFi AP:", DASH_AP_SSID)
            print("Dash URL:", self.status["url"])
            return self.status
        except Exception as exc:
            self.status = wifi_status_template(error=str(exc))
            print("WiFi server failed:", exc)
            return self.status

    def poll(self):
        if self.server is None:
            return self.status
        try:
            self.server.poll()
            self.status["ok"] = True
            self.status["last_error"] = None
        except Exception as exc:
            self.status["ok"] = False
            self.status["last_error"] = str(exc)
        return self.status


def run_self_test(controller):
    test_state = {
        "page": 0,
        "prndl": "8",
        "cluster": {
            "speed_mph": 188.0,
            "rpm": 8888.0,
            "fuel_percent": 88.0,
            "oil_psi": 88.0,
            "coolant_f": 188.0,
        },
        "derived_warnings": {
            "low_fuel": True,
            "low_oil": True,
            "high_coolant": True,
            "stale_vss": True,
            "stale_tach": True,
        },
        "odometer": {"display": "888888.8"},
        "indicators": {
            "HiBeam": {"active": True},
            "L Turn": {"active": True},
            "R Turn": {"active": True},
            "SeatBelts": {"active": True},
        },
        "warnings": {
            "ABS": {"active": True},
            "ALT": {"active": True},
            "AirBag": {"active": True},
            "DRL": {"active": True},
            "MIL": {"active": True},
            "ParkBrake": {"active": True},
            "Spare1": {"active": True},
            "Spare2": {"active": True},
        },
    }
    controller.update(test_state)
    time.sleep(1.0)


i2c, i2c_found = init_i2c()
pcf_indicator, pcf_indicator_error = init_pcf(i2c, PCF_INDICATOR_ADDRESS)
pcf_warning, pcf_warning_error = init_pcf(i2c, PCF_WARNING_ADDRESS)
ads, ads_inputs, ads_error = init_ads(i2c)
display, backlight, display_error = init_display()

page_button = make_input(PAGE_BUTTON_PIN)
vss_counter = PulseCounter(make_input(VSS_PIN), "VSS")
tach_counter = PulseCounter(make_input(TACH_PIN), "Tach")
odometer = Odometer()
display_controller = DisplayController(display)
run_self_test(display_controller)

state = {
    "page": 0,
    "i2c_found": i2c_found,
    "pcf_indicator_ok": pcf_indicator is not None,
    "pcf_warning_ok": pcf_warning is not None,
    "ads_ok": ads is not None,
    "display_ok": display_error is None,
    "indicators": read_signal_group(pcf_indicator, INDICATOR_SIGNALS),
    "warnings": read_signal_group(pcf_warning, WARNING_SIGNALS),
    "analog": read_ads_channels(ads_inputs),
    "prndl": "NO DATA",
    "pulses": {
        "VSS": vss_counter.snapshot(time.monotonic()),
        "Tach": tach_counter.snapshot(time.monotonic(), ENGINE_OFF_TACH_STALE_SECONDS),
    },
    "cluster": {
        "speed_mph": 0.0,
        "rpm": 0.0,
        "fuel_percent": None,
        "oil_psi": None,
        "coolant_f": None,
    },
    "derived_warnings": {},
    "odometer": odometer.snapshot(),
    "wifi": wifi_status_template(),
    "loop_hz": 0.0,
}
    
#ADDED FOR DEBUGGING 06/06/2026
def snapshot_for_wifi(state):
    return {
        "prndl": state["prndl"],
        "cluster": state["cluster"],
        "derived_warnings": state["derived_warnings"],
        "odometer": {"display": state["odometer"]["display"]},
        "indicators": state["indicators"],
        "warnings": state["warnings"],
    }

state["odometer"]["display"] = odometer.formatted()
state["derived_warnings"] = derived_warning_state(state)

wifi_telemetry = WiFiTelemetry()
state["wifi"] = wifi_telemetry.start()

last_pcf_poll = 0.0
last_ads_poll = 0.0
last_display = 0.0
last_serial = 0.0
last_button_raw = page_button.value
last_button_change = time.monotonic()
last_loop_report = time.monotonic()
loop_count = 0
engine_was_running = False
engine_shutdown_saved = False

while True:
    now = time.monotonic()
    state["wifi"] = wifi_telemetry.poll()#ADDED FOR DEBUGGING 06/06/2026
    loop_count += 1

    if now - last_loop_report >= 1.0:
        state["loop_hz"] = loop_count / (now - last_loop_report)
        loop_count = 0
        last_loop_report = now

    vss_edges = vss_counter.update(now)
    tach_counter.update(now)
    odometer.add_pulses(vss_edges)

    button_raw = page_button.value
    if button_raw != last_button_raw:
        last_button_raw = button_raw
        last_button_change = now
    elif not button_raw and now - last_button_change >= BUTTON_DEBOUNCE:
        state["page"] = (state["page"] + 1) % len(PAGES)
        while not page_button.value:
            now = time.monotonic()
            odometer.add_pulses(vss_counter.update(now))
            tach_counter.update(now)
            time.sleep(0.005)
        last_button_raw = True
        last_button_change = time.monotonic()
        gc.collect()
        last_display = 0.0

    if now - last_pcf_poll >= PCF_POLL_INTERVAL:
        last_pcf_poll = now
        state["indicators"] = read_signal_group(pcf_indicator, INDICATOR_SIGNALS)
        state["warnings"] = read_signal_group(pcf_warning, WARNING_SIGNALS)
        state["prndl"] = prndl_state(state["indicators"])

    if now - last_ads_poll >= ADS_POLL_INTERVAL:
        last_ads_poll = now
        state["analog"] = read_ads_channels(ads_inputs)

    state["pulses"] = {
        "VSS": vss_counter.snapshot(now),
        "Tach": tach_counter.snapshot(now, ENGINE_OFF_TACH_STALE_SECONDS),
    }

    tach_running = not state["pulses"]["Tach"]["stale"]
    if tach_running:
        engine_was_running = True
        engine_shutdown_saved = False
    elif engine_was_running and not engine_shutdown_saved:
        odometer.save(now)
        engine_shutdown_saved = True

    state["cluster"] = {
        "speed_mph": speed_from_frequency(state["pulses"]["VSS"]["frequency_hz"]),
        "rpm": rpm_from_frequency(state["pulses"]["Tach"]["frequency_hz"]),
        "fuel_percent": state["analog"]["Fuel"]["converted"],
        "oil_psi": state["analog"]["OilPres"]["converted"],
        "coolant_f": state["analog"]["ECT"]["converted"],
    }
    state["odometer"] = odometer.snapshot()
    state["odometer"]["display"] = odometer.formatted()
    state["derived_warnings"] = derived_warning_state(state)

    odometer.maybe_periodic_save(now, tach_running)
#    state["wifi"] = wifi_telemetry.poll()# COMMENTED OUT FOR DEBUGGING 06/06/2026

    display_interval = DISPLAY_INTERVAL if state["page"] == 0 else TEXT_DISPLAY_INTERVAL
    if now - last_display >= display_interval:
        last_display = now
        if state["page"] != 0:
            gc.collect()
        display_controller.update(state)
        if state["page"] != 0:
            gc.collect()

    if now - last_serial >= SERIAL_INTERVAL:
        last_serial = now
        gc.collect()
        print("free mem:", gc.mem_free(), "loop hz:", state["loop_hz"]) #ADDED FOR DEBUGGING 06/06/2026
#        print(json.dumps(snapshot_for_serial(state))) #COMMENTED OUT FOR DEBUGGING 06/06/2026
#        print() 
        gc.collect()

    time.sleep(PULSE_POLL_INTERVAL)
