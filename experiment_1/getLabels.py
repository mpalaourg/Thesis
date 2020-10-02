# Get the labeled dataset
import pandas
import gower
import os
import pickle
import numpy as np


if __name__ == "__main__":
    current_directory = os.getcwd()
    df = pandas.read_csv(f"{current_directory}//combinedDataset_user_1.csv")

    # Get dataframe ready to compute distance
    df_distance = df.copy()
    df_distance = df_distance.drop(["level", "temperature", "voltage", "status", "health", "output"], axis=1) # I want Phone Usage
    df_distance["Connectivity"] = df_distance["Cellular"] | df_distance["WiFi"]
    df_distance = df_distance.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    print(f"Distance dataframe: {df_distance.shape}")

    modelComplete = pickle.load( open( "modelComplete.pickle", "rb" ) )
    #modelAverage = pickle.load( open( "modelAverage.pickle", "rb" ) )
    # Compute distance for the dataset
    print("Computing distance...")
    distance = gower.gower_matrix(df_distance)
    print(f"Distance matrix: {distance.shape}")
    del df_distance
    print("Getting the labels...")
    labels = modelComplete.fit_predict(distance)
    #labels = modelAverage.fit_predict(distance)
    
    df["Connectivity"] = df["Cellular"] | df["WiFi"]
    df = df.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    df["label"] = labels
    
    df.to_csv("labeled_combinedDataset.csv", ",", index=False)