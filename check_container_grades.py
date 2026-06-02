import requests
from dateutil import parser
import json
import os

DEV_SPACES_CONTAINER_LIST = []

DWO_CONTAINER_LIST = []
WTO_CONTAINER_LIST = []

BASE_URL = "https://catalog.redhat.com/api/containers/v1/repositories/registry/registry.access.redhat.com/repository/{0}%2F{1}/grades"

def fetch_container_grades(project, base_url, container_list, tag="latest"):
    container_grade_dict = {}
    for container in container_list:
        current_url = base_url.format(project, container)
        response = requests.get(current_url)
        if response.status_code == 200:
            print("Fetched grades for", container)
            raw_data = response.json()
            this_container_string = ""
            if tag == None:
                selected_entry = raw_data[0]
            for entry in raw_data:
                if entry["tag"] == "latest":
                    selected_entry = entry
                    break
            if "next_drop_date" in selected_entry:
                next_drop_pretty = parser.parse(selected_entry["next_drop_date"]).date()
                this_container_string += selected_entry["current_grade"] + ", next grade drop is " + next_drop_pretty.strftime("%d/%m/%Y")
            else:
                this_container_string += selected_entry["current_grade"]
            container_grade_dict[container] = this_container_string
        else:
            container_grade_dict[container] = "Error parsing container grade."
    return container_grade_dict

# Import Slack webhooks
dev_spaces_workflow_hook = os.environ.get("DEV_SPACES_WORKFLOW_HOOK")
if not dev_spaces_workflow_hook:
    raise ValueError("Missing DEV_SPACES_WORKFLOW_HOOK environment variable!")

dwo_wto_workflow_hook = os.environ.get("DWO_WTO_WORKFLOW_HOOK")
if not dwo_wto_workflow_hook:
    raise ValueError("Missing DWO_WTO_WORKFLOW_HOOK environment variable!")

# Popular container lists
with open('DEV_SPACES_CONTAINERS') as file:
    for line in file:
        DEV_SPACES_CONTAINER_LIST.append(line.rstrip())

with open('DWO_CONTAINERS') as file:
    for line in file:
        DWO_CONTAINER_LIST.append(line.rstrip())

with open('WTO_CONTAINERS') as file:
    for line in file:
        WTO_CONTAINER_LIST.append(line.rstrip())

# Fetch Dev Spaces container grades
dev_spaces_final_grades = fetch_container_grades("devspaces", BASE_URL, DEV_SPACES_CONTAINER_LIST)

# Publish Dev Spaces container grades
slack_json = json.dumps(dev_spaces_final_grades)
r = requests.post(dev_spaces_workflow_hook, data=slack_json)
print("Publishing of Dev Spaces container grades returned ", r.status_code)

# Fetch DWO/WTO container grades
dwo_final_grades = fetch_container_grades("devworkspace", BASE_URL, DWO_CONTAINER_LIST)
wto_final_grades = fetch_container_grades("web-terminal", BASE_URL, WTO_CONTAINER_LIST, None)
merged_dwo_wto_grades = dwo_final_grades | wto_final_grades

# Publish DWO/WTO container grades
slack_json = json.dumps(merged_dwo_wto_grades)
r = requests.post(dwo_wto_workflow_hook, data=slack_json)
print("Publishing of DWO/WTO container grades returned ", r.status_code)
        