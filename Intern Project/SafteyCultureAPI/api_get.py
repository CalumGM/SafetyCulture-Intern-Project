"""
This script will get a specified audit file from SafteyCulture API and write to a JSON file in the directory
"""

import requests
import json

user = 'christopher.ordorica@my.jcu.edu.au'
pwd = 'password'
auth_url = 'https://sandpit-api.safetyculture.io/auth'
grant_type = pwd

audit_id = 'audit_f0bd28dc8f3b42ad828c23d19c0df381'  # original
# audit_id = 'audit_053b83ce721142b391c036fdc72638ff'  # modified version with failing answers
audit_url = 'https://sandpit-api.safetyculture.io/audits/' + audit_id  # Christopher Ordorica's audit

auth_data = {'username': user, 'password': pwd, 'grant_type': grant_type}
headers = {}

# get authentication
auth_response = requests.post(auth_url, data=auth_data)
auth_json = auth_response.json()
print("Authorized: " + str(auth_response), auth_response.text)

# format access_token
access_token = auth_json['token_type'] + ' ' + auth_json['access_token']
headers['Authorization'] = access_token

# retrieve json from api
response = requests.get(audit_url, headers=headers) # gets a specific audit
response_json = response.json()

print(response_json)

# create json file
try:
    f = open("retrieved_json_file.json", "xt")
except FileExistsError:
    f = open("retrieved_json_file.json", "wt")

f.write(str(json.dumps(response_json, indent=4)))

f.close()
