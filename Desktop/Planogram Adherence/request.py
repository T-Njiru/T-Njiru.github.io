import requests

data = {
    "planogram_id": 1,  
    "image_id": 2       
}

response = requests.post("http://127.0.0.1:5000/process", json=data)

print("Status Code:", response.status_code)
try:
    print("Response:", response.json())
except requests.exceptions.JSONDecodeError:
    print("Error: Response is not in JSON format:", response.text)
