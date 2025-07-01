# app/routes.py

from app import app
from flask import request, jsonify, render_template

from .ai import pddl as ai
from .tasks import long_running_task
from app.db.sqldb import get_last_n_pddl_problems


items = []

@app.route('/')
def hello():
    text = ai.ai_fun()
    return text

@app.route('/items', methods=['GET'])
def get_items():
    return {'items': items}

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    if item_id < len(items):
        return {'item': items[item_id]}
    else:
        return {'error': 'Item not found'}, 404

@app.route('/items', methods=['POST'])
def add_item():
    item = request.get_json()
    items.append(item)
    return {'message': 'Item added successfully'}, 201

@app.route('/plans')
def plans_view():
    # Load the domain file
    with open('app/ai/planner/domain.pddl', 'r') as f:
        domain_content = f.read()
    plans = get_last_n_pddl_problems(5)
    return render_template('plans_view.html', domain=domain_content, plans=plans)


