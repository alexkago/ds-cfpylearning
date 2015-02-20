import numpy as np
import json

def train(data):
    dict_data = [json.loads(el) for el in data]
    x = [el['input'] for el in dict_data]
    y = [el['label'] for el in dict_data]

    parameters = np.polyfit(x, y, 1)
    return zip(['input', 'constant'], parameters)
