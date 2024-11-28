import requests
from datetime import datetime
import subprocess

#How to call the API

def call_api(url):
    if 'items' in url:
        params = {'q': 'test'}
        response = requests.get(url, params=params)
    else:
        response = requests.get(url)
    
    if response.status_code == 200:
        print("Success:", response.json())
        return response.json()
    else:
        print("Failed with status code:", response.status_code)

if __name__ == "__main__":
    t1 = datetime.now()
    process = subprocess.Popen(["ping", "-f", "10.0.0.2"])
    url1 = "http://10.0.0.2:8000/analyze2"
    json_message = call_api(url1)
    process.terminate()  
    process.wait()  
    if json_message and "time" in json_message:
        t2_str = json_message["time"]
        t2 = datetime.strptime(t2_str,"%Y-%m-%d %H:%M:%S.%f")
    if json_message and "IP" in json_message:
        IP = json_message["IP"]
    detection_time = (t2 - t1).total_seconds() 
    if IP!="NULL":
        print(f"Temps de detection attack : {detection_time} for the IP address: {IP}")
    else: 
        print(f"Temps de detection flow normal  : {detection_time} ")

    t1 = datetime.now()
    process = subprocess.Popen(["ping", "10.0.0.2"])
    url1 = "http://10.0.0.2:8000/analyze2"
    json_message = call_api(url1)
    process.terminate()  
    process.wait()  
    if json_message and "time" in json_message:
        t2_str = json_message["time"]
        t2 = datetime.strptime(t2_str,"%Y-%m-%d %H:%M:%S.%f")
    if json_message and "IP" in json_message:
        IP = json_message["IP"]
    detection_time = (t2 - t1).total_seconds() 
    if IP!="NULL":
        print(f"Temps de detection attack : {detection_time} for the IP address: {IP}")
    else: 
        print(f"Temps de detection flow normal  : {detection_time} ")

  
