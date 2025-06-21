(define (domain greenhouse)

  (:requirements :strips :typing :negative-preconditions :numeric-fluents)

  (:types
    measurement
    time
    temperature
    servo
  )

  (:predicates
    (alert-warning)
    (alert-high)
    (no_alert)
    (fan_on)
    (fan_off)
    (outside_environment_safe)
    (run_servo ?x - servo)
    (close_servo ?x - servo)
  )

  (:functions 
    (water_tank_level)
    (hours_until_rain)
    (temperature)
    (humidity)
  )

;-------------------------------
; Notifications
;-------------------------------

  (:action issue_high_alert
    :parameters ()
    :precondition (and
      (> (hours_until_rain) 30)
      (<= (water_tank_level) 10)
    )
    :effect (and
      (alert-high)
      (not (alert-warning))
      (not (no_alert))
    )
  )

  (:action issue_warning
    :parameters ()
    :precondition (and
      (> (hours_until_rain) 30)
      (> (water_tank_level) 10)
      (<= (water_tank_level) 50)
    )
    :effect (and
      (alert-warning)
      (not (alert-high))
      (not (no_alert))
    )
  )

  (:action issue_no_alert
    :parameters ()
    :precondition (and
      (> (water_tank_level) 50)
    )
    :effect (and
      (no_alert)
      (not (alert-warning))
      (not (alert-high))
    )
  )

;---------------------------------
; Fan Module
;---------------------------------

  (:action turn_on_fan
    :parameters ()
    :precondition (and
      (fan_off)
      (or 
        (> (temperature) 24)
        (> (humidity) 10)
      )
    )
    :effect (and 
      (fan_on)
      (not (fan_off))
    )
  )

  (:action turn_off_fan
    :parameters ()
    :precondition (and
      (fan_on)
      (<= (temperature) 24)
      (<= (humidity) 10)
    )
    :effect (and 
      (fan_off)
      (not (fan_on))
    )
  )

;--------------------------------
; Roof Servo
;--------------------------------

  (:action open_roof
    :parameters (?x - servo)
    :precondition (and
      (outside_environment_safe)
      (fan_on)
    )
    :effect (and 
      (run_servo ?x)
      (not (close_servo ?x))
    )
  )

  (:action close_roof
    :parameters (?x - servo)
    :precondition (or
      (run_servo ?x)
      (not (outside_environment_safe))
    )
    :effect (and 
      (close_servo ?x)
      (not (run_servo ?x))
    )
  )
  
)