# Future Revision Notes

- Add a one-time odometer set mode for matching the truck's actual mileage:
  `ODOMETER_FORCE_SET`, `ODOMETER_FORCE_TENTHS`, and
  `ODOMETER_FORCE_REMAINDER_PULSES`. Boot once with force set enabled to write
  the target mileage to FRAM, then disable it before normal use.
- Confirm final VSS calibration. Current default is `VSS_PULSES_PER_MILE = 4000`
  and `VSS_PULSES_PER_TENTH_MILE = 400`.
- Confirm final tach calibration. Current default is `TACH_PULSES_PER_REV = 2.0`.
- Replace placeholder fuel, oil pressure, and coolant sender conversions with
  tested sender curves.
- After hardware display testing, adjust the cluster layout for readability,
  spacing, and lamp placement on the physical ST7789 screen.
- PRNDL should display only the current gear selected as decoded by the logic
  table. Examples: when in Park display `P` or `PARK`; Reverse display `R` or
  `REV`; Overdrive/Drive display `OD` or `D`; lower gears display `3`, `2`, or
  `1`.
- Remove captions from idiot lights and odometer.
- Consider replacing text-only idiot lights with small bitmap icons once the
  main layout is proven on hardware.
