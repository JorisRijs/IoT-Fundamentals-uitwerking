import paho.mqtt.client as mqtt
import ssl
import asyncio
import time
import re
import iothub.iothub as sender
import sqlite3 as lite
import datetime
import settings as conf
#pmName = input('iothub')
#iotHub = __import__(pmName)


con = lite.connect('Webserver/measurements.db')
iothub = asyncio.run(sender.set_connection(conf.CONN_STR))

##################
def on_message(client, userdata, message):
    global iothub
    print("message received ", str(message.payload.decode("utf-8")))
    print("Message topic = ", message.topic)
    print("message qos =", message.qos)
    print("Message retain flag =", message.retain)
    results = split_message(message.payload.decode("utf-8"))
    if iothub is not None:
        asyncio.run(sender.main(iothub, results[0], results[1], results[2]))
    else:
        pass
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO measurements VALUES(?, ?, ?, ?, ?)", ("Fundamentals-pi", results[0], results[1], results[2], datetime.datetime.now()))
 
#################################

def split_message(message):
    temp = re.search("\d\d\.\d\dC", message).group(0)
    temp= temp.strip("C")
    hum = re.search("\d\d\.\d\d%", message).group(0)
    hum = hum.strip("%")
    pres = re.search("\d\d\d\d\.\d\d", message).group(0)
    results = (temp, hum, pres)
    return results


broker_address = conf.MQTT_BROKER
print("Creating a new instance")
client = mqtt.Client("P1", transport = "websockets")
client.tls_set(ca_certs=conf.CA_CERTS, certfile=conf.CERTFILE, keyfile=conf.KEYFILE,cert_reqs=ssl.CERT_NONE)
client.username_pw_set(conf.MOSQUITTO_USERNAME, conf.MOSQUITTO_PASSWORD)
client.tls_insecure_set(True)

client.on_message = on_message
try:
    print("Connecting to broker")
    client.connect(broker_address, 8883)
    client.subscribe('house')
    client.loop_forever()  # Start the loop
except KeyboardInterrupt:
    print("The program was canceled by the user")
    iothub.disconnect()
