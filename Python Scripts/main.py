import requests


username = "calum.maitland00@gmail.com"
password = "password"
auth = {"username": username, "password": password, "grant_type": "password"}
request_URL = "https://sandpit-api.safetyculture.io/audits/search?order=asc&archived=false&completed=both&owner=all" \
              "&limit=1000 "

r = requests.post('https://sandpit-api.safetyculture.io/auth', data=auth)
access_token = r.json()['token_type'] + " " + r.json()['access_token']  # header formatting
print("Authorisation token: " + r.json()['access_token'])
request_header = {"Authorization": access_token}
g = requests.get(request_URL, headers=request_header)  # HTTP request /auth
count = g.json().get('count')
audits = g.json().get('audits')  # list of every audit

for audit in audits:  # read data from each audit
    audit_id = audit['audit_id']
    request_URL = "https://sandpit-api.safetyculture.io/audits/" + audit_id
    g = requests.get(request_URL, headers=request_header)  # HTTP request /audits/{auditId}
    print(g.json()['audit_data'])
    break
print("\n\n")

request_URL = "https://sandpit-api.safetyculture.io/templates/search?order=asc&archived=false&owner=all&limit=1000"
g = requests.get(request_URL, headers=request_header)  # HTTP request /templates/search
print(g.status_code)