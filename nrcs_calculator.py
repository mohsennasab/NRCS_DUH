import numpy as np

class NRCSHydrographGenerator:
    """
    Class to generate hydrographs using the NRCS Dimensionless Unit Hydrograph methodology.
    """
    
    def __init__(self):
        """Initialize the generator with default parameters"""
        # Standard NRCS dimensionless unit hydrograph parameter
        self.m = 3.7  # for standard NRCS unit hydrograph
        
        # Default watershed parameters
        self.area_mi2 = 2.0  # catchment area in square miles
        self.cn = 80  # curve number (dimensionless)
        self.avg_slope = 2.0  # average catchment slope in %
        self.S = 2.5  # potential maximum storage (mm)
        self.time_interval = 5.0  # time interval for hydrograph in minutes
        
        # Calculation method
        self.method = "CN"  # CN or S
        
        # Time parameters (will be calculated)
        self.t_lag = None
        self.tc = None
        self.tr = None
        self.Tp = None
        self.dt = None  # time step in hours
        
    def calculate_tlag(self):
        """
        Calculate time lag based on CN or S method
        Returns time lag in hours
        """
        # Convert area from square miles to km²
        area_km2 = self.area_mi2 * 2.58999
        
        # Compute hydraulic length L (meters)
        L = 1740 * (area_km2 ** 0.6)
        
        # Compute time lag based on method
        if self.method == "CN":
            self.t_lag = 1.362e-3 * ((1000 / self.cn - 9) ** 0.7) * (L ** 0.8) / np.sqrt(self.avg_slope)
        elif self.method == "S":
            self.t_lag = 1.362e-3 * ((self.S / 25.4 + 1) ** 0.7) * (L ** 0.8) / np.sqrt(self.avg_slope)
        else:
            raise ValueError("Invalid method for time lag calculation. Use 'CN' or 'S'.")
        
        return self.t_lag
        
    def calculate_time_parameters(self):
        """Calculate all time parameters based on watershed characteristics"""
        # Calculate time lag if not already done
        if self.t_lag is None:
            self.calculate_tlag()
        
        # Estimate time of concentration (tc)
        self.tc = self.t_lag / 0.6
        
        # Compute duration of rainfall excess (tr)
        self.tr = 0.133 * self.tc
        
        # Compute time to peak (Tp)
        self.Tp = 0.5 * self.tr + self.t_lag
        
        # Set time step based on user's time interval (convert from minutes to hours)
        self.dt = self.time_interval / 60.0
        
        # Verify NRCS dimensionless unit hydrograph validity
        if self.tr > 0.2 * self.tc or self.tr > 0.3 * self.Tp:
            return False, "Warning: NRCS dimensionless unit hydrograph may not be valid for these parameters"
        
        return True, "Parameters valid for NRCS dimensionless unit hydrograph"
            
    def generate_hydrograph(self, peak_flow_cfs, duration=5):
        """
        Generate the hydrograph for a given peak flow
        
        Args:
            peak_flow_cfs: Peak flow in cubic feet per second (CFS)
            duration: Duration multiple of Tp (default=5)
            
        Returns:
            time_hours: Time array in hours
            flow_m3s: Flow array in m³/s
            flow_cfs: Flow array in CFS
        """
        # Convert peak flow from CFS to m³/s
        peak_flow_m3s = peak_flow_cfs * 0.0283168
        
        # Create time array from 0 to duration*Tp with step dt
        time_hours = np.arange(0, duration * self.Tp, self.dt)
        
        # Calculate flow using gamma function
        # Q/Qp = ((t/Tp)^m) * exp(m * (1 - t/Tp))
        t_ratio = time_hours / self.Tp
        flow_ratio = np.power(t_ratio, self.m) * np.exp(self.m * (1 - t_ratio))
        
        # Set values to zero for t > duration*Tp or t/Tp > 5 (end of hydrograph)
        flow_ratio[t_ratio > 5] = 0
        
        # Scale by peak flow to get actual hydrograph
        flow_m3s = flow_ratio * peak_flow_m3s
        
        # Convert back to CFS for user convenience
        flow_cfs = flow_m3s * 35.3147
        
        return time_hours, flow_m3s, flow_cfs
    
    def get_time_parameters(self):
        """Return calculated time parameters as a dictionary"""
        return {
            'Time Lag (hr)': round(self.t_lag, 3),
            'Time of Concentration (hr)': round(self.tc, 3),
            'Rainfall Duration (hr)': round(self.tr, 3),
            'Time to Peak (hr)': round(self.Tp, 3)
        }
