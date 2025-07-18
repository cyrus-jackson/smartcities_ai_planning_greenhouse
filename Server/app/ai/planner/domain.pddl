(define (domain greenhouse)
  (:requirements :strips :typing :numeric-fluents)
  (:types
    actuator sensor - object
    fan servo motor - actuator
    alert-level
  )

  (:predicates
    ;; Actuator states
    (fan_on ?f - fan)
    (servo_on ?s - servo)
    (water_pump_on ?m - motor)

    ;; Comfort state predicates
    (temperature_comfortable)
    (humidity_comfortable)
    (soil_moisture_adequate)

    ;; Assessment markers
    (temperature_assessed)
    (humidity_assessed)
    (soil_assessed)
    (water_managed)

    ;; Alerts
    (alert_issued ?level - alert-level)

    ;; Global completion marker
    (all_conditions_assessed)
  )

  (:functions
    ;; Climate sensor readings
    (temperature-reading ?ts - sensor)
    (temperature-threshold)

    (humidity-reading ?hs - sensor)
    (humidity-threshold)

    ;; Soil and water
    (soil_moisture ?ss - sensor)
    (soil_moisture_threshold)

    (water_tank_level ?wl - sensor)
    (water_level_threshold)

    ;; Fan/servo parameters
    (cooling-rate ?f - fan)
    (required-duration ?f - fan)

    (servo-cooling-rate ?s - servo)
    (servo-duration ?s - servo)

    (hours_until_rain)

    ;; Water alert thresholds (configurable)
    (water_alert_high_threshold)
    (water_alert_warning_threshold)
    (rain_expected_threshold)

    ;; Optimization cost
    (total-cost)
  )

  ;; === FAN ACTIONS ===
  (:action turn_on_fan
    :parameters (?ts - sensor ?hs - sensor ?f - fan)
    :precondition (and
      (not (fan_on ?f))
      (or
        (>= (temperature-reading ?ts) (temperature-threshold))
        (>= (humidity-reading ?hs) (humidity-threshold))
      )
    )
    :effect (and
      (fan_on ?f)
      (decrease (temperature-reading ?ts)
        (* (cooling-rate ?f) (required-duration ?f)))
      (decrease (humidity-reading ?hs)
        (* (cooling-rate ?f) (required-duration ?f)))
      (increase (total-cost) 15)
    )
  )

  (:action turn_off_fan
    :parameters (?ts - sensor ?hs - sensor ?f - fan)
    :precondition (and
      (fan_on ?f)
      (< (temperature-reading ?ts) (temperature-threshold))
      (< (humidity-reading ?hs) (humidity-threshold))
      (all_conditions_assessed)
    )
    :effect (not (fan_on ?f))
  )

  ;; === SERVO / ROOF ACTIONS ===
  (:action open_roof
    :parameters (?ts - sensor ?hs - sensor ?s - servo)
    :precondition (and
      (not (servo_on ?s))
      (or
        (>= (temperature-reading ?ts) (temperature-threshold))
        (>= (humidity-reading ?hs) (humidity-threshold))
      )
    )
    :effect (and
      (servo_on ?s)
      (decrease (temperature-reading ?ts)
        (* (servo-cooling-rate ?s) (servo-duration ?s)))
      (decrease (humidity-reading ?hs)
        (* (servo-cooling-rate ?s) (servo-duration ?s)))
      (increase (total-cost) 10)
    )
  )

  (:action close_roof
    :parameters (?ts - sensor ?hs - sensor ?s - servo)
    :precondition (and
      (servo_on ?s)
      (< (temperature-reading ?ts) (temperature-threshold))
      (< (humidity-reading ?hs) (humidity-threshold))
      (all_conditions_assessed)
    )
    :effect (and
      (not (servo_on ?s))
      (increase (total-cost) 1)
    )
  )

  ;; === PUMP ACTIONS ===
  (:action turn_on_pump
    :parameters (?ss - sensor ?wl - sensor ?m - motor)
    :precondition (and 
      (not (water_pump_on ?m))
      (>= (water_tank_level ?wl) (water_level_threshold))
      (< (soil_moisture ?ss) (soil_moisture_threshold))
    )
    :effect (and 
      (water_pump_on ?m)
      (increase (soil_moisture ?ss) 10)
      (increase (total-cost) 5)
    )
  )

  (:action turn_off_pump
    :parameters (?ss - sensor ?wl - sensor ?m - motor)
    :precondition (and 
      (water_pump_on ?m)
      (or
        (< (water_tank_level ?wl) (water_level_threshold))
        (>= (soil_moisture ?ss) (soil_moisture_threshold))
      )
      (all_conditions_assessed)
    )
    :effect (not (water_pump_on ?m))
  )

  ;; ====================
  ;; WATER MANAGEMENT ACTIONS
  ;; ====================

  (:action issue_high_alert
    :parameters (?wl - sensor)
    :precondition (and
      (> (hours_until_rain) (rain_expected_threshold))
      (<= (water_tank_level ?wl) (water_alert_high_threshold))
    )
    :effect (alert_issued high)
  )

  (:action issue_warning
    :parameters (?wl - sensor)
    :precondition (and
      (> (hours_until_rain) (rain_expected_threshold))
      (> (water_tank_level ?wl) (water_alert_high_threshold))
      (<= (water_tank_level ?wl) (water_alert_warning_threshold))
    )
    :effect (alert_issued warning)
  )

  (:action issue_no_alert
    :parameters (?wl - sensor)
    :precondition (and
      (> (water_tank_level ?wl) (water_alert_warning_threshold))
    )
    :effect (alert_issued none)
  )

  (:action expecting_rain_alert
    :parameters (?wl - sensor)
    :precondition (<= (hours_until_rain) (rain_expected_threshold))
    :effect (alert_issued rain-expected)
  )

  (:action issue_low_water_alert
    :parameters (?wl - sensor ?ss - sensor)
    :precondition (and
      (< (water_tank_level ?wl) (water_level_threshold))
      (< (soil_moisture ?ss) (soil_moisture_threshold))
    )
    :effect (alert_issued low-water)
  )

  (:action confirm_water_managed
    :parameters ()
    :precondition (and
      (not (water_managed))
      (exists (?level - alert-level) (alert_issued ?level))
    )
    :effect (water_managed)
  )

  ;; === COMFORT ASSESSMENTS ===
  (:action assess_temperature_comfort
    :parameters (?ts - sensor)
    :precondition (and
      (not (temperature_comfortable))
      (<= (temperature-reading ?ts) (temperature-threshold))
    )
    :effect (and
      (temperature_comfortable)
      (temperature_assessed)
    )
  )

  (:action assess_humidity_comfort
    :parameters (?hs - sensor)
    :precondition (and
      (not (humidity_comfortable))
      (<= (humidity-reading ?hs) (humidity-threshold))
    )
    :effect (and
      (humidity_comfortable)
      (humidity_assessed)
    )
  )

  (:action assess_soil_moisture_adequacy
    :parameters (?ss - sensor)
    :precondition (and
      (not (soil_moisture_adequate))
      (>= (soil_moisture ?ss) (soil_moisture_threshold))
    )
    :effect (and
      (soil_moisture_adequate)
      (soil_assessed)
    )
  )

  (:action assess_soil_moisture_blocked
    :parameters (?ss - sensor ?wl - sensor)
    :precondition (and
      (not (soil_moisture_adequate))
      (< (soil_moisture ?ss) (soil_moisture_threshold))
      (< (water_tank_level ?wl) (water_level_threshold))
      (alert_issued low-water)
    )
    :effect (and
      (soil_moisture_adequate)
      (soil_assessed)
    )
  )

  ;; === FINALIZATION ===
  (:action finalize_assessment
    :parameters ()
    :precondition (and
      (temperature_assessed)
      (humidity_assessed)
      (soil_assessed)
    )
    :effect (all_conditions_assessed)
  )
)