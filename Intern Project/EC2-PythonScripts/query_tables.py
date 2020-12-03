""""""

import pymongo
import datetime

DATABASE_URL = "mongodb+srv://calum_maitland:InternDatabase@cluster0.qg16e.mongodb.net/RealEstateData?retryWrites" \
               "=true&w=majority "


def main():
    """main bruh"""
    db_client, db_retrieve_col, db_audits_col, db_agents_col = db_connect()
    audit_list, agent_list = reformat_audits(db_retrieve_col=db_retrieve_col)
    agent_create_thing(agent_list=agent_list, db_retrieve_col=db_retrieve_col)
    write_to_db(db_audits_col=db_audits_col, db_agents_col=db_agents_col, audit_list=audit_list)
    db_client.close()


def db_connect():
    """Connect to the mongodb cloud"""
    db_client = pymongo.MongoClient(DATABASE_URL)
    db_name = db_client['RealEstateData']
    db_retrieve_col = db_name['inspections']  # inspections collection
    db_audits_col = db_name['audits']  # audits collection
    db_agents_col = db_name['agents']  # agents collection
    return db_client, db_retrieve_col, db_audits_col, db_agents_col


def reformat_audits(db_retrieve_col):
    """find audits from inspection and reformat them"""
    audit_list = []
    agent_list = []

    for audit in db_retrieve_col.find({}, {"_id": 0, "audit_id": 1, "audit_data.score": 1, "audit_data.total_score": 1,
                                           "audit_data.score_percentage": 1, "header_items.responses.datetime": 1,
                                           "header_items.responses.text": 1,
                                           "header_items.responses.location_text": 1}):
        # assign query results to variables
        score = str(audit["audit_data"]["score"])
        total_score = str(audit["audit_data"]["total_score"])
        score_percentage = str(audit["audit_data"]["score_percentage"])
        datetime2 = datetime.datetime.strptime(audit["header_items"][1]["responses"]["datetime"],
                                               "%Y-%m-%dT%H:%I:%S.%fZ")
        date = datetime2.strftime("%d/%m/%Y")
        agent_name = audit["header_items"][2]["responses"]["text"]
        agent_list.append(agent_name)
        address_lat_long = str(audit["header_items"][3]["responses"]["location_text"]).split("\n")
        address = address_lat_long[0]
        lat_long = address_lat_long[1].split(",")
        lat = lat_long[0].lstrip("(")  # around -19
        long = lat_long[1].strip(")")  # around 146

        # create new dictionary
        new_audit_dict = {"audit_id": audit["audit_id"], "agent_name": agent_name, "date": date,
                          "scores": {"score": score, "total_score": total_score, "score_percentage": score_percentage},
                          "location": {"text": address, "lat": lat, "long": long}}
        audit_list.append(new_audit_dict)

    return audit_list, agent_list


def agent_create_thing(agent_list, db_retrieve_col):
    """"""
    unique_agent_list = []
    agent_dict = {}
    # get unique agents
    set1 = set(agent_list)
    unique_list = (list(set1))
    for x in unique_list:
        unique_agent_list.append(x)

    # for each agent, retrieve all audits from them
    print(unique_agent_list)

    # This ends up creating a list similar to the previous function (new_audit_dict). Goal is to create list with an
    #   agent and an array/dict of his scores with dates.
    for agent in unique_agent_list:
        # TODO create key for dict here
        # agent_dict[f"{agent}"] = ""
        temp_audit_list = []
        for audit in db_retrieve_col.find({"header_items.responses.text": f"{agent}"},
                                          {"_id": 0, "audit_data.score": 1, "audit_data.total_score": 1,
                                           "audit_data.score_percentage": 1, "header_items.responses.datetime": 1}):
            # TODO format find and place into list
            score = audit["audit_data"]["score"]

            temp_audit_list.append(audit)
        agent_dict[f"{agent}"] = temp_audit_list

            # in this step, create a list of audits from a certain agent

            # can create a list with agent name and populate with audits NVM

            # TODO Problem: i need a way to dynamically assign 'variables' that themselves are related to some amount of entries. The end point is a named array with date and score (tuples/dictionaries whatever) as its contents
        # TODO array of 365 days that will have a score if an audit was done on that day

        # TODO Big point here, the 365 thing is based on number of audits, not score. score could be stored also but maybe not yet.
    print(agent_dict)



def write_to_db(db_audits_col, db_agents_col, audit_list):
    """Takes list of audits and puts them into database"""

    # for audit in audit_list:
    #     dbEntry = audit
    #     db_audits_col.insert_one(dbEntry)
    #
    # for agent in agent_list:
    #     dbEntry = agent
    #     db_agents_col.insert_one(dbEntry)


main()
