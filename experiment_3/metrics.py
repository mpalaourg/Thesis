import numpy as np
import sklearn.metrics        

def r2_score(y_true, y_pred):
    return sklearn.metrics.r2_score(y_true, y_pred)

def standard_Error(y_true, y_pred):
    return np.sqrt( sum( np.square(y_true-y_pred) ) / len(y_pred) )

def mean_squared_error(y_true, y_pred, squared=True):
    return sklearn.metrics.mean_squared_error(y_true, y_pred, squared=squared)

def mean_absolute_error(y_true, y_pred):
    return sklearn.metrics.mean_absolute_error(y_true, y_pred)
