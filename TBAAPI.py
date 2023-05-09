import requests
import json


payload = {}
headers = {
  'Accept': 'application/json',
  'X-TBA-Auth-Key': ''
}




def callTBAAPI(team):

    url = "https://www.thebluealliance.com/api/v3/team/frc"+str(team)+"/events/2023"

    response_from_api = requests.request("GET", url, headers=headers, data=payload)

    response = response_from_api.json()

    return response
