""""""

import pymongo
import datetime

DATABASE_URL = "mongodb+srv://calum_maitland:InternDatabase@cluster0.qg16e.mongodb.net/RealEstateData?retryWrites" \
               "=true&w=majority"
LOG = open("log.log", "a")


def main():
    """main bruh"""
    db_client, db_retrieve_col, db_audits_col, db_agents_col = db_connect()

    try:  # flag may exist in db. If present, exit.
        if not db_retrieve_col.find_one()["audit"]:  # see if flag is in db
            print("Flag Detected: Exiting", file=LOG)
            raise SystemExit  # exit program
    except KeyError:
        print("No Flag: Continuing", file=LOG)

    audit_dict_list, unique_agents = reformat_audits(db_retrieve_col=db_retrieve_col)
    agent_dict_list = agent_transform(unique_agents=unique_agents, audit_dict_list=audit_dict_list, db_agents_col=db_agents_col)
    all_agents = get_all_agents(db_agents_col=db_agents_col)
    write_to_db(db_audits_col=db_audits_col, db_agents_col=db_agents_col, audit_dict_list=audit_dict_list, agent_dict_list=agent_dict_list, all_agents=all_agents, unique_agents=unique_agents)

    db_client.close()
    print(datetime.datetime.now(), file=LOG)  # runtime of program
    LOG.close()


def get_all_agents(db_agents_col):
    all_agents = []

    if db_agents_col.count_documents({}) != 0:
        all_agents_cursor = list(db_agents_col.find({}, {"_id": 0, "agent_name": 1}))
        for agent in all_agents_cursor:
            all_agents.append(agent["agent_name"])

    return all_agents


def db_connect():
    """Connect to the mongodb cloud"""
    print("Connecting to Database...", file=LOG, end='')
    db_client = pymongo.MongoClient(DATABASE_URL)
    db_name = db_client['RealEstateData']
    db_audits_col = db_name['audits']  # audits collection
    db_agents_col = db_name['agents']  # agents collection
    # TODO change back from temp
    db_audits_col = db_name['temp_audits']  # audits collection
    db_agents_col = db_name['temp_agents']  # agents collection
    db_retrieve_col = db_name['temp_inspections']  # inspections collection, staging db

    print("...Done", file=LOG)
    return db_client, db_retrieve_col, db_audits_col, db_agents_col


def reformat_audits(db_retrieve_col):
    """find audits from inspection and reformat them"""
    print("Retrieve and Reformat Audits...", file=LOG, end='')
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
        address_lat_long = str(audit["header_items"][3]["responses"]["location_text"]).split("\n")
        address = address_lat_long[0]
        lat_long = address_lat_long[1].split(",")
        lat = lat_long[0].lstrip("(")  # around -19
        long = lat_long[1].strip(")")  # around 146

        # set up unique names for later processing
        agent_name = audit["header_items"][2]["responses"]["text"]
        agent_list.append(agent_name)

        # create new dictionary
        new_audit_dict = {"audit_id": audit["audit_id"], "agent_name": agent_name, "date": datetime_var,
                          "scores": {"score": score, "total_score": total_score, "score_percentage": score_percentage},
                          "location": {"text": address, "lat": lat, "long": long}}
        audit_dict_list.append(new_audit_dict)

    # convert all names to only unique agents
    set1 = set(agent_list)
    unique_agent_list = (list(set1))

    print("...Done", file=LOG)
    return audit_dict_list, unique_agent_list


def agent_transform(unique_agents, audit_dict_list, db_agents_col):
    """create the dictionaries that will update/insert in the agents collection"""
    print("Transform Agents...", file=LOG, end='')
    agent_dict_list = []

    for agent in unique_agents:
        # query that uses agent name to retrieve that agent's document

        historical_agent = db_agents_col.find_one({"agent_name": agent},
                                                  {"_id": 0, "avg_score": 1, "total_inspection_count": 1,
                                                   "time_series": 1})

        if historical_agent is None:  # not in collection, set default values to prevent exception
            historical_score = 0.0000
            historical_inspection_count = 0
            time_series = [[], []]
        else:  # in collection, retrieve values
            historical_score = float(historical_agent["avg_score"])
            historical_inspection_count = int(historical_agent["total_inspection_count"])
            time_series = historical_agent["time_series"]

        # get count and daily score, and datelist
        count = 0
        audit_daily_score = []
        date_list = []
        for audit in audit_dict_list:  # bit inefficient
            if audit["agent_name"] == agent:
                daily_score = float(audit["scores"]["score_percentage"])
                count += 1
                audit_daily_score.append(daily_score)

                # audit in audit_dict_list loop is too resource intensive to have multiple times
                if historical_agent is None:
                    date_list.append(audit["date"])

        daily_score = sum(audit_daily_score)
        new_count = historical_inspection_count + count
        new_score = ((historical_score * historical_inspection_count) + daily_score) / new_count

        # construct time-series if agent is not in collection
        if historical_agent is None:
            # final calculation for oldest day
            oldest_date = min(date_list)
            elapsed_time = int(str((datetime.datetime.now() - oldest_date).days)) + 1

            # create array to contain every day's score since an agent's first day
            for i in range(1, elapsed_time + 1):
                temp_array = []
                count2 = 0
                days = datetime.datetime.now()
                days = days - datetime.timedelta(days=(int(elapsed_time) - i))

                for audit in audit_dict_list:
                    if audit["agent_name"] == agent:
                        if str(audit["date"].date()) == str(days.date()):
                            temp_array.append(float(audit["scores"]["score_percentage"]))
                            count2 += 1

                if count2 != 0:  # day has at least 1 audit entry
                    time_series[0].append(sum(temp_array)/count2)
                    time_series[1].append(count2)
                else:  # count == 0, no new audit and scores are 0
                    time_series[0].append(0.0000)
                    time_series[1].append(0)

        else:  # agent in collection, append new values to time_series
            time_series[0].append(daily_score / count)
            time_series[1].append(count)

        agent_dict = {"agent_name": agent, "avg_score": f"{new_score:.4f}", "total_inspection_count": new_count,
                      "time_series": time_series}

        agent_dict_list.append(agent_dict)
    print("...Done", file=LOG)
    return agent_dict_list


def write_to_db(db_audits_col, db_agents_col, audit_dict_list, agent_dict_list, all_agents, unique_agents):
    """Takes lists of audits and agents and correctly places them into database"""
    # insert new audits
    print("Inserting Audits to Database...", file=LOG, end='')
    db_audits_col.insert_many(audit_dict_list)
    print("...Done", file=LOG)

    # check condition for agent and take appropriate action
    print("Processing Agents and Inserting into Database...", file=LOG, end='')

    for agent_dict in agent_dict_list:
        if agent_dict["agent_name"] in all_agents:  # exists and has report
            print("Old User, New Audit", file=LOG)
            db_agents_col.update_one({"agent_name": agent_dict["agent_name"]}, {"$set": {"avg_score": agent_dict["avg_score"], "total_inspection_count": agent_dict["total_inspection_count"], "time_series": agent_dict["time_series"]}})
        else:  # doesnt exist, had report
            print("New User, New Audit", file=LOG)
            db_agents_col.insert_one(agent_dict)

    for agent in all_agents:
        if agent not in unique_agents:
            print("Old User, No Report", file=LOG)
            agent_dict = db_agents_col.find_one({"agent_name": agent}, {"_id": 0, "time_series": 1})
            agent_dict['time_series'][0].append(0.0)
            agent_dict['time_series'][1].append(0)
            db_agents_col.update_one({"agent_name": agent}, {"time_series": agent_dict["time_series"]})

    print("...Done", file=LOG)
