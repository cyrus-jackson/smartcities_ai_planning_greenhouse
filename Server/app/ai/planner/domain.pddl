(define (domain greenhouse)
 (:requirements :strips :typing :numeric-fluents)
 (:types
  actuator sensor - object
  fan servo - actuator
 )
 (:predicates
  (fan_on ?f - fan)
  (servo_on ?s - servo)
 )
 (:functions
  (temperature-reading ?ts - sensor)
  (temperature-threshold)
  (humidity-reading ?hs - sensor)
  (humidity-threshold)
  (cooling-rate ?f - fan)
  (required-duration ?f - fan)
  (servo-cooling-rate ?s - servo)
  (servo-duration ?s - servo)
  (total-cost)
 )

 ;; Fan actions - work independently
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
    (* (required-duration ?f) (cooling-rate ?f)))
   (decrease (humidity-reading ?hs)
    (* (required-duration ?f) (cooling-rate ?f)))
   (increase (total-cost) 10)
  )
 )

 (:action turn_off_fan
  :parameters (?ts - sensor ?hs - sensor ?f - fan)
  :precondition (and
   (fan_on ?f)
   (< (temperature-reading ?ts) (temperature-threshold))
   (< (humidity-reading ?hs) (humidity-threshold))
  )
  :effect (and
   (not (fan_on ?f))
   (increase (total-cost) 1)
  )
 )

 ;; Servo/roof actions - work independently
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
    (* (servo-duration ?s) (servo-cooling-rate ?s)))
   (decrease (humidity-reading ?hs)
    (* (servo-duration ?s) (servo-cooling-rate ?s)))
   (increase (total-cost) 10)
  )
 )

 (:action close_roof
  :parameters (?ts - sensor ?hs - sensor ?s - servo)
  :precondition (and
   (servo_on ?s)
   (< (temperature-reading ?ts) (temperature-threshold))
   (< (humidity-reading ?hs) (humidity-threshold))
  )
  :effect (and
   (not (servo_on ?s))
   (increase (total-cost) 1)
  )
 )
)