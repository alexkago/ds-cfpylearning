import abc
import StandardModels

class ModelInterface:
    __metaclass__  = abc.ABCMeta
    def __init__(self, model_name, retrain_counter, model_type):
        self.model_name = model_name
        self.model_type = model_type
        self.trained = False
        self.used_training_data = 0
        self.retrain_counter = retrain_counter

    @abc.abstractmethod
    def train(self, train_data):
        """This method needs to be implemented"""

    @abc.abstractmethod
    def score(self, score_data):
        """This method needs to be implemented"""

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __str__(self):
        return str(self.__dict__)


def createModel(model_type, model_name, retrain_counter):
    return getattr(StandardModels, model_type)(model_name, retrain_counter)
