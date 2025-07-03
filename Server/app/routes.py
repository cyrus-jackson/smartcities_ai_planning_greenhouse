# app/routes.py

from app import app
from flask import request, jsonify, render_template, current_app

from .ai import pddl as ai
from app.db.sqldb import get_last_n_pddl_problems
from app.db.timeseriesdb import get_sensor_timeseries_data



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
    data["notifications"] = [{"message": "Fan turned on", "type": "success"}]
    return jsonify(data)

@app.route('/notifications', methods=['GET'])
def get_notifications():
    return jsonify({"notifications": ai.get_current_notifications()})

@app.route('/control', methods=['GET', 'POST'])
def control_panel():
    message = ""
    if request.method == 'POST':
        password = request.form.get('password', '')
        action = request.form.get('action', '')
        if password == "admin123":
            message = f"Action '{action}' executed successfully!"
        else:
            message = "Invalid password."
    return render_template('control_panel.html', message=message)


