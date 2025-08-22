# 🧭 MAGCAL - Magnetometer Calibration Tool

A CLI-based magnetometer calibration tool for embedded systems.

```
███╗   ███╗ █████╗  ██████╗  ██████╗ █████╗ ██╗     
████╗ ████║██╔══██╗██╔════╝ ██╔════╝██╔══██╗██║     
██╔████╔██║███████║██║  ███╗██║     ███████║██║     
██║╚██╔╝██║██╔══██║██║   ██║██║     ██╔══██║██║     
██║ ╚═╝ ██║██║  ██║╚██████╔╝╚██████╗██║  ██║███████╗
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝
```

## ✨ Features

- 🎨 **Beautiful CLI Interface** - Rich-powered interface with progress bars, tables, and real-time displays
- 🛰️ **Space-Grade Calibration** - Advanced ellipsoid fitting for hard + soft iron correction
- 📊 **Real-Time Monitoring** - Live data visualization during collection
- 🔄 **Auto-Reconnection** - Handles watchdog reboots seamlessly
- 📁 **Multiple Input Sources** - Serial data collection or file-based calibration
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

Just type `magcal` to see all available commands:

```bash
magcal
```

### Quick Calibration

Run a complete calibration workflow:

```bash
magcal calibrate
```

### Interactive Mode

For guided setup and configuration:

```bash
magcal interactive
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

### Examples

```bash
# Basic calibration with defaults
magcal calibrate

# Custom port and sample count
magcal calibrate --port /dev/ttyUSB0 --samples 2000

# Sphere calibration (hard iron only)
magcal calibrate --method sphere

# Custom data pattern
magcal calibrate --pattern "MAG: ([-\d.]+),([-\d.]+),([-\d.]+)"

# Monitor real-time data
magcal monitor --port /dev/ttyUSB0

# Calibrate from existing data
magcal from-file data/mag_calibration_20240101_120000.json
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

## 🔍 Troubleshooting

### No Data Being Collected
- Check serial port path with `ls /dev/tty*`
- Verify baudrate matches your device
- Ensure device is sending magnetometer data
- Check data format matches expected pattern

### Poor Calibration Quality
- Collect more samples (increase `--samples`)
- Ensure full 3D rotation during collection
- Check for electromagnetic interference
- Verify raw (unnormalized) magnetometer values

### Connection Issues
- The tool auto-reconnects on watchdog reboots
- Check USB cable and connections
- Verify device permissions: `sudo chmod 666 /dev/ttyUSB0`

## 🛠️ Development

Install in development mode:

```bash
pip install -e .
```

Run tests:

```bash
python -m pytest tests/
```

## 📝 License

MIT License - see LICENSE file for details.

---

**🧭 Happy calibrating! 🛰️**