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
    (keep_greenhouse_comfortable)
    (expecting_rain)
  )

  (:functions 
    (water_tank_level)
    (hours_until_rain)
    (temperature)
    (humidity)
  )

;-------------------------------
; Meta-goal Action
;-------------------------------

  (:action keep_greenhouse_comfortable
    :parameters ()
    :precondition (and
      ;; Alert precondition based on fluent value ranges
      (or
        (and (> (hours_until_rain) 30) (<= (water_tank_level) 10) (alert-high))
        (and (> (hours_until_rain) 30) (> (water_tank_level) 10) (<= (water_tank_level) 50) (alert-warning))
        (and (> (water_tank_level) 50) (no_alert))
        (expecting_rain) ; <-- new branch
      )

      ;; Fan preconditions
      (or
        (and (fan_on) (or (> (temperature) 24) (> (humidity) 10)))
        (and (fan_off) (<= (temperature) 24) (<= (humidity) 10))
      )

      ;; Servo preconditions
      (forall (?s - servo)
        (or
          (and (outside_environment_safe) (fan_on) (run_servo ?s))
          (and (not (outside_environment_safe)) (close_servo ?s))
          (and (outside_environment_safe) (fan_off) (close_servo ?s))
        )
      )
    )
    :effect (keep_greenhouse_comfortable)
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
      (not (outside_environment_safe))
      (or
        (run_servo ?x)
        (fan_off)
      )
    )
    :effect (and 
      (close_servo ?x)
      (not (run_servo ?x))
    )
  )

  (:action expecting_rain_alert
    :parameters ()
    :precondition (and
      (<= (hours_until_rain) 30)
      (<= (water_tank_level) 10)
    )
    :effect (expecting_rain)
  )

  (:action expecting_rain_warning
    :parameters ()
    :precondition (and
      (<= (hours_until_rain) 30)
      (> (water_tank_level) 10)
      (<= (water_tank_level) 50)
    )
    :effect (expecting_rain)
  )

)