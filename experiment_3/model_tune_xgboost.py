# Xgboost final parameter tuning ...
import pandas
import numpy as np
import os
from xgboost import XGBRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV, train_test_split
from scipy import stats
import matplotlib.pyplot as plt

if __name__== "__main__" :
    current_directory = os.getcwd()
    df = pandas.read_csv("labeled_combinedDataset.csv")
    df = df.drop(["status", "health", "voltage", "Hotspot"], axis=1)
    # Get dummy variables for boolean
    df = pandas.get_dummies(df, columns = ["GPS", "Bluetooth", "Connectivity"])
    #df = df.drop(["GPS", "Bluetooth", "Connectivity"], axis=1)
    
    # Create param grids for each model individual
    n_estimators = [i for i in range(500, 1500, 100)]
    learning_rates = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    max_depths = [3, 4, 5, 6, 7, 8]
    colsample_bytree=[0.40, 0.45, 0.50, 0.55]
    reg_lambda = [0.30, 0.35, 0.40, 0.45]
    param_grid = {'n_estimators': n_estimators, 'learning_rate': learning_rates, 'max_depth': max_depths, 
                  'colsample_bytree': colsample_bytree, 'reg_lambda': reg_lambda}

    param_grids = [param_grid, param_grid, param_grid]    
    
    # The selected column names for each label
    column_0 = ['temperature Brightness', 'usage Brightness', 'Brightness^2', 'level Brightness', 'level^2', 'Brightness RAM', 'level', 'temperature^2']
    column_1 = ['Brightness^2', 'temperature Brightness', 'usage Brightness', 'level Brightness', 'Brightness RAM', 'level', 'usage^2']
    column_3 = ['temperature Brightness', 'Brightness', 'usage^2', 'temperature usage', 'usage Brightness', 'level^2', 'level Brightness',
                'temperature^2', 'level', 'Brightness RAM', 'level temperature', 'usage']
    selColumns = [column_0, column_1, column_3]
    
    labels = [0, 1, 3] # The only meaningfull clusters and with the necessarily points
    for idx, label in enumerate(labels):
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
        
        # Keep only the selected columns for each labels
        X_label = X_label[selColumns[idx]]

        # Split data training and testing ...
        X_train_label, X_test_label, y_train_label, y_test_label = train_test_split(X_label, y_label, test_size=0.25, random_state=42)
        
        # Create the model
        regressor = XGBRegressor()
        
        # find optimal values with grid search (test if grid search is working)
        #n_estimators = [100] 
        #learning_rates = [0.1]
        #max_depths = [2]
        #colsample_bytree=[0.4]
        
        scoring = ['neg_mean_absolute_error', 'neg_root_mean_squared_error']
        grid = GridSearchCV(estimator=regressor, param_grid=param_grids[idx], scoring=scoring, refit=scoring[1], verbose=1, cv=3)
        grid_result = grid.fit(X_train_label, y_train_label)
        
        print(f"Best Score: {abs(grid_result.best_score_)} - Best Params: {grid_result.best_params_} for label {label} ({df_label.shape})")
        
        bestRegressor = grid.best_estimator_
        cv_results = grid.cv_results_
        best_index = grid.best_index_
        print(f"MAE: {cv_results['mean_test_neg_mean_absolute_error'][best_index]} - RMSE: {cv_results['mean_test_neg_root_mean_squared_error'][best_index]} model_{label}")
