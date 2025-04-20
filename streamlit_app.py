import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
import io
from datetime import datetime
import os
import sys

# Import the NRCS calculator from the same directory
from nrcs_calculator import NRCSHydrographGenerator

def generate_csv_download_link(df, filename):
    """Generate a link to download the dataframe as a CSV file"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

def main():
    # Configure the page with a specific port to avoid permission issues
    # Note: We don't need to set this here as it's handled with command line arguments
    st.set_page_config(
        page_title="NRCS Hydrograph Generator", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("NRCS Dimensionless Unit Hydrograph Generator")
    st.markdown("""
    This application generates hydrographs for different Annual Exceedance Probabilities (AEPs) 
    using the NRCS Dimensionless Unit Hydrograph methodology. Enter watershed parameters and peak flows 
    to generate corresponding hydrographs.
    """)
    
    # Use st.expander to create a collapsible container with instructions
    with st.expander("How to use this application"):
        st.markdown("""
        1. **Select calculation method**: Choose between CN-based or S-based method for time lag calculation
        2. **Enter watershed parameters**: Fill in the required fields in the sidebar
        3. **Enter peak flows**: Input peak flows (in CFS) for the AEPs you want to analyze (leave others blank)
        4. **Generate hydrographs**: Click the button to calculate and display results
        5. **View results**: Explore the plot, data table, and calculated parameters in the tabs below
        6. **Export data**: Download the hydrograph data as a CSV file
        """)
    
    # Create sidebar for inputs
    with st.sidebar:
        st.header("Calculation Settings")
        
        # Select calculation method
        calc_method = st.radio(
            "Select time lag calculation method:",
            ["CN", "S"],
            help="Choose whether to calculate time lag using Curve Number (CN) or potential maximum storage (S)"
        )
        
        st.header("Watershed Parameters")
        
        # Input watershed parameters
        area = st.number_input(
            "Catchment Area (square miles)", 
            min_value=0.1, 
            value=2.0, 
            step=0.1,
            help="Watershed area in square miles"
        )
        
        # Parameters based on selected method
        if calc_method == "CN":
            cn = st.number_input(
                "Curve Number (CN)", 
                min_value=30, 
                max_value=100, 
                value=80, 
                step=1,
                help="NRCS Curve Number representing soil and land cover characteristics"
            )
        else:  # S method
            s_value = st.number_input(
                "Potential Maximum Storage (mm)", 
                min_value=0.1, 
                value=2.5, 
                step=0.1,
                help="Potential maximum storage in millimeters"
            )
        
        avg_slope = st.number_input(
            "Average Catchment Slope (%)", 
            min_value=0.1, 
            value=2.0, 
            step=0.1,
            help="Average slope of the watershed in percent"
        )
        
        time_interval = st.number_input(
            "Time Interval (minutes)", 
            min_value=1, 
            value=5, 
            step=1,
            help="Time interval for hydrograph calculations in minutes"
        )
        
        m_value = st.number_input(
            "m Parameter", 
            min_value=1.0, 
            value=3.7, 
            step=0.1,
            help="Parameter for gamma function (3.7 for standard NRCS hydrograph)"
        )
        
        # Display units selection
        display_units = st.radio(
            "Display units:",
            ["CFS", "m³/s"], 
            index=0,
            help="Choose units for displaying hydrograph results"
        )
        
        st.header("Peak Flows for AEPs (CFS)")
        
        # AEP values
        aep_values = [1, 2, 5, 10, 25, 50, 100, 200, 500, 1000]
        
        # Create two columns for AEP inputs to save space
        col1, col2 = st.columns(2)
        
        # Dictionary to store peak flow values
        peak_flows = {}
        
        # Create input fields for each AEP
        for i, aep in enumerate(aep_values):
            if i % 2 == 0:
                peak_flows[aep] = col1.text_input(f"{aep} year AEP", key=f"aep_{aep}")
            else:
                peak_flows[aep] = col2.text_input(f"{aep} year AEP", key=f"aep_{aep}")
        
        # Generate button
        generate_button = st.button("Generate Hydrographs", type="primary")
    
    # Main content area
    # Create three tabs - one for plot, one for data, and one for parameters
    tab1, tab2, tab3 = st.tabs(["Hydrograph Plot", "Hydrograph Data", "Calculated Parameters"])
    
    # Initialize variables to store results
    if 'hydrographs_df' not in st.session_state:
        st.session_state.hydrographs_df = None
    
    if 'parameters' not in st.session_state:
        st.session_state.parameters = None
    
    # Process when generate button is clicked
    if generate_button:
        try:
            # Initialize the NRCS hydrograph generator
            generator = NRCSHydrographGenerator()
            
            # Update generator parameters
            generator.area_mi2 = area
            generator.avg_slope = avg_slope
            generator.time_interval = time_interval
            generator.m = m_value
            generator.method = calc_method
            
            # Set method-specific parameters
            if calc_method == "CN":
                generator.cn = cn
            else:  # S method
                generator.S = s_value
            
            # Calculate time parameters
            valid, message = generator.calculate_time_parameters()
            
            if not valid:
                st.warning(message)
            
            # Dictionary to store processed peak flows
            valid_peak_flows = {}
            
            # Process peak flows input
            for aep in aep_values:
                peak_flow_str = peak_flows[aep].strip()
                if peak_flow_str:  # Only process if there's a value
                    try:
                        valid_peak_flows[aep] = float(peak_flow_str)
                    except ValueError:
                        st.error(f"Invalid peak flow value for {aep} year AEP. Please enter a number.")
            
            # If no valid peak flows, show message
            if not valid_peak_flows:
                st.error("No valid peak flows provided. Please enter at least one peak flow value.")
            else:
                # Dictionary to store hydrograph data
                time_series = None
                flow_series = {}
                
                # Generate hydrographs for each AEP with valid peak flow
                for aep, peak_flow_cfs in valid_peak_flows.items():
                    time_hours, flow_m3s, flow_cfs = generator.generate_hydrograph(peak_flow_cfs)
                    
                    # Store the time series (should be the same for all hydrographs)
                    if time_series is None:
                        time_series = time_hours
                    
                    # Store flow series
                    flow_series[aep] = {
                        'flow_m3s': flow_m3s,
                        'flow_cfs': flow_cfs
                    }
                
                # Create DataFrame for hydrograph data
                df = pd.DataFrame({'Time(hr)': time_series})
                
                # Add flow data for each AEP
                for aep, data in flow_series.items():
                    df[f"{aep}yr_Flow(CFS)"] = data['flow_cfs']
                    df[f"{aep}yr_Flow(m3/s)"] = data['flow_m3s']
                
                # Store in session state
                st.session_state.hydrographs_df = df
                
                # Calculated parameters
                st.session_state.parameters = generator.get_time_parameters()
                
                # Display the plot in tab1
                with tab1:
                    # Determine which units to display based on sidebar selection
                    if display_units == "CFS":
                        y_column_suffix = "Flow(CFS)"
                        y_axis_title = "Discharge (CFS)"
                    else:  # m³/s
                        y_column_suffix = "Flow(m3/s)"
                        y_axis_title = "Discharge (m³/s)"
                    
                    # Create Plotly figure
                    fig = go.Figure()
                    
                    # Add trace for each AEP
                    for aep in valid_peak_flows.keys():
                        fig.add_trace(go.Scatter(
                            x=df['Time(hr)'],
                            y=df[f"{aep}yr_{y_column_suffix}"],
                            mode='lines',
                            name=f"{aep} year AEP"
                        ))
                    
                    # Update layout
                    fig.update_layout(
                        title="NRCS Dimensionless Unit Hydrographs",
                        xaxis_title="Time (hours)",
                        yaxis_title=y_axis_title,
                        template="plotly_white",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # Display figure
                    st.plotly_chart(fig, use_container_width=True)
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    # Display hydrograph data if available
    if st.session_state.hydrographs_df is not None:
        # Display the data in tab2
        with tab2:
            # Option to show only specific columns
            units = st.radio("Select units to display:", ["CFS", "m³/s", "Both"], horizontal=True)
            
            # Filter columns based on selection
            df_display = st.session_state.hydrographs_df.copy()
            
            if units == "CFS":
                # Keep only Time and CFS columns
                cols_to_keep = ['Time(hr)'] + [col for col in df_display.columns if 'CFS' in col]
                df_display = df_display[cols_to_keep]
            elif units == "m³/s":
                # Keep only Time and m3/s columns
                cols_to_keep = ['Time(hr)'] + [col for col in df_display.columns if 'm3/s' in col]
                df_display = df_display[cols_to_keep]
            
            # Display the data
            st.dataframe(df_display, use_container_width=True)
            
            # Generate download link
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"NRCS_Hydrographs_{timestamp}.csv"
            st.markdown(generate_csv_download_link(st.session_state.hydrographs_df, filename), unsafe_allow_html=True)
            st.write(f"Click the link above to download the hydrograph data as a CSV file.")
        
        # Display calculated parameters in tab3
        with tab3:
            # Display parameters
            if st.session_state.parameters is not None:
                params_df = pd.DataFrame(list(st.session_state.parameters.items()), columns=['Parameter', 'Value'])
                st.table(params_df)
                
                # Add explanation
                st.markdown("""
                ### Explanation of Parameters:
                
                - **Time Lag (hr)**: Time from the centroid of rainfall excess to the hydrograph peak. Calculated using the equation:
                  
                  t_lag = 1.362 × 10⁻³ × [(1000/CN - 9)⁰·⁷] × [L⁰·⁸/√S₀] (CN method)
                  
                  t_lag = 1.362 × 10⁻³ × [(S/25.4 + 1)⁰·⁷] × [L⁰·⁸/√S₀] (S method)
                  
                  where L is the hydraulic length in meters and S₀ is the average catchment slope in percent.
                
                - **Time of Concentration (hr)**: The time required for runoff to travel from the hydraulically most distant point to the outlet of the watershed. Calculated as:
                  
                  tc = t_lag / 0.6
                
                - **Rainfall Duration (hr)**: Duration of effective rainfall. Calculated as:
                  
                  tr = 0.133 × tc
                
                - **Time to Peak (hr)**: Time from the beginning of the hydrograph to the peak. Calculated as:
                  
                  Tp = 0.5 × tr + t_lag
                
                The NRCS dimensionless unit hydrograph is valid when:
                tr ≤ 0.2 × tc   or   tr ≤ 0.3 × Tp
                """)

if __name__ == "__main__":
    main()