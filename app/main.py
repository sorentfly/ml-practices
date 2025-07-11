import pandas as pd

from perceptron import Perceptron

def main():
    df = pd.read_csv("data/iris.csv", names=["sepal_length", "sepal_width", "petal_length", "petal_width", "name"])
    X = df[df["name"].str.contains("Iris-virginica")==False].drop('sepal_width', axis=1).drop('petal_width', axis=1).drop('name', axis=1).to_numpy()
    y = df[df["name"].str.contains("Iris-virginica")==False]['name'].replace('Iris-setosa', -1).replace('Iris-versicolor', 1).to_numpy()

    print(X)
    print('....')
    print(y)
    print(Perceptron(10, 0.2))

if __name__ == "__main__":
    main()
