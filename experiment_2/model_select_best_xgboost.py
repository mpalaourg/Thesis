# Xgboost best selected models ...
import pandas
import numpy as np
import os
from copy import copy
from xgboost import XGBRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV, train_test_split, cross_validate
from sklearn.feature_selection import SelectFromModel
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

    # The best models for each label (after model_tune_xgboost.py)
    regressor_0 = XGBRegressor(n_estimators=600, learning_rate=0.06, max_depth=6, colsample_bytree=0.45, reg_lambda=0.40)
    regressor_1 = XGBRegressor(n_estimators=600, learning_rate=0.06, max_depth=8, colsample_bytree=0.40, reg_lambda=0.45)
    regressor_2 = XGBRegressor(n_estimators=1100, learning_rate=0.03, max_depth=7, colsample_bytree=0.50, reg_lambda=0.40)
    regressors = [copy(regressor_0), copy(regressor_1), copy(regressor_2)]
    sel_regressors = [copy(regressor_0), copy(regressor_1), copy(regressor_2)]
    
    # The selected column names for each label
    column_0 = ['temperature Brightness', 'Brightness RAM', 'Brightness^2', 'usage Brightness', 'level Brightness', 'level', 'temperature RAM']
    column_1 = ['Brightness^2', 'temperature Brightness', 'level Brightness', 'usage^2', 'level', 'level^2', 'usage Brightness',
                'Brightness RAM', 'Brightness', 'temperature^2', 'level temperature']
    column_2 = ['Brightness^2', 'usage Brightness', 'temperature usage', 'temperature Brightness', 'level Brightness', 'Brightness',
                'level temperature', 'temperature^2', 'Brightness RAM', 'level']
    selColumns = [column_0, column_1, column_2]

    labels = [0, 1, 2] # The only meaningfull clusters and with the necessarily points
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
        regressor = regressors[idx].fit(X_train_label, y_train_label)
        
        # Get numerical feature importances and plot them
        feature_list = list(X_train_label.columns)
        importances = list(regressor.feature_importances_)# List of tuples with variable and importance
        feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)] # Sort the feature importances by most important first
        feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)# Print out the feature and importances 
        [print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances]

        pair=zip(importances, feature_list)
        pair=sorted(pair, reverse=False)
        feature_list = [feature for _, feature in pair]
        importances = [importance for importance, _ in pair]
        plt.title(f"Feature Importance [selected xgboost model_{label}]", fontweight='bold')
        plt.barh(feature_list, importances)
        plt.xlabel("Feature importance", fontweight='bold')
        plt.show()
        
        #''' Uncomment for ploting ...
        # Plotting selected model ...
        y_pred_label = regressor.predict(X_test_label)
        y_pred_label[ np.where(y_pred_label < 0) ] = 0 
        print(f"RMSE: {metrics.mean_squared_error(y_test_label, y_pred_label, squared=False)}, ΜΑΕ {metrics.mean_absolute_error(y_test_label, y_pred_label)} model_{label}")
        error = abs(y_test_label-y_pred_label)
        plt.figure()
        plt.title(f"Prediction error histogram [selected xgboost model_{label}]", fontweight='bold')
        plt.hist(error)
        plt.xlabel("Error bins", fontweight='bold')
        plt.ylabel("Appearances", fontweight='bold')
        plt.show()
        
        plt.figure()
        plt.plot(range(len(y_test_label)), y_test_label, color = 'blue', label = 'Real value', marker = 'o')
        plt.plot(range(len(y_pred_label)), y_pred_label, color = 'red', label = 'Estimated value', marker = 'o')
        plt.title(f"Estimation of energy drain [selected xgboost model_{label}]", fontweight='bold')
        plt.ylabel('Energy drain', fontweight='bold')
        plt.xlabel('Test Case', fontweight='bold')
        plt.legend()
        plt.show()
        
        fig, axs = plt.subplots(2)
        axs[0].set_title(f"Estimation of energy drain [selected xgboost model_{label}] zoomed", fontweight='bold')
        axs[0].plot(range(len(y_test_label[200:230])), y_test_label[200:230], color = 'blue', label = 'Real value', marker = 'o')
        axs[0].plot(range(len(y_pred_label[200:230])), y_pred_label[200:230], color = 'red', label = 'Estimated value', marker = 'o')
        axs[0].set_ylabel('Energy drain', fontweight='bold')
        axs[0].legend()
        
        axs[1].plot(range(len(y_pred_label[200:230])), y_test_label[200:230]-y_pred_label[200:230], color = 'blue', label = 'Error', marker = 'o')
        axs[1].set_title(f"Estimation error [selected xgboost model_{label}] zoomed", fontweight='bold')
        axs[1].set_ylabel('Error', fontweight='bold')
        axs[1].set_xlabel('Test Case', fontweight='bold')
        axs[1].legend()
        plt.show()