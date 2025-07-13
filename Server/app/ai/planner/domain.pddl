(define (domain greenhouse)

  (:requirements :strips :typing :negative-preconditions :numeric-fluents :existential-preconditions :universal-preconditions)

  (:types
    servo
    alert-level
  )

  (:predicates
    ;; Equipment states
    (fan_on)
    (roof_open ?s - servo)
    
    ;; Environment conditions
    (outside_environment_safe)
    (temperature_comfortable)
    (humidity_comfortable)
    (water_level_adequate)
    
    ;; Alert states
    (alert_issued ?level - alert-level)
    
    ;; Composite goals
    (climate_optimal)
    (water_managed)
    (roof_properly_configured)
  )

  (:functions 
    (water_tank_level)
    (hours_until_rain)
    (temperature)
    (humidity)
  )

  ;; ====================
  ;; BASIC EQUIPMENT ACTIONS
  ;; ====================
  
  (:action turn_on_fan
    :parameters ()
    :precondition (not (fan_on))
    :effect (fan_on)
  )

  (:action turn_off_fan
    :parameters ()
    :precondition (fan_on)
    :effect (not (fan_on))
  )

  (:action open_roof
    :parameters (?s - servo)
    :precondition (and
      (not (roof_open ?s))
      (outside_environment_safe)
    )
    :effect (roof_open ?s)
  )

  (:action close_roof
    :parameters (?s - servo)
    :precondition (roof_open ?s)
    :effect (not (roof_open ?s))
  )

  ;; ====================
  ;; COMFORT ASSESSMENT ACTIONS
  ;; ====================

  (:action assess_temperature_comfort
    :parameters ()
    :precondition (and
      (not (temperature_comfortable))
      (or
        ;; Temperature is good naturally
        (and (<= (temperature) 24) (not (fan_on)))
        ;; Temperature controlled by fan
        (and (> (temperature) 24) (fan_on))
      )
    )
    :effect (temperature_comfortable)
  )

  (:action assess_humidity_comfort
    :parameters ()
    :precondition (and
      (not (humidity_comfortable))
      (or
        ;; Humidity is good naturally
        (and (<= (humidity) 10) (not (fan_on)))
        ;; Humidity controlled by fan
        (and (> (humidity) 10) (fan_on))
      )
    )
    :effect (humidity_comfortable)
  )

  (:action establish_climate_optimality
    :parameters ()
    :precondition (and
      (not (climate_optimal))
      (temperature_comfortable)
      (humidity_comfortable)
    )
    :effect (climate_optimal)
  )

  ;; ====================
  ;; WATER MANAGEMENT ACTIONS
  ;; ====================

  (:action issue_high_alert
    :parameters ()
    :precondition (and
      (> (hours_until_rain) 30)
      (<= (water_tank_level) 10)
    )
    :effect (alert_issued high)
  )

  (:action issue_warning
    :parameters ()
    :precondition (and
      (> (hours_until_rain) 30)
      (> (water_tank_level) 10)
      (<= (water_tank_level) 50)
    )
    :effect (alert_issued warning)
  )

  (:action issue_no_alert
    :parameters ()
    :precondition (> (water_tank_level) 50)
    :effect (alert_issued none)
  )

  (:action expecting_rain_alert
    :parameters ()
    :precondition (<= (hours_until_rain) 30)
    :effect (alert_issued rain-expected)
  )

  (:action confirm_water_managed
    :parameters ()
    :precondition (and
      (not (water_managed))
      (exists (?level - alert-level) (alert_issued ?level))
    )
    :effect (water_managed)
  )

  ;; ====================
  ;; ROOF CONFIGURATION ACTIONS
  ;; ====================

  (:action configure_roof_for_ventilation
    :parameters ()
    :precondition (and
      (not (roof_properly_configured))
      (fan_on)
      (outside_environment_safe)
      (forall (?s - servo) (roof_open ?s))
    )
    :effect (roof_properly_configured)
  )

  (:action configure_roof_for_protection
    :parameters ()
    :precondition (and
      (not (roof_properly_configured))
      (or
        (not (outside_environment_safe))
        (not (fan_on))
      )
      (forall (?s - servo) (not (roof_open ?s)))
    )
    :effect (roof_properly_configured)
  )

)