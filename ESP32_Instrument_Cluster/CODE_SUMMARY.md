# code.py Summary

`code.py` is a CircuitPython instrument-cluster application for an ESP32-S3.
It reads the K1500/KITT interface hardware, converts the raw signals into dash
values, drives a 320x240 ST7789 LCD, tracks odometer distance, and cycles
between a graphical cluster page and diagnostic text pages.

## Hardware Interfaces

- I2C runs on `board.IO9` SCL and `board.IO8` SDA.
- PCF8574 at `0x20` reads indicator and PRNDL inputs.
- PCF8574 at `0x21` reads warning-light inputs.
- ADS1115 at `0x48` reads analog channels:
  - `ECT` on ADS channel 0
  - `OilPres` on ADS channel 1
  - `Fuel` on ADS channel 2
  - `ADS3` on ADS channel 3
- ST7789 LCD uses SPI pins `IO12`, `IO11`, `IO10`, `IO13`, `IO14`, and
  backlight pin `IO21`.
- Page button uses `IO17`.
- VSS pulse input uses `IO15`.
- Tach pulse input uses `IO16`.

## Data Collection

- `DirectPCF8574` reads each PCF8574 device as a raw byte over I2C, then
  `read_signal_group()` decodes configured bits into raw and active states.
- Indicator signals include high beam, turn signals, seat belt, and PRNDL
  switch bits. High beam, turn signals, and seat belt are active-low.
- Warning signals include ABS, alternator, air bag, DRL, MIL, park brake, and
  two spare warning inputs. These are active-low.
- `read_ads_channels()` reads ADS1115 voltage and converts it into estimated
  sender resistance.
- Fuel percent and oil pressure scale directly from sender resistance.
- Coolant temperature is interpolated from the `GM_ECT_TABLE` resistance table.
- `PulseCounter` counts falling-edge pulses for VSS and tach, calculates
  frequency over a one-second window, and reports stale pulse state.

## Derived Values

- Speed is calculated from VSS frequency using `VSS_PULSES_PER_MILE`.
- RPM is calculated from tach frequency using `TACH_PULSES_PER_REV`.
- PRNDL is decoded from four PRNDL indicator bits using `PRNDL_TABLE`.
- Derived warnings are calculated for:
  - low fuel
  - low oil pressure
  - high coolant temperature
  - stale VSS signal
  - stale tach signal

## Odometer

- `Odometer` stores distance as tenths of a mile plus remainder pulses.
- It loads and saves `/odometer.json` on the CircuitPython filesystem.
- It starts from `253000.0` miles if no valid odometer file is available.
- It periodically saves while the engine is running and saves once after the
  tach signal becomes stale following prior engine activity.

## Display

- `ClusterPage` is the main graphical display page. It shows:
  - speed
  - RPM
  - fuel percent
  - coolant temperature
  - oil pressure
  - PRNDL
  - odometer
  - indicator and warning lamps
- `TextPage` displays diagnostic pages for:
  - indicators and warnings
  - ADS1115 analog readings
  - VSS, tach, and odometer details
  - system status
- `DisplayController` switches between the graphical page and text pages.
- The main graphical page refreshes every `DISPLAY_INTERVAL`; text pages use
  `TEXT_DISPLAY_INTERVAL`.
- Garbage collection is run around page switches and text-page updates to reduce
  memory pressure on the ESP32-S3.

## Main Loop

The main loop continuously:

1. Tracks loop frequency.
2. Updates VSS and tach pulse counters.
3. Adds VSS pulses to the odometer.
4. Handles page-button debounce and page changes.
5. Polls PCF8574 inputs.
6. Polls ADS1115 analog channels.
7. Updates pulse snapshots, cluster values, derived warnings, and odometer state.
8. Saves odometer data when needed.
9. Refreshes the display at the page-specific interval.
10. Prints memory and loop-rate debug output once per second.

## Notes

- The file currently contains no WiFi, access-point, HTTP server, or laptop
  telemetry features.
- Serial JSON output via `snapshot_for_serial()` still exists but is currently
  commented out in the main loop in favor of memory and loop-rate debug prints.
