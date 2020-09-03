import numpy as np
import sklearn.metrics        

def absolute_percentage_error(y_true, y_pred):
    # Make sure that inputs are nd arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    length = y_true.size
    error = []
    epsilon = 1e-10
    for i in range(length):
        if not y_true[i]:
            y_true[i] += epsilon
        
        currError = abs( (y_true[i] - y_pred[i]) ) / y_true[i] * 100
        error.append(currError)
    return np.array(error)

def mean_squared_percentage_error(y_true, y_pred, squared=True):
    #Checked with RMSPE() function of R
    error = y_true - y_pred
    MSPE = np.mean( np.square( error / y_true ) )
    if squared:
        return MSPE * 100
    else:  #RMSPE
        return np.sqrt( MSPE ) * 100

def mean_absolute_percentage_error(y_true, y_pred):
    epsilon = 1e-10
    y_true[ np.where(y_true == 0) ] += epsilon
    error = y_true - y_pred
    return np.mean( np.abs( error / y_true ) ) * 100

def r2_score(y_true, y_pred):
    return sklearn.metrics.r2_score(y_true, y_pred)