import requests

url = 'http://localhost:5000/api/task'
myobj = {'data': 'd6a63c444cf80fd218ff9b665948ce5250ba97ad3d4d189e2b48adafd5f09b9f'}

x = requests.post(url, json = myobj)

print(x.text)
