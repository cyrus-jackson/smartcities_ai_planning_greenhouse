;!pre-parsing:{type: "jinja2", data: "static.json"}

(define (problem {{data.name}})
  (:domain greenhouse)

  (:objects
    m1 - measurement
    t1 - time
  )

  (:init
    (= (hours-until-rain) {{data.hours_until_rain}})
    (= (water-tank-level) {{data.water_tank_level}})
  )

  (:goal
    {% for goal in data.goals %}
      ({{ goal.type }}
        {% for s in goal.states %}
          ({{ s }})
        {% endfor %}
      )
    {% endfor %}
  )
)
