import sys,os
sys.path.append(os.path.abspath('.'))
from util.Metrics import Metrics

from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

import torch
import torch.nn as nn
import numpy as np
import time
import math
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import matplotlib
matplotlib.use('TKAgg')
from util.Dictionary import Dictionary as Dic

torch.manual_seed(0)
np.random.seed(0)

input_window = 80
output_window = 1
class MyLinearRegression():
    def __init__(self):
        # Create linear regression object
        self.regr = linear_model.LinearRegression()
    def create_inout_sequences(self, input_data, tw):
        inout_seq = []
        L = len(input_data)
        for i in range(L - tw):
            train_seq = input_data[i:i + tw]
            train_label = input_data[i + output_window:i + tw + output_window]
            inout_seq.append((train_seq, train_label))
        return torch.FloatTensor(inout_seq)

    def get_data(self, code):
        series = pd.read_csv(Dic.filename.format(code), usecols=['{}.close'.format(code)])
        series = series.values.reshape(-1)

        train_samples = int(0.7 * len(series))
        train_data = series[:train_samples]
        test_data = series[train_samples:]


        train_sequence = self.create_inout_sequences(train_data, input_window)
        train_sequence = train_sequence[:-output_window]

        test_data = self.create_inout_sequences(test_data, input_window)
        test_data = test_data[:-output_window]

        return train_sequence, test_data  

    def get_batch(self, source):
        input = torch.stack([item[0] for item in source])
        target = torch.stack([item[1][-1] for item in source])
        return input, target

    def train(self, train_data):
        diabetes_X_train, diabetes_y_train = self.get_batch(train_data)
        # Train the model using the training sets
        self.regr.fit(diabetes_X_train, diabetes_y_train)

    def evaluate(self):
        diabetes_X_test, diabetes_y_test = self.get_batch(val_data)
        # Make predictions using the testing set
        diabetes_y_pred = self.regr.predict(diabetes_X_test)

        # The coefficients
        # print("Coefficients: \n", self.regr.coef_)
        # The mean squared error
        # print("Mean squared error: %.2f" % mean_squared_error(diabetes_y_test, diabetes_y_pred))
        # The coefficient of determination: 1 is perfect prediction
        # print("Coefficient of determination: %.2f" % r2_score(diabetes_y_test, diabetes_y_pred))

    def plot_and_loss(self):
        diabetes_X_test, truth = self.get_batch(val_data)
        # Make predictions using the testing set
        diabetes_y_pred = self.regr.predict(diabetes_X_test)

        txt_test_result =""
        for index, s in enumerate(diabetes_y_pred):
            txt_test_result += "({},{:.2f})".format(index, s)
        txt_truth =""
        for index, s in enumerate(truth):
            txt_truth += "({},{:.2f})".format(index, s)
    
        metrics = Metrics()
        X_input = np.array(diabetes_X_test)[:,-1]
        # metrics.performance(X_input, diabetes_y_pred, truth, "Linear Regression SSE.600031")
        metrics.performance_metrics("LR{}".format(self.code), X_input, diabetes_y_pred, truth.reshape(-1))
        metrics.performance_values("LR{}".format(self.code), X_input, diabetes_y_pred, truth.reshape(-1))


        plt.plot(diabetes_y_pred, color="red")
        plt.plot(truth, color="blue")
        plt.grid(True, which='both')
        plt.axhline(y=0, color='k')
        plt.savefig('graph/Linear-epoch.png')
        plt.close()
        # return total_loss / i

# A50 stocks
Dic.codes = sorted(Dic.codes,reverse=True)
for code in Dic.codes:
    # one stock
    lr = MyLinearRegression()
    lr.code = code
    print("code={}".format(lr.code))
    train_data, val_data = lr.get_data(code)
    lr.train(train_data)
    lr.evaluate(val_data)
    lr.plot_and_loss()