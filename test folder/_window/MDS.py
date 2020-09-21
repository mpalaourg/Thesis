import pandas
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
import gower
import os

if __name__ == "__main__":
    print("MDSing ...")
    current_directory = os.getcwd()
    df = pandas.read_csv(f"{current_directory}\\combinedTrain_csv.csv")
    df = df.drop(["level", "voltage", "status", "health"], axis=1) # I want Phone Usage
    df["Connectivity"] = df["Cellular"] | df["WiFi"]
    df = df.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    df = df.drop(["temperature"], axis=1) # for testing
    #df = df.sample(frac=0.01, random_state=1) # Sample part of dataframe 

    distance = gower.gower_matrix(df)
    del df
    with open("distance.pickle","wb") as f:
        pickle.dump(distance, f)
    #distance = pickle.load( open( "distance.pickle", "rb" ) )
    print("Done with distance!")
    
    modelAverage = pickle.load( open( "modelAverage.pickle", "rb" ) )
    labels = modelAverage.fit_predict(distance)
    del modelAverage
    print("Done with predict the labels")
    
    distance_2d = MDS(n_components=2, random_state=0, dissimilarity="precomputed").fit_transform(distance)
    del distance
    print("Done with MDS!")
    x = distance_2d[:,0]
    y = distance_2d[:,1]
    plt.scatter(x,y, c=labels)
    plt.savefig(f"mds_ModelAverage_clusters.png", format='png')