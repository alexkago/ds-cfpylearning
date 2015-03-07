from ModelFactory import ModelInterface
import numpy as np
import json

class LinearRegression(ModelInterface):
    def __init__(self, name, rt_counter):
        ModelInterface.__init__(self, name, rt_counter, 'LinearRegression')

    def train(self, data):
        dict_data = [json.loads(el) for el in data]

        col_names = el[0].keys()
        input_keys = col_names.remove('label')

        x = [[el[key] for key in input_keys] for el in dict_data]
        y = [el['label'] for el in dict_data]

        parameters = np.polyfit(x, y, 1)
        self.parameter_dict = zip(input_keys.append['constant'], parameters)
        
        return parameter_dict

    def score(self, data):
        pass
