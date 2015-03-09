from ModelFactory import ModelInterface, train_wrapper
import numpy as np

class OnlineLinearRegression(ModelInterface):
    def __init__(self, name, rt_counter):
        ModelInterface.__init__(self, name, rt_counter, 'OnlineLinearRegression')
        self.alpha = 0.002

    @train_wrapper
    def train(self, data, col_names):
        # only use the last data point all the time
        data = [data[-1]]

        # initialize theta
        if not self.trained:
            self.theta = np.zeros(shape=(len(col_names), 1))

        # create training data and append constant to x for intercept
        input_keys = col_names[:]
        input_keys.remove('label')

        x = [[el[key] for key in input_keys] for el in data]
        y = [el['label'] for el in data]
        x.append([1])

        # create numpy array for X data
        X = np.array(x)
        X.shape = (1,len(col_names))

        # SGD functions
        def compute_cost(X, y, theta):
            '''
            Comput cost for linear regression
            '''
            #Number of training samples
            m = y.size
            predictions = X.dot(theta).flatten()
            sqErrors = (predictions - y) ** 2
            J = (1.0 / (2 * m)) * sqErrors.sum()

            return J

        def gradient_descent(X, y, theta, alpha):
            '''
            Performs gradient descent to learn theta
            by taking num_items gradient steps with learning
            rate alpha
            '''
            m = len(y)

            predictions = X.dot(theta).flatten()

            errors_x1 = (predictions - y) * X[:, 0]
            errors_x2 = (predictions - y) * X[:, 1]

            theta[0][0] = theta[0][0] - alpha * (1.0 / m) * errors_x1.sum()
            theta[1][0] = theta[1][0] - alpha * 10 * (1.0 / m) * errors_x2.sum()

            return theta


        self.theta = gradient_descent(X, y, self.theta, self.alpha)

        return self.get_parameters()

    def score(self, data):
        data.append(1)
        return np.sum(self.theta * data)

    def get_parameters(self):
        coefficients = self.theta

        col_names = self.col_names[:]
        col_names.remove('label')
        col_names.append('constant')

        return dict(zip(col_names, coefficients))
