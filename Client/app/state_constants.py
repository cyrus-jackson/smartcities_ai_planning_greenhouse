PLAN_ID = "PLAN_ID"

FAN_ON = "fan_on"
FAN_OFF = "fan_off"


RUN_ROOF_SERVO_S1 = "run_servo s1"
RUN_ROOF_SERVO_S2 = "run_servo s2"
CLOSE_ROOF_SERVO_S1 = "close_servo s1"
CLOSE_ROOF_SERVO_S2 = "close_servo s2"

WATER_PUMP_ON = "water_pump_on"
WATER_PUMP_OFF = "water_pump_off"

HUMIDITY = "humidity"
TEMPERATURE = "temperature"
SOIL_MOISTURE = "soil_moisture"
WATER_LEVEL = "water_tank_level"

ISSUE_HIGH_ALERT = "issue_high_alert"
ISSUE_WARNING = "issue_warning"
ISSUE_NO_ALERT = "issue_no_alert"
EXPECTING_RAIN_WARNING = "expecting_rain_warning"
EXPECTING_RAIN_ALERT = "expecting_rain_alert"

DEFAULT_STATE = {
    CLOSE_ROOF_SERVO_S1: 1, 
    CLOSE_ROOF_SERVO_S2: 1, 
    RUN_ROOF_SERVO_S1: 0,
    RUN_ROOF_SERVO_S2: 0,
    FAN_OFF: 1,
    FAN_ON: 0,
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