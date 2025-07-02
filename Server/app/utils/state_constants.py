PLAN_ID = "PLAN_ID"

FAN_ON = "fan_on"
FAN_OFF = "fan_off"


RUN_ROOF_SERVO_S1 = "run_servo s1"
RUN_ROOF_SERVO_S2 = "run_servo s2"
CLOSE_ROOF_SERVO_S1 = "close_servo s1"
CLOSE_ROOF_SERVO_S2 = "close_servo s2"



HUMIDITY = "humidity"
TEMPERATURE = "temperature"
SOIL_MOISTURE = "soil_moisture"

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
    PLAN_ID: 0
}

NOTIFICATIONS = [
    ISSUE_HIGH_ALERT, ISSUE_WARNING, 
    ISSUE_NO_ALERT, EXPECTING_RAIN_WARNING, 
    EXPECTING_RAIN_ALERT
    ]