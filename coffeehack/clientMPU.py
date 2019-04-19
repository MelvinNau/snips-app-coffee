#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_demo_helper.hermes_demo_helper import *

class ClientMPU(ClientAction):

    def __init__(self, mqtt_addr, lang_config, coffee):
        ClientAction.__init__(self, mqtt_addr, lang_config)
        #init intent subscribe 
        self.intent_funcs = [
                (self.coffee_toggle_callback, "coffee_toggle"),
                (self.pour_callback, "pour"),
                (self.clean_callback, "clean"),
                (self.steam_callback, "steam"),
                (self.stop_callback, "stop")
                ]
        self.coffee = coffee
        self.number_map = {}
        tmp = lang_config.config.get_value("numberMap")
        for k in tmp:
            for item in tmp[k]:
                 self.number_map[item] = int(k)

    def extract_coffee_number(self, intent_message):
        tmp = self.extract_value(intent_message, "coffee_number")
        if tmp is not None:
            try:
                return int(tmp)
            except:
                return self.number_map.get(tmp, -1)
        return -1

    @is_simple_intent_callback
    def pour_callback(self, hermes, intent_message):
        coffee_type = self.extract_value(intent_message, "coffee_type")
        coffee_size = self.extract_value(intent_message, "coffee_size")
        coffee_taste = self.extract_value(intent_message, "coffee_taste")
        number = self.extract_coffee_number(intent_message)
        if (coffee_type is None and coffee_size is None and
                coffee_taste is None and number != -1):
            return self.config.tts.get_value("nlu_error_slot_soup")
        if (coffee_type is None and coffee_size is not None):
            coffee_type = "coffee"
        number = 1 if number == -1 else number
        coffee_type = "" if coffee_type is None else coffee_type
        coffee_size = "" if coffee_size is None else coffee_size
        coffee_taste = "" if coffee_taste is None else coffee_taste
        if self.coffee.pour(coffee_type = coffee_type, coffee_size = coffee_size,
                coffee_taste = coffee_taste, number = number):
            data = {
                    "number" : number,
                    "test": "test",
                    "coffee_size" : coffee_size,
                    "coffee_taste" : coffee_taste,
                    "coffee_type" : coffee_type
                    }
            if (number == 1):
                return self.config.tts.get_value("coffee_pour_1").format(**data)
            return self.config.tts.get_value("coffee_pour_2").format(**data)
        return self.config.tts.get_value("nlu_error_slot_soup")

    @is_simple_intent_callback
    def coffee_toggle_callback(self, hermes, intent_message):
        self.coffee.toggle_on_off()
        return self.config.tts.get_value("coffee_toggle")

    @is_simple_intent_callback
    def clean_callback(hermes, intent_message):
        self.coffee.clean()
        return self.config.tts.get_value("cleaning")

    @is_simple_intent_callback
    def steam_callback(hermes, intent_message):
        self.coffee.steam()
        return self.config.tts.get_value("steaming")

    @is_simple_intent_callback
    def stop_callback(self, hermes, intent_message):
        if self.coffee.stop():
            return self.config.tts.get_value("coffee_stop")
        return self.config.tts.get_value("coffee_no_stop")
