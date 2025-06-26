import os, time
from influxdb_client_3 import InfluxDBClient3, Point

token = os.environ.get("INFLUXDB_TOKEN")
org = "SmartCities"
host = "https://eu-central-1-1.aws.cloud2.influxdata.com"

database="smart-greenhouse"

data = {
  "name": "all_checks_case",
  "fluents": {
    "hours_until_rain": 40,
    "water_tank_level": 70,
    "temperature": 5,
    "humidity": 5
  },
  "init": [
    "outside_environment_safe",
    "not (alert-warning)",
    "not (alert-high)",
    "not (no_alert)"
  ],
  "goals": [
    {
      "type": "or",
      "states": ["alert-high", "alert-warning", "no_alert"]
    },
    {
      "type": "or",
      "states": ["fan_on", "fan_off"]
    },
    {
      "type": "or",
      "states": ["run_servo s1", "close_servo s1"]
    },
    {
      "type": "or",
      "states": ["run_servo s2", "close_servo s2"]
    }
  ]
}


client = None

def create_client():
    return InfluxDBClient3(host=host, token=token, org=org)

def get_client():
    return client

def get_data():
    return data
    

def write_data(client, data):
    for key in data:
        point = (
            Point("greenhouse")
            .tag("location", data[key]["location"])
            .field(data[key]["species"], data[key]["count"])
        )
        time.sleep(1) # separate points by 1 second
        client.write(database=database, record=point)


# data = {
#   "point1": {
#     "location": "Klamath",
#     "species": "bees",
#     "count": 23,
#   },
#   "point2": {
#     "location": "Portland",
#     "species": "ants",
#     "count": 30,
#   },
#   "point3": {
#     "location": "Klamath",
#     "species": "bees",
#     "count": 28,
#   },
#   "point4": {
#     "location": "Portland",
#     "species": "ants",
#     "count": 32,
#   },
#   "point5": {
#     "location": "Klamath",
#     "species": "bees",
#     "count": 29,
#   },
#   "point6": {
#     "location": "Portland",
#     "species": "ants",
#     "count": 40,
#   },
# }


print("Complete. Return to the InfluxDB UI.")


client = create_client()
print(client)
# write_data(client, data)