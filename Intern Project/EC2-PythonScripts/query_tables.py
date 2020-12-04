""""""

import pymongo
import datetime
import random

DATABASE_URL = "mongodb+srv://calum_maitland:InternDatabase@cluster0.qg16e.mongodb.net/RealEstateData?retryWrites" \
               "=true&w=majority "


def main():
    """main bruh"""
    db_client, db_retrieve_col, db_audits_col, db_agents_col = db_connect()  # setup collections for other functions to use
    audit_list, agent_list = reformat_audits(db_retrieve_col=db_retrieve_col)

    # unique_agent_list = identify_unique_agents(agent_list)
    unique_agent_list = ["Donald Glover", "Calum Hawaii", "Chris Ornott"]

    agent_pull = emulate_agent_db()  # emulates the db for code construction purposes

    daily_agent_transform(agent_list=agent_list, db_retrieve_col=db_retrieve_col)  # WIP function

    # write_to_db(db_audits_col=db_audits_col, db_agents_col=db_agents_col, audit_list=audit_list)
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
        for x in range (0,5):
            time_series_score.append(round(random.uniform(75, 100), 4))
            time_series_inspection_count.append(random.randint(0, 7))
        agent["time_series"][0] = time_series_score
        agent["time_series"][1] = time_series_inspection_count

    print(agent_pull)
    return agent_pull


def identify_unique_agents(agent_list):
    # make unique_agents another function
    unique_agent_list = []
    # get unique agents
    set1 = set(agent_list)
    unique_list = (list(set1))
    for x in unique_list:
        unique_agent_list.append(x)

    # for each agent, retrieve all audits from them
    print(unique_agent_list)

    return unique_agent_list


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
        datetime_var = datetime.datetime.strptime(audit["header_items"][1]["responses"]["datetime"],
                                                  "%Y-%m-%dT%H:%I:%S.%fZ")
        date = datetime_var.strftime("%d/%m/%Y")
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


# TODO two functions. one for once off and other for daily. first below is now daily
def daily_agent_transform(agent_list, db_retrieve_col):
    """"""
    # rundown.
    # for loop with unique agent names.
    #   avg score (for percentages) gets original avg, * by original count, result + new avg (however many times that is), that result/(count+however many new audits there are)
    #   inspection count += new audit count
    #   time series [0] = essentially append any new percent on the end, sorted by date (assumed) - and expect 0s for no data
    #   time series [1] = append the count of new audits under agent name on the end
    #   TODO: will need a way to store info for writing to db






    # """"""
    #

    #
    # # This ends up creating a list similar to the previous function (new_audit_dict). Goal is to create list with an
    # #   agent and an array/dict of his scores with dates.
    # for agent in unique_agent_list:
    #     agent_audit_list = []
    #     temp_audit_list = []
    #     avg_score = 0
    #     count = 0
    #     for audit in db_retrieve_col.find({"header_items.responses.text": f"{agent}"},
    #                                       {"_id": 0,"audit_id": 1, "audit_data.score": 1, "audit_data.total_score": 1,
    #                                        "audit_data.score_percentage": 1, "header_items.responses.datetime": 1}):
    #         # TODO format find and place into list
    #         score_percentage = audit["audit_data"]["score_percentage"]
    #         datetime_var = datetime.datetime.strptime(audit["header_items"][1]["responses"]["datetime"],
    #                                                   "%Y-%m-%dT%H:%I:%S.%fZ")
    #         date = datetime_var.strftime("%d/%m/%Y")
    #
    #         new_audit_dict = {"audit_id": audit["audit_id"], "date": date,
    #                           "score_percentage": score_percentage}  # dont need the other scores, only %
    #         temp_audit_list.append(new_audit_dict)
    #     # agent_dict[f"{agent}"] = temp_audit_list  # list of agents with their audits
    #
    #     for audit in temp_audit_list:
    #         # print(audit)
    #         count += 1
    #         # print(audit)
    #         # print(audit["score_percentage"])
    #         avg_score += float(audit["score_percentage"])
    #     print(agent)
    #     print("avg: " + str(avg_score/count))
    #
    #     agent_dict = {"agent_name": str(agent), "avg_score": avg_score/count, "inspection_count": count}
    #
    #     # agent_audit_list.append()
    #     # print(count)
    #
    #
    #     # real basic code for date array
    #     test_array = []
    #     y=0
    #     for y in range(0, 365):
    #         if y == y%10:
    #             test_array.append("0")
    #         else:
    #             test_array.append("1")
    #         y+=1
    #     print(test_array)
    #     print(len(test_array))
    #     print(test_array.count("0"))
    #     print(test_array.count("1"))
    #
    #
    #     # create average score
    #     # for score in agent_dict[""]
    #
    # # {agent_name: "", avg_score: "", total_inspection_count: "", time_series: [[],[]]}
    # # TODO need to .split the dictionary so i can write each agent as a single document
    #
    # # in this step, create a list of audits from a certain agent
    #
    # # can create a list with agent name and populate with audits NVM
    #
    # # TODO Problem: i need a way to dynamically assign 'variables' that themselves are related to some amount of entries. The end point is a named array with date and score (tuples/dictionaries whatever) as its contents
    # # TODO array of 365 days that will have a score if an audit was done on that day
    #
    # # TODO Big point here, the 365 thing is based on number of audits, not score. score could be stored also but maybe not yet.
    #
    # # TODO just a thought... if an agent has a score on a day then an audit was performed, assuming one per day (can be more tho maybe)
    # # print(agent_dict)
    #
    # # TODO hello todo my old friend... make an array that contains the jsons i want to submit rahter than this bullshit


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
