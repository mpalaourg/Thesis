# Xgboost choose variables to keep from init best model...
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
        
    # Initial best models for parameter selection (after model_xgboost.py)
    regressor_0 = XGBRegressor(n_estimators=900, learning_rate=0.06, max_depth=4, colsample_bytree=0.45, reg_lambda=0.45)
    regressor_1 = XGBRegressor(n_estimators=900, learning_rate=0.03, max_depth=8, colsample_bytree=0.50, reg_lambda=0.40)
    regressor_3 = XGBRegressor(n_estimators=1200, learning_rate=0.06, max_depth=4, colsample_bytree=0.40, reg_lambda=0.40)
    regressors = [copy(regressor_0), copy(regressor_1), copy(regressor_3)]
    sel_regressors = [copy(regressor_0), copy(regressor_1), copy(regressor_3)]
    
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
        importances = [round(importance, 2) for importance, _ in pair]
        plt.title(f"Feature Importance [xgboost model_{label}]", fontweight='bold')
        plt.barh(feature_list, importances)
        plt.xlabel("Feature importance", fontweight='bold')
        plt.show()
        
        ''' Uncoment to compute best threshold for importance via cross validation on Train set
        # Fit model using each importance as a threshold
        thresholds = np.sort(regressor.feature_importances_)
        MAEs=[]
        for thresh in np.unique(thresholds):
            # select features using threshold
            selection = SelectFromModel(regressor, threshold=thresh, prefit=True)
            select_X_train_label = selection.transform(X_train_label)
            # train model
            selection_model = sel_regressors[idx]
            #selection_model.fit(select_X_train_label, y_train_label)
            scoring = ['neg_mean_absolute_error', 'neg_root_mean_squared_error']
            scores = cross_validate(selection_model, select_X_train_label, y_train_label, cv=3, scoring=scoring, return_train_score=True)
            print(f"thres: {thresh} - MAE: {np.mean(scores['test_neg_mean_absolute_error'])} - RMSE: {np.mean(scores['test_neg_root_mean_squared_error'])} model_{label}")
            MAEs.append( abs(np.mean(scores['test_neg_mean_absolute_error'])) )
        # Plot mean MAE per importance threshold
        plt.figure()
        plt.plot(np.unique(thresholds), MAEs)
        plt.title(f"Performance for different feature importance [xgboost model_{label}]", fontweight='bold')
        plt.ylabel('Mean MAE', fontweight='bold')
        plt.xlabel('Feature importance threshold', fontweight='bold')
        plt.show()
        '''
        
        #''' Uncomment for ploting ...
        # Plotting initial model ...
        y_pred_label = regressor.predict(X_test_label)
        y_pred_label[ np.where(y_pred_label < 0) ] = 0 
        print(f"RMSE: {metrics.mean_squared_error(y_test_label, y_pred_label, squared=False)}, ΜΑΕ {metrics.mean_absolute_error(y_test_label, y_pred_label)} model_{label}")
        error = abs(y_test_label-y_pred_label)
        plt.figure()
        plt.title(f"Prediction error histogram [xgboost model_{label}]", fontweight='bold')
        plt.hist(error)
        plt.xlabel("Error bins", fontweight='bold')
        plt.ylabel("Appearances", fontweight='bold')
        plt.show()
        
        fig, axs = plt.subplots(2)
        axs[0].set_title(f"Estimation of energy drain [xgboost model_{label}] zoomed", fontweight='bold')
        axs[0].plot(range(len(y_test_label[215:245])), y_test_label[215:245], color = 'blue', label = 'Real value', marker = 'o')
        axs[0].plot(range(len(y_pred_label[215:245])), y_pred_label[215:245], color = 'red', label = 'Estimated value', marker = 'o')
        axs[0].set_ylabel('Energy drain', fontweight='bold')
        axs[0].legend()
        
        axs[1].plot(range(len(y_pred_label[215:245])), y_test_label[215:245]-y_pred_label[215:245], color = 'blue', label = 'Error', marker = 'o')
        axs[1].set_title(f"Estimation error [xgboost model_{label}] zoomed", fontweight='bold')
        axs[1].set_ylabel('Error', fontweight='bold')
        axs[1].set_xlabel('Test Case', fontweight='bold')
        axs[1].legend()
        plt.show()

        plt.figure()
        plt.plot(range(len(y_test_label)), y_test_label, color = 'blue', label = 'Real value', marker = 'o')
        plt.plot(range(len(y_pred_label)), y_pred_label, color = 'red', label = 'Estimated value', marker = 'o')
        plt.title(f"Estimation of energy drain [xgboost model_{label}]", fontweight='bold')
        plt.ylabel('Energy drain', fontweight='bold')
        plt.xlabel('Test Case', fontweight='bold')
        plt.legend()
        plt.show()