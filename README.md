# MAGCAL - Magnetometer calibration python tool for robotics, drones, satellites, and embedded systems

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/magcal.svg)](https://badge.fury.io/py/magcal)

```
███╗   ███╗  █████╗   ██████╗   ██████╗  █████╗  ██╗     
████╗ ████║ ██╔══██╗ ██╔════╝  ██╔════╝ ██╔══██╗ ██║     
██╔████╔██║ ███████║ ██║  ███╗ ██║      ███████║ ██║     
██║╚██╔╝██║ ██╔══██║ ██║   ██║ ██║      ██╔══██║ ██║     
██║ ╚═╝ ██║ ██║  ██║ ╚██████╔╝ ╚██████╗ ██║  ██║ ███████╗
╚═╝     ╚═╝ ╚═╝  ╚═╝  ╚═════╝   ╚═════╝ ╚═╝  ╚═╝ ╚══════╝
```

**Magnetometer calibration CLI tool using ellipsoid correction for robotics, drones, satellites, and other critical embedded systems. Originally developed in python for Stanford SSI's satellite SAMWISE for attitude determination.**

## Why MAGCAL?

If you're working with magnetometers, you know the pain. Your compass readings are off by 30 degrees. Your drone's heading is all over the place. Your satellite's attitude determination is unreliable. Sound familiar?

The problem? **Magnetic interference**. Your magnetometer isn't just measuring Earth's magnetic field - it's also picking up interference from batteries, motors, metal frames, and anything else magnetic nearby.

MAGCAL fixes this. We use ellipsoid fitting (the gold standard for magnetometer calibration) to remove both hard iron and soft iron distortions. The result? Accurate, reliable magnetic field measurements you can actually trust.

## What can you use it for?

- **Satellites & Cubesats** - Get accurate attitude determination (like we did for Stanford SSI's SAMWISE)
- **Drones & UAVs** - Fix that wonky compass behavior once and for all
- **Marine navigation** - Reliable compass readings for boats and ships
- **Robotics** - Dead reckoning and navigation that actually works
- **Research** - Precise magnetometer data for scientific applications
- **IoT devices** - Any embedded system that needs to know which way is north

Works with pretty much any 3-axis magnetometer: RM3100, HMC5883L, MPU9250, LSM9DS1, QMC5883, MMC5983MA, BMM150, AK8963, you name it. If your microcontroller can output over serial, this tool is for you. 

## How it works

1. **Connect your magnetometer** - Plug in via serial/USB (Arduino, Raspberry Pi, Pico, Feather, etc.)
2. **Run the calibration** - Just type `magcal` and follow the prompts
3. **Wave it around** - Rotate your device through all orientations while it collects data
4. **Get results** - MAGCAL spits out calibration parameters as a C header file
5. **Integrate** - Drop the calibration into your firmware and you're done

## Features

- **Real-time visualization** - Watch your data points form a sphere as you collect them
- **Professional algorithms** - Ellipsoid fitting that actually works (not some hack from Stack Overflow)
- **Easy integration** - Generates clean C header files for embedded projects  
- **Quality metrics** - Know if your calibration is good or if you need more data
- **Works everywhere** - Any magnetometer with serial output, any platform
- **Beautiful CLI** - No config files to mess with, just an interactive menu that makes sense

## 🚀 Quick Start

### Installation

Clone and install the package:

```bash
git clone <repository-url>
cd magcal
pip install -e .
```

### Basic Usage

Just type `magcal` to launch the interactive menu:

```bash
magcal
```

This will show you a beautiful menu with all available options - perfect for getting started quickly!

### Direct Commands

You can also use specific commands directly:

```bash
magcal calibrate     # Run calibration with default settings
magcal interactive   # Guided configuration mode
magcal monitor       # Real-time data monitoring
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `magcal` | Show help and available commands |
| `magcal calibrate` | Run complete calibration workflow |
| `magcal interactive` | Interactive configuration mode |
| `magcal from-file <file>` | Calibrate from existing data file |
| `magcal monitor` | Real-time data monitoring |

## ⚙️ Command Options

### `magcal calibrate`

```bash
magcal calibrate [OPTIONS]

Options:
  -p, --port TEXT        Serial port path [default: /dev/tty.usbmodem101]
  -b, --baudrate INTEGER Serial baudrate [default: 115200]
  -n, --samples INTEGER  Number of samples to collect [default: 1000]
  -m, --method [sphere|ellipsoid] Calibration method [default: ellipsoid]
  --pattern TEXT         Custom regex pattern for data parsing
  --no-plot             Disable real-time plotting
```

## 🔧 Prerequisites

Before running calibration:

1. **Hardware Setup**
   - Connect your magnetometer to the computer via serial
   - Ensure the device is powered and sending data

2. **Firmware Preparation**
   - Modify your embedded firmware to send **raw** magnetometer values
   - Comment out any normalization in your magnetometer driver
   - Flash the updated firmware

3. **Data Format**
   - Default expected format: `Magnetometer reading: [x, y, z]`
   - Values should be in µT (microTesla) units
   - Use `--pattern` option for custom formats

## 🤔 Why Calibrate Your Magnetometer?

**Uncalibrated magnetometers suffer from:**
- **Hard iron distortion** - Permanent magnetic fields from nearby ferrous materials, motors, batteries
- **Soft iron distortion** - Induced magnetic fields in ferrous materials that vary with orientation  
- **Scale factor errors** - Different sensitivities on X, Y, Z axes
- **Misalignment errors** - Sensor mounting angles affecting measurements
- **Temperature drift** - Magnetic properties changing with temperature

**Results without calibration:**
- ❌ Inaccurate compass heading (can be off by 30-180°)
- ❌ Poor attitude determination in satellites
- ❌ Unreliable navigation in drones/vehicles  
- ❌ Failed magnetometer-based applications

**Results after calibration:**
- ✅ Sub-degree heading accuracy
- ✅ Reliable magnetic field measurements
- ✅ Professional-grade sensor performance
- ✅ Successful deployment in real applications

## 📊 Calibration Methods

### Ellipsoid Fitting (Recommended)
- Corrects both hard iron and soft iron effects
- Accounts for sensor mounting misalignment and scale factors
- Industry standard for aerospace and precision applications
- Generates 3x3 transformation matrix + offset vector

### Sphere Fitting  
- Simple hard iron correction (offset only)
- Faster computation for basic applications
- Good when soft iron effects are minimal

## 📁 Output Files

Calibration generates files in the `output/` directory:

- **`mag_calibration_YYYYMMDD_HHMMSS.json`** - Raw collected data
- **`mag_calibration_YYYYMMDD_HHMMSS.h`** - C header file with calibration parameters

### Using Generated Files

Include the header file in your embedded project:

Example: 
```c
#include "mag_calibration_20240101_120000.h"

// Apply calibration
float3 raw_reading = get_magnetometer_reading();
float3 corrected = raw_reading - MAG_HARD_IRON_OFFSET;
float3 calibrated = MAG_SOFT_IRON_MATRIX * corrected;
```

## 🎯 Quality Assessment

The tool provides quality metrics:

- **Sphericity**: Higher is better (max 1.0 for perfect sphere)
- **Quality Score**: Lower is better (< 0.05 is excellent)

| Score | Assessment |
|-------|------------|
| < 0.05 | 🟢 Excellent |
| < 0.10 | 🟡 Good |
| < 0.20 | 🟠 Fair |
| ≥ 0.20 | 🔴 Poor - collect more data |

## 🔧 Troubleshooting & FAQ

### Common Calibration Issues

**Q: My compass/magnetometer readings are still inaccurate after calibration**
- Ensure you collected data while rotating the sensor through ALL orientations (full 3D sphere)
- Check for strong magnetic interference sources nearby during calibration
- Verify your device outputs RAW magnetometer values (not normalized/filtered)

**Q: How to calibrate HMC5883L / MPU9250 / LSM9DS1 magnetometer?**  
- Use MagCal with the appropriate data pattern for your sensor's output format
- Most sensors work with default settings, just specify your serial port

**Q: Calibration quality is poor (high error scores)**
- Collect more data points (try 2000+ samples instead of 1000)
- Ensure smooth, complete rotation through all orientations
- Remove or move away from magnetic interference sources

**Q: How to integrate calibration into Arduino/embedded firmware?**
- Use the generated `.h` header file - it contains the calibration matrix and offset
- Apply: `calibrated = (raw - offset) * transformation_matrix`

**Q: What's the difference between hard iron and soft iron calibration?**
- **Hard iron**: Fixed magnetic offsets (like from a nearby magnet)
- **Soft iron**: Variable magnetic distortion that changes with orientation
- Most applications need BOTH corrections (use ellipsoid method)

## 📝 License

MIT License - see LICENSE file for details.

---

**🧭 Happy calibrating! 🛰️**