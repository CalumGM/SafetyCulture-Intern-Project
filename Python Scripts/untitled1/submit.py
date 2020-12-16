import json
import random

template_responses = ""
# default responses in a seperate json file
with open('response_sets.json', "r") as file:
    template_responses = file.read()
template_responses_json = json.loads(template_responses)

# audit downloaded from iAuditor, read but not written to
with open('example_audit.json', "r") as file:  # file to edit
    example_file = file.read()
responses_json = json.loads(example_file)

# copy of original audit
with open('before.json', "w") as outfile:
    json.dump(responses_json, outfile, indent=4)

# loop through each item in the responses template
random_choices = []
for i, item in enumerate(responses_json["items"]):
    try:
        print("item {}".format(i))
        # print("set: ", item['options']['response_set'])
        # print("label: ", item['label'])  # the question label
        response_set = item['options']['response_set']
        question_options = []

        # print details of each response type, for each question
        for response in template_responses_json["response_sets"][response_set]["responses"]:
            question_options.append(response)
            print(response)
        random_choice = random.choice(question_options) # TODO: skew random choice
        random_choices.append(random_choice['label'])
        # change the response of a question to one of the available choices
        responses_json["items"][i]['responses']['selected'] = [random_choice]
        try:  #
            random_choice['failed']  # Good, Fair, N/A, etc dont have a 'failed' key
            responses_json["items"][i]['responses']['failed'] = True
        except KeyError:
            responses_json["items"][i]['responses']['failed'] = False
    except KeyError:  # exception raised when item isnt a question
        try:
            print("resp: ", item['responses'])
        except KeyError:
            pass

with open('after.json', "w") as outfile:
    json.dump(responses_json, outfile, indent=4)

print(random_choices)