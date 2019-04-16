# coding: utf8
import os
from os.path import expanduser
import subprocess
import serial
import serial.tools.list_ports
import sys
import time
import threading
import warnings

MAX_COFFEE = 2
MIN_COFFEE = 1

class CoffeeHack:
    extra_foam_d ={
            "" : 0,
            "no frost" : 1,
            "min frost" : 2,
            "max frost" : 3
            }
    extra_size_d = {
            'short' : 1,
            'standard' : 2,
            'long' : 3,
            'extra long' : 4
            }

    extra_type_d = {
            'flat white' : 0,
            'machiato' : 1,
            'latte' : 2,
            'coffee' : 9,
            'cappuccino' : 8
            }
    extra_taste_d = {
            "standard" : 1,
            "mild" : 0,
            "strong" : 2,
            "extra-strong" : 3
            }
    
    size_d = {
            'short' : 1,
            'standard' : 1,
            'long' : 2,
            'extra long': 2
            }
    type_d = {
            'coffee' : 9
            }

    taste_d = {
            'standard' : 1,
            'mild' : 0,
            'strong' : 2,
            'extra-strong' : 3
            }

    foam_d ={
            u"" : 0
            }

    @classmethod
    def __init__(self, extra = False):
        arduino_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                for x in range (0, 10)
                if 'ttyUSB%d' % x  in p.name or "ttyACM%d" % x in p.name]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            warnings.warn('Multiple Arduinos found - using the first')
        self.ser = serial.Serial(
                port = arduino_ports[0],
                baudrate = 9600
                )
        self.is_serving = False
        if (extra):
            CoffeeHack.type_d = CoffeeHack.extra_type_d
            CoffeeHack.size_d = CoffeeHack.extra_size_d
            CoffeeHack.taste_d = CoffeeHack.extra_taste_d
            CoffeeHack.foam_d = CoffeeHack.extra_foam_d
        tmp = lang_config.config.get("coffeeSize")
        for k in tmp:
            for item in tmp[k]:
                if (k in CoffeeHack.size_d):
                    CoffeeHack.size_d[item] = CoffeeHack.size_d[k]
        tmp = lang_config.config.get("coffeeType")
        for k in tmp:
            for item in tmp[k]:
                if (k in CoffeeHack.type_d):
                    CoffeeHack.type_d[item] = CoffeeHack.type_d[k]
        tmp = lang_config.config.get("coffeeType")
        for k in tmp:
            for item in tmp[k]:
                if (k in CoffeeHack.type_d):
                    CoffeeHack.type_d[item] = CoffeeHack.type_d[k]
        tmp = lang_config.config.get("coffeeFoam")
        for k in tmp:
            for item in tmp[k]:
                if (k in CoffeeHack.foam_d):
                    CoffeeHack.foam_d[item] = CoffeeHack.foam_d[k]
    
    @staticmethod
    def compute_value(coffee_type, coffee_size, coffee_taste, number,coffee_foam=""):
        if (coffee_type == u'ristretto'):
            coffee_size = u'short'
        if (coffee_type == u'expresso'):
            coffee_taste = u'strong'
            coffee_size = u'short'
        if (coffee_type == u'latte' or coffee_type == u'milk' and coffee_foam == u''):
            coffee_foam = u'no frost'
        if (coffee_type == u'macchiato' or coffee_type == u'Flat White'  and coffee_foam == u''):
            coffee_foam = u'min frost'
        if (coffee_type == u'cappuccino' and coffee_foam == u''):
            coffee_foam = u'max frost'
        tmp_type = CoffeeHack.coffee_type_dict.get(coffee_type,
                CoffeeHack.coffee_type_dict[u'coffee'])
        size = CoffeeHack.coffee_size_dict.get(coffee_size,
                CoffeeHack.coffee_size_dict[u''])
        taste = CoffeeHack.coffee_taste_dict.get(coffee_taste,
                CoffeeHack.coffee_taste_dict[u''])
        foam = CoffeeHack.coffee_foam_dict.get(coffee_foam,
                CoffeeHack.coffee_foam_dict[u''])
        return number + tmp_type * 10 + size * 100 + \
                taste * 1000 + foam * 10000
    
    @staticmethod
    def is_able(coffee_type, coffee_size, coffee_taste, number):
        return coffee_type in CoffeeHack.coffee_type_dict
            and coffee_size not in CoffeeHack.coffee_size_dict
            and coffee_taste in CoffeeHack.coffee_taste_dict

    @classmethod
    def _stop_serving(self):
        self.is_serving = False

    @classmethod
    def pour(self, coffee_type, coffee_size, coffee_taste, number):
        coffee_type = coffee_type.encode('utf8')
        coffee_size = coffee_size.encode('utf8')
        coffee_taste = coffee_taste.encode('utf8')
        number = max(number, MIN_COFFEE)
        number = min(number, MAX_COFFEE)
        if (not CoffeeHack.is_able(coffee_type, coffee_size, coffee_taste, number)):
            return False
        value = CoffeeHack.compute_value(coffee_type, coffee_size, coffee_taste, number, u'')
        self.is_serving = True
        self.ser.write('B%dE\n'%(value))
        threading.Timer(20.0, self._stop_serving).start()
        return True

    def toggle_on_off(self):
        self.ser.write('T\n')

    def clean(self):
        self.ser.write('C\n')

    def steam(self):
        self.ser.write('V\n')

    def stop(self):
        if self.is_serving:
            self.ser.write('S\n')
            self.is_serving = False
            return True
        return False

    def is_pourring(self):
        return self.is_serving

if (__name__ == "__main__"):
    c = CoffeeHack();
    c.pour("normal", "short","fort",1)
    c.pour("normal",u"allongé","fort",1)
    c.pour("normal", "short","fort",2)
    c.pour("normal",u"allongé","fort",2)
    c.pour("normal", "short","mild",1)
    c.pour("normal",u"allongé","mild",1)
    c.pour("normal", "short","mild",2)
    c.pour("normal",u"allongé","mild",2)
    c.pour("normal", "short","normal",1)
    c.pour("normal",u"allongé","normal",1)
    c.pour("normal", "short","normal",2)
    c.pour("normal",u"allongé","normal",2)
    c.pour("normal", "short","extra strong",1)
    c.pour("normal",u"allongé","extra strong",1)
    c.pour("normal", "short","extra strong",2)
    c.pour("normal",u"allongé","extra strong",2)
