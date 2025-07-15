import numpy as np


class Perceptron:
    def __init__(
            self,
            iterations_count: int = 10,
            eta: float = 0.1,
    ):
        self.iterations_count = iterations_count
        self.eta = eta
        self.weights = []
        self.errors = []

    def execute(
            self,
            input_set,
            expected_set,
    ):
        self.weights = np.zeros(input_set.shape[1] + 1)

        for _ in range(self.iterations_count):
            error = 0
            for xi, y in zip(input_set, expected_set):
                y_ = self.predict(xi)
                update = self.eta * (y - y_)
                self.weights[1:] += update * xi
                self.weights[0] += update

                error += 1 if y != y_ else 0
            self.errors.append(error)

    def test(
            self,
            input_set,
            expected_set,
    ):
        errors = 0
        for xi, y in zip(input_set, expected_set):
            y_ = self.predict(xi)
            update = self.eta * (y - y_)
            self.weights[1:] += update * xi
            self.weights[0] += update

            errors += 1 if y != y_ else 0
        return f'test ended with {errors} errors'

    def net_input(
            self,
            input_set,
    ) -> float:
        return np.dot(input_set, self.weights[1:]) + self.weights[0]

    def predict(self, input_set):
        return np.where(self.net_input(input_set) >= 0, 1, - 1)
