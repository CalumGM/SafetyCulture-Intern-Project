import requests

TEMPLATE_ID = "template_f0dfd0f0c20c4b30800d12fa8ab3764b"


def authenticate(username, password):
    auth = {"username": username, "password": password, "grant_type": "password"}
    request_URL = "https://sandpit-api.safetyculture.io/audits/search?order=asc&archived=false&completed=both&owner=all" \
                  "&limit=1000 "
    r = requests.post('https://sandpit-api.safetyculture.io/auth', data=auth)
    access_token = r.json()['token_type'] + " " + r.json()['access_token']  # header formatting
    print("Authorisation token: " + r.json()['access_token'])
    request_header = {"Authorization": access_token}
    g = requests.get(request_URL, headers=request_header)  # HTTP request /auth
    audit_search(0, access_token)


def search_template(access_token):  # currently useless since the templates shared with me dont come under 'me'
    # search for templates created by 'me'
    owner = "me"
    request_URL = "https://sandpit-api.safetyculture.io/templates/search?order=asc&archived=false&owner=" \
                  + owner + "&limit=1000"
    request_header = {"Authorization": access_token}
    r = requests.get(request_URL, headers=request_header)  # HTTP request /templates/search
    templates = r.json()['templates']
    for index in templates:
        print(index['name'])
        if index['name'] == 'Interns2020-RealEstate-Property-Inspection':
            template_index = templates.index(index)
    try:
        template = templates[template_index]
        print(template['name'])
    except UnboundLocalError:
        print("Interns-2020-Rental-Inspection template not found")
        return
    audit_search(template['template_id'], access_token)


def audit_search(template_id, access_token):
    request_URL = "https://sandpit-api.safetyculture.io/audits/search?order=asc&template=" \
                  + TEMPLATE_ID + "&archived=false&completed=both&owner=all&limit=1000 "
    request_header = {"Authorization": access_token}
    r = requests.get(request_URL, headers=request_header)  # HTTP request /audits/search
    audits = r.json()['audits']
    for audit in audits:
        audit_lookup(audit['audit_id'], access_token)


def audit_lookup(audit_id, access_token):
    request_URL = "https://sandpit-api.safetyculture.io/audits/" + audit_id
    request_header = {"Authorization": access_token}
    r = requests.get(request_URL, headers=request_header)  # HTTP request /audits/{auditId}
    print("\n")
    print(r.json()['audit_data']['name'])
    print(r.json())
    print("\n")


def create_audit(template_id, access_token):
    request_URL = "https://sandpit-api.safetyculture.io/audits"
    request_header = {"Authorization": access_token}
    # r = requests.post(request_URL, headers=request_header,json=#file in json format .read())
    # HTTP request /audits/{auditId}


def cool_function():
    print("i hate github")


if __name__ == "__main__":
    authenticate("calum.maitland00@gmail.com", "password")
