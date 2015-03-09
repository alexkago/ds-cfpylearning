import main
import time
import json
import numpy as np
import sys

class DataSender:
    def __init__(self, input_coef, constant_coef):
        self.input = input_coef
        self.constant = constant_coef

    def setUp(self):
        print "starting setup"
        main.app.config["TESTING"] = True
        main.connect_db()
        self.app = main.app.test_client()
        try:
            rv = self.app.get('/models/test_model1')
        except:
            self.app.post('/createModel',
                          data = json.dumps({"model_name": "test_model1",
                                             "model_type": "OnlineLinearRegression",
                                             "retrain_counter": 1}))
        print "finished setup"


    def test_training(self):
        while True:
            print "sending data"
            x = np.random.uniform(low=-5, high=5)
            self.app.post('/ingest',
                          data = json.dumps({"model_name": "test_model1",
                                             "input": x,
                                             "label": self.data_generator(x)}))
            time.sleep(0.2)

    def data_generator(self,x):
        return x * self.input + self.constant + np.random.normal()

input_coef = float(sys.argv[1])
constant_coef = float(sys.argv[2])
D = DataSender(input_coef, constant_coef)
D.setUp()
D.test_training()
