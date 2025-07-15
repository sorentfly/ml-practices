import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from perceptron import Perceptron
from adaline import Adaline

df = pd.read_csv("data/iris.csv", names=["sepal_length", "sepal_width", "petal_length", "petal_width", "name"])

X = df.iloc[0:100, [0, 2]].values

y = df.loc[0:100, 'name']
y = np.where(y == 'Iris-setosa', -1, 1)

# standard normalization
X_std = np.copy(X)
X_std[:, 0] = (X[:, 0] - X[:, 0].mean()) / X[:, 0].std()
X_std[:, 1] = (X[:, 1] - X[:, 1].mean()) / X[:, 1].std()


def process_classifier(input_features, answers_vector, classifier: Perceptron, plots: bool = True):
    classifier.execute(input_set=input_features, expected_set=answers_vector)

    if plots:
        show_error_plot(classifier.errors)

        plot_decision_regions(input_features, answers_vector, classifier)
        plt.title('ADALINE (градиентный спуск) ')
        plt.xlabel(' длина чашелистика [стандартизованная]')
        plt.ylabel('длина лепестка [стандартизованная]')
        plt.legend(loc='upper left')
        plt.show()


def show_error_plot(input_vector):
    plt.plot(input_vector, 'o-r')
    plt.ylabel('errors')
    plt.xlabel('iteration')
    plt.show()


def plot_decision_regions(X, y, classifier, resolution=0.02):
    # настроить генератор маркеров и палитру
    markers = ('s', 'x', '0', '^', 'v')
    colors = ('red', 'blue', 'lightgreen ', 'gray', 'cyan')
    cmap = ListedColormap(colors[:len(np.unique(y))])
    # вывести поверхность решения
    x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, resolution),
                           np.arange(x2_min, x2_max, resolution))
    z = classifier.predict(np.array([xx1.ravel(), xx2.ravel()]).T)
    z = z.reshape(xx1.shape)
    plt.contourf(xx1, xx2, z, alpha=0.4, cmap=cmap)
    plt.xlim(xx1.min(), xx1.max())
    plt.ylim(xx2.min(), xx2.max())
    # показать образцы классов
    for idx, cl in enumerate(np.unique(y)):
        plt.scatter(x=X[y == cl, 0], y=X[y == cl, 1],
                    alpha=0.8, c=cmap(idx),
                    marker=markers[idx], label=cl)


if __name__ == "__main__":
    x_train = np.concatenate((X_std[:25], X_std[50:90]))
    # y_train = np.concatenate((y[:25], y[50:90]))
    # x_test = np.concatenate((X_std[25:50], X_std[90:]))
    # y_test = np.concatenate((y[25:50], y[90:]))

    # x_train = np.concatenate((X[:25], X[50:90]))
    y_train = np.concatenate((y[:25], y[50:90]))
    # x_test = np.concatenate((X[25:50], X[90:]))
    y_test = np.concatenate((y[25:50], y[90:]))

    ada = Adaline(iterations_count=13, eta=0.01)
    # ppt = Perceptron(iterations_count=60)
    process_classifier(x_train, y_train, ada)
    # print(ppt.test(x_test, y_test))
