import pandas
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def boxplotAll(current_directory):
    #df = pandas.read_csv(f"{current_directory}\\labeled_combinedDataset_Average.csv") 
    #df = pandas.read_csv(f"{current_directory}\\labeled_combinedDataset_Complete.csv")

    df = pandas.read_csv(f"{current_directory}\\labeled_combinedDataset.csv")

    labels = df.label
    labels = list( set(labels) )
    for label in labels:
        df_label = df[ (df["label"] == label) ]
        
        GPS_label = df_label.GPS
        Bluetooth_label = df_label.Bluetooth
        Connectivity_label = df_label.Connectivity
        print(f"label: {label} -- Bluetooth: {Bluetooth_label.sum()}, GPS: {GPS_label.sum()}, Connectivity: {Connectivity_label.sum()} of {len(df_label.index)}")
        
        usage_label = df_label["usage"]
        RAM_label = df_label["RAM"]
        Brightness_label = df_label["Brightness"]
        
        fig, axes = plt.subplots(1,3)
        fig.suptitle(f"Phone usage boxplots ~ cluster {label}", fontweight='bold')
        sns.boxplot(usage_label, ax=axes[0])
        axes[0].set_xlabel("CPU Usage", fontweight='bold')

        sns.boxplot(RAM_label, ax=axes[1])
        axes[1].set_xlabel("Available RAM", fontweight='bold')
        
        sns.boxplot(Brightness_label, ax=axes[2])
        axes[2].set_xlabel("Brightness", fontweight='bold')
        
        plt.show()
    
if __name__ == "__main__":
    current_directory = os.getcwd()
    boxplotAll(current_directory)