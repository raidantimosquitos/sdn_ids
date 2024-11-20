import requests
#How to call the API

def call_api(url):
    if 'items' in url:
        params = {'q': 'test'}
        response = requests.get(url, params=params)
    else:
        response = requests.get(url)
    
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed with status code:", response.status_code)

if __name__ == "__main__":
    url1 = "http://10.0.0.2:8000/analyze"
    call_api(url1)