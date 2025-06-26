import requests
import time
import os
import re
from pprint import pprint
from .planner import pddl_transform as pt

from app.db import sqldb as db


def parse_enhsp_output(response_json):
    try:
        raw_output = response_json['result']['output']['plan']

        if "Found Plan:" not in raw_output:
            return False

        plan_steps = re.findall(r'\d+\.\d+:\s+\([^)]+\)', raw_output)

        return [step.strip() for step in plan_steps] if plan_steps else False

    except (KeyError, IndexError, TypeError):
        return False
    

def insert_problem(data):
    req_body = {
        'domain': pt.get_domain_data(),
        'problem': pt.get_problem_file_with_data(unrendered_data=data)
        }

    # print(req_body)
    problem_name = "problem_"+str(time.time())
    
    solve_request_url=requests.post("https://solver.planning.domains:5001/package/enhsp/solve", json=req_body).json()

    # Query the result
    result = requests.post('https://solver.planning.domains:5001' + solve_request_url['result'])

    while result.json().get("status","")== 'PENDING':

        # Query the result every 0.5 seconds while the job is executing
        result=requests.post('https://solver.planning.domains:5001' + solve_request_url['result'])
        time.sleep(0.5)

    parsed_plan = parse_enhsp_output(result.json())
    # print(parsed_plan)
    if parsed_plan:
        db.insert_pddl_problem(problem_name, req_body['problem'], parsed_plan)




def ai_fun():
    #insert_problem()
    return "Hello, AI Planning"