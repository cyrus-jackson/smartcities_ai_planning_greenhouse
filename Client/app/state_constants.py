PLAN_ID = "PLAN_ID"

# Planner states
PLANNER_FAN_ON = "turn_on_fan"
PLANNER_FAN_OFF = "turn_off_fan"
PLANNER_RUN_ROOF_SERVO_S1 = "open_roof s1"
PLANNER_RUN_ROOF_SERVO_S2 = "open_roof s2"
PLANNER_CLOSE_ROOF_SERVO_S1 = "close_roof s1"
PLANNER_CLOSE_ROOF_SERVO_S2 = "close_roof s2"
PLANNER_WATER_PUMP_ON = "turn_on_pump"
PLANNER_WATER_PUMP_OFF = "turn_off_pump"
PLANNER_HUMIDITY_CHANGE = "humidity"

# Planner states (predicates)
FAN_ON = "fan_on fan1 "
FAN_OFF = "not (fan_on fan1)"
RUN_ROOF_SERVO_S1 = "servo_on s1"
RUN_ROOF_SERVO_S2 = "servo_on s2"
CLOSE_ROOF_SERVO_S1 = "not (servo_on s1)"
CLOSE_ROOF_SERVO_S2 = "not (servo_on s2)"
WATER_PUMP_ON = "water_pump_on mp1"
WATER_PUMP_OFF = "not (water_pump_on mp1)"

# Fluent names (match PDDL and JSON)
TEMPERATURE_READING = "temperature-reading ts1"
TEMPERATURE_THRESHOLD = "temperature-threshold"
HUMIDITY_READING = "humidity-reading hs1"
HUMIDITY_THRESHOLD = "humidity-threshold"
SOIL_MOISTURE_READING = "soil_moisture ss"
SOIL_MOISTURE_THRESHOLD = "soil_moisture_threshold"
WATER_TANK_LEVEL = "water_tank_level wl"
WATER_LEVEL_THRESHOLD = "water_level_threshold"
COOLING_RATE_FAN1 = "cooling-rate fan1"
REQUIRED_DURATION_FAN1 = "required-duration fan1"
SERVO_COOLING_RATE_S1 = "servo-cooling-rate s1"
SERVO_DURATION_S1 = "servo-duration s1"
TOTAL_COST = "total-cost"
HOURS_UNTIL_RAIN = "hours_until_rain"
WATER_ALERT_HIGH_THRESHOLD = "water_alert_high_threshold"
WATER_ALERT_WARNING_THRESHOLD = "water_alert_warning_threshold"
RAIN_EXPECTED_THRESHOLD = "rain_expected_threshold"

# Notification/alert predicates
ISSUE_HIGH_ALERT = "issue_high_alert"
ISSUE_WARNING = "issue_warning"
ISSUE_NO_ALERT = "issue_no_alert"
EXPECTING_RAIN_WARNING = "expecting_rain_warning"
EXPECTING_RAIN_ALERT = "expecting_rain_alert"

DEFAULT_STATE = {
    FAN_OFF: 1,
    FAN_ON: 0,
    RUN_ROOF_SERVO_S1: 0,
    RUN_ROOF_SERVO_S2: 0,
    CLOSE_ROOF_SERVO_S1: 1,
    CLOSE_ROOF_SERVO_S2: 1,
    WATER_PUMP_OFF: 1,
    WATER_PUMP_ON: 0,
    PLAN_ID: 0
}

NOTIFICATIONS = [
    ISSUE_HIGH_ALERT, ISSUE_WARNING,
    ISSUE_NO_ALERT, EXPECTING_RAIN_WARNING,
    EXPECTING_RAIN_ALERT
]

INFO_MESSAGES = {
    'assess_humidity_comfort': 'Assessing humidity comfort level',
    'assess_temperature_comfort': 'Assessing temperature comfort level',
    'establish_climate_optimality': 'Climate conditions are optimal',
    'confirm_water_managed': 'Water management status confirmed',
    'expecting_rain_alert': 'Rain is expected soon',
    'configure_roof_for_protection': 'Configuring roof for protection',
    'configure_roof_for_ventilation': 'Configuring roof for ventilation'
}