import json
import os
import sys
import pickle
import MetaArray #pip install MetaArray
array = [
    [],  #brightness set        #array[0][x]
    [],  #ambient light         #array[1][x]
    [],  #distance              #array[2][x]
    [],  #cct set               #array[3][x]
    []   #time of day (hours)   #array[4][x]
        ]
class Data:
    def __init__(self, data):
        self.json = 'data.json'
        self.arr = 'dat.diyson'

    # write list to binary file
    def write_list(self,array):
        with open(self.arr, 'wb') as f:
            pickle.dump(array, f)
            return True
    # Read list to memory
    def read_list(self):
        with open(self.arr, 'rb') as fp:
            array = pickle.load(fp)
            return array
    def append_list(self, type, value):
        array = self.read_list()
        array[type].append(value)
        write = self.write_list(array)
        return write