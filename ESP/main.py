# Complete project details at https://RandomNerdTutorials.com
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
from machine import Pin, I2C
from time import sleep
import BME280

esp.osdebug(None)
import gc
gc.collect()

SSID = ''
password = ""
mqtt_server = ''


last_message = 0
message_interval = 5
counter = 0

# ESP32 - Pin assignment
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
# ESP8266 - Pin assignment
#i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)
bme = BME280.BME280(i2c=i2c)


def get_data():
    temp = bme.temperature
    hum = bme.humidity
    pres = bme.pressure
    # uncomment for temperature in Fahrenheit
    # temp = (bme.read_temperature()/100) * (9/5) + 32
    # temp = str(round(temp, 2)) + 'F'
    print('Temperature: ', temp)
    print('Humidity: ', hum)
    print('Pressure: ', pres)
    return temp, hum, pres


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network....')
        wlan.connect(SSID,password)
        while not wlan.isconnected():
            pass
    print('network.config:', wlan.ifconfig())


def sub_cb(topic, msg):
    print(topic, msg)
    if topic == b'house' and msg == b'received':
        print("ESP received the data")


def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server, user="esp32", password="Gam3nM44r11")
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

client_id=ubinascii.hexlify(machine.unique_id())
topic_sub=b'house'
topic_pub = b'hello'

def restart_and_connect():
    print('Failed to connect to MQTT broker. Reconnecting .....')
    time.sleep(10)
    machine.reset()


def main():
    do_connect()


if __name__ == "__main__":
    main()


try:
    client = connect_and_subscribe()
except OSError as e:
    print(e)
    restart_and_connect()


while True:
    try:
        client.check_msg()
        values = get_data()
        if (time.time() - last_message) > message_interval:
            msg = b'temp = %s, hum = %s, pres = %s' % (values[0], values[1], values[2])
            client.publish(topic_sub, msg)
            last_message = time.time()
            counter += 1
            time.sleep(2)
    except OSError as e:
        restart_and_connect()






