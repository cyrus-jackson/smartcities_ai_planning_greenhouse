(define (domain greenhouse)

  (:requirements :strips :typing :negative-preconditions :numeric-fluents)

  (:types
    servo
  )

  (:predicates
    ;; Equipment states
    (fan_on)
    (roof_open ?s - servo)
    
    ;; Environment conditions
    (outside_environment_safe)
    (climate_controlled)
    
    ;; Alert states
    (water_alert_handled)
    
    ;; Main goal
    (keep_greenhouse_comfortable)
  )

  (:functions 
    (water_tank_level)
    (hours_until_rain)
    (temperature)
    (humidity)
  )

  ;; ====================
  ;; CLIMATE CONTROL ACTIONS
  ;; ====================
  
  (:action turn_on_fan
    :parameters ()
    :precondition (and
      (not (fan_on))
      (or 
        (> (temperature) 24)
        (> (humidity) 10)
      )
    )
    :effect (fan_on)
  )

  (:action turn_off_fan
    :parameters ()
    :precondition (and
      (fan_on)
      (<= (temperature) 24)
      (<= (humidity) 10)
    )
    :effect (not (fan_on))
  )

  (:action establish_climate_control
    :parameters ()
    :precondition (and
      (not (climate_controlled))
      (or
        ;; Fan should be on if temp/humidity high
        (and (fan_on) (or (> (temperature) 24) (> (humidity) 10)))
        ;; Fan should be off if temp/humidity low
        (and (not (fan_on)) (<= (temperature) 24) (<= (humidity) 10))
      )
    )
    :effect (climate_controlled)
  )

  ;; ====================
  ;; ROOF CONTROL ACTIONS
  ;; ====================

  (:action open_roof
    :parameters (?s - servo)
    :precondition (and
      (not (roof_open ?s))
      (outside_environment_safe)
      (fan_on)
    )
    :effect (roof_open ?s)
  )

  (:action close_roof
    :parameters (?s - servo)
    :precondition (and
      (roof_open ?s)
      (or
        (not (outside_environment_safe))
        (not (fan_on))
      )
    )
    :effect (not (roof_open ?s))
  )

  ;; ====================
  ;; NOTIFICATION ACTIONS
  ;; ====================

  (:action issue_high_alert
    :parameters ()
    :precondition (and
      (> (hours_until_rain) 30)
      (<= (water_tank_level) 10)
      (not (water_alert_handled))
    )
    :effect (water_alert_handled)
  )

  (:action issue_warning
    :parameters ()
    :precondition (and
      (> (hours_until_rain) 30)
      (> (water_tank_level) 10)
      (<= (water_tank_level) 50)
      (not (water_alert_handled))
    )
    :effect (water_alert_handled)
  )

  (:action issue_no_alert
    :parameters ()
    :precondition (and
      (> (water_tank_level) 50)
      (not (water_alert_handled))
    )
    :effect (water_alert_handled)
  )

  (:action expecting_rain_alert
    :parameters ()
    :precondition (and
      (<= (hours_until_rain) 30)
      (not (water_alert_handled))
    )
    :effect (water_alert_handled)
  )

  ;; ====================
  ;; MAIN GOAL ACTION
  ;; ====================
  
  (:action achieve_greenhouse_comfort
    :parameters ()
    :precondition (and
      ;; Climate must be controlled
      (climate_controlled)
      
      ;; Water alerts must be handled
      (water_alert_handled)
      
      ;; Roof servos must be in correct state
      (forall (?s - servo)
        (or
          ;; Case 1: Safe environment + fan on and roof open
          (and (outside_environment_safe) (fan_on) (roof_open ?s))
          ;; Case 2: Unsafe environment and roof closed
          (and (not (outside_environment_safe)) (not (roof_open ?s)))
          ;; Case 3: Fan off and roof closed
          (and (not (fan_on)) (not (roof_open ?s)))
        )
      )
    )
    :effect (keep_greenhouse_comfortable)
  )
)
