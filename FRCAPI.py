import requests
import base64
import json


message = ""
message_bytes = message.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)
key = base64_bytes.decode('ascii')

payload={}
headers = {
  'Authorization': 'Basic '+ key,
  'If-Modified-Since': ''
}


def callFRCAPI(event, api, team, level = 0):

    torunament_level = ['Qualification', 'Playoff']
    
    endpoints = [
        "https://frc-api.firstinspires.org/v3.0/2023/matches/"+event+"?tournamentLevel="+torunament_level[level]+"&teamNumber="+str(team),
        "https://frc-api.firstinspires.org/v3.0/2023/scores/"+event+"/"+torunament_level[level]+"?teamNumber="+str(team),
        "https://frc-api.firstinspires.org/v3.0/2023/rankings/"+event+"?teamNumber="+str(team),
        "https://frc-api.firstinspires.org/v3.0/2023/rankings/district?teamNumber="+str(team)
    ]

    
    request_to_api = requests.get(endpoints[api], headers=headers, data=payload)

    response = json.loads(request_to_api.text)

    return response
