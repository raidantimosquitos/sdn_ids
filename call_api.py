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
    url1 = "http://127.0.0.1:8000/items/42"
    url2 = "http://127.0.0.1:8000/"
    call_api(url2)