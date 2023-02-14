import json
import os
import sys
import pickle

class Data:
    def __init__(self, data):
        self.json = 'data.json'

    # write list to binary file
    def write_json(self,data):
        with open(self.json, 'wt') as f:
            json.dump(data, f)

    # Read list to memory
    def read_json(self):
        with open(self.json, 'rt') as f:
            array = json.load(f)
            return array
        
    def append_list(self, type, value):
        array = self.read_json()
        array[type[0]][type[1]] = value
        write = self.write_list(array)
        return write
    
    def compare(self, type, value):
        file = self.read_json()
        low = float(file[type]['low'])
        high = float(file[type]['high'])
        if float(value) < low:
            return self.append_list([type,'low'], value)
        elif float(value) > high:
            return self.append_list([type,'high'], value)
        else:
            return False
    def find(self,type):
        file = self.read_json()
        return file[type[0]][type[1]]