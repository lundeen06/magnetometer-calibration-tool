```
███╗   ███╗  █████╗   ██████╗   ██████╗  █████╗  ██╗     
████╗ ████║ ██╔══██╗ ██╔════╝  ██╔════╝ ██╔══██╗ ██║     
██╔████╔██║ ███████║ ██║  ███╗ ██║      ███████║ ██║     
██║╚██╔╝██║ ██╔══██║ ██║   ██║ ██║      ██╔══██║ ██║     
██║ ╚═╝ ██║ ██║  ██║ ╚██████╔╝ ╚██████╗ ██║  ██║ ███████╗
╚═╝     ╚═╝ ╚═╝  ╚═╝  ╚═════╝   ╚═════╝ ╚═╝  ╚═╝ ╚══════╝
```
A CLI-based magnetometer calibration tool


## ✨ Features

- 🛰️ **Space-Grade Calibration** - Advanced ellipsoid fitting for hard + soft iron correction. Used for Stanford SSI's 2U Cubesat SAMWISE :)
- 📊 **Real-Time Monitoring** - Live data visualization during collection
- 📡 **Universal Serial Support** - Reads magnetic field data from any
  serial device with configurable data patterns
- 📟 **CLI Interface** - Interactive menus and command-line options for easy
   setup and operation without editing config files
- 💾 **Embedded-Ready Output** - Generates C header files for direct integration

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

## 📊 Calibration Methods

### Ellipsoid (Recommended)
- Corrects both hard iron and soft iron effects
- Accounts for sensor mounting misalignment
- Best for precision applications

### Sphere
- Simple hard iron correction (offset only)
- Faster computation
- Good for basic applications

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

## 📝 License

MIT License - see LICENSE file for details.

---

**🧭 Happy calibrating! 🛰️**