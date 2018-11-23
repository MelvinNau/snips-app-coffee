#!/usr/bin/env python2
# -*-: coding utf-8 -*-

import ConfigParser
from coffeehack.coffeehack import CoffeeHack
from hermes_python.hermes import Hermes
import io
import Queue
import time
import functools

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
            res.append((r.slot_value.value.value, r.confidence))
    return res

def extract_coffee_taste(intent_message, confidence):
    tmp = extract_value(intent_message.slots.coffee_taste)
    if len(tmp) and tmp[0][1] > confidence:
        return tmp[0][0]
    return ""

def extract_coffee_number(intent_message, confidence):
    tmp = extract_value(intent_message.slots.coffee_number)
    number = 1
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
        , tts = "Sorry, I don't know how to help you",
        action_resume = False):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(hermes, intent_message):
            print(tts)
            probability = intent_message.intent.probability
            if action_resume or probability > min_proba:
                return func(hermes, intent_message)
            else:
                hermes.publish_end_session(intent_message.session_id, tts)
                return None
        return wrapper_repeat
    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)

@check_proba
@check_proba(min_proba = 0.6, tts = "Sorry, I don't think I understood")
def pour_callback(hermes, intent_message):
    coffee_type = extract_coffee_type(intent_message, 0.5)
    coffee_size = extract_coffee_size(intent_message, 0.5)
    coffee_taste = extract_coffee_taste(intent_message, 0.5)
    number = extract_coffee_number(intent_message, 0.5)
    probability = intent_message.intent.probability
    done = hermes.skill.pour(coffee_type = coffee_type,
                coffee_size = coffee_size,
                coffee_taste = coffee_taste,
                number = number)
    if done:
        #TODO add TTS Serving
        print("pourring: {} {} {} {}".format(number,
                                        coffee_type,
                                        coffee_taste,
                                        coffee_size))
    else:
        #TODO Error
        print("ERROR pourring: {} {} {} {}".format(number,
                                        coffee_type,
                                        coffee_taste,
                                        coffee_size))

@check_proba
@check_proba(min_proba = 0.6, tts = "Sorry, I don't think I understood")
def coffee_toggle_callback(hermes, intent_message):
    print("toggle On or Off Coffee")
    #TODO add TTS Now the coffee machine is turned On
    hermes.skill.toggle_on_off()

@check_proba
@check_proba(min_proba = 0.6, tts = "Sorry, I don't think I understood")
def clean_callback(hermes, intent_message):
    print("Clean Coffee Machine")
    #TODO add TTS Now in steaming Mode
    hermes.skill.clean()

@check_proba
@check_proba(min_proba = 0.6, tts = "Sorry, I don't think I understood")
def steam_callback(hermes, intent_message):
    print("Steam coffee machine")
    #TODO add TTS Now in steaming Mode
    hermes.skill.steam()

@check_proba
@check_proba(min_proba = 0.6, tts = "Sorry, I don't think I understood",
        action_resume = True)
def stop_callback(hermes, intent_message):
    print("Stop coffee machine")
    if hermes.skill.stop():
        #TODO add TTS  OK, I've stop stopped preparing your coffee
        pass
    else:
        #TODO close session
        pass

intents = [ ("coffee_toggle",  coffee_toggle_callback),
            ("pour", pour_callback),
            ("clean", clean_callback),
            ("steam", steam_callback),
            ("stop", stop_callback)]

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
    print("coffe maker {}".format(extra))
    print("Subscribe on {}".format(broker))
    with Hermes(broker) as h:
        h.skill = None
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
