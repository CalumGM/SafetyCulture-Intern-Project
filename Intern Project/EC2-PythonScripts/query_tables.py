""""""

import pymongo
import datetime
import random

DATABASE_URL = "mongodb+srv://calum_maitland:InternDatabase@cluster0.qg16e.mongodb.net/RealEstateData?retryWrites" \
               "=true&w=majority"


def main():
    """main bruh"""
    # DOTO LIST:
    # TODO pull all agents from agents db and if agent not in unique_agents: add a 0 to time-series with update
    # TODO code will not account for a new agent joining on a date (that agent will have smaller array: needs processing)
    db_client, db_retrieve_col, db_audits_col, db_agents_col = db_connect()  # setup collections for other functions to use
    audit_dict_list, unique_agents = reformat_audits(db_retrieve_col=db_retrieve_col)

    unique_agents = ["Donald Glover", "Calum Hawaii", "Chris Ornott"]

    agent_pull = emulate_agent_db()  # emulates the db for code construction purposes

    agent_dict_list = daily_agent_transform(unique_agents=unique_agents, db_emulation=agent_pull,
                                            audit_dict_list=audit_dict_list)  # WIP function
    # pull all agents
    all_agents = db_retrieve_col.find({}, {"_id": 0, "agent_name": 1})
    # need code that will determine if agent is in db, update if he is else take dictionary created in code and insert


    write_to_db(db_audits_col=db_audits_col, db_agents_col=db_agents_col, audit_dict_list=audit_dict_list, agent_dict_list=agent_dict_list, all_agents=all_agents, unique_agents=unique_agents)
    db_client.close()


def emulate_agent_db():
    # emulation of db pull for daily_agent_transform
    agent_pull = [
        {"agent_name": "Donald Glover", "avg_score": "94.444", "total_inspection_count": "2", "time_series": [[], []]},
        {"agent_name": "Calum Hawaii", "avg_score": "83.5495", "total_inspection_count": "3", "time_series": [[], []]},
        {"agent_name": "Chris Ornott", "avg_score": "86.26875", "total_inspection_count": "5", "time_series": [[], []]}]
    # TODO WARNING: Total_inspection_count will not equal actual time_series array
    # TODO WARNING: There is no corrolation between the paralell arrays. You could submit no audits but get a percent score (logic error)

    time_series_score = []  # measured in percentages
    time_series_inspection_count = []  # simple count of inspections done per day

    for agent in agent_pull:
        for x in range(0, 5):
            time_series_score.append(round(random.uniform(75, 100), 4))
            time_series_inspection_count.append(random.randint(0, 7))
        agent["time_series"][0] = time_series_score
        agent["time_series"][1] = time_series_inspection_count

    return agent_pull


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
        print(datetime_var)

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

    # get only unique agents
    set1 = set(agent_list)
    unique_agent_list = (list(set1))

    return audit_dict_list, unique_agent_list


# TODO two functions. one for once off and other for daily. first below is now daily
def daily_agent_transform(unique_agents, db_emulation, audit_dict_list):
    """create the dictionaries that will update/insert in the agents collection"""
    # TODO: will need a way to store info for writing to db
    agent_dict_list = []
    for agent in unique_agents:
        # TODO db query for info using agent name

        # get old scores
        historical_score = float(db_emulation[0]["avg_score"])
        historical_inspection_count = int(db_emulation[0]["total_inspection_count"])
        time_series = db_emulation[0]["time_series"]

        # get new data
        count = 0
        audit_daily_score = []
        for audit in audit_dict_list:
            if audit["agent_name"] == agent:
                # get stuff
                daily_score = float(audit["scores"]["score_percentage"])
                count += 1  # todo check to see if this works as intended
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
    """Takes list of audits and puts them into database"""
    # x=0
    # for audit in audit_dict_list:
    #     if x==1:
    #         break
    #     x+=1
    #     dbEntry = audit
    #     db_audits_col.insert_one(dbEntry)

    # db_audits_col.insert_many(audit_dict_list)  # use this one

    # three conditions:
    # agent exists and has an audit
    # agent exists and has no audit
    # agent does not exist and has an audit (add agent to db)
    for agent in unique_agents:  # must see if i can condense later
        if agent in all_agents:
            # agent exists and has an audit
            # update using dictionary
            pass
        else:
            # agent does not exist and has an audit
            # insert using full dictionary
            pass

    for agent in all_agents:
        if agent not in unique_agents:
            # agent exists and has no audit
            # append 0 to timeseries
            pass

main()
