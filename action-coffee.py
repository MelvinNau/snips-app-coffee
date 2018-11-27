#!/usr/bin/env python2
# -*-: coding utf-8 -*-

import ConfigParser
from coffeehack.coffeehack import CoffeeHack
from hermes_python.hermes import Hermes
import io
import Queue
import time
import functools
import json
import random

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
READY = "ready"
ERROR_CABLE = "error_cable"
ERROR_DISABLE = "error_disable"
NLU_ERROR = "nlu_error"
NLU_ERROR_INTENT_LOW = "nlu_error_intent_low"
NLU_ERROR_INTENT_MIDLE = "nlu_error_intent_midle"
NLU_ERROR_SLOT_LOW = "nlu_error_slot_low"
NLU_ERROR_SLOT_SOUP = "nlu_error_slot_soup"
COFFEE_STOP = "coffee_stop"
COFFEE_NO_STOP = "coffee_no_stop"
COFFEE_TOGGLE = "coffee_toggle"
COFFEE_POUR_SINGLE = "coffee_pour_single"
COFFEE_POUR_TWO = "coffee_pour_two"
COFFEE_POUR_TWO_NO_TASTE="coffee_pour_two_no_taste"

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
            res.append((r.slot_value.value.value, r.confidence))
    return res

def extract_coffee_taste(intent_message, confidence):
    tmp = extract_value(intent_message.slots.coffee_taste)
    if len(tmp) and tmp[0][1] > confidence:
        return tmp[0][0]
    return ""

def extract_coffee_number(intent_message, confidence):
    tmp = extract_value(intent_message.slots.coffee_number)
    number = -1
    if len(tmp) and tmp[0][1] > confidence:
        try:
            number = int(tmp[0][0])
        except ValueError, e:
            number = 2
    return number

def extract_coffee_type(intent_message, confidence):
    tmp = extract_value(intent_message.slots.coffee_type)
    if len(tmp) and tmp[0][1] > confidence:
        return tmp[0][0]
    return ""

def extract_coffee_size(intent_message, confidence):
    tmp = extract_value(intent_message.slots.coffee_size)
    if len(tmp) and tmp[0][1] > confidence:
        return tmp[0][0]
    return ""

def check_proba(_func=None, min_proba=0.3
        , tts = NLU_ERROR_INTENT_LOW,
        action_resume = False):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(hermes, intent_message):
            probability = intent_message.intent.probability
            if action_resume or probability > min_proba:
                return func(hermes, intent_message)
            else:
                hermes.publish_end_session(intent_message.session_id,
                        random.choice(hermes.tts_coffee[tts]))
                return None
        return wrapper_repeat
    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)

@check_proba
@check_proba(min_proba = 0.6, tts = NLU_ERROR_INTENT_MIDLE)
def pour_callback(hermes, intent_message):
    coffee_type = extract_coffee_type(intent_message, 0.6)
    coffee_size = extract_coffee_size(intent_message, 0.6)
    coffee_taste = extract_coffee_taste(intent_message, 0.6)
    number = extract_coffee_number(intent_message, 0.6)
    if (coffee_type != "" or coffee_size != "" or
            coffee_taste != "" or number != -1):
        coffee_type = extract_coffee_type(intent_message, 0)
        coffee_size = extract_coffee_size(intent_message, 0)
        coffee_taste = extract_coffee_taste(intent_message, 0)
        number = extract_coffee_number(intent_message, 0)
    if (coffee_type == "" and coffee_size != ""):
        coffee_type = "coffee"
    done = hermes.skill.pour(coffee_type = coffee_type,
                coffee_size = coffee_size,
                coffee_taste = coffee_taste,
                number = number)
    res = None
    if done:
        if(number == -1):
            number = 1
        if (number == 1):
            res = random.choice(hermes.tts_coffee[COFFEE_POUR_SINGLE])
        else:
            res = random.choice(hermes.tts_coffee[COFFEE_POUR_TWO])
        res = res.format(number=number,
                coffee_size=coffee_size,
                coffee_taste = coffee_taste if coffee_taste != "normal" else "",
                coffee_type = coffee_type)
    else:
        res = random.choice(hermes.tts_coffee[NLU_ERROR_SLOT_SOUP])
    print(res)
    hermes.publish_end_session(intent_message.session_id, res)

@check_proba
@check_proba(min_proba = 0.6, tts = NLU_ERROR_INTENT_MIDLE)
def coffee_toggle_callback(hermes, intent_message):
    print("toggle On or Off Coffee")
    hermes.publish_end_session(intent_message.session_id,
                random.choice(hermes.tts_coffee[COFFEE_TOGGLE]))
    hermes.skill.toggle_on_off()

@check_proba
@check_proba(min_proba = 0.6, tts = NLU_ERROR_INTENT_MIDLE)
def clean_callback(hermes, intent_message):
    print("Clean Coffee Machine")
    hermes.publish_end_session(intent_message.session_id, "Cleaning")
    hermes.skill.clean()

@check_proba
@check_proba(min_proba = 0.6, tts = NLU_ERROR_INTENT_MIDLE)
def steam_callback(hermes, intent_message):
    print("Steam coffee machine")
    hermes.publish_end_session(intent_message.session_id, "Steaming")
    hermes.skill.steam()

@check_proba
@check_proba(min_proba = 0.6, tts = NLU_ERROR_INTENT_MIDLE,
        action_resume = True)
def stop_callback(hermes, intent_message):
    print("Stop coffee machine")
    if hermes.skill.stop():
        hermes.publish_end_session(intent_message.session_id,
                random.choice(hermes.tts_coffee[COFFEE_STOP]))
    else:
        hermes.publish_end_session(intent_message.session_id,
                random.choice(hermes.tts_coffee[COFFEE_NO_STOP]))
        pass

def create_intent(config):
    intents_list = config.get("intents")
    if (intents_list is not None):
        return [ (intents_list.get("coffee_toggle", "coffee_toggle"),  coffee_toggle_callback),
                (intents_list.get("pour", "pour"), pour_callback),
                (intents_list.get("clean", "clean"), clean_callback),
                (intents_list.get("steam", "steam"), steam_callback),
                (intents_list.get("stop", "stop"), stop_callback)]
    else:
        return [ ("coffee_toggle",  coffee_toggle_callback),
                ("pour", pour_callback),
                ("clean", clean_callback),
                ("steam", steam_callback),
                ("stop", stop_callback)]

def create_tts(config):
    tts_list = config.get("TTS")
    res = {}
    if (tts_list is not None):
        for k in tts_list.keys():
            res[k] = json.loads(tts_list[k])
        pass
    default = {
                READY: ["Ready to make a wonderful coffee"],
                ERROR_CABLE: ["connect Coffee machine, Please"],
                ERROR_DISABLE: ["Disabling, Coffee machine"],
                NLU_ERROR: ["Sorry, I don't know how to help you with that"],
                NLU_ERROR_INTENT_LOW: ["Sorry, I don't know how to help you\
                        with that"],
                NLU_ERROR_INTENT_MIDLE: ["Sorry, I don't think I've understood"],
                NLU_ERROR_SLOT_LOW: ["Sorry, not sure I got what type of coffee\
                        you wanted. Can you please try again"],
                NLU_ERROR_SLOT_SOUP: ["Sorry, we currently only do a variety of\
                        coffees. Check the list to see what you can order"],
                COFFEE_STOP: ["OK STOPING"],
                COFFEE_NO_STOP: [""],
                COFFEE_TOGGLE: ["OK"],
                COFFEE_POUR_SINGLE: ["Serving {number} {coffee_size} \
                        {coffee_taste} {coffee_type}"],
                COFFEE_POUR_TWO: ["Serving {number} {coffee_size} \
                        {coffee_taste} {coffee_type}s"]
                }
    for k in default.keys():
        if k not in res:
            res[k] = default[k]
    return res;

if __name__ == "__main__":
    config = read_configuration_file(CONFIG_INI)
    addr = config.get("secret", {"coffee_broker_ip": "localhost"})\
            .get("coffee_broker_ip")
    port = config.get("secret", {"coffee_broker_port": 1883})\
            .get("coffee_broker_port")
    extra = config["global"].get("extra", False)
    if (extra is None or extra == "" or extra == "False" or extra == "false" or extra == "0"):
        extra = False
    if (addr is None or addr == ""):
        addr = "localhost"
    if (port is None or port == 0 or port  == ""):
        port = 1883
    broker = "{}:{}".format(addr, port)
    intents = create_intent(config)
    print("coffe maker {}".format(extra))
    print("Subscribe on {}".format(broker))
    with Hermes(broker) as h:
        h.skill = None
        h.tts_coffee = create_tts(config)
        for x in range(3):
            try:
                h.skill = CoffeeHack(extra = extra)
            except:
                #TODO add TTS connect the usb cable
                print("connect Coffee machine, Please")
                time.sleep(30 * x)
            else:
                break
        if h.skill is None:
            #TODO add TTS disable skill
            pass
        else:
            for intent in intents:
                h.subscribe_intent(intent[0], intent[1]) 
                print("Subscribe to: {}".format(intent[0]))
            #TODO add TTS ready to make a coffee
            h.loop_forever()
