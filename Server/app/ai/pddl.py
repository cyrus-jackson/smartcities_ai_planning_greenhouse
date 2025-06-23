import requests
import time
import os
from pprint import pprint
from .adaptor import planning_editor_adaptor
from .planner import pddl_transform as pt


req_body = {
    'domain': pt.get_domain_data(),
    'problem': pt.get_problem_file_with_data()
    }

print(req_body)

# req_body = {
# "domain":"(define (domain BLOCKS) (:requirements :strips) (:predicates (on ?x ?y) (ontable ?x) (clear ?x) (handempty) (holding ?x) ) (:action pick-up :parameters (?x) :precondition (and (clear ?x) (ontable ?x) (handempty)) :effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x))) (:action put-down :parameters (?x) :precondition (holding ?x) :effect (and (not (holding ?x)) (clear ?x) (handempty) (ontable ?x))) (:action stack :parameters (?x ?y) :precondition (and (holding ?x) (clear ?y)) :effect (and (not (holding ?x)) (not (clear ?y)) (clear ?x) (handempty) (on ?x ?y))) (:action unstack :parameters (?x ?y) :precondition (and (on ?x ?y) (clear ?x) (handempty)) :effect (and (holding ?x) (clear ?y) (not (clear ?x)) (not (handempty)) (not (on ?x ?y)))))",
# "problem":"(define (problem BLOCKS-4-0) (:domain BLOCKS) (:objects D B A C ) (:INIT (CLEAR C) (CLEAR A) (CLEAR B) (CLEAR D) (ONTABLE C) (ONTABLE A) (ONTABLE B) (ONTABLE D) (HANDEMPTY)) (:goal (AND (ON D C) (ON C B) (ON B A))) )"
# }

# # Send job request to solve endpoint
# solve_request_url=requests.post("https://solver.planning.domains:5001/package/lama-first/solve", json=req_body).json()

# # Query the result in the job
# result = requests.post('https://solver.planning.domains:5001' + solve_request_url['result'])

# print('Computing...')
# while result.json().get("status","")== 'PENDING':

#     # Query the result every 0.5 seconds while the job is executing
#     result=requests.post('https://solver.planning.domains:5001' + solve_request_url['result'])
#     time.sleep(0.5)

# pprint(result.json()['result']['output'])



def ai_fun():
    return "Hello, AI Planning"