import numpy as np
import matplotlib.pyplot as plt
import metrics

def plot_dSOC(y_true, y_est):#, sampleNumber):
    real_dSOC = y_true #/ sampleNumber
    est_dSOC  = y_est #/ sampleNumber
    
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot(real_dSOC, color = 'blue', label = 'Real value', marker = 'o')
    ax1.plot(est_dSOC, color = 'red', label = 'Estimated value', marker = 'o')
    ax1.set_title(f"Estimation for dSOC/dt")
    ax1.set(ylabel = 'dSOC/dt', xlabel = 'Test Case')
    ax1.set_xlim(0, len(real_dSOC))
    ax1.legend()

    APE = metrics.absolute_percentage_error(real_dSOC, est_dSOC)
    ax2.scatter(range(len(real_dSOC)), APE, label = 'Absolute Percentage Error', color = 'black', marker = 'o')    
    ax2.set_title(f"Error of dSOC/dt Estimation")
    ax2.legend()
    ax2.set(ylabel = 'APE (%)', xlabel = 'Test Case')
    ax2.set_xlim(0, len(real_dSOC))
