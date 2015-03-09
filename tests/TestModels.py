"""Tests for model architecture"""

from models import StandardModels
from models import ModelFactory
import unittest

class TestModelCreation(unittest.TestCase):
    def test_linear_regression(self):
        model_name = 'lin_reg'
        retrain_counter = 10
        model_obj = StandardModels.LinearRegression(model_name, retrain_counter)

        self.assertEqual(model_obj.model_name, model_name)
        self.assertEqual(model_obj.retrain_counter, retrain_counter)
        self.assertEqual(model_obj.model_type, "LinearRegression")

    def test_online_linear_regression(self):
        model_name = 'onl_lin_reg'
        retrain_counter = 1
        model_obj = ModelFactory.createModel('OnlineLinearRegression',
                                              model_name,
                                              retrain_counter)

        self.assertEqual(model_obj.model_name, model_name)
        self.assertEqual(model_obj.retrain_counter, retrain_counter)
        self.assertEqual(model_obj.model_type, "OnlineLinearRegression")

    def test_factory_creation(self):
        model_name = 'lin_reg'
        retrain_counter = 10
        model_obj = StandardModels.LinearRegression(model_name, retrain_counter)
        model_obj2 = ModelFactory.createModel('LinearRegression',
                                              model_name,
                                              retrain_counter)

        self.assertEqual(model_obj, model_obj2)
