# WMM Declination Calculator
Desktop calculator for magnetic declination at a chosen location and date,
using the World Magnetic Model (WMM) via [pygeomag](https://github.com/boxpet/pygeomag).

## Features
- Location input as UTM (easting, northing, zone, hemisphere) or latitude/longitude
- Date selection by year / month / day dropdowns
- Valid range: **2019-12-31** to **2029-12-31** (WMM-2020 / WMM-2025)
- Time is treated as **00:00** on the selected day
- Map figure with declination, uncertainty, and magnetic-north compass

## Requirements
- Python 3.10+
- See `requirements.txt` (`numpy`, `pandas`, `matplotlib`, `pyproj`, `pygeomag`, `cartopy`)
Internet access is needed for the shaded-relief basemap tiles when calculating.

## Setup
```powershell
cd "path\to\WMM declination calculator"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt