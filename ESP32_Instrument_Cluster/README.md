# ESP32 Instrument Cluster

CircuitPython digital instrument cluster for the ESP32-S3 K1500/KITT interface.

Copy `code.py` to the CircuitPython board root as `code.py`.

## Maintenance Rule

For every future change to `code.py`, add one short dated sentence to the
`# Change log:` block at the top of `code.py` before committing.

## Main Screen

- Landscape 320x240 ST7789 layout
- Large digital MPH and RPM
- Fuel, coolant temp, oil pressure, PRNDL
- Indicator/warning lamp rows
- Bottom-center digital odometer

The page button cycles from the cluster screen to diagnostic pages for
indicators, analog inputs, VSS/tach/odometer, and system status.

## Important Constants

At the top of `code.py`:

- `VSS_PULSES_PER_MILE = 4000`
- `VSS_PULSES_PER_TENTH_MILE = 400`
- `TACH_PULSES_PER_REV = 2.0`
- `ODOMETER_START_TENTHS = 2530000`
- `ODOMETER_START_REMAINDER_PULSES = 0`
- `ODOMETER_SAVE_INTERVAL_SECONDS = 60.0`

The analog sender conversions are placeholders and should be adjusted after
bench or vehicle testing.

## Odometer Storage

The odometer is stored in the MB85RC256V FRAM module at I2C address `0x50`.
The code stores two FRAM records with a magic header, sequence number, odometer
tenths, remainder pulses, and checksum, then loads the newest valid record on
startup.

`tenths` is the total completed 0.1-mile count. `remainder_pulses` is the VSS
pulse count since the last completed 0.1 mile. On startup, the app resumes from
both values so it continues toward the next tenth-mile increment.

The app saves periodically while tach is active and saves once when tach becomes
stale, which is treated as engine shutdown.
