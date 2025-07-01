import app.utils.state_constants as states
from datetime import datetime, timezone
import pandas as pd
import os
import certifi
from influxdb_client_3 import InfluxDBClient3, Point, flight_client_options

token = os.environ.get("INFLUXDB_TOKEN")
org = os.environ.get("INFLUXDB_ORG")
host = os.environ.get("INFLUXDB_HOST")
database = os.environ.get("INFLUXDB_DATABASE")

fh = open(certifi.where(), "r")
cert = fh.read()
fh.close()

sample_data = {
    "name": "all_checks_case",
    "fluents": {
        "hours_until_rain": 40,
        "water_tank_level": 70,
        "temperature": 50,
        "humidity": 5
    },
    "init": [
        "outside_environment_safe",
        "close_servo s1",
        "run_servo s2",
        "fan_on"
    ],
    "goals": [
        {
            "type": "or",
            "states": ["keep_greenhouse_comfortable"]
        }
    ]
}

def validate_fluents(fluents):
    for key in sample_data["fluents"]:
        if key not in fluents or fluents[key] is None:
            fluents[key] = 1
    return fluents

# Singleton pattern for InfluxDBClient3
class _InfluxSingleton:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = InfluxDBClient3(host=host, 
                                          token=token, 
                                          org=org, 
                                          flight_client_options 
                                          = flight_client_options(tls_root_certs=cert))
        return cls._client

def get_latest_plan_id(client):
    query = f'''
        SELECT * FROM "greenhouse_sensors" ORDER BY time DESC LIMIT 1
    '''
    result = client.query(query, database=database)
    
    df = result.to_pandas()
    plan_id = df[states.PLAN_ID][0] if len(df[states.PLAN_ID]) > 0 else None
    return plan_id

def get_temperature_humidity_means(client, plan_id):
    fluents = {}
    for fluent in [states.TEMPERATURE, states.HUMIDITY]:
        query = f'''
            SELECT AVG("{fluent}") FROM "greenhouse_sensors"
            WHERE "{states.PLAN_ID}" = '{plan_id}'
        '''
        result = client.query(query, database=database)
        df = result.to_pandas()
        col_name = f'avg(greenhouse_sensors.{fluent})'
        if not df.empty and col_name in df.columns:
            value = df[col_name].iloc[0]
            if value is not None:
                fluents[fluent] = float(value)
    return fluents

def get_latest_hours_until_rain(client):
    query = '''
        SELECT * FROM "hours_until_rain" ORDER BY time DESC LIMIT 1
    '''
    result = client.query(query, database=database)
    df = result.to_pandas()
    if not df.empty and "hours_until_rain" in df.columns and "time" in df.columns:
        value = df["hours_until_rain"].iloc[0]
        ts = df["time"].iloc[0]
        if value is not None and ts is not None:
            now = datetime.now(timezone.utc)
            if not isinstance(ts, pd.Timestamp):
                ts = pd.to_datetime(ts)
            if ts.tzinfo is None:
                ts = ts.tz_localize('UTC')
            hours_since = (now - ts).total_seconds() / 3600.0
            hours_until_rain = max(0, float(value) - hours_since)
            hours_until_rain = round(hours_until_rain, 2)
            return hours_until_rain
    return None

def get_fluent_means(client, plan_id):
    fluents = get_temperature_humidity_means(client, plan_id)
    hours_until_rain = get_latest_hours_until_rain(client)
    if hours_until_rain is not None:
        fluents["hours_until_rain"] = hours_until_rain
    fluents = validate_fluents(fluents)
    return fluents

def get_init_state(client, plan_id):
    query = f'''
        SELECT * FROM "greenhouse_state"
        WHERE "{states.PLAN_ID}" = '{plan_id}'
        ORDER BY time DESC
        LIMIT 1
    '''
    init = []
    result = client.query(query, database=database)
    df = result.to_pandas()
    if not df.empty:
        for key, value in states.DEFAULT_STATE.items():
            # Only include if column exists and value is 1 in the latest row
            if key in df.columns and df[key].iloc[0] == 1:
                init.append(key)
    return init

def get_data():
    # return sample_data
    client = _InfluxSingleton.get_client()
    plan_id = get_latest_plan_id(client)
    if plan_id is None:
        return sample_data

    fluents = get_fluent_means(client, plan_id)
    init = get_init_state(client, plan_id)
    data = {
        "name": f"plan_{plan_id}",
        "fluents": fluents,
        "init": init,
        "goals": sample_data["goals"],
    }
    print(data)
    return data

def insert_hours_until_rain(data):
    try:
        client = _InfluxSingleton.get_client()
        probabilities = data["hourly"]["precipitation_probability"]
        hours_until_rain = None
        for idx, prob in enumerate(probabilities):
            if prob > 10:
                hours_until_rain = idx  # hours from now
                break
        if hours_until_rain is not None:
            point = (
                Point("hours_until_rain")
                .field("hours_until_rain", hours_until_rain)
            )
            client.write(database=database, record=point)
            print(f"Inserted hours_until_rain={hours_until_rain} into timeseriesdb.")
        else:
            print("No rain expected in the forecast period (precipitation_probability > 10% not found).")
    except Exception as e:
        print(f"Error inserting hours_until_rain into timeseriesdb: {e}")


def write_sensor_data(message_list):
    client = _InfluxSingleton.get_client()
    points = []
    for message in message_list:
        point = (
            Point("greenhouse_sensors")
            .field(states.HUMIDITY, message[states.HUMIDITY])
            .field(states.TEMPERATURE, message[states.TEMPERATURE])
            .field(states.SOIL_MOISTURE, message[states.SOIL_MOISTURE])
        )
        # if message.get("plan_id") is not None:
        point = point.tag(states.PLAN_ID, message[states.PLAN_ID])
        points.append(point)
    print(f"Writing to tdb: {points}")
    client.write(database=database, record=points)

def write_state_data(message):
    print(f"The state message is: {message}")
    client = _InfluxSingleton.get_client()
    point = Point("greenhouse_state")
    for key, value in message.items():
        if key == states.PLAN_ID:
            point = point.tag(key, value)
        else:
            point = point.field(key, value)
    client.write(database=database, record=point)


# Singleton pattern
_InfluxSingleton.get_client()