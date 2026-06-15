
# KITT Master Design Document
## Revision 2.0

### Project
K1500 Integrated Truck Technology (KITT)

Vehicle: 1996 Chevrolet K1500 Extended Cab
Owner: Michael Paulsen

# Executive Summary

KITT is a long-term modernization effort transforming a 1996 Chevrolet K1500 into a modular software-defined vehicle platform. The project centers around an ESP32-S3 vehicle interface controller, an Orange Pi 5 Plus vehicle control computer, a 12.3-inch digital instrument cluster, a future center touchscreen display, advanced diagnostics, HVAC automation, multimedia integration, and a future offline AI assistant.

# System Architecture

Vehicle Interface Layer
- ESP32-S3 DevKitC-1 N16
- ADS1115
- MCP23017
- FRAM
- PC837 Optocouplers

Vehicle Control Layer
- Orange Pi 5 Plus (Confirmed)

Human Interface Layer
- 12.3-inch Digital Instrument Cluster
- 10-inch Center Touchscreen (Under Evaluation)
- Voice Interface

# Dashboard System

Primary Display
- 12.3-inch LCD instrument cluster
- Speedometer
- Tachometer
- Fuel
- Oil Pressure
- Coolant Temperature
- Warnings
- Vehicle Status

Future Center Display
- HVAC
- Navigation
- Audio
- Diagnostics
- Camera Views
- AI Interaction

# Communications Architecture

Priority Order
1. Ethernet (Preferred)
2. Isolated CANBUS (Under Evaluation)
3. USB Serial (Fallback)
4. WiFi (Testing/Beta Only)

WiFi is presently used as an electrical isolation layer during development to protect the SBC from prototype hardware faults.

# Sensor Systems

Analog Inputs
- Fuel Level
- Engine Coolant Temperature
- Oil Pressure

Digital Inputs
- Left Turn
- Right Turn
- High Beam
- Fog Lamps
- Brake Warning
- Check Engine
- Alternator Warning
- Oil Warning
- Illumination

Pulse Inputs
- Vehicle Speed Sensor
- Tachometer

# Odometer System

Status: Implemented

Storage Medium
- FRAM

Method
- 400 VSS Pulses = 0.1 Mile

# HVAC System

Confirmed Hardware
- SyRen 50 Motor Controller

Planned Sensors
- Cabin Temperature
- Ambient Temperature
- Evaporator Temperature

# Audio System

Objectives
- DSP Processing
- Voice Feedback
- Navigation Prompts
- Vehicle Alerts
- 4.1 Channel System

# Camera System

Current
- Rear Camera Planning

Future
- 360 Degree Camera System
- Bird's Eye View
- Parking Assistance
- Trailer Hookup Assistance

# Artificial Intelligence System

Objectives
- Voice-First Vehicle Operation
- Diagnostics
- Navigation
- HVAC Control
- Audio Control
- Predictive Maintenance

Historical Data Analysis
The AI will compare current operating conditions against historical baselines to identify abnormal trends and developing faults.

# Confirmed Hardware

- ESP32-S3 DevKitC-1 N16
- Orange Pi 5 Plus
- ADS1115
- MCP23017
- FRAM
- PC837 Optocouplers
- SyRen 50

# Hardware Under Evaluation

- 10-inch Center Touchscreen
- CANBUS Communications
- Final Connector System
- Final Audio Hardware
- 360 Degree Camera System

# Rejected Hardware / Approaches

- Raspberry Pi as Primary SBC
- WiFi as Permanent Communications Backbone
- Fully Isolated Analog Ground Architecture

# Development Status

Implemented
- Interface PCB
- FRAM Integration
- VSS Hardware
- Tach Hardware
- Sensor Acquisition

In Progress
- Firmware Debugging
- Communications Testing
- Dashboard Software

# Documentation Policy

Authoritative Project File:
KITT_Master_Design_Document.md

Update When:
- Hardware selected
- Hardware rejected
- Architecture changes
- Major features added
- Milestones completed

Revision Format:
v2.0 Initial Master Document
v2.1 Orange Pi Confirmed
v2.2 CANBUS Added
v2.3 Center Display Selected

# Vision Statement

Create a reliable, modular, expandable vehicle computing platform capable of evolving for years while preserving the character and serviceability of the 1996 Chevrolet K1500.
