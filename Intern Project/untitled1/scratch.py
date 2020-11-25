import json
import requests as requests

user = 'timothy.walsh@my.jcu.edu.au'
pwd = 'password'
grant_type = 'password'

headers = {}
params = {}

# Request Auth Token
url = 'https://sandpit-api.safetyculture.io/auth'
auth_request = requests.post(url, data={'username': user, 'password': pwd, 'grant_type': 'password'})
auth_json = auth_request.json()
print('Authorized: ' + str(auth_request), auth_request.text)
access_token = auth_json['token_type'] + " " + auth_json['access_token']
headers['Authorization'] = access_token
headers['Content-Type'] = 'application/json; charset=utf-8'

# Request Data
# url = 'https://sandpit-api.safetyculture.io/audits/search?order=asc&archived=false&completed=both&owner=all&limit=50'
#
# audit_list_response = requests.get(url, headers=headers)
# audit_list_json = audit_list_response.json()
#
# # for item in audit_list_json.keys():
# #     print(item,audit_list_json[item])
# audits = audit_list_json['audits']
#
# for audit in audits:
#     url_audit = 'https://sandpit-api.safetyculture.io/audits/'+audit['audit_id']
#     audit_response = requests.get(url_audit, headers=headers)
#     audit_response_json = audit_response.json()
#     data_json = json.loads(audit_response.text)
#     print()
#     print("########### ",str(audit['audit_id'])," ##########")
#     print("modified: ", data_json['modified_at'])
#     print("\n items \n",data_json['items'])
#     print("\n data \n",data_json['audit_data'])
