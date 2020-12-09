"""
Gets audits from database with specific template ID then puts them into local MongoDB
"""

import pymongo
import requests
import datetime

USER = 'christopher.ordorica@my.jcu.edu.au'
PWD = 'password'
AUTH_URL = 'https://sandpit-api.safetyculture.io/auth'
GRANT_TYPE = PWD

TEMPLATE_ID = 'template_f0dfd0f0c20c4b30800d12fa8ab3764b'
TEMPLATE_SEARCH_URL = f"https://sandpit-api.safetyculture.io/audits/search?order=asc&template={TEMPLATE_ID}&archived=false&completed=both&owner=all&limit=1000"

DATABASE_URL = "mongodb+srv://calum_maitland:InternDatabase@cluster0.qg16e.mongodb.net/RealEstateData?retryWrites=true&w=majority"

auth_data = {'username': USER, 'password': PWD, 'grant_type': GRANT_TYPE}
headers = {}
audit_data_list = []


def main():
    """main does main things"""
    authenticate()
    db_client, db_col = db_connect()
    x = int(db_col.estimated_document_count())
    if x > 0:  # if db has documents
        # execute code that adds all new audits
        url = get_datetime()
    else:
        # execute code that adds all audits
        url = TEMPLATE_SEARCH_URL
    db_col.drop()  # erase collection so that next script doesnt get confused, poor baby
    audit_list = retrieve_audit_ids(url)
    retrieve_audit_data(audit_list)
    write_to_db(db_col)
    close_db(db_client)


def authenticate():
    """Authenticate user credentials and create header for API requests"""
    print("Authenticating...")
    auth_response = requests.post(AUTH_URL, data=auth_data)
    auth_json = auth_response.json()
    # format access token
    access_token = auth_json['token_type'] + ' ' + auth_json['access_token']
    headers['Authorization'] = access_token
    print("...Authenticated")


def retrieve_audit_ids(url):
    """Use a pre-determined template_id to find any audits made from that template"""
    print("Getting template...")
    template_search = requests.get(url, headers=headers).json()
    audit_list = template_search["audits"]
    if template_search["total"] >= 1001:  # greater than 1000
        for i in range(round(float(template_search["total"])/1000)-1):  # accounts for first request
            last_date = audit_list[-1]["modified_at"]
            template_search = requests.get(f"https://sandpit-api.safetyculture.io/audits/search?order=asc&template={TEMPLATE_ID}&modified_after={last_date}&archived=false&completed=both&owner=all&limit=1000 ", headers=headers).json()
            audit_list += template_search["audits"]
    print("...Received")
    return audit_list


def retrieve_audit_data(audit_list):
    """From audit_list, get all information from each audit"""
    print("Retrieving Audits...")
    batch_requests = []
    responses = []
    for x in enumerate(audit_list):  # can try to make a batch request
        audit_id = x[1]['audit_id']
        audit_url = '/audits/' + audit_id
        batch_requests.append('{"method": "get", "path": "' + audit_url + '"}')

        # a multiple of 15 since only 15 request per batch are allowed, skip first one since it will be empty
        if (((x[0])+1) % 15 == 0) & (x[0] != 0) | (x[0] == len(audit_list) - 1):
            print(f"{(x[0] + 1.00) / len(audit_list) * 100 :.2f}%")
            batch = requests.post("https://sandpit-api.safetyculture.io/batch", headers=headers, data='{"requests": [' + ', '.join(batch_requests) + ']}')
            responses += batch.json()
            batch_requests.clear()

    print("Requested Audits Length: " + str(len(responses)))
    print("Length of Audit List: " + str(len(audit_list)))
    print("...All Audits Retrieved")


def get_datetime():
    """get date, subtract a day, then return formatted value"""
    d1 = datetime.datetime.today()
    day = d1 - datetime.timedelta(days=1)
    audit_date = day.strftime("%Y-%m-%dT%H:%I:%S.%fZ")  # API compatible time
    template_search_url = f"https://sandpit-api.safetyculture.io/audits/search?order=asc&template={TEMPLATE_ID}&modified_after={audit_date}&archived=false&completed=both&owner=all&limit=1000"
    return template_search_url


def db_connect():
    """Connect to the mongodb cloud"""
    db_client = pymongo.MongoClient(DATABASE_URL)
    db_name = db_client['RealEstateData']
    db_col = db_name['temp_inspections']  # database 'columns'
    return db_client, db_col


def write_to_db(db_col):
    """Takes list of audits and puts them into database"""
    for audit in audit_data_list:
        dbEntry = audit
        db_col.insert_one(dbEntry)


def close_db(db_client):
    """Closes database"""
    db_client.close()


main()
