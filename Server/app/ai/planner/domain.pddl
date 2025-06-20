(define (domain greenhouse)

  (:requirements :strips :typing :negative-preconditions)

  (:types
    measurement
    time
  )

  (:predicates
    (alert-warning)
    (alert-high)
  )

  (:functions 
    (water-tank-level)
    (hours-until-rain)
  )

  (:action issue_high_alert
    :parameters ()
    :precondition (and
      (> (hours-until-rain) 30)
      (< (water-tank-level) 10)
    )
    :effect (alert-high)
  )

  (:action issue_warning
    :parameters ()
    :precondition (and
      (> (hours-until-rain) 30)
      (< (water-tank-level) 30)
    )
    :effect (alert-warning)
  )

)