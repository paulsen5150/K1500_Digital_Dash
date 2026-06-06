# Codex Session Log: ESP32 Instrument Cluster WiFi

Date: 2026-05-27

## User Request

Create a new version based on `ESP32_Instrument_Cluster/code.py` in a new
directory named `ESP32_Instrument_Cluster_WIFI`, with the ability to transmit
dash data by WiFi to a laptop.

## Planning Decisions

After inspecting the existing CircuitPython cluster code and related serial
testbed scripts, Codex identified that the existing app already builds a single
live `state` object and prints a JSON snapshot over serial. That state snapshot
was chosen as the source for WiFi telemetry.

User selected:

- WiFi mode: ESP32 hotspot/access point
- Laptop access style: ESP web server

Implementation plan:

- Copy the existing cluster app into a new `ESP32_Instrument_Cluster_WIFI`
  directory.
- Keep the original display, sensor polling, odometer, diagnostic pages, and
  serial JSON behavior intact.
- Add AP mode using CircuitPython `wifi.radio.start_ap(...)`.
- Add an HTTP server using `socketpool` and `adafruit_httpserver`.
- Serve:
  - `/` as a small browser dashboard
  - `/data.json` as live telemetry JSON
  - `/health.json` as WiFi/server health JSON
- Add WiFi/server status to the existing system diagnostic page.
- Add setup documentation and a laptop polling script.

## Files Created

- `ESP32_Instrument_Cluster_WIFI/code.py`
- `ESP32_Instrument_Cluster_WIFI/README.md`
- `ESP32_Instrument_Cluster_WIFI/settings.example.toml`
- `ESP32_Instrument_Cluster_WIFI/laptop_poll_dash.py`
- `ESP32_Instrument_Cluster_WIFI/CODEX_session.md`

## Implementation Summary

`code.py` was copied from `ESP32_Instrument_Cluster/code.py` and updated with:

- Optional imports for:
  - `wifi`
  - `socketpool`
  - `adafruit_httpserver`
- Settings read from `settings.toml` via `os.getenv()`:
  - `DASH_AP_SSID`
  - `DASH_AP_PASSWORD`
  - `DASH_AP_CHANNEL`
  - `DASH_HTTP_PORT`
- Default settings:
  - SSID: `K1500_Dash`
  - Password: `k1500dash`
  - Channel: `6`
  - HTTP port: `5000`
- A `WiFiTelemetry` class that:
  - starts the ESP32 AP
  - creates a `socketpool.SocketPool`
  - starts an `adafruit_httpserver.Server`
  - registers `/`, `/data.json`, and `/health.json`
  - calls `server.poll()` from the main loop
  - reports errors without stopping the dash app
- The system diagnostic page now shows WiFi status and the HTTP URL.
- The serial JSON snapshot now includes the `wifi` key.

The browser dashboard at `/` polls `/data.json` once per second and displays:

- MPH
- RPM
- PRNDL
- Fuel
- Oil pressure
- Coolant temperature
- Odometer
- Raw JSON

`laptop_poll_dash.py` is a normal laptop-side Python script that fetches:

```text
http://192.168.4.1:5000/data.json
```

and prints selected dash fields once per second.

## Verification

Codex ran:

```bash
python3 -m py_compile ESP32_Instrument_Cluster_WIFI/code.py ESP32_Instrument_Cluster_WIFI/laptop_poll_dash.py
```

The syntax check passed.

Codex removed the generated `__pycache__` afterward.

Hardware WiFi/AP behavior was not tested in this session because the ESP32 board
was not available through the local environment.

## Usage Notes

To use the WiFi version:

1. Copy `ESP32_Instrument_Cluster_WIFI/code.py` to the CircuitPython board as
   `/code.py`.
2. Install the original cluster libraries plus `adafruit_httpserver.mpy`.
3. Optionally copy `settings.example.toml` to the board root as
   `/settings.toml` and edit the values.
4. Boot the ESP32.
5. Connect the laptop to the ESP32 AP, default `K1500_Dash`.
6. Open:

```text
http://192.168.4.1:5000/
```

or read raw telemetry from:

```text
http://192.168.4.1:5000/data.json
```

