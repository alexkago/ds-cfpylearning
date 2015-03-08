"""Tests for cfpylearning"""

import main
import json

class TestServiceExists:

    def setUp(self):
        main.app.config["TESTING"] = True
        self.app = main.app.test_client()

    def test_service_exists(self):
        rv = self.app.get('/')
        assert rv.status_code == 200


class TestModelCreationEndpoint:

    def setUp(self):
        main.app.config["TESTING"] = True
        self.app = main.app.test_client()
        self.r = main.r

    def test_missing_retrain_information(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_name": "model1",
                                              "model_type": "linear_regression"}))
        assert rv.status_code == 422

    def test_missing_model_name(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_type": "linear_regression"}))
        assert rv.status_code == 422

    def test_missing_model_type(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_type": "linear_regression"}))
        assert rv.status_code == 422

    def test_model_creation(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_name": "test_model1",
                                              "model_type": "linear_regression",
                                              "retrain_counter": 10}))
        assert rv.status_code == 201

    def tearDown(self):
        self.r.flushall()
#
# class TestPredictEndpoint:
#
#     def setUp(self):
#         app.config["TESTING"] = True
#         self.app = app.test_client()
#
#     def test_endpoint_exists(self):
#         rv = self.app.post('/predict/1',
#                            data = json.dumps(dict(x=1, y=1)))
#         self.assertEqual(rv.status_code, 200)
#
#     def test_json_returned(self):
#         rv = self.app.post('/predict/1',
#                            data = json.dumps(dict(x=1, y=1)))
#         self.assertEqual(from_json(rv), dict(x=1, y=1, z=2))
#
#     def test_args_received(self):
#         rv = self.app.post('/predict/1',
#                            data = json.dumps(dict(x=2, y=3)))
#         self.assertEqual(from_json(rv), dict(x=2, y=3, z=13))
#
#     def test_bad_args(self):
#         rv = self.app.post('/predict/1',
#                            data = json.dumps(dict(x="Hello", y="World")))
#         self.assertEqual(rv.status_code, 400) #Bad Request
