from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import subprocess
import time
import threading
from datetime import datetime
import re




def extract_top_ports(user, log_file, extract_file):
    log_path = Path(f"/home/{user}/log/") / log_file
    extract_path = Path(f"/home/{user}/log/") / extract_file

    if not log_path.exists():
        raise FileNotFoundError(f"Log file {log_path} does not exist.")

    try:
        # Step 1: zeek-cut
        with open(log_path, "r") as infile:
            zeek_cut = subprocess.Popen(
                ["/usr/local/zeek/bin/zeek-cut", "id.resp_h"], stdin=infile, stdout=subprocess.PIPE
            )

        # Step 2: sort
        sort = subprocess.Popen(
            ["sort"], stdin=zeek_cut.stdout, stdout=subprocess.PIPE
        )

        # Step 3: uniq -c
        uniq = subprocess.Popen(
            ["uniq", "-c"], stdin=sort.stdout, stdout=subprocess.PIPE
        )

        # Step 4: sort -rn
        sort_rn = subprocess.Popen(
            ["sort", "-rn"], stdin=uniq.stdout, stdout=subprocess.PIPE
        )

        # Step 5: head -n 10
        with open(extract_path, "w") as outfile:
            subprocess.run(
                ["head", "-n", "10"],
                stdin=sort_rn.stdout,
                stdout=outfile,
                check=True
            )

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr}")

    return f"Top ports written to {extract_path}"

# Create the FastAPI application
app = FastAPI()

# Define a simple route  (GET   just to test the API)
@app.get("/")
def read_root():
    return {"message": "Welcome to my API!"}


@app.get("/analyze2")  
def analyze2_existing_logs():
    """
    Endpoint to analyze a log file produced by Zeek.
    
    """
    user = "p4"
    timeout = 3 
    stop_word = "Potential" 

    # Create directories if they don't exist
    pcap_dir = Path(f"/home/{user}/pcap_file")
    log_dir = Path(f"/home/{user}/log")
    zeek_dir = Path(f"/home/{user}/zeek_script")
    
    pcap_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    zeek_dir.mkdir(parents=True, exist_ok=True)

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
    
    
    log_file = f"/home/{user}/log/conn.log"
    extract_file = f"/home/{user}/log/extract.csv"



    def monitor_output(proc, stop_word, timeout, start_tim, result):
        for line in iter(proc.stdout.readline, ""):
            print(line.strip())  
            if stop_word in line:
                proc.terminate()  
                match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line)
                if match:
                    ip_address = match.group(1)  # Adresse IP trouvée
                result.append('Floating attack detected')
                result.append(ip_address)
                return "Floating attack detected"
                
            if time.time() - start_time > timeout:
                proc.terminate()  
                result.append('OK')
                result.append('NULL')
                raise HTTPException(
                    status_code=500,
                    detail=f"Zeek command timed out after {timeout} seconds."
                )
                return "nothing found"




    try:
        result= []
        proc = subprocess.Popen(["stdbuf", "-oL", "/usr/local/zeek/bin/zeek","-i", "zeek2-eth0", f"/home/{user}/zeek_script/detect_icmp_dos_attack.zeek"],cwd=f"/home/{user}/log/",  stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)

        start_time = time.time()
        output_thread = threading.Thread(target=monitor_output, args=(proc, stop_word, timeout, start_time,result))
        output_thread.start()

        output_thread.join()
        
        proc.wait()

    except subprocess.TimeoutExpired:
        proc.terminate()  
        raise HTTPException(
            status_code=500,
            detail=f"Zeek command timed out after {timeout} seconds."
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Zeek command failed: {e.stderr}"
        )
    
    return JSONResponse(
        content={"status": "success", "result": result[0],"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),"IP":result[1]}
    )
