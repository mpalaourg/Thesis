import pandas
import numpy as np
import os
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.utils import shuffle
from scipy import stats
import metrics
import matplotlib.pyplot as plt

if __name__== "__main__" :
    current_directory = os.getcwd()
    df = pandas.read_csv("labeled_combinedDataset.csv")
    df = df.drop(["status", "health", "voltage", "Hotspot"], axis=1)
    # Get dummy variables for boolean
    df = pandas.get_dummies(df, columns = ["GPS", "Bluetooth", "Connectivity"])
    #df = df.drop(["GPS", "Bluetooth", "Connectivity"], axis=1)
    
    labels = [0, 1] # The only meaningfull clusters and with the necessarily points
    for label in labels:
        df_label = df[ (df["label"] == label) ]
        df_label = df_label.drop(["label"], axis=1)
        
        # Clear the data from outliers
        z = np.abs(stats.zscore(df_label["output"]))
        threshold = 2
        df_label = df_label[ (z<threshold) ]

        # Reset the index for the polynomial features merge
        df_label = df_label.reset_index(drop=True)

        # Get polynomial features
        polyTrans = PolynomialFeatures(degree=2, include_bias=False)
        df_label_Num = df_label[["level", "temperature", "usage", "Brightness", "RAM"]]
        df_label = df_label.drop(["level", "temperature", "usage", "Brightness", "RAM"], axis=1) # Drop them to get back later the poly Trans of them

        polyData_Num = polyTrans.fit_transform(df_label_Num)
        columnNames = polyTrans.get_feature_names(["level", "temperature", "usage", "Brightness", "RAM"])
        df_label_Num = pandas.DataFrame(polyData_Num, columns=columnNames)
        
        for column in columnNames:
            df_label[column] = pandas.Series( df_label_Num[column] )
        
        # Shuffle the data
        df_label = shuffle(df_label, random_state=1)
        df_label.reset_index(inplace=True, drop=True) 
        
        # Get dataframes
        y_label = df_label["output"]
        X_label = df_label.drop(["output"], axis=1)

        # Split data in training and testing
        X_train_label, X_test_label, y_train_label, y_test_label = train_test_split(X_label, y_label, test_size=0.25, random_state=42)
        
        # Create the model
        regressor = LinearRegression(normalize=False) # already normalized
        
        # get cross validation scores
        scoring = ['neg_mean_absolute_error', 'neg_root_mean_squared_error']
        scores = cross_validate(regressor, X_train_label, y_train_label, cv=3, scoring=scoring, return_train_score=True)
        print(f"MAE: {np.mean(scores['test_neg_mean_absolute_error'])} - RMSE: {np.mean(scores['test_neg_root_mean_squared_error'])} model_{label}")
        
        ''' Uncomment for ploting ...
        regressor = LinearRegression(normalize=False)
        # i need sizes of (n_Samples, features) , (n_Samples, )
        regressor.fit(X_train_label, y_train_label) 
        y_pred_label = regressor.predict(X_test_label)
        y_pred_label[ np.where(y_pred_label < 0) ] = 0                                           # Preciction cannot be < 0

        # Plotting linear model ...
        y_pred_label = regressor.predict(X_test_label)
        y_pred_label[ np.where(y_pred_label < 0) ] = 0 
        print(f"RMSE: {metrics.mean_squared_error(y_test_label, y_pred_label, squared=False)}, ΜΑΕ {metrics.mean_absolute_error(y_test_label, y_pred_label)} model_{label}")
        error = abs(y_test_label-y_pred_label)
        plt.figure()
        plt.title(f"Prediction error histogram [linear model_{label}]", fontweight='bold')
        plt.hist(error)
        plt.xlabel("Error bins", fontweight='bold')
        plt.ylabel("Appearances", fontweight='bold')
        plt.show()
        
        plt.figure()
        plt.plot(range(len(y_test_label)), y_test_label, color = 'blue', label = 'Real value', marker = 'o')
        plt.plot(range(len(y_pred_label)), y_pred_label, color = 'red', label = 'Estimated value', marker = 'o')
        plt.title(f"Estimation of energy drain [linear model_{label}]", fontweight='bold')
        plt.ylabel('Energy drain', fontweight='bold')
        plt.xlabel('Test Case', fontweight='bold')
        plt.legend()
        plt.show()
        '''