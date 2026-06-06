# ESP32 Instrument Cluster WiFi

CircuitPython ESP32-S3 instrument cluster with a built-in WiFi access point and
HTTP telemetry server for laptop viewing.

This version is based on `ESP32_Instrument_Cluster/code.py`. It keeps the
display, sensor polling, odometer, diagnostic pages, and serial JSON output,
then adds:

- ESP32 access point mode
- Browser dashboard at `/`
- Machine-readable JSON at `/data.json`
- Health/status JSON at `/health.json`

## Board Setup

Copy `code.py` to the CircuitPython board root as `/code.py`.

Install the same libraries required by the original cluster, plus:

- `adafruit_httpserver.mpy`

The existing hardware libraries are still required:

- `adafruit_display_text`
- `adafruit_ads1x15`
- `adafruit_pcf8574`
- `adafruit_st7789`
- `fourwire`

## WiFi Settings

The code has defaults, so `settings.toml` is optional. To customize the AP name,
password, channel, or port, copy `settings.example.toml` to the board root as
`/settings.toml` and edit it.

Defaults:

```toml
DASH_AP_SSID = "K1500_Dash"
DASH_AP_PASSWORD = "k1500dash"
DASH_AP_CHANNEL = "6"
DASH_HTTP_PORT = "5000"
```

Port `5000` is used to avoid conflicting with CircuitPython Web Workflow on
port `80`.

## Laptop Use

1. Boot the ESP32.
2. Connect the laptop WiFi to `K1500_Dash`.
3. Open the URL shown on the ESP32 system page or serial console.

Common default URL:

```text
http://192.168.4.1:5000/
```

Useful endpoints:

```text
http://192.168.4.1:5000/
http://192.168.4.1:5000/data.json
http://192.168.4.1:5000/health.json
```

For terminal testing from the laptop:

```bash
python3 laptop_poll_dash.py
```

Run that script from this directory after connecting the laptop to the ESP32 AP.

## Notes

If the HTTP server library is missing or WiFi setup fails, the dash still runs.
The error is reported on the system diagnostic page and in the serial JSON under
the `wifi` key.
