"""Tests for cfpylearning"""

import main
import json
import unittest


class TestServiceExists(unittest.TestCase):

    def setUp(self):
        main.app.config["TESTING"] = True
        self.app = main.app.test_client()

    def test_service_exists(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)


class TestModelCreationEndpoint(unittest.TestCase):

    def setUp(self):
        main.app.config["TESTING"] = True
        main.connect_db()
        self.app = main.app.test_client()

    def test_missing_retrain_information(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_name": "model1",
                                              "model_type": "LinearRegression"}))
        self.assertEqual(rv.status_code, 422)

    def test_missing_model_name(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_type": "LinearRegression"}))
        self.assertEqual(rv.status_code, 422)

    def test_missing_model_type(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_type": "LinearRegression"}))
        self.assertEqual(rv.status_code, 422)

    def test_model_creation(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_name": "test_model1",
                                              "model_type": "LinearRegression",
                                              "retrain_counter": 10}))
        self.assertEqual(rv.status_code, 201)

    def test_non_defined_model(self):
        rv = self.app.post('/createModel',
                           data = json.dumps({"model_name": "test_model1",
                                              "model_type": "SuperDuperModel",
                                              "retrain_counter": 10}))
        self.assertEqual(rv.status_code, 422)

    def tearDown(self):
        main.app.r.flushdb()
