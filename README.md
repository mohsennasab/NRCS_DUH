# NRCS Dimensionless Unit Hydrograph Generator

<p align="center">
  <img src="Images/Logo.png" alt="NRCS Hydrograph Generator Logo" width="200">
</p>

## Overview

The NRCS Dimensionless Unit Hydrograph Generator is an interactive web application that creates hydrographs for different Annual Exceedance Probabilities (AEPs) using the Natural Resources Conservation Service (NRCS) Dimensionless Unit Hydrograph methodology. This tool helps hydrologists and water resources engineers quickly generate and visualize runoff hydrographs for watershed analysis and design.

## Features

- **Interactive Interface**: Clean, user-friendly Streamlit web application
- **Multiple AEPs**: Support for 10 different AEP values (1, 2, 5, 10, 25, 50, 100, 200, 500, 1000 years)
- **Versatile Calculation Methods**: Choose between CN-based or S-based time lag calculations
- **Dynamic Visualization**: Interactive Plotly charts for hydrograph visualization
- **Flexible Units**: Display results in CFS or m³/s
- **Data Export**: Export results to CSV for further analysis
- **Detailed Parameters**: View and understand all calculated time parameters

## Technical Background

This application implements the NRCS Dimensionless Unit Hydrograph methodology, which represents the average runoff response from watersheds. Key equations include:

### Time Parameters

- **Time Lag (tₗₐg)**: Can be calculated using either:
  - CN-based: `tₗₐg = 1.362×10⁻³ × [(1000/CN - 9)⁰·⁷] × [L⁰·⁸/√S₀]`
  - S-based: `tₗₐg = 1.362×10⁻³ × [(S/25.4 + 1)⁰·⁷] × [L⁰·⁸/√S₀]`
  
  where `L` is the hydraulic length in meters and `S₀` is the average catchment slope in percent.

- **Time of Concentration (tc)**: `tc = tₗₐg / 0.6`
- **Rainfall Duration (tr)**: `tr = 0.133 × tc`
- **Time to Peak (Tp)**: `Tp = 0.5 × tr + tₗₐg`

### Gamma Function for the NRCS Unit Hydrograph

The application uses the gamma function approach:

```
Q/Qp = [(t/Tp)·exp(1-t/Tp)]^m
```

where:
- `m = 3.7` for the standard NRCS unit hydrograph (configurable in the app)
- `Q` is the runoff rate at time `t`
- `Qp` is the peak runoff rate
- `Tp` is the time to peak

The application validates that the NRCS dimensionless unit hydrograph conditions are met:
`tr ≤ 0.2 × tc` or `tr ≤ 0.3 × Tp`

## Installation

### Option 1: Clone Repository

1. Clone this repository:
```bash
git clone https://github.com/mohsennasab/NRCS_DUH.git
cd NRCS_DUH
```

### Option 2: Download ZIP

1. Download the ZIP file from the GitHub repository
2. Extract the contents to a folder on your computer

### Set Up Virtual Environment (Recommended)

Creating a virtual environment ensures all dependencies are properly installed without affecting your other Python projects:

```bash
# Create a virtual environment named nrcs_duh
python -m venv nrcs_duh

# Activate the virtual environment
# On Windows:
nrcs_duh\Scripts\activate
# On Mac/Linux:
source nrcs_duh/bin/activate

# Install required packages with exact versions
pip install streamlit==1.41.1 pandas==1.5.3 numpy==1.26.4 plotly==5.15.0
```

## How to Run

### Manual Method

If the easy method doesn't work, you can run the application manually:

```bash
python run_app.py
```

Or directly with Streamlit:

```bash
streamlit run streamlit_app.py --server.port=8888
```

## Usage

1. In the sidebar, select your calculation method (CN or S)
2. Enter your watershed parameters:
   - Catchment Area (square miles)
   - Curve Number (CN) or Potential Maximum Storage (S)
   - Average Catchment Slope (%)
   - Time Interval (minutes)
   - Display units (CFS or m³/s)
3. Enter peak flows for the AEPs you want to analyze (leave others blank)
4. Click "Generate Hydrographs"
5. View your results in the three tabs:
   - **Hydrograph Plot**: Visual representation of all hydrographs
   - **Hydrograph Data**: Tabular data with download option
   - **Calculated Parameters**: Time parameters with explanations

## Project Structure

- `streamlit_app.py`: Main application file with the UI and logic
- `nrcs_calculator.py`: Core calculation module implementing the NRCS methodology
- `run_app.py`: Python launcher script to automatically start the application
- `run_app.bat`: Windows batch file for easy launching
- `run_app.sh`: Shell script for Mac/Linux users
- `Images/`: Contains the application logo and other images

## References

This implementation is based on the NRCS Dimensionless Unit Hydrograph methodology as described in:

- **NRCS Chapter 16 - Hydrographs**: [NRCS Hydrographs Manual](https://directives.nrcs.usda.gov/sites/default/files2/1720461096/Chapter%2016%20-%20Hydrographs.pdf)
- **NOAA Unit Hydrograph Manual**: [NOHRSC GIS Unit Hydrograph Manual](https://www.nohrsc.noaa.gov/technology/gis/uhg_manual.html)  

## Troubleshooting

If you encounter issues:

1. **Port in use**: The launcher will automatically try to find an available port
2. **Streamlit not found**: Make sure you have installed Streamlit (`pip install streamlit==1.41.1`)
3. **Browser doesn't open**: Manually navigate to the URL shown in the console (typically http://localhost:8888)
4. **Permission errors**: Try running as administrator (Windows) or with sudo (Mac/Linux)

## License

This project is available for educational and professional use.

## Author

Created by [Mohsen Tahmasebi Nasab, PhD](https://www.hydromohsen.com/)

---

<p align="center">© 2025 | NRCS Hydrograph Generator</p>
