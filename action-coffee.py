#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes
import Queue
from coffeehack.coffeehack import CoffeeHack
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class Skill:

    def __init__(self):
        self.coffee = CoffeeHack(extra=False)

def extract_coffee_taste(intent_message):
    res = []
    if intent_message.slots.coffee_taste is not None:
        for r in intent_message.slots.coffee_taste:
            res.append(r.slot_value.value.value)
    return res

def extract_coffee_number(intent_message):
    res = []
    if intent_message.slots.coffee_number is not None:
        for r in intent_message.slots.coffee_number:
            res.append(r.slot_value.value.value)
    return res
def extract_coffee_type(intent_message):
    res = []
    if intent_message.slots.coffee_type is not None:
        for r in intent_message.slots.coffee_type:
            res.append(r.slot_value.value.value)
    return res
def extract_coffee_size(intent_message):
    res = []
    if intent_message.slots.coffee_size is not None:
        for r in intent_message.slots.coffee_size:
            res.append(r.slot_value.value.value)
    return res

def callback(hermes, intent_message):
    t = extract_coffee_type(intent_message)
    s = extract_coffee_size(intent_message)
    ta = extract_coffee_taste(intent_message)
    n = extract_coffee_number(intent_message)
    coffee_type = ""
    coffee_size = ""
    coffee_taste = ""
    number = 1
    if len(t):
        coffee_type = t[0]
    if len(s):
        coffee_size = s[0]
    if len(ta):
        coffee_taste = ta[0]
    if len(n):
        number = int(n[0])
    print(t)
    print(s)
    print(ta)
    hermes.skill.coffee.pour(coffee_type = coffee_type,
                coffee_size = coffee_size,
                coffee_taste = coffee_taste,
                number = number)

def coffee_toggle(hermes, intent_message):
      hermes.skill.coffee.toggle_on_off()

if __name__ == "__main__":
    skill = Skill()
    with Hermes(MQTT_ADDR) as h:
        h.skill = skill
        h.subscribe_intent("airstream_project:pour", callback) \
                .subscribe_intent("airstream_project:coffee_toggle", coffee_toggle) \
         .loop_forever()
