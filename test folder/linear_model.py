'''
    Linear model for prediction on dSOC/dt
'''
import os
import numpy as np
import pandas
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import metrics
import helpers

if __name__== "__main__" :
    current_directory = os.getcwd()
    #test_directory = current_directory + '\\testFiles'
    test_directory = current_directory + '\\combined'
    currentFileList = os.listdir(test_directory)
    for f in currentFileList:
        user = f.split('-')[0]
        df = pandas.read_csv(test_directory + "\\" + f)
        # Drop strings values #
        df.drop(['_id', 'ID', 'technology', 'brandModel', 'androidVersion'], axis=1, inplace=True)
        X = df.drop('output', axis=1)
        y = np.array( df["output"] )
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)
        
        regressor = LinearRegression()
        # i need sizes of (n_Samples, features) , (n_Samples, )
        regressor.fit(X_train, y_train) 
        y_pred = regressor.predict(X_test)
        # Calculate some metrics for good measure
        #MSE  = metrics.mean_squared_error(y_test, y_pred, squared=True)
        #RMSE = metrics.mean_squared_error(y_test, y_pred, squared=False)
        #MAE  = metrics.median_absolute_error(y_test, y_pred)
        MSPE  = metrics.mean_squared_percentage_error(y_test, y_pred, squared=True)
        RMSPE = metrics.mean_squared_percentage_error(y_test, y_pred, squared=False)
        MAPE   = metrics.mean_absolute_percentage_error(y_test, y_pred)
        # https://en.wikipedia.org/wiki/Coefficient_of_determination -> (y_i-y_hat_i)^2/y_i / (y_i-y_mean_i)^2/y_i => y_i would cancel out
        R_sq = metrics.r2_score(y_test, y_pred) # does not be affected by percentage
        adj_R_sq = 1 - (1 - R_sq) * (len(y_train) - 1) / (len(y_train) - X_train.shape[1] - 1)
        print(f"MSPE = {round(MSPE,4)}\tRMSPE = {round(RMSPE,4)}\tMAPE = {round(MAPE,4)}\tR^2 = {round(R_sq,4)}\tadjusted R^2 = {round(adj_R_sq,4)} for user {user}")
        
        ## Plots ##
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot(y_test, color = 'blue', label = 'Real value', marker = 'o')
        ax1.plot(y_pred, color = 'red', label = 'Estimated value', marker = 'o')
        ax1.set_title(f"dSOC/dt")
        ax1.set(ylabel = 'dSOC/dt', xlabel = 'Test Case')
        ax1.set_xlim(0, len(y_test))
        ax1.legend()

        #AE = abs( y_test - y_pred)
        APE = helpers.APE(y_test, y_pred)
        ax2.scatter(range(len(y_test)), APE, label = 'Absolute Percentage Error', color = 'black', marker = 'o')    
        ax2.set_title(f"Error of dSOC/dt Estimation")
        ax2.legend()
        ax2.set(ylabel = 'APE (%)', xlabel = 'Test Case')
        ax2.set_xlim(0, len(y_test))
        
        plt.show()

        #MSE at each tree (best = 2)
        #errors = [mean_squared_error(y_test, y_pred) for y_pred in regressor.staged_predict(X_test)]
        #best_n_estimators = np.argmin(errors)
        #print(best_n_estimators)
        