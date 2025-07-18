# Unified state_constants.py for both Client and Server

PLAN_ID = "PLAN_ID"

# Planner states
def _planner():
    return {
        'PLANNER_FAN_ON': "turn_on_fan",
        'PLANNER_FAN_OFF': "turn_off_fan",
        'PLANNER_RUN_ROOF_SERVO_S1': "open_roof s1",
        'PLANNER_RUN_ROOF_SERVO_S2': "open_roof s2",
        'PLANNER_CLOSE_ROOF_SERVO_S1': "close_roof s1",
        'PLANNER_CLOSE_ROOF_SERVO_S2': "close_roof s2",
        'PLANNER_WATER_PUMP_ON': "turn_on_pump",
        'PLANNER_WATER_PUMP_OFF': "turn_off_pump",
        'PLANNER_HUMIDITY_CHANGE': "humidity"
    }

# Planner states (predicates)
def _predicates():
    return {
        'FAN_ON': "fan_on fan1 ",
        'FAN_OFF': "not (fan_on fan1)",
        'RUN_ROOF_SERVO_S1': "servo_on s1",
        'RUN_ROOF_SERVO_S2': "servo_on s2",
        'CLOSE_ROOF_SERVO_S1': "not (servo_on s1)",
        'CLOSE_ROOF_SERVO_S2': "not (servo_on s2)",
        'WATER_PUMP_ON': "water_pump_on mp1",
        'WATER_PUMP_OFF': "not (water_pump_on mp1)"
    }

# Fluent names (match PDDL and JSON)
def _fluents():
    return {
        'TEMPERATURE_READING': "temperature-reading ts1",
        'TEMPERATURE_THRESHOLD': "temperature-threshold",
        'HUMIDITY_READING': "humidity-reading hs1",
        'HUMIDITY_THRESHOLD': "humidity-threshold",
        'SOIL_MOISTURE_READING': "soil_moisture ss",
        'SOIL_MOISTURE_THRESHOLD': "soil_moisture_threshold",
        'WATER_TANK_LEVEL': "water_tank_level wl",
        'WATER_LEVEL_THRESHOLD': "water_level_threshold",
        'COOLING_RATE_FAN1': "cooling-rate fan1",
        'REQUIRED_DURATION_FAN1': "required-duration fan1",
        'SERVO_COOLING_RATE_S1': "servo-cooling-rate s1",
        'SERVO_DURATION_S1': "servo-duration s1",
        'TOTAL_COST': "total-cost",
        'HOURS_UNTIL_RAIN': "hours_until_rain",
        'WATER_ALERT_HIGH_THRESHOLD': "water_alert_high_threshold",
        'WATER_ALERT_WARNING_THRESHOLD': "water_alert_warning_threshold",
        'RAIN_EXPECTED_THRESHOLD': "rain_expected_threshold"
    }

# Notification/alert predicates
def _alerts():
    return {
        'ISSUE_HIGH_ALERT': "issue_high_alert",
        'ISSUE_WARNING': "issue_warning",
        'ISSUE_NO_ALERT': "issue_no_alert",
        'EXPECTING_RAIN_WARNING': "expecting_rain_warning",
        'EXPECTING_RAIN_ALERT': "expecting_rain_alert"
    }

DEFAULT_STATE = {
    _predicates()['FAN_OFF']: 1,
    _predicates()['FAN_ON']: 0,
    _predicates()['RUN_ROOF_SERVO_S1']: 0,
    _predicates()['RUN_ROOF_SERVO_S2']: 0,
    _predicates()['CLOSE_ROOF_SERVO_S1']: 1,
    _predicates()['CLOSE_ROOF_SERVO_S2']: 1,
    _predicates()['WATER_PUMP_OFF']: 1,
    _predicates()['WATER_PUMP_ON']: 0,
    PLAN_ID: 0
}

NOTIFICATIONS = [
    _alerts()['ISSUE_HIGH_ALERT'], _alerts()['ISSUE_WARNING'],
    _alerts()['ISSUE_NO_ALERT'], _alerts()['EXPECTING_RAIN_WARNING'],
    _alerts()['EXPECTING_RAIN_ALERT']
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

# Export all constants for import * usage
__all__ = [
    'PLAN_ID',
    *_planner().keys(),
    *_predicates().keys(),
    *_fluents().keys(),
    *_alerts().keys(),
    'DEFAULT_STATE',
    'NOTIFICATIONS',
    'INFO_MESSAGES'
]

# Flatten for direct import
globals().update(_planner())
globals().update(_predicates())
globals().update(_fluents())
globals().update(_alerts())
