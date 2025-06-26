# app/routes.py

from app import app
from flask import request, jsonify

from .ai import pddl as ai
from .tasks import long_running_task
from .celery_worker import celery


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




@app.route('/run-task', methods=['POST'])
def run_task():
    data = request.get_json()
    x = data.get('x', 0)
    y = data.get('y', 0)
    task = long_running_task.apply_async(args=[x, y])
    return jsonify({"task_id": task.id}), 202

@app.route('/task-status/<task_id>')
def task_status(task_id):
    task = celery.AsyncResult(task_id)
    return jsonify({
        "state": task.state,
        "result": task.result
    })