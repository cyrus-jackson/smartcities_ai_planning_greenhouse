;!pre-parsing:{type: "jinja2", data: "all_checks.json"}

(define (problem {{ data.name }})
  (:domain greenhouse)

  (:objects
    s1 s2 - servo
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

  (:goal (keep_greenhouse_comfortable))
)