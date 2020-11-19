import os
import json
import datetime
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

async def set_connection(conn_str):
    # Create instance of the device client using the authentication provider
    try:
        device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
        # Connect to the device client
        await device_client.connect()
    except:
        print("unable to connect")
        device_client = None

    return device_client
    
async def main(device_client, temp, hum, pres):


    temp = temp.strip("C")
    hum = hum.strip("%")
    pres = pres.strip("hPa")



    print("%s, %s, %s" %(temp, hum, pres))
    # Send a single message
    print("Sending message...")
    timecur = datetime.datetime.now()
    time_formatted = timecur.strftime("%A %B %d, %Y, %H.%M.%S")
    data_set = {"deviceId":"Fundamentals-Rasp", "Temperature": temp, "Humidity":hum, "Pressure":pres, "Timestamp":time_formatted }
    json_dump = json.dumps(data_set)
    print(json_dump)
    await device_client.send_message(json_dump)
    print("Message successfully sent")




