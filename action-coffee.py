#!/usr/bin/env python3
# -*-: coding utf-8 -*-

from coffeehack.coffeehack import CoffeeHack
from coffeehack.clientMPU import ClientMPU
from hermes_demo_helper import *

CONFIG_INI = "config.ini"

config = SnipsConfigParser.read_configuration_file(CONFIG_INI).get('global')

MQTT_ADDR_LOCAL_HOST = str(config.get('addr_local_host', 'localhost'))
MQTT_ADDR_LOCAL_PORT = str(config.get('addr_local_port', '1883'))
MQTT_ADDR_LOCAL = "{}:{}".format(MQTT_ADDR_LOCAL_HOST, MQTT_ADDR_LOCAL_PORT)

lang_config = Lang_config(config.get('ressources'))

#Coffee machine configuration
extra = config.get("extra", False)
if (extra is None or extra == "" or extra == "False" or extra == "false" or extra == "0"):
    extra = False
coffee = CoffeeHack(lang_config, extra = extra)

#Default configuration
clientLocal = ClientMPU(MQTT_ADDR_LOCAL, lang_config, coffee)

#snips Demo purpose Only
try:
    MQTT_ADDR_GLOBAL_HOST = str(config.get('addr_global_host'))
    MQTT_ADDR_GLOBAL_PORT = str(config.get('addr_global_port'))
    MQTT_ADDR_GLOBAL = "{}:{}".format(MQTT_ADDR_GLOBAL_HOST, MQTT_ADDR_GLOBAL_PORT)
    clientGlobal = ClientMPU(MQTT_ADDR_GLOBAL, lang_config, coffee)
except:
    clientClobal = None
    pass

if __name__ == "__main__":
    try:
        if clientGlobal is not None:
            try:
                clientGlobal.start()
            except:
                print("Can not connect to global broker")
        clientLocal.start()
        while True:
            pass
    except KeyboardInterrupt:
        print("Please force to kill this process!")
