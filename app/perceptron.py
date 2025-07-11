import numpy as np

class Perceptron:
    def __init__(
            self,
            iterations_count: int=10,
            eta: float=0.1,
    ):
        self.iterations_count = iterations_count
        self.eta = eta

    def execute(
            self,
            input_set,
            expected_set,
    ):
        self.weights = np.zeros(input_set.shape[1] + 1)

        for _ in range(self.iterations_count):
            for xi, y in zip(input_set, expected_set):
                update = self.eta * (y - self.predict(xi))
                self.weights[1:] += update * xi
                self.weights[0] += update

    def net_input(
            self,
            input_set,
    ) -> float:
        return np.dot(input_set, self.weigths[1:]) + self.weigths[0]

    def predict(self, input_set):
        return 1 if self.net_input(input_set) >= 0 else -1