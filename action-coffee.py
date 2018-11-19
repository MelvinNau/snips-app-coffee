#!/usr/bin/env python2
# -*-: coding utf-8 -*-

import ConfigParser
from coffeehack.coffeehack import CoffeeHack
from hermes_python.hermes import Hermes
import io
import Queue

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def extract_value(val):
    res = []
    if val is not None:
        for r in val:
            res.append(r.slot_value.value.value)
    return res

def extract_coffee_taste(intent_message):
    ta = extract_value(intent_message.slots.coffee_taste)
    return ta[0] if len(ta) else ""

def extract_coffee_number(intent_message):
    n = extract_value(intent_message.slots.coffee_number)
    number = 1
    if len(n):
        try:
            number = int(n[0])
        except ValueError, e:
            number = 2
    return number

def extract_coffee_type(intent_message):
    t = extract_value(intent_message.slots.coffee_type)
    return t[0] if len(t) else ""

def extract_coffee_size(intent_message):
    s = extract_value(intent_message.slots.coffee_size)
    return s[0] if len(s) else ""

def pour_callback(hermes, intent_message):
    coffee_type = extract_coffee_type(intent_message)
    coffee_size = extract_coffee_size(intent_message)
    coffee_taste = extract_coffee_taste(intent_message)
    number = extract_coffee_number(intent_message)
    print("pourring: {} {} {} {}".format(number,
                                        coffee_type,
                                        coffee_taste,
                                        coffee_size))
    hermes.skill.pour(coffee_type = coffee_type,
                coffee_size = coffee_size,
                coffee_taste = coffee_taste,
                number = number)

def coffee_toggle_callback(hermes, intent_message):
    print("toggle On or Off Coffee")
    hermes.skill.toggle_on_off()

def clean_callback(hermes, intent_message):
    print("Clean Coffee Machine")
    hermes.skill.clean()

def steam_callback(hermes, intent_message):
    print("Steam coffee machine")
    hermes.skill.steam()

intents = [ ("coffee_toggle",  coffee_toggle_callback),
            ("pour", pour_callback),
            ("clean", clean_callback),
            ("steam", steam_callback)]

if __name__ == "__main__":
    config = read_configuration_file(CONFIG_INI)
    addr = config.get("secret", {"coffee_broker_ip": "localhost"})\
            .get("coffee_broker_ip")
    port = config.get("secret", {"coffee_broker_port": 1883})\
            .get("coffee_broker_port")
    extra = config["global"].get("extra", False)
    if (extra is None or extra == ""):
        extra = False
    if (addr is None or addr == ""):
        addr = "localhost"
    if (port is None or port == 0 or port  == ""):
        port = 1883
    broker = "{}:{}".format(addr, port)
    print("Subscribe on {}".format(broker))

    with Hermes(broker) as h:
        h.skill = CoffeeHack(extra = extra)
        for intent in intents:
            h.subscribe_intent(intent[0], intent[1]) 
            print("Subscribe to: {}".format(intent[0]))
        h.loop_forever()
