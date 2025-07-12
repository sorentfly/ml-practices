import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from perceptron import Perceptron


df = pd.read_csv("data/iris.csv", names=["sepal_length", "sepal_width", "petal_length", "petal_width", "name"])


X = df[df["name"].str.contains("Iris-virginica") == False].drop('sepal_width', axis=1).drop('petal_width', axis=1).drop('name', axis=1).to_numpy()


y = df[df["name"].str.contains("Iris-virginica") == False]['name'].replace('Iris-setosa', -1).replace('Iris-versicolor', 1).to_numpy()


def process_classifier(input_features, answers_vector, classifier: Perceptron):
    classifier.execute(input_set=input_features, expected_set=answers_vector)

    show_error_plot(classifier.errors)

    show_decision_plot(classifier)


def show_decision_plot(classifier):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.scatter(X[:len(X) // 2, 0], X[:len(X) // 2, 1], color='green', edgecolor='black', alpha=1)
    ax1.scatter(X[len(X) // 2:, 0], X[len(X) // 2:, 1], color='red', edgecolor='black', alpha=1)
    x = np.linspace(4, 8, 100)
    f = - classifier.weights[0] - classifier.weights[1] / classifier.weights[2] * x
    ax1.plot(x, f, 'k')
    plt.title('Result border calculated with perceptron')
    plt.xlabel('sepal lenth')
    plt.ylabel('petal_lenght')
    plt.show()


def show_error_plot(input_vector):
    plt.plot(input_vector, 'o-r')
    plt.ylabel('errors')
    plt.xlabel('iteration')
    plt.show()


if __name__ == "__main__":
    ppt = Perceptron()
    process_classifier(X, y, ppt)
