;!pre-parsing:{type: "jinja2", data: "all_checks.json"}

(define (problem {{ data.name }})
  (:domain greenhouse)

  (:objects
    m1 - measurement
    t1 - time
    s1 s2 - servo
    temp - temperature
  )

  (:init
    ; Fluents
    {% for key, value in data.fluents.items() %}
    (= ({{ key }}) {{ value }})
    {% endfor %}

    ; Boolean predicates
    {% for fact in data.init %}
    ({{ fact }})
    {% endfor %}
  )

  (:goal
    (and
      {% for goal in data.goals %}
      ({{ goal.type }}
        {% for state in goal.states %}
        ({{ state }})
        {% endfor %}
      )
      {% endfor %}
    )
  )
)
