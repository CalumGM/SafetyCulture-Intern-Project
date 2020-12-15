"""
Gets audits from database with specific template ID then puts them into local MongoDB
"""

import pymongo
import requests
import datetime
import time
import sys

# helps start second script
from query_tables import main as q_main


# Authentication constants
USER = 'christopher.ordorica@my.jcu.edu.au'
PWD = 'password'
AUTH_URL = 'https://sandpit-api.safetyculture.io/auth'
GRANT_TYPE = PWD
AUTH_DATA = {'username': USER, 'password': PWD, 'grant_type': GRANT_TYPE}
headers = {}

# API Constants
TEMPLATE_ID = 'template_f0dfd0f0c20c4b30800d12fa8ab3764b'
TEMPLATE_SEARCH_URL = f"https://sandpit-api.safetyculture.io/audits/search?order=asc&template={TEMPLATE_ID}&archived=false&completed=both&owner=all&limit=1000"

# DB Constant
DATABASE_URL = "mongodb+srv://calum_maitland:InternDatabase@cluster0.qg16e.mongodb.net/RealEstateData?retryWrites=true&w=majority"

# Log file Constant, with debug condition
DEBUG = False
if DEBUG:
    LOG = sys.stdout
else:
    LOG = open("log.log", "a")


def main():
    """main does main things"""
    print(datetime.datetime.now(), file=LOG)
    authenticate()
    db_client, db_col = db_connect()

    x = int(db_col.estimated_document_count())
    if x > 0:  # if db has documents
        # execute code that adds all new audits
        url = get_datetime()
    else:  # x == 0
        # execute code that adds all audits
        url = TEMPLATE_SEARCH_URL

    audit_list = retrieve_audit_ids(url)
    responses = retrieve_audit_data(audit_list)
    write_to_db(db_col, responses)

    # final script formalities
    close_db(db_client)
    LOG.close()
    time.sleep(1)  # feels better if you wait
    q_main()  # start next script


def authenticate():
    """Authenticate user credentials and create header for API requests"""
    print("Authenticating...", file=LOG, end='')
    auth_response = requests.post(AUTH_URL, data=AUTH_DATA)
    auth_json = auth_response.json()
    # format access token
    access_token = auth_json['token_type'] + ' ' + auth_json['access_token']
    headers['Authorization'] = access_token
    print("...Done", file=LOG)


def retrieve_audit_ids(url):
    """Use a pre-determined template_id to find any audits made from that template"""
    print("Looking for Audits Using the Template...", file=LOG, end='')
    template_search = requests.get(url, headers=headers).json()
    audit_list = template_search["audits"]
    if template_search["total"] >= 1001:  # greater than 1000
        for i in range(round(float(template_search["total"])/1000)-1):  # accounts for first request
            last_date = audit_list[-1]["modified_at"]
            template_search = requests.get(f"https://sandpit-api.safetyculture.io/audits/search?order=asc&template={TEMPLATE_ID}&modified_after={last_date}&archived=false&completed=both&owner=all&limit=1000 ", headers=headers).json()
            audit_list += template_search["audits"]
    print("...Done", file=LOG)
    return audit_list


def retrieve_audit_data(audit_list):
    """From audit_list, get all information from each audit"""
    if len(audit_list) == 0:
        print("List is Empty: No new Audits", file=LOG)
        responses = no_new_audits()
        return responses
    print("Retrieving Audits...", file=LOG)
    print(f"\tThere are {len(audit_list)} Audits\n\t", file=LOG, end='')
    batch_requests = []
    responses = []
    timer = datetime.datetime.now()

    for count, audit in enumerate(audit_list):
        audit_id = audit['audit_id']
        audit_url = '/audits/' + audit_id
        batch_requests.append('{"method": "get", "path": "' + audit_url + '"}')

        # submit a batch request when there have been 15 ids added to requests list or
        # when the final id in the list is reached or
        # when 100 iterations have been made
        if ((count+1) % 15 == 0) | (count+1 == len(audit_list)) | ((count+1) % 100 == 0):
            print(f"{(count + 1.00) / len(audit_list) * 100 :.2f}%", file=LOG, end=",")  # percentage of completion
            batch = requests.post("https://sandpit-api.safetyculture.io/batch", headers=headers, data='{"requests": [' + ', '.join(batch_requests) + ']}')
            responses += batch.json()
            batch_requests.clear()

        # sleep only after 100 iterations have occurred
        if (count + 1) % 100 == 0:
            timer = datetime.datetime.now() - timer
            sleep_time = round(60 - timer.total_seconds())+2
            print("\n\tLimiting Rate - Sleep: ", sleep_time, " seconds\n\t", file=LOG, end='')
            time.sleep(sleep_time)
            timer = datetime.datetime.now()

    print("\n\tRequested Audits Length: " + str(len(responses)), file=LOG)
    print("\tLength of Audit List: " + str(len(audit_list)), file=LOG)
    print("...Done: All Audits Retrieved", file=LOG)
    error_count = 0  # TODO maybe do something with this so db doesnt break? cancel if not 0?
    for response in responses:
        try:
            if response["statusCode"]:
                error_count += 1
                print("Error", file=LOG)
        except KeyError:
            pass
    print("Error Count: ", error_count, file=LOG)
    return responses


def get_datetime():
    """get date, subtract a day, then return formatted value"""
    d1 = datetime.datetime.today()
    day = d1 - datetime.timedelta(days=1)
    audit_date = day.strftime("%Y-%m-%dT%H:%I:%S.%fZ")  # API compatible time
    template_search_url = f"https://sandpit-api.safetyculture.io/audits/search?order=asc&template={TEMPLATE_ID}&modified_after={audit_date}&archived=false&completed=both&owner=all&limit=1000"
    return template_search_url


def no_new_audits():
    """Create a flag to send to db to prevent script failure"""
    flag_dict = {"audit": False}
    flag = [flag_dict]
    return flag


def db_connect():
    """Connect to the mongodb cloud"""
    db_client = pymongo.MongoClient(DATABASE_URL)
    db_name = db_client['RealEstateData']
    db_col = db_name['temp_inspections']  # database 'columns'
    return db_client, db_col


def write_to_db(db_col, responses):
    """Takes list of audits and puts them into database"""
    db_col.drop()  # erase collection so that next script doesnt get confused, poor baby
    print("Inserting into Database...", file=LOG, end='')
    db_col.insert_many(responses)
    print("...Done\n", file=LOG)


def close_db(db_client):
    """Closes database"""
    db_client.close()


main()
