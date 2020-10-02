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
        
    # The best models for each label
    regressor_0 = XGBRegressor(n_estimators=1000, learning_rate=0.05, max_depth=6, colsample_bytree=0.6, reg_lambda=0.3)
    regressor_1 = XGBRegressor(n_estimators=1000, learning_rate=0.03, max_depth=8, colsample_bytree=0.5, reg_lambda=0.4)
    regressors = [copy(regressor_0), copy(regressor_1)]
    sel_regressors = [copy(regressor_0), copy(regressor_1)]
    labels = [0, 1] # The only meaningfull clusters and with the necessarily points
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
        
        # Get numerical feature importances
        feature_list = list(X_train_label.columns)
        importances = list(regressor.feature_importances_)# List of tuples with variable and importance
        feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)] # Sort the feature importances by most important first
        feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)# Print out the feature and importances 
        [print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances]

        ''' Uncoment to compute best threshold for importance via cross validation on Train set
        # Fit model using each importance as a threshold
        thresholds = np.sort(regressor.feature_importances_)
        for thresh in thresholds:
            # select features using threshold
            selection = SelectFromModel(regressor, threshold=thresh, prefit=True)
            select_X_train_label = selection.transform(X_train_label)
            # train model
            selection_model = sel_regressors[idx]
            #selection_model.fit(select_X_train_label, y_train_label)
            scoring = ['neg_mean_absolute_error', 'neg_root_mean_squared_error']
            scores = cross_validate(selection_model, select_X_train_label, y_train_label, cv=3, scoring=scoring, return_train_score=True)
            print(f"thres: {thresh} - MAE: {np.mean(scores['test_neg_mean_absolute_error'])} - RMSE: {np.mean(scores['test_neg_root_mean_squared_error'])} model_{label}")
        '''

        thres = [0.043, 0.037]
        # select features using threshold
        selection = SelectFromModel(regressor, threshold=thres[idx], prefit=True)
        select_X_train_label = selection.transform(X_train_label)
        #print(f"{X_train_label.shape} - {select_X_train_label.shape}")
        # train model
        selection_model = sel_regressors[idx]
        selection_model.fit(select_X_train_label, y_train_label)  
        # eval model
        select_X_test = selection.transform(X_test_label)
        predictions = selection_model.predict(select_X_test)
        print(f"thres: {thres[idx]} - RMSE: {metrics.mean_squared_error(y_test_label, predictions, squared=False)}, ΜΑΕ {metrics.mean_absolute_error(y_test_label, predictions)} model_{label}")
        
        ''' Uncomment for ploting ...
        # Plotting selected model ...
        error = abs(y_test_label-predictions)
        plt.figure()
        plt.title(f"Prediction error histogram [selected xgboost model_{label}]", fontweight='bold')
        plt.hist(error)
        plt.xlabel("Error bins", fontweight='bold')
        plt.ylabel("Appearances", fontweight='bold')
        plt.show()
        
        plt.figure()
        plt.plot(range(len(y_test_label)), y_test_label, color = 'blue', label = 'Real value', marker = 'o')
        plt.plot(range(len(predictions)), predictions, color = 'red', label = 'Estimated value', marker = 'o')
        plt.title(f"Estimation of energy drain [selected xgboost model_{label}]", fontweight='bold')
        plt.ylabel('Energy drain', fontweight='bold')
        plt.xlabel('Test Case', fontweight='bold')
        plt.legend()
        plt.show()
        
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
        
        plt.figure()
        plt.plot(range(len(y_test_label)), y_test_label, color = 'blue', label = 'Real value', marker = 'o')
        plt.plot(range(len(y_pred_label)), y_pred_label, color = 'red', label = 'Estimated value', marker = 'o')
        plt.title(f"Estimation of energy drain [xgboost model_{label}]", fontweight='bold')
        plt.ylabel('Energy drain', fontweight='bold')
        plt.xlabel('Test Case', fontweight='bold')
        plt.legend()
        plt.show()
        '''