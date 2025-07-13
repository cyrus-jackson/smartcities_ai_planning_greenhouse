;!pre-parsing:{type: "jinja2", data: "improved_greenhouse_case.json"}

(define (problem {{ data.name }})
  (:domain greenhouse)

  (:objects
    {% for type, objects in data.objects.items() %}
    {% for obj in objects %}{{ obj }}{% if not loop.last %} {% endif %}{% endfor %} - {{ type }}
    {% endfor %}
  )

  (:init
    ;; Numeric fluents from sensors
    {% for key, value in data.fluents.items() %}
    (= ({{ key }}) {{ value }})
    {% endfor %}

    ;; Initial boolean predicates
    {% for fact in data.init %}
    {% if fact.startswith('fan_off') %}
    ;; Fan starts off (not (fan_on) is implicit)
    {% elif fact.startswith('roof_open') %}
    ({{ fact }})
    {% elif fact.startswith('roof_closed') %}
    ;; Roof closed means not open: (not (roof_open {{ fact.split()[1] }}))
    {% else %}
    ({{ fact }})
    {% endif %}
    {% endfor %}
  )

  (:goal 
    (and 
      {% for goal in data.goals %}
      {% if goal.type == "and" %}
      {% for state in goal.states %}
      ({{ state }})
      {% endfor %}
      {% elif goal.type == "or" %}
      (or
        {% for state in goal.states %}
        ({{ state }})
        {% endfor %}
      )
      {% endif %}
      {% endfor %}
    )
  )
)