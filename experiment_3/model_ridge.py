import pandas
import numpy as np
import os
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, train_test_split
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
    
    labels = [0, 1, 3] # The only meaningfull clusters and with the necessarily points
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

        # Get dataframes 
        y_label = df_label["output"]
        X_label = df_label.drop(["output"], axis=1)
        
        # Split data training and testing ...
        X_train_label, X_test_label, y_train_label, y_test_label = train_test_split(X_label, y_label, test_size=0.25, random_state=42)
        
        # Create the model
        regressor = Ridge()
        
        # find optimal alpha with grid search
        alpha = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
        param_grid = {'alpha': alpha}
        scoring = ['neg_mean_absolute_error', 'neg_root_mean_squared_error']
        grid = GridSearchCV(estimator=regressor, param_grid=param_grid, scoring=scoring, refit=scoring[0], return_train_score=True, cv=3)
        grid_result = grid.fit(X_train_label, y_train_label)
        
        print(f"Best Score: {abs(grid_result.best_score_)} - Best Params: {grid_result.best_params_} for label {label} ({df_label.shape}) [{min(y_train_label)}, {max(y_train_label)}]")
        
        cv_results = grid.cv_results_
        best_index = grid.best_index_
        print(f"MAE: {cv_results['mean_test_neg_mean_absolute_error'][best_index]} - RMSE: {cv_results['mean_test_neg_root_mean_squared_error'][best_index]} model_{label}")
    
        ''' Uncomment for ploting ...
        # Get best model for each label
        bestRegressor = grid.best_estimator_

        # Plotting ridge model ...
        y_pred_label = bestRegressor.predict(X_test_label)
        y_pred_label[ np.where(y_pred_label < 0) ] = 0 
        print(f"RMSE: {metrics.mean_squared_error(y_test_label, y_pred_label, squared=False)}, ΜΑΕ {metrics.mean_absolute_error(y_test_label, y_pred_label)} model_{label}")
        error = abs(y_test_label-y_pred_label)
        plt.figure()
        plt.title(f"Prediction error histogram [ridge model_{label}]", fontweight='bold')
        plt.hist(error)
        plt.xlabel("Error bins", fontweight='bold')
        plt.ylabel("Appearances", fontweight='bold')
        plt.show()
        
        plt.figure()
        plt.plot(range(len(y_test_label)), y_test_label, color = 'blue', label = 'Real value', marker = 'o')
        plt.plot(range(len(y_pred_label)), y_pred_label, color = 'red', label = 'Estimated value', marker = 'o')
        plt.title(f"Estimation of energy drain [ridge model_{label}]", fontweight='bold')
        plt.ylabel('Energy drain', fontweight='bold')
        plt.xlabel('Test Case', fontweight='bold')
        plt.legend()
        plt.show()
        '''