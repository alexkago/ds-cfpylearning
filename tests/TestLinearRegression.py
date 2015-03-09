import unittest
import main
import json
import pickle
from models import StandardModels


class TestLinearRegressionEndPoint(unittest.TestCase):

    def setUp(self):
        main.app.config["TESTING"] = True
        main.connect_db()
        self.app = main.app.test_client()
        self.app.post('/createModel',
                      data = json.dumps({"model_name": "test_model1",
                                         "model_type": "LinearRegression",
                                         "retrain_counter": 10}))

    def test_no_label_available(self):
        pass #TODO

    def test_training(self):
        for i in range(1,11):
            self.app.post('/ingest',
                          data = json.dumps({"model_name": "test_model1",
                                             "input": i,
                                             "label": i}))
        pickled_mdl = main.app.r.get('test_model1_object')
        mdl = pickle.loads(pickled_mdl)

        self.assertEqual(mdl.trained, True)
        self.assertEqual(mdl.available_data, 10)
        self.assertEqual(mdl.used_training_data, 10)
        self.assertEqual(mdl.col_names, ['input', 'label'])

    def test_training_with_added_data(self):
        for i in range(1,16):
            self.app.post('/ingest',
                          data = json.dumps({"model_name": "test_model1",
                                             "input": i,
                                             "label": i}))
        pickled_mdl = main.app.r.get('test_model1_object')
        mdl = pickle.loads(pickled_mdl)

        self.assertEqual(mdl.trained, True)
        self.assertEqual(mdl.available_data, 15)
        self.assertEqual(mdl.used_training_data, 10)
        self.assertEqual(mdl.col_names, ['input', 'label'])

    def test_object_equality(self):
        for i in range(1,11):
            self.app.post('/ingest',
                          data = json.dumps({"model_name": "test_model1",
                                             "input": i,
                                             "label": i}))
        pickled_mdl = main.app.r.get('test_model1_object')
        mdl = pickle.loads(pickled_mdl)

        # compare to manually created object
        model_name = 'test_model1'
        retrain_counter = 10
        model_obj = StandardModels.LinearRegression(model_name, retrain_counter)

        for i in range(0,10):
            model_obj.avail_data_incr()

        model_obj.train(['{"input": 1, "label": 1}',
                         '{"input": 2, "label": 2}',
                         '{"input": 3, "label": 3}',
                         '{"input": 4, "label": 4}',
                         '{"input": 5, "label": 5}',
                         '{"input": 6, "label": 6}',
                         '{"input": 7, "label": 7}',
                         '{"input": 8, "label": 8}',
                         '{"input": 9, "label": 9}',
                         '{"input": 10, "label": 10}'])

        self.assertEqual(model_obj.get_parameters(), mdl.get_parameters())

        del mdl.mdl
        del model_obj.mdl
        self.assertEqual(model_obj, mdl)

    def test_model_name_missing(self):
        rv = self.app.post('/ingest',
                           data = json.dumps({"input": 1,
                                              "label": 1}))

        self.assertEqual(rv.status_code, 422)

    def test_wrong_data_format(self):
        rv = self.app.post('/ingest',
                           data = json.dumps({"model_name": "test_model1",
                                              "input": 1,
                                              "label": 1}))

        self.assertEqual(rv.status_code, 201)

        rv = self.app.post('/ingest',
                           data = json.dumps({"model_name": "test_model1",
                                              "input": 1,
                                              "label": 1,
                                              "foo": 1}))

        self.assertEqual(rv.status_code, 422)

    def test_scoring_untrained(self):
        rv = self.app.post('/score',
                           data = json.dumps({"model_name": "test_model1",
                                              "input": 5}))

        self.assertEqual(rv.status_code, 404)

    def test_scoring_wrong_data(self):
        for i in range(1,11):
            self.app.post('/ingest',
                          data = json.dumps({"model_name": "test_model1",
                                             "input": i,
                                             "label": i}))

        rv = self.app.post('/score',
                           data = json.dumps({"model_name": "test_model1",
                                              "input_foo_bar": 5}))

        self.assertEqual(rv.status_code, 422)

    def test_scoring(self):
        for i in range(1,11):
            self.app.post('/ingest',
                          data = json.dumps({"model_name": "test_model1",
                                             "input": i,
                                             "label": i}))

        rv = self.app.post('/score',
                           data = json.dumps({"model_name": "test_model1",
                                              "input": 5}))

        response = json.loads(rv.data)
        self.assertEqual(response, {"request": {"input": 5,
                                                "model_name": "test_model1"},
                                    "predicted_label": 5.0})

    def tearDown(self):
        main.app.r.flushdb()
