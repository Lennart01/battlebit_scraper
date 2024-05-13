from dotenv import load_dotenv
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
import json
from datetime import datetime

load_dotenv()

def init_influxdb():
    token = os.getenv("INFLUXDB_TOKEN")
    org = "org"
    url = "http://localhost:8086"

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

    return client

def write_data(data, client):
    bucket = "battlebit_gameserver_stats"
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Generate a single timestamp for this batch of data points
    timestamp = datetime.utcnow()

    # Create a list to hold the points for this batch
    points = []

    # Vars for the stats we want to track
    # Map, MapSize, Gamemode, Region, Players, QueuePlayers, MaxPlayers, Hz, DayNight, IsOfficial, HasPassword, AntiCheat, Build
    Map_Count = {}
    MapSize_Count = {}
    Gamemode_Count = {}
    Region_Count = {}
    Players_Count = 0
    QueuePlayers_Count = 0
    MaxPlayers_Count = {}
    Hz_Count = {}
    DayNight_Count = {}
    IsOfficial_Count = {}
    HasPassword_Count = {}
    AntiCheat_Count = {}
    Build_Count = {}

    for server in data:
        # Map
        if server["Map"] in Map_Count:
            Map_Count[server["Map"]] += 1
        else:
            Map_Count[server["Map"]] = 1

        # MapSize
        if server["MapSize"] in MapSize_Count:
            MapSize_Count[server["MapSize"]] += 1
        else:
            MapSize_Count[server["MapSize"]] = 1

        # Gamemode
        if server["Gamemode"] in Gamemode_Count:
            Gamemode_Count[server["Gamemode"]] += 1
        else:
            Gamemode_Count[server["Gamemode"]] = 1

        # Region
        if server["Region"] in Region_Count:
            Region_Count[server["Region"]] += 1
        else:
            Region_Count[server["Region"]] = 1

        # Players
        Players_Count += server["Players"]

        # QueuePlayers
        QueuePlayers_Count += server["QueuePlayers"]

        # MaxPlayers
        if server["MaxPlayers"] in MaxPlayers_Count:
            MaxPlayers_Count[server["MaxPlayers"]] += 1
        else:
            MaxPlayers_Count[server["MaxPlayers"]] = 1

        # Hz
        if server["Hz"] in Hz_Count:
            Hz_Count[server["Hz"]] += 1
        else:
            Hz_Count[server["Hz"]] = 1

        # DayNight
        if server["DayNight"] in DayNight_Count:
            DayNight_Count[server["DayNight"]] += 1
        else:
            DayNight_Count[server["DayNight"]] = 1

        # IsOfficial
        if server["IsOfficial"] in IsOfficial_Count:
            IsOfficial_Count[server["IsOfficial"]] += 1
        else:
            IsOfficial_Count[server["IsOfficial"]] = 1

        # HasPassword
        if server["HasPassword"] in HasPassword_Count:
            HasPassword_Count[server["HasPassword"]] += 1
        else:
            HasPassword_Count[server["HasPassword"]] = 1

        # AntiCheat
        if server["AntiCheat"] in AntiCheat_Count:
            AntiCheat_Count[server["AntiCheat"]] += 1
        else:
            AntiCheat_Count[server["AntiCheat"]] = 1

        # Build
        if server["Build"] in Build_Count:
            Build_Count[server["Build"]] += 1
        else:
            Build_Count[server["Build"]] = 1
        
    
    # Write the stats to influxdb
    for key, value in Map_Count.items():
        point = Point("map_stats")\
            .tag("Map", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in MapSize_Count.items():
        point = Point("mapsize_stats")\
            .tag("MapSize", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in Gamemode_Count.items():
        point = Point("gamemode_stats")\
            .tag("Gamemode", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in Region_Count.items():
        point = Point("region_stats")\
            .tag("Region", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    point = Point("players_stats")\
        .field("count", Players_Count)\
        .time(timestamp, WritePrecision.NS)
    points.append(point)

    point = Point("queueplayers_stats")\
        .field("count", QueuePlayers_Count)\
        .time(timestamp, WritePrecision.NS)
    points.append(point)

    for key, value in MaxPlayers_Count.items():
        point = Point("maxplayers_stats")\
            .tag("MaxPlayers", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in Hz_Count.items():
        point = Point("hz_stats")\
            .tag("Hz", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in DayNight_Count.items():
        point = Point("daynight_stats")\
            .tag("DayNight", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in IsOfficial_Count.items():
        point = Point("isofficial_stats")\
            .tag("IsOfficial", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in HasPassword_Count.items():
        point = Point("haspassword_stats")\
            .tag("HasPassword", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in AntiCheat_Count.items():
        point = Point("anticheat_stats")\
            .tag("AntiCheat", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    for key, value in Build_Count.items():
        point = Point("build_stats")\
            .tag("Build", key)\
            .field("count", value)\
            .time(timestamp, WritePrecision.NS)
        points.append(point)
    
    # Write the entire batch of points
    write_api.write(bucket=bucket, record=points)

    # for server in data:
    #     point = Point("server_stats")\
    #         .tag("Name", server["Name"])\
    #         .field("Map", server["Map"])\
    #         .field("MapSize", server["MapSize"])\
    #         .field("Gamemode", server["Gamemode"])\
    #         .field("Region", server["Region"])\
    #         .field("Players", server["Players"])\
    #         .field("QueuePlayers", server["QueuePlayers"])\
    #         .field("MaxPlayers", server["MaxPlayers"])\
    #         .field("Hz", server["Hz"])\
    #         .field("DayNight", server["DayNight"])\
    #         .field("IsOfficial", server["IsOfficial"])\
    #         .field("HasPassword", server["HasPassword"])\
    #         .field("AntiCheat", server["AntiCheat"])\
    #         .field("Build", server["Build"])\
    #         .time(timestamp, WritePrecision.NS)  # Use the timestamp generated before the loop
    #     # Add the point to the batch
    #     points.append(point)

    # Write the entire batch of points
    write_api.write(bucket=bucket, record=points)

    
    # write server count to influxdb
    point = Point("server_count")\
        .field("count", len(data))\
        .time(timestamp, WritePrecision.NS)
    write_api.write(bucket=bucket, record=point)
        

    print("Wrote data to InfluxDB")
    print("Server count: " + str(len(data)))



def get_data():
    url = "https://publicapi.battlebit.cloud/Servers/GetServerList"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the response status code is not 200
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Error occurred during API call:", e)
        return None

def main():
    client = init_influxdb()
    while True:
        data = get_data()
        if data is not None:
            write_data(data, client)
        else:
            print("No data received. Retrying in 15 seconds...")
        time.sleep(15)

if __name__ == "__main__":
    main()
