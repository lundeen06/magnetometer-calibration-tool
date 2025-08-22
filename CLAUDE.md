# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python magnetometer calibration tool for satellite/embedded systems. The repository is now a complete Python package with a beautiful CLI interface built using Rich and questionary for an exceptional user experience.

## Installation

Install the package in development mode:

```bash
pip install -e .
```

This installs all dependencies: numpy, scipy, matplotlib, pyserial, rich, click, questionary

## Running the Tool

### Interactive Menu (Recommended)

Simply run the main command to access the interactive menu:

```bash
magcal
```

This provides a beautiful menu-driven interface with arrow-key navigation.

### Direct Commands

You can also use specific commands directly:

```bash
magcal calibrate --pattern "Magnetometer: [\x, \y, \z]"
magcal monitor --pattern "MAG: x=\x y=\y z=\z"
magcal from-file data.json
```

### First-Time Setup

First-time users are automatically guided through setup. The tool saves all configuration to `~/.magcal_config.json` for future use.

## Data Format Configuration

**IMPORTANT**: You must specify your device's data format using the simple pattern system:

- Use `\x`, `\y`, `\z` as placeholders for numbers
- Examples:
  - Device output: `Magnetometer: [1.23, 4.56, 7.89]`
  - Pattern: `Magnetometer: [\x, \y, \z]`
  - Device output: `MAG: x=1.23 y=4.56 z=7.89`
  - Pattern: `MAG: x=\x y=\y z=\z`

## Preparation Steps

Before running calibration:
1. Connect your magnetometer via serial
2. Ensure device sends RAW magnetometer values (not normalized)
3. Know your serial port and baudrate
4. Have your data format pattern ready

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