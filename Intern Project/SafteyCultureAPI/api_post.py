"""
This script will take a JSON file from the local directory and upload it through SafteyCulture's API
"""

import requests

user = 'christopher.ordorica@my.jcu.edu.au'
pwd = 'password'
auth_url = 'https://sandpit-api.safetyculture.io/auth'
grant_type = pwd

template_id = 'audit_f0bd28dc8f3b42ad828c23d19c0df381'

auth_data = {'username': user, 'password': pwd, 'grant_type': grant_type}
headers = {}

# get authentication
auth_response = requests.post(auth_url, data=auth_data)
auth_json = auth_response.json()
print("Authorized: " + str(auth_response), auth_response.text)

# format access_token
access_token = auth_json['token_type'] + ' ' + auth_json['access_token']
headers['Authorization'] = access_token

# open JSON file
f = open('after.json', 'rt')
post_audit = requests.post('https://sandpit-api.safetyculture.io/audits', headers=headers, json=f.read())
print(post_audit.status_code)
f.close()
