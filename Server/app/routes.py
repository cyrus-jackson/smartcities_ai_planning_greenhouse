# app/routes.py

from app import app
from flask import request, jsonify, render_template, current_app

from .ai import pddl as ai
from app.db.sqldb import get_last_n_pddl_problems, get_recent_weather_forecast, check_control_panel_password
from app.db.timeseriesdb import get_sensor_timeseries_data, get_avg_tank_level_mean
from app.utils.rabbitmq_helper import RabbitMQHelper
from app.utils.config import load_config
import app.utils.state_constants as states
import psycopg2
import json
import os
from functools import wraps



items = []

@app.route('/home')
def hello():
    text = ai.ai_fun()
    return text


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/plans')
def plans_view():
    # Load the domain file
    with open('app/ai/planner/domain.pddl', 'r') as f:
        domain_content = f.read()
    plans = get_last_n_pddl_problems(5)
    return render_template('plans_view.html', domain=domain_content, plans=plans)


@app.route('/data', methods=['GET'])
def get_data():
    interval = request.args.get("interval", "1h")  # "15m", "30m", or "1h"
    data = get_sensor_timeseries_data(interval)
    data['weather'] = get_recent_weather_forecast()
    data["notifications"] = [{"message": "Fan turned on", "type": "success"}]
    return jsonify(data)

@app.route('/notifications', methods=['GET'])
def get_notifications():
    return_data = {}
    return_data["notifications"] = ai.get_current_notifications()
    return_data["currentStates"] = ai.get_current_states()
    return_data["rainTime"] = ai.get_rain_hours()
    return_data["waterLevel"] = ai.get_water_tank_level()
    return jsonify(return_data)

@app.route('/control', methods=['GET', 'POST'])
def control_panel():
    message = ""
    if request.method == 'POST':
        password = request.form.get('password', '')
        action = request.form.get('action', '')
        
        try:
            if check_control_panel_password(password):
                config = load_config()
                planner_queue = config["rabbitmq"].get("planner_queue", "planner_queue")
                
                # Map UI actions to state constants
                action_mapping = {
                    'Fan On': states.FAN_ON,
                    'Fan Off': states.FAN_OFF,
                }
                
                action = action_mapping.get(action, action)  # Use mapped action or original if not in mapping
                
                action_data = {
                    "action": action
                }
                
                
                if action.startswith("Humidity"):
                    try:
                        humidity = int(action.split()[-1])
                        if 0 <= humidity <= 100:
                            action_data["humidity"] = humidity
                        else:
                            raise ValueError("Humidity must be between 0 and 100")
                    except ValueError as e:
                        message = f"Invalid humidity value: {str(e)}"
                        return render_template('control_panel.html', message=message)
                
                # Send to planner queue
                with RabbitMQHelper() as helper:
                    helper.send_message(planner_queue, json.dumps(action_data))
                
                message = f"Action '{action}' executed successfully!"
            else:
                message = "Invalid password."
                
        except Exception as e:
            message = f"Error executing action: {str(e)}"
            print(f"Control panel error: {str(e)}")
                
    return render_template('control_panel.html', message=message)


