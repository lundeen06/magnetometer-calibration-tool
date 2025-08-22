# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python magnetometer calibration tool for satellite/embedded systems. The repository contains a single module (`core.py`) that provides comprehensive magnetometer calibration capabilities for correcting hard iron and soft iron effects.

## Required Dependencies

Install the following Python packages before running the calibration script:

```bash
pip install numpy scipy matplotlib pyserial
```

## Running the Calibration

The main script can be executed directly:

```bash
python3 core.py
```

Before running calibration, you must:
1. Modify `src/drivers/magnetometer.cpp` in your embedded firmware
2. Comment out the normalization line in `rm3100_get_reading()`
3. Flash the updated firmware to get raw magnetometer values

## Architecture

### Core Class: MagnetometerCalibrator

Located in `core.py:13`, this class handles the complete calibration workflow:

**Data Collection** (`core.py:94`):
- Connects to magnetometer via serial (default: `/dev/tty.usbmodem101` at 115200 baud)
- Auto-reconnects on watchdog reboots
- Real-time 3D visualization during collection
- Collects minimum 1000 samples (configurable)

**Calibration Methods** (`core.py:259`):
- **Sphere fit** (`core.py:187`): Hard iron correction only (offset correction)
- **Ellipsoid fit** (`core.py:213`): Hard + soft iron correction (offset + scaling/rotation)

**Output Generation** (`core.py:336`):
- Generates C header files with calibration parameters
- Compatible with embedded systems (float3, float3x3 format)
- Includes quality metrics and documentation

### Key Methods

- `collect_data()`: Serial data collection with real-time plotting
- `calibrate(method='ellipsoid')`: Performs calibration using specified method
- `apply_calibration()`: Applies calibration to raw readings
- `save_calibration()`: Exports calibration as C header file

### Data Flow

1. Raw magnetometer data collection via serial
2. 3D visualization for data quality assessment
3. Calibration parameter computation (sphere or ellipsoid fitting)
4. Quality evaluation using sphericity metrics
5. C header file generation for embedded integration

### File Structure

- `core.py`: Complete magnetometer calibration implementation
- `output/`: Directory for generated calibration files and data dumps (created automatically)

### Expected Data Format

The script expects serial input matching this regex pattern:
```
Magnetometer reading: \[([-\d.]+), ([-\d.]+), ([-\d.]+)\]
```

This corresponds to raw magnetometer readings in µT units.