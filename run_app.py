"""
NRCS Hydrograph Generator Launcher

This script automatically launches the NRCS Hydrograph Generator Streamlit app
with the correct port settings to avoid permission issues.
"""

import os
import sys
import subprocess
import webbrowser
import time
import platform
import socket

def find_available_port(start_port=8501, max_attempts=10):
    """Find an available port starting from start_port"""
    current_port = start_port
    attempts = 0
    
    while attempts < max_attempts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', current_port))
                return current_port
        except OSError:
            current_port += 1
            attempts += 1
    
    # If we couldn't find an available port in the range, return a default
    return 8888

def run_streamlit_app():
    """Run the Streamlit app with appropriate settings"""
    # Find the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Streamlit app
    app_path = os.path.join(script_dir, "streamlit_app.py")
    
    # Check if the app file exists
    if not os.path.exists(app_path):
        print(f"Error: Could not find the Streamlit app at {app_path}")
        print("Make sure 'streamlit_app.py' is in the same directory as this launcher.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Find an available port
    port = find_available_port()
    print(f"Launching NRCS Hydrograph Generator on port {port}...")
    
    # Command to run the Streamlit app
    cmd = [
        "streamlit", "run", app_path,
        "--server.port", str(port),
        "--server.address", "localhost",
        "--server.headless", "true"  # Don't automatically open browser
    ]
    
    try:
        # Start the Streamlit process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if the process is still running
        if process.poll() is None:
            # Process is running, now open browser
            url = f"http://localhost:{port}"
            print(f"Opening {url} in your default browser...")
            webbrowser.open(url)
            
            print("\nNRCS Hydrograph Generator is running!")
            print("Close this window or press Ctrl+C to stop the application.")
            
            # Keep the process running until user interrupts
            process.wait()
        else:
            # Process failed to start, get error output
            stdout, stderr = process.communicate()
            print("Error starting Streamlit app:")
            print(stderr.decode('utf-8'))
            
            # Check if streamlit is installed
            if "No such file or directory" in stderr.decode('utf-8') or "not recognized" in stderr.decode('utf-8'):
                print("\nIt looks like Streamlit might not be installed.")
                print("Try installing it with: pip install streamlit")
            
            input("Press Enter to exit...")
    
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nShutting down NRCS Hydrograph Generator...")
        process.terminate()
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    # Print welcome message
    print("=" * 60)
    print("NRCS Dimensionless Unit Hydrograph Generator Launcher")
    print("=" * 60)
    
    # Run the app
    run_streamlit_app()
