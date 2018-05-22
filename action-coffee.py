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
        self.coffee = CoffeeHack()

def extract_coffee_taste(intent_message):
    res = []
    if intent_message.slots.coffe_taste is not None:
        for r in intent_message.slots.taste:
            res.append(r.slot_value.value.value)
    return res

def extract_coffee_number(intent_message):
    res = []
    if intent_message.slots.coffe_number is not None:
        for r in intent_message.slots.number:
            res.append(r.slot_value.value.value)
    return res
def extract_coffee_type(intent_message):
    res = []
    if intent_message.slots.coffe_type is not None:
        for r in intent_message.slots.type:
            res.append(r.slot_value.value.value)
    return res
def extract_coffee_size(intent_message):
    res = []
    if intent_message.slots.coffe_size is not None:
        for r in intent_message.slots.size:
            res.append(r.slot_value.value.value)
    return res

def callback(hermes, intent_message):
    t = extract_coffee_type(intent_message)
    s = extract_coffee_type(intent_message)
    ta = extract_coffee_type(intent_message)
    n = extract_coffee_type(intent_message)
    if len(t):
        coffee_type = t[0]
    if len(s):
        coffee_size = s[0]
    if len(ta):
        coffee_taste = ta[0]
    if len(n):
        number = int(n[0])
    hermes.skill.coffee.pour(coffee_type = coffee_type,
                coffee_size = coffee_size,
                coffee_taste = coffee_taste,
                number = number,
                dialogue = snips.dialogue)

def coffee_toggle(hermes, intent_message):
      hermes.skill.coffee.toggle_on_off(snips.dialogue)

if __name__ == "__main__":
    skill = Skill()
    with Hermes(MQTT_ADDR) as h:
        h.skill = skill
        h.subscribe_intent("akaisuisei:print", callback) \
         .loop_forever()
