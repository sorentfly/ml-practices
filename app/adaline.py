import numpy as np
import numpy.typing as npt
from typing import Any


class Adaline:
    def __init__(
            self,
            iterations_count: int = 10,
            eta: float = 0.0001,
    ):
        self.iterations_count = iterations_count
        self.eta = eta
        self.weights = []
        self.error = 0

    def net_input(
            self,
            input_set: npt.NDArray[Any],
    ) -> float:
        return input_set.dot(self.weights[1:]) + self.weights[0]

    def activation(self, input_set):
        return self.net_input(input_set)

    def predict(self, input_set):
        return np.where(self.activation(input_set) >= 0, 1, -1)

    def execute(
            self,
            input_set: npt.NDArray[Any],
            expected_set: npt.NDArray[Any],
    ):
        self.weights = np.zeros(input_set.shape[1] + 1)

        self.errors = []

        for _ in range(self.iterations_count):
            vector_y_ = self.net_input(input_set)
            delta_y = expected_set - vector_y_

            self.weights[1:] += self.eta * input_set.T.dot(delta_y)
            self.weights[0] += self.eta * delta_y.sum()

            error = (delta_y ** 2).sum() / 2.0

            self.errors.append(error)
