# coding: utf8
import os
from os.path import expanduser
import subprocess
import serial
import serial.tools.list_ports
import sys
import time
import warnings

MAX_COFFEE = 2
MIN_COFFEE = 1

class CoffeeHack:

    coffee_size_dict = {
        u'standard': 1,
        u'normal': 1,
        u'': 1,
        u'mon' : 1,
        u'my': 1,
        u'court': 1,
        u'short': 1,
        u'allongé'.encode('utf8'): 2,
        u'long': 2,
        u'extra allongé'.encode('utf8'): 2,
        u'extra long': 2,
    }
    """
    ok
    """

    coffee_type_dict = {
        u'': 9,
        u'café'.encode('utf8'): 9,
        u'coffee': 9,
        u'expresso': 9,
        u'ristretto': 9,
        u'cappuccino' : 9,
        u'flat white' : 9,
        u'café au lait'.encode('utf8'): 9,
        u'lattee machiato' : 9,
        u'machiato' : 9,
        u'latte': 9,
        u'milk' : 9,
        u'frothed milk' : 9,
    }
    """
    ok
    """

    coffee_taste_dict = {
        u'normal': 1,
        u'standard': 1,
        u'': 1,
        u'extra-léger'.encode('utf8'): 0,
        u'extra mild':0,
        u'léger': 0,
        u'mild': 0,
        u'fort': 2,
        u'strong': 2,
        u'extra-fort': 3,
        u'extra-strong': 3
    }
    """
    ok
    """
    coffee_foam_dict ={
        u"": 0,
        u"no frost": 1,
        u"min frost":2,
        u"max frost":3
    }

    @staticmethod
    def compute_value(coffee_type, coffee_size, coffee_taste, number,coffee_foam=""):
        if (coffee_type == u'ristretto'):
            coffee_size = u'short'
        if (coffee_type == u'expresso'):
            coffee_taste = u'strong'
            coffee_size = u'short'
        if (coffee_type == u'latte' and coffee_foam == u''):
            coffee_foam = u'no frost'
        if (coffee_type == u'milk' and coffee_foam ==u''):
            coffee_foam = u'no frost'
        if (coffee_type == u'machiato' and coffee_foam == u''):
            coffee_foam = u'min frost'
        if (coffee_type == u'flat white' and coffee_foam == u''):
            coffee_foam = u'min frost'
        if (coffee_type == u'capucino' and coffee_foam == u''):
            coffee_foam = u'max frost'
        #print("preparing: %i %s %s %s" % (number, coffee_type, coffee_size,
        #                                      coffee_taste))
        if (coffee_type not in CoffeeHack.coffee_type_dict):
            coffee_type = ""
        if (coffee_size not in CoffeeHack.coffee_size_dict):
            coffee_size = ""
        if (coffee_taste not in CoffeeHack.coffee_taste_dict):
            coffee_taste = ""
        tmp_type = CoffeeHack.coffee_type_dict[coffee_type]
        size = CoffeeHack.coffee_size_dict[coffee_size]
        taste = CoffeeHack.coffee_taste_dict[coffee_taste]
        foam = 0
        #return [number, tmp_type, size, taste, foam]
        return number + tmp_type * 10 + size * 100 + \
                taste * 1000 + foam * 10000
    @classmethod
    def __init__(self, locale = "EN_US"):
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
                            port=arduino_ports[0],
                            baudrate = 9600
                        )

    @classmethod
    def pour(self, coffee_type, coffee_size, coffee_taste, number, dialogue):
        coffee_type =coffee_type.encode('utf8')
        coffee_size =coffee_size.encode('utf8')
        coffee_taste =coffee_taste.encode('utf8')
        number = max(number, MIN_COFFEE)
        number = min(number, MAX_COFFEE)
        print(coffee_type)
        print(coffee_taste)
        print(coffee_size)
        value = CoffeeHack.compute_value(coffee_type, coffee_size, coffee_taste, number, u'')
        print(value)
        self.ser.write('B%dE\n'%(value))
        if (dialogue is not None):
            dialogue.end_session(None)


    def toggle_on_off(self, dialogue):
        self.ser.write('B10000E\n')
        if (dialogue is not None):
            dialogue.end_session(None)

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
