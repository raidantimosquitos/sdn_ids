from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import subprocess
import time

# Create the FastAPI application
app = FastAPI()

# Define a simple route
@app.get("/")
def read_root():
    return {"message": "Welcome to my API!"}

# Define a route with a parameter
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# Path where Zeek stores analysis files
ZEEK_LOG_DIR = "zeek_output"

@app.get("/analyze")
def analyze_existing_logs(log_type: str = "conn"):
    """
    Endpoint to analyze a log file produced by Zeek.
    :param log_type: Type of Zeek log to read (default: 'conn').
    """
    user = "p4"
    # Change directory to Zeek installation and start Zeek
    try:
        subprocess.run(["sudo", "zeekctl", "start"], cwd=f"/usr/local/zeek/zeek_install/bin", check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start Zeek: {e.stderr}"
        )
    
    # Create directories if they don't exist
    pcap_dir = Path(f"/home/{user}/pcap_file")
    log_dir = Path(f"/home/{user}/log")
    
    pcap_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    #cleaning old files
    tcpdump_file = Path(f"/home/{user}/pcap_file/tcptraffic.pcap")
    if tcpdump_file.exists():
        tcpdump_file.unlink()
    log_file = Path(f"/home/{user}/log/conn.log")
    if log_file.exists():
        log_file.unlink()
    extract_file = Path(f"/home/{user}/pcap_file/extract.csv")
    if extract_file.exists():
        extract_file.unlink()
    
    # Change directory and listen to the Zeek logs
    try:
        subprocess.Popen(["tcpdump", "-i", "zeek2-eth0", "-s", "0", "-w", "tcptraffic.pcap"], cwd=f"/home/{user}/pcap_file/")
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start Zeek: {e.stderr}"
        )
    
    # Wait for 15 seconds to send the paquet manually and capture the traffic
    time.sleep(15)


    # Stop the tcpdump process
    try:
        subprocess.run(["pkill", "-f", "tcpdump"], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to stop tcpdump: {e.stderr}"
        )

    # Execute a Zeek analysing command
    try:
        result = subprocess.run(["zeek","-C", "-r", f"/home/{user}/pcap_file/tcptraffic.pcap"],cmd=f"/home/{user}/log/", capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Zeek command failed: {e.stderr}"
        )
    # Construct the log file path
    log_file = f"/home/{user}/log/conn.log"
    extract_file = f"/home/{user}/log/extract.csv"

    # Check if the log file exists
    if not log_file.exists():
        raise HTTPException(
            status_code=404, detail=f"The file log file {log_file} does not exist."
        )
    




    # Extract IP and occurrence using zeek-cut and save to extract.csv
    try:
        extract_command = (
            f"zeek-cut id.resp_p < {log_file} | "
            f"sort | uniq -c | sort -rn | head -n 10 > {extract_file}"
        )
        subprocess.run(extract_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to extract data: {e.stderr}"
        )
    
    # Read the content of the log file
    try:
        with open(extract_file, "r") as f:
            extract_content = f.readlines()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading the extract file: {str(e)}"
        )

    # Return the lines of the log file
    return JSONResponse(
        content={"status": "success", "logs": extract_content}
    )
