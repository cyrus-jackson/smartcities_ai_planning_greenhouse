import requests
import time
import os
import re
import json
import redis
from pprint import pprint
from .planner import pddl_transform as pt

from app.db import sqldb as db
import app.utils.state_constants as states
from app.utils.state_constants import NOTIFICATIONS

# Initialize Redis client here
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
NOTIFICATIONS_KEY = "latest_notifications"

def get_current_notifications():
    data = redis_client.get(NOTIFICATIONS_KEY)
    if data:
        return json.loads(data)
    return []

def process_notification_actions(action, fluents):
    notif_types = {
        "issue_warning": "warning",
        "issue_high_alert": "danger",
        "expecting_rain_alert": "info",
        "expecting_rain_warning": "warning"
    }
    if action in notif_types:
        message = action.replace("_", " ").capitalize()

        if fluents and "hours_until_rain" in fluents:
            message += f" (hours_until_rain: {fluents['hours_until_rain']})"
        notif_type = notif_types[action]
        
        return {
            "message": message,
            "type": notif_type
        }
    return None

def parse_enhsp_output(response_json, fluents):
    try:
        raw_output = response_json['result']['output']['plan']

        if "Found Plan:" not in raw_output:
            return False

        plan_steps = re.findall(r'(\d+\.\d+):\s+\(([^)]+)\)', raw_output)
        # plan_steps is now a list of tuples: [("0.0", "turn_off_fan"), ...]
        # Mapping from PDDL actions to state_constants
        action_map = {
            "turn_on_fan": states.FAN_ON,
            "turn_off_fan": states.FAN_OFF,
            "open_roof s1": states.RUN_ROOF_SERVO_S1,
            "open_roof s2": states.RUN_ROOF_SERVO_S2,
            "close_roof s1": states.CLOSE_ROOF_SERVO_S1,
            "close_roof s2": states.CLOSE_ROOF_SERVO_S2,
        }

        parsed = {}
        notifications = []
        for step_num, action in plan_steps:
            action = action.strip()
            mapped = action_map.get(action)
            if mapped:
                parsed[step_num] = mapped
            else:
                parsed[step_num] = action
            # Process notification actions
            notif = process_notification_actions(action, fluents)
            if notif:
                notifications.append(notif)
        print("Notifications found:", notifications)

        return parsed, notifications if parsed else False

    except (KeyError, IndexError, TypeError):
        return False

def insert_problem(data):
    req_body = {
        'domain': pt.get_domain_data(),
        'problem': pt.get_problem_file_with_data(unrendered_data=data)
    }
    problem_name = "problem_" + str(time.time())
    solve_request_url = requests.post(
        "https://solver.planning.domains:5001/package/enhsp/solve", json=req_body
    ).json()

    # Query the result
    result = requests.post('https://solver.planning.domains:5001' + solve_request_url['result'])

    while result.json().get("status", "") == 'PENDING':
        # Query the result every 0.5 seconds while the job is executing
        result = requests.post('https://solver.planning.domains:5001' + solve_request_url['result'])
        time.sleep(0.5)

    parsed_plan, notifications = parse_enhsp_output(result.json(), data['fluents'])
    plan_id = -1
    if parsed_plan:
        plan_id = db.insert_pddl_problem(problem_name, req_body['problem'], parsed_plan)
        parsed_plan['PLAN_ID'] = plan_id

    # Store notifications in Redis cache
    if notifications:
        redis_client.set(NOTIFICATIONS_KEY, json.dumps(notifications))

    return plan_id, parsed_plan, notifications

def ai_fun():
    #insert_problem()
    return "Hello, AI Planning"