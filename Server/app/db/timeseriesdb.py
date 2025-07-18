import app.utils.state_constants as states
from datetime import datetime, timedelta, timezone

import pandas as pd
import os
import certifi
from influxdb_client_3 import InfluxDBClient3, Point, flight_client_options
from app.db.sqldb import get_all_configs

token = os.environ.get("INFLUXDB_TOKEN").strip()
org = os.environ.get("INFLUXDB_ORG").strip()
host = os.environ.get("INFLUXDB_HOST").strip()
database = os.environ.get("INFLUXDB_DATABASE").strip()

fh = open(certifi.where(), "r")
cert = fh.read()
fh.close()

sample_data = {
    "name": "greenhouse_problem",
    "fluents": {
        "temperature-threshold": 25,
        "temperature-reading ts1": 20,
        "humidity-threshold": 25,
        "humidity-reading hs1": 21,
        "soil_moisture ss": 30,
        "soil_moisture_threshold": 35,
        "cooling-rate fan1": 2,
        "required-duration fan1": 100,
        "servo-cooling-rate s1": 1,
        "servo-duration s1": 100,
        "total-cost": 0,
        "water_tank_level wl": 10,
        "water_level_threshold": 20,
        "hours_until_rain": 10,
        "water_alert_high_threshold": 10,
        "water_alert_warning_threshold": 50,
        "rain_expected_threshold": 30
    },
    "init": [
        "not (fan_on fan1)",
        "not (servo_on s1)"
    ],
    "goals": [
        "(temperature_comfortable)",
        "(humidity_comfortable)",
        "(soil_moisture_adequate)",
        "(water_managed)"
    ],
    "objects": {
        "sensor": ["ts1", "hs1", "ss", "wl"],
        "fan": ["fan1"],
        "servo": ["s1"],
        "motor": ["mp1"],
        "alert-level": ["high", "warning", "none", "rain-expected"]
    },
    "metric": "minimize"
    }

def validate_fluents(fluents):
    for key in sample_data["fluents"]:
        if key not in fluents or fluents[key] is None:
            fluents[key] = 30
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
    plan_id = df[states.PLAN_ID][0] if len(df[states.PLAN_ID]) > 0 else 0
    return plan_id

def get_avg_tank_level_mean():
    client = _InfluxSingleton.get_client()
    query = f'''
        SELECT AVG("{states.WATER_TANK_LEVEL}") FROM "greenhouse_sensors" WHERE time >= now() - interval '5 minute'
    '''
    result = client.query(query, database=database)
    
    df = result.to_pandas()
    col_name = f'avg(greenhouse_sensors.{states.WATER_TANK_LEVEL})'
    print(df[col_name].iloc[0])
    return df[col_name].iloc[0]

def get_sensor_means(client, plan_id):
    fluents = {}
    for fluent in [states.TEMPERATURE_READING, states.HUMIDITY_READING, states.WATER_TANK_LEVEL]:
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

def get_latest_hours_until_rain():
    client = _InfluxSingleton.get_client()
    query = '''
        SELECT * FROM "weather" ORDER BY time DESC LIMIT 1
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
    fluents = get_sensor_means(client, plan_id)
    hours_until_rain = get_latest_hours_until_rain()
    if hours_until_rain is not None:
        fluents[states.HOURS_UNTIL_RAIN] = hours_until_rain
    fluents = validate_fluents(fluents)
    # Fetch configs from db and update fluents
    configs = get_all_configs()
    if configs:
        fluents.update(configs)
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
        "name": f"plan_{str(plan_id)}",
        "fluents": fluents,
        "init": init,
        "goals": [
            "(temperature_comfortable)",
            "(humidity_comfortable)",
            "(soil_moisture_adequate)",
            "(water_managed)"
        ],
        "objects": {
            "sensor": ["ts1", "hs1", "ss", "wl"],
            "fan": ["fan1"],
            "servo": ["s1"],
            "motor": ["mp1"],
            "alert-level": ["high", "warning", "none", "rain-expected"]
        },
        "metric": "minimize"
    }
    print(data)
    return data

def insert_hours_until_rain(data):
    try:
        required_prob = 20
        client = _InfluxSingleton.get_client()
        probabilities = data["hourly"]["precipitation_probability"]
        hours_until_rain = None
        for idx, prob in enumerate(probabilities):
            if prob > required_prob:
                hours_until_rain = idx  # hours from now
                break
        if hours_until_rain is None:
            print(f"No rain expected in the forecast period (precipitation_probability > {required_prob}% not found). Setting it to default 100")
            hours_until_rain = 100
        point = (
            Point("weather")
            .field("hours_until_rain", hours_until_rain)
        )
        client.write(database=database, record=point)
        print(f"Inserted hours_until_rain={hours_until_rain} into timeseriesdb.")
    except Exception as e:
        print(f"Error inserting hours_until_rain into timeseriesdb: {e}")


def write_sensor_data(message_list):
    client = _InfluxSingleton.get_client()
    points = []
    for message in message_list:
        point = (
            Point("greenhouse_sensors")
            .field(states.HUMIDITY_READING, message[states.HUMIDITY_READING])
            .field(states.TEMPERATURE_READING, message[states.TEMPERATURE_READING])
            .field(states.SOIL_MOISTURE_READING, message[states.SOIL_MOISTURE_READING])
            .field(states.WATER_TANK_LEVEL, message[states.WATER_TANK_LEVEL])
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

def get_sensor_timeseries_data(interval="1h"):

    client = _InfluxSingleton.get_client()
    now = datetime.now(timezone.utc)
    if interval == "15m":
        start = now - timedelta(minutes=15)
    elif interval == "30m":
        start = now - timedelta(minutes=30)
    else:  # default to 1 hour
        start = now - timedelta(hours=1)

    # Query all metrics at once (do NOT select plan_id as a field; it's a tag)
    query = f'''
        SELECT *
        FROM "greenhouse_sensors"
        WHERE time >= '{start.isoformat()}'
        ORDER BY time ASC
    '''
    print(query)
    result = client.query(query, database=database)
    df = result.to_pandas()
    print(df)

    # If PLAN_ID is a tag, it may appear as a column or as an index level
    plan_id_col = states.PLAN_ID
    if plan_id_col not in df.columns and plan_id_col in getattr(df, 'index', pd.Index([])).names:
        # If PLAN_ID is an index level, reset index to get it as a column
        df = df.reset_index()

    result_data = {
        states.TEMPERATURE_READING: [],
        states.HUMIDITY_READING: [],
        states.SOIL_MOISTURE_READING: [],
        states.WATER_TANK_LEVEL: [],
        states.PLAN_ID: []
    }

    if not df.empty and "time" in df.columns:
        for _, row in df.iterrows():
            time_str = row["time"].strftime("%H:%M")
            if states.TEMPERATURE_READING in df.columns and row[states.TEMPERATURE_READING] is not None:
                result_data[states.TEMPERATURE_READING].append({"time": time_str, "value": float(row[states.TEMPERATURE_READING])})
            if states.HUMIDITY_READING in df.columns and row[states.HUMIDITY_READING] is not None:
                result_data[states.HUMIDITY_READING].append({"time": time_str, "value": float(row[states.HUMIDITY_READING])})
            if states.SOIL_MOISTURE_READING in df.columns and row[states.SOIL_MOISTURE_READING] is not None:
                result_data[states.SOIL_MOISTURE_READING].append({"time": time_str, "value": float(row[states.SOIL_MOISTURE_READING])})
            if states.WATER_TANK_LEVEL in df.columns and row[states.WATER_TANK_LEVEL] is not None:
                result_data[states.WATER_TANK_LEVEL].append({"time": time_str, "value": float(row[states.WATER_TANK_LEVEL])}) 
            # Get plan_id from column if present, else None
            plan_id_val = str(row[plan_id_col]) if plan_id_col in row and row[plan_id_col] is not None else None
            result_data[states.PLAN_ID].append({"time": time_str, "value": plan_id_val})

    return result_data

# Singleton pattern
_InfluxSingleton.get_client()