# app/routes.py

from app import app
from flask import request, jsonify, render_template, current_app

from .ai import pddl as ai
from app.db.sqldb import get_last_n_pddl_problems, get_recent_weather_forecast, check_control_panel_password, get_all_configs, update_config_in_db
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
    plans = get_last_n_pddl_problems(10)
    return render_template('plans_view.html', domain=domain_content, plans=plans)


@app.route('/data', methods=['GET'])
def get_data():
    interval = request.args.get("interval", "1h")  # "15m", "30m", or "1h"
    raw_data = get_sensor_timeseries_data(interval)
    # Map backend keys
    mapped_data = {
        "temperature": raw_data.get("temperature-reading ts1", []),
        "humidity": raw_data.get("humidity-reading hs1", []),
        "soil_moisture": raw_data.get("soil_moisture ss", []),
        "water_tank_level": raw_data.get("water_tank_level wl", []),
        "PLAN_ID": raw_data.get("PLAN_ID", []),
    }
    mapped_data['weather'] = get_recent_weather_forecast()
    mapped_data["notifications"] = [{"message": "Fan turned on", "type": "success"}]
    return jsonify(mapped_data)

@app.route('/notifications', methods=['GET'])
def get_notifications():
    return_data = {}
    return_data["notifications"] = ai.get_current_notifications()
    return_data["currentStates"] = ai.get_current_states()
    return_data["rainTime"] = ai.get_rain_hours()
    return_data["waterLevel"] = ai.get_water_tank_level()
    # Add configs to the response
    return_data["configs"] = get_all_configs()
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
                
                # Special handling for humidity
                if action.lower().startswith("humidity"):
                    try:
                        humidity = int(action.split()[-1])
                        if 0 <= humidity <= 100:
                            action_str = f"humidity {humidity}"
                        else:
                            raise ValueError("Humidity must be between 0 and 100")
                    except ValueError as e:
                        message = f"Invalid humidity value: {str(e)}"
                        return render_template('control_panel.html', message=message)
                else:
                    action_str = action
                
                # Send as dict with PLAN_ID and action key for client compatibility
                msg = {"PLAN_ID": 0, "action": action_str}
                with RabbitMQHelper() as helper:
                    helper.send_message(planner_queue, json.dumps(msg))
                
                message = f"Action '{action}' executed successfully!"
            else:
                message = "Invalid password."
                
        except Exception as e:
            message = f"Error executing action: {str(e)}"
            print(f"Control panel error: {str(e)}")
                
    return render_template('control_panel.html', message=message)

@app.route('/configs')
def configs():
    configs = get_all_configs()
    return render_template('configs.html', configs=configs)

@app.route('/update_config', methods=['POST'])
def update_config():
    try:
        data = request.get_json()
        name = data.get('name')
        value = float(data.get('value'))
        password = data.get('password', '')
        if not check_control_panel_password(password):
            return jsonify({"status": "error", "message": "Invalid password."}), 401
        if update_config_in_db(name, value):
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Failed to update config"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


