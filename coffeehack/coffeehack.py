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

    extra_size_dict = {
        u'standard': 2,
        u'normal': 2,
        u'': 1,
        u'mon' : 1,
        u'my': 1,
        u'court': 1,
        u'short': 1,
        u'allongé'.encode('utf8'): 3,
        u'long': 3,
        u'extra allongé'.encode('utf8'): 4,
        u'extra long': 4,
}
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
    extra_type_dict = {
        u'café'.encode('utf8'): 9,
        u'coffee': 9,
        u'expresso': 9,
        u'espresso': 9,
        u'ristretto': 9,
        u'cappuccino' : 8,
        u'flat white' : 0,
        u'Flat White' : 0,
        u'café au lait'.encode('utf8'): 0,
        u'lattee machiato' : 1,
        u'latte machiato' : 1,
        u'macchiato' : 1,
        u'machiato' : 1,
        u'latte': 2,
        u'milk' : 2,
        u'frothed milk' : 2,
    }

    coffee_type_dict = {
        u'café'.encode('utf8'): 9,
        u'coffee': 9,
        u'espresso': 9,
        u'expresso': 9,
        u'ristretto': 9,
    }
    """
    ok
    """
    extra_taste_dict = {
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
    extra_foam_dict ={
        u"": 0,
        u"no frost": 1,
        u"min frost": 2,
        u"max frost": 3
    }

    coffee_foam_dict ={
        u"": 0,
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
        if (coffee_type == u'macchiato' and coffee_foam == u''):
            coffee_foam = u'min frost'
        if (coffee_type == u'Flat White' and coffee_foam == u''):
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
        if coffee_type not in CoffeeHack.coffee_type_dict:
            return False
        if coffee_size not in CoffeeHack.coffee_size_dict:
            return False
        return coffee_taste in CoffeeHack.coffee_taste_dict

    @classmethod
    def __init__(self, locale = "EN_US", extra = False):
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
        if (extra):
            CoffeeHack.coffee_type_dict = CoffeeHack.extra_type_dict
            CoffeeHack.coffee_size_dict = CoffeeHack.extra_size_dict
            CoffeeHack.coffee_taste_dict = CoffeeHack.extra_taste_dict
            CoffeeHack.coffee_foam_dict = CoffeeHack.extra_foam_dict
        self.is_serving = False

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
        self.ser.write('B%dE\n'%(value))
        threading.Timer(20.0, self._stop_serving).start()
        return True

    def toggle_on_off(self):
        self.ser.write('B10000E\n')

    def clean(self):
        self.ser.write('B20000E\n')

    def steam(self):
        self.ser.write('B30000E\n')

    def stop(self):
        if self.is_serving:
            self.ser.write('B191E\n')
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
