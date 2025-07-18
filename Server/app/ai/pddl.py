import requests
import time
import logging
# Set up logging
logging.basicConfig(level=logging.INFO)
import re
import json
import redis
from .planner import pddl_transform as pt

from app.db import sqldb as db
import app.utils.state_constants as states
from app.utils.state_constants import NOTIFICATIONS


# Initialize Redis client here
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
NOTIFICATIONS_KEY = "latest_notifications"
CURRENT_STATES = "current_states"
RAIN_HOURS = "rain_hours"


def get_current_notifications():
    data = redis_client.get(NOTIFICATIONS_KEY)
    if data:
        return json.loads(data)
    return []

def get_current_states():
    data = redis_client.get(CURRENT_STATES)
    if data:
        return json.loads(data)
    return []

def get_rain_hours():
    data = redis_client.get(RAIN_HOURS)
    if data:
        return json.loads(data)
    return []

def get_water_tank_level():
    data = redis_client.get(states.WATER_TANK_LEVEL)
    if data:
        return json.loads(data)
    return []

def process_notification_actions(action, fluents):
    notif_types = {
        "issue_no_alert": ["success", "Water Tank has enough water"],
        "issue_warning": ["warning", "Water Tank Level is low. Rain is not expected soon"],
        "issue_high_alert": ["danger", "Fill the Water Tank immediately. Rain is not expected soon"],
        "expecting_rain_alert": ["info", "Rain is expected. Do not fill the tank"],
        "expecting_rain_warning": ["warning", "Water Tank Level is low. Rain is expected soon"]
    }
    if action in notif_types:
        message = notif_types[action][1]

        if fluents and "hours_until_rain" in fluents:
            message += f" (Rain in: {int(fluents['hours_until_rain'])} hours)"
        notif_type = notif_types[action][0]
        
        return {
            "message": message,
            "type": notif_type
        }
    logging.debug(f"Fluents: {fluents}")
    redis_client.set(states.WATER_TANK_LEVEL, fluents[states.WATER_TANK_LEVEL])
    return None

def parse_enhsp_output(response_json, fluents):
    logging.info("parse_enhsp_output")
    try:
        raw_output = response_json['result']['output']['plan']
        logging.error(raw_output)
        if "Found Plan:" not in raw_output:
            return False

        plan_steps = re.findall(r'(\d+\.\d+):\s+\(([^)]+)\)', raw_output)
        parsed = {}
        notifications = []
        logging.info(plan_steps)
        for step_num, action in plan_steps:
            action = action.strip()
            tokens = action.split()
            act = tokens[0]

            parsed[step_num] = action  # keep as-is for info/assessment actions

            # Process notification actions
            notif = process_notification_actions(act, fluents)
            if notif:
                notifications.append(notif)

        logging.info(f"Notifications found: {notifications}")
        return (parsed, notifications) if parsed else ({}, notifications)

    except (KeyError, IndexError, TypeError) as e:
        logging.exception("Exception in parse_enhsp_output:")
        return {}, []

def insert_problem(data):
    req_body = {
        'domain': pt.get_domain_data(),
        'problem': pt.get_problem_file_with_data(unrendered_data=data)
    }
    # logging.info(req_body['problem'])
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