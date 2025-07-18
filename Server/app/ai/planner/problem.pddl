(define (problem {{ data.name }})
 (:domain greenhouse)
 (:objects
{% for type, objects in data.objects.items() %}
{% for obj in objects %}
   {{ obj }} - {{ type }}
{% endfor %}
{% endfor %}
 )
 (:init
   ;; Numeric fluents from sensors
{% for key, value in data.fluents.items() %}
   (= ({{ key }}) {{ value }})
{% endfor %}
   ;; Initial boolean predicates
{% for fact in data.init %}
   ({{ fact }})
{% endfor %}
 )
 (:goal {% if data.goals|length == 1 %}{{ data.goals[0] }}{% else %}(and
{% for goal in data.goals %}
   {{ goal }}
{% endfor %}
 ){% endif %})
 (:metric minimize (total-cost))
)