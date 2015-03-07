"""Tests for model architecture"""

from models import StandardModels
from models import ModelFactory

class TestLinearRegression:
    def test_model_creation(self):
        model_name = 'lin_reg'
        retrain_counter = 10
        model_obj = StandardModels.LinearRegression(model_name, retrain_counter)

        assert model_obj.model_name == model_name
        assert model_obj.retrain_counter == retrain_counter
        assert model_obj.model_type == "LinearRegression"

class TestModelInterface:
    def test_factory_creation(self):
        model_name = 'lin_reg'
        retrain_counter = 10
        model_obj = StandardModels.LinearRegression(model_name, retrain_counter)
        model_obj2 = ModelFactory.createModel('LinearRegression',
                                              model_name,
                                              retrain_counter)

        assert model_obj == model_obj2
