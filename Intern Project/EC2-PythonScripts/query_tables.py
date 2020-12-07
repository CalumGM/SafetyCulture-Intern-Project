""""""

import pymongo
import datetime
import random

DATABASE_URL = "mongodb+srv://calum_maitland:InternDatabase@cluster0.qg16e.mongodb.net/RealEstateData?retryWrites" \
               "=true&w=majority"


def main():
    """main bruh"""
    # DOTO LIST:
    db_client, db_retrieve_col, db_audits_col, db_agents_col = db_connect()  # setup collections for other functions to use
    audit_dict_list, unique_agents = reformat_audits(db_retrieve_col=db_retrieve_col)
    agent_dict_list = agent_transform(unique_agents=unique_agents, audit_dict_list=audit_dict_list, db_agents_col=db_agents_col)

    # pull all agents for processing in write_to_db()
    all_agents = db_retrieve_col.find({}, {"_id": 0, "agent_name": 1})

    write_to_db(db_audits_col=db_audits_col, db_agents_col=db_agents_col, audit_dict_list=audit_dict_list, agent_dict_list=agent_dict_list, all_agents=all_agents, unique_agents=unique_agents)
    db_client.close()


def db_connect():
    """Connect to the mongodb cloud"""
    db_client = pymongo.MongoClient(DATABASE_URL)
    db_name = db_client['RealEstateData']
    db_retrieve_col = db_name['inspections']  # inspections collection, staging db
    db_audits_col = db_name['audits']  # audits collection
    db_agents_col = db_name['agents']  # agents collection
    return db_client, db_retrieve_col, db_audits_col, db_agents_col


def reformat_audits(db_retrieve_col):
    """find audits from inspection and reformat them"""
    audit_dict_list = []
    agent_list = []

    for audit in db_retrieve_col.find({}, {"_id": 0, "audit_id": 1, "audit_data.score": 1, "audit_data.total_score": 1,
                                           "audit_data.score_percentage": 1, "header_items.responses.datetime": 1,
                                           "header_items.responses.text": 1,
                                           "header_items.responses.location_text": 1}):
        # assign query results to variables
        score = str(audit["audit_data"]["score"])
        total_score = str(audit["audit_data"]["total_score"])
        score_percentage = str(audit["audit_data"]["score_percentage"])
        datetime_var = datetime.datetime.strptime(audit["header_items"][1]["responses"]["datetime"],
                                                  "%Y-%m-%dT%H:%I:%S.%fZ")
        datetime_var = datetime.datetime.strftime(datetime_var, "%Y-%m-%d")
        datetime_var = datetime.datetime.strptime(datetime_var, "%Y-%m-%d")

        # date = datetime_var.date()
        agent_name = audit["header_items"][2]["responses"]["text"]
        agent_list.append(agent_name)
        address_lat_long = str(audit["header_items"][3]["responses"]["location_text"]).split("\n")
        address = address_lat_long[0]
        lat_long = address_lat_long[1].split(",")
        lat = lat_long[0].lstrip("(")  # around -19
        long = lat_long[1].strip(")")  # around 146

        # create new dictionary
        new_audit_dict = {"audit_id": audit["audit_id"], "agent_name": agent_name, "date": datetime_var,
                          "scores": {"score": score, "total_score": total_score, "score_percentage": score_percentage},
                          "location": {"text": address, "lat": lat, "long": long}}
        audit_dict_list.append(new_audit_dict)

    # convert all names to only unique agents
    set1 = set(agent_list)
    unique_agent_list = (list(set1))

    return audit_dict_list, unique_agent_list


# TODO two functions. one for once off and other for daily. first below is now daily
def agent_transform(unique_agents, audit_dict_list, db_agents_col):
    """create the dictionaries that will update/insert in the agents collection"""
    agent_dict_list = []
    for agent in unique_agents:
        # query that uses agent name to retrieve that agent's document

        historical_agent = db_agents_col.find_one({"agent_name": agent}, {"_id": 0, "avg_score": 1, "total_inspection_count": 1, "time_series": 1})

        # if agents collection is empty, set default values to prevent exception
        if historical_agent is None:
            historical_score = 0.0000
            historical_inspection_count = 0
            time_series = [[], []]
        else:
            historical_score = float(historical_agent["avg_score"])
            historical_inspection_count = int(historical_agent["total_inspection_count"])
            time_series = historical_agent["time_series"]

        # get new data
        count = 0
        audit_daily_score = []
        for audit in audit_dict_list:  # bit inefficient
            if audit["agent_name"] == agent:
                daily_score = float(audit["scores"]["score_percentage"])
                count += 1
                audit_daily_score.append(daily_score)

        daily_score = sum(audit_daily_score)
        new_count = historical_inspection_count + count
        new_score = ((historical_score * historical_inspection_count) + daily_score) / new_count

        time_series[0].append(daily_score / count)
        time_series[1].append(count)

        agent_dict = {"agent_name": agent, "avg_score": f"{new_score:.4f}", "total_inspection_count": new_count,
                      "time_series": time_series}

        agent_dict_list.append(agent_dict)
    return agent_dict_list


def write_to_db(db_audits_col, db_agents_col, audit_dict_list, agent_dict_list, all_agents, unique_agents):
    """Takes lists of audits and agents and correctly places them into database"""
    # insert new audits
    db_audits_col.insert_many(audit_dict_list)

    # check condition for agent and take appropriate action
    for agent in unique_agents:
        if agent in all_agents:
            # agent exists and has a new audit
            db_agents_col.update({"agent_name": agent}, {"avg_score": agent_dict_list["avg_score"], "total_inspection_count": agent_dict_list["total_inspection_count"], "time_series": agent_dict_list["time_series"]})
        else:
            # agent does not exist and has a new audit
            for agent_dict in agent_dict_list:
                if agent_dict["agent_name"] == agent:
                    db_agents_col.insert(agent_dict)
    for agent in all_agents:
        if agent not in unique_agents:
            # agent exists but has no new audit
            time_series = db_agents_col.find({"agent_name": agent}, {"time_series": 1})
            time_series[0].append(0.0000)
            time_series[1].append(0)
            db_agents_col.update({"agent_name": agent}, time_series)


main()
