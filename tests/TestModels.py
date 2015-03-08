"""Tests for model architecture"""

from models import StandardModels
from models import ModelFactory
import unittest

class TestLinearRegression(unittest.TestCase):
    def test_model_creation(self):
        model_name = 'lin_reg'
        retrain_counter = 10
        model_obj = StandardModels.LinearRegression(model_name, retrain_counter)

        self.assertEqual(model_obj.model_name, model_name)
        self.assertEqual(model_obj.retrain_counter, retrain_counter)
        self.assertEqual(model_obj.model_type, "LinearRegression")

class TestModelInterface(unittest.TestCase):
    def test_factory_creation(self):
        model_name = 'lin_reg'
        retrain_counter = 10
        model_obj = StandardModels.LinearRegression(model_name, retrain_counter)
        model_obj2 = ModelFactory.createModel('LinearRegression',
                                              model_name,
                                              retrain_counter)

        self.assertEqual(model_obj, model_obj2)
