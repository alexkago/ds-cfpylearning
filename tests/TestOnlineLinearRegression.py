import unittest
import main
import json
import pickle

class TestOnlineLinearRegressionEndPoint(unittest.TestCase):

    def setUp(self):
        main.app.config["TESTING"] = True
        main.connect_db()
        self.app = main.app.test_client()
        self.app.post('/createModel',
                      data = json.dumps({"model_name": "test_model1",
                                         "model_type": "OnlineLinearRegression",
                                         "retrain_counter": 1}))


    def test_training(self):
        for i in range(1,11):
            self.app.post('/ingest',
                          data = json.dumps({"model_name": "test_model1",
                                             "input": i,
                                             "label": i}))
        pickled_mdl = main.app.r.get('test_model1_object')
        mdl = pickle.loads(pickled_mdl)

        print mdl

        self.assertEqual(mdl.trained, True)
        self.assertEqual(mdl.available_data, 10)
        self.assertEqual(mdl.used_training_data, 10)
        self.assertEqual(mdl.col_names, ['input', 'label'])

    def tearDown(self):
        main.app.r.flushdb()
