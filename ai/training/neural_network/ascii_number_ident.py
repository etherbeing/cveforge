import numpy as np
from numpy.random import random


class NeuralNetwork:
    _body: dict = {}
    def __init__(self, data: str, no_layers: int=4, ) -> None:
        self.input_layer = map(lambda: x: ord(x), data)
        self.neurons = np.minimum(4, no_layers)
        self.weights = np.random([no_layers])

    def _sigmoid_fnc(self, x: float) -> float:
        """Activation function for output value or prediction"""
        return 1/(1+np.e**(-x))
    
    def _relu_fnc(self, x: float):
        return np.maximum(0, x)
    
    def is_number(self,):
        """Do NOT use this function to determine whether or not something is a number, instead use something lower level and more straightforward
        this function it use a neural network to determine whether or not an ascii value is a number, this is OVERKILL.
        """

        return False