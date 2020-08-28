import numpy as np
# Compute absolute percentage error
def APE(y_true, y_pred):
    # Make sure that inputs are nd arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    length = y_true.size
    error = []
    for i in range(length):
        if y_true[i]:
            currError = abs( (y_true[i] - y_pred[i]) ) / y_true[i] * 100
        else:
            currError = abs( (y_true[i] - y_pred[i]) )
        error.append(currError)
    return np.array(error)