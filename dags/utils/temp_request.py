import requests

url = "https://www.arbeitnow.com/api/job-board-api"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)