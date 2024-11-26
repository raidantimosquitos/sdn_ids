from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import subprocess
import time
import threading




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

# Define a route with a parameter  (GET just to test the API)
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/analyze")  
def analyze_existing_logs():
    """
    Endpoint to analyze a log file produced by Zeek.
    
    """
    user = "p4"

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
        subprocess.Popen(["tcpdump", "-i", "zeek2-eth0", "-s", "0", "-w", f"/home/{user}/pcap_file/tcptraffic.pcap"], cwd=pcap_dir)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start Zeek: {e.stderr}"
        )
    
    # Wait for 20 seconds to send the paquet manually and capture the traffic
    time.sleep(20)

    # Stop the tcpdump process
    try:
        subprocess.run(["pkill", "-f", "tcpdump"], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to stop tcpdump: {e.stderr}"
        )
    
    # Construct the log file path
    log_file = f"/home/{user}/log/conn.log"
    extract_file = f"/home/{user}/log/extract.csv"


    # Execute a Zeek analysing command
    try:
        result = subprocess.run(["/usr/local/zeek/bin/zeek","-C", "-r", f"/home/{user}/pcap_file/tcptraffic.pcap"],cwd=f"/home/{user}/log/", capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Zeek command failed: {e.stderr}"
        )
    
    # Check if the log file exists
    if not Path(log_file).exists():
        raise HTTPException(
            status_code=404, detail=f"The file log file {log_file} does not exist."
        )
    
    # Extract IP and occurrence using zeek-cut and save to extract.csv
    extract_top_ports("p4", "conn.log", "extract.csv")
    
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




@app.get("/analyze2")  
def analyze2_existing_logs():
    """
    Endpoint to analyze a log file produced by Zeek.
    
    """
    user = "p4"
    timeout = 20  # Temps maximum en secondes
    stop_word = "potential"  # Mot-clé à détecter

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



    def monitor_output(proc, stop_word, timeout, start_time):
        # Fonction pour lire la sortie en temps réel dans un thread séparé
        for line in iter(proc.stdout.readline, ""):
            print(line.strip())  # Affiche la sortie immédiatement
            if stop_word in line:
                proc.terminate()  # Terminer Zeek si le mot-clé est trouvé
                return {"detail": f"Zeek stopped after detecting '{stop_word}'."}
            if time.time() - start_time > timeout:
                proc.terminate()  # Timeout après 20 secondes
                raise HTTPException(
                    status_code=500,
                    detail=f"Zeek command timed out after {timeout} seconds."
                )
        return None



    # Execute a Zeek analysing command
    #zeek -i enp7s0 detect_icmp_dos_attack.zeek

    try:
        proc = subprocess.Popen(["stdbuf", "-oL", "/usr/local/zeek/bin/zeek","-i", "zeek2-eth0", f"/home/{user}/zeek_script/detect_icmp_dos_attack.zeek"],cwd=f"/home/{user}/log/",  stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        # Lire la sortie ligne par ligne jusqu'au timeout ou détection du mot-clé
          # Démarrer un thread pour surveiller la sortie de Zeek

        start_time = time.time()
        output_thread = threading.Thread(target=monitor_output, args=(proc, stop_word, timeout, start_time))
        output_thread.start()

        # Attendre que le thread se termine ou un autre événement
        output_thread.join()
        
        # Attendre que le processus Zeek se termine (en cas d'erreur ou de timeout)
        proc.wait()

        return {"detail": "Zeek command completed successfully."}

    except subprocess.TimeoutExpired:
        proc.terminate()  # Arrête la commande si le délai est dépassé
        out_put = "nothing detected"
        raise HTTPException(
            status_code=500,
            detail=f"Zeek command timed out after {timeout} seconds."
            
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Zeek command failed: {e.stderr}"
        )
    
    # Return the lines of the log file
    return JSONResponse(
        content={"status": "success", "logs": out_put}
    )
