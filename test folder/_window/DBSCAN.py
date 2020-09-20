import pandas
import numpy as np
import os
import gower
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, OPTICS
from sklearn import metrics
from sklearn.neighbors import NearestNeighbors

def plotCorr(df):
    numDF = df.copy()
    f = plt.figure(figsize=(11, 11))
    corr = numDF.corr()
    plt.matshow(corr, fignum=f.number)
    plt.xticks(range(numDF.shape[1]), numDF.columns, fontsize=14, rotation=90)
    plt.yticks(range(numDF.shape[1]), numDF.columns, fontsize=14)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=14)
    plt.show()
    print(corr)

if __name__ == "__main__":
    print("DBSCANing ...")
    current_directory = os.getcwd()
    df = pandas.read_csv(f"{current_directory}\\combinedTrain_csv.csv")
    df = df.drop(["level", "voltage", "status", "health"], axis=1) # I want Phone Usage
    df["Connectivity"] = df["Cellular"] | df["WiFi"]
    df = df.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    df = df.sample(frac=0.5) # Sample part of dataframe 
    #print(df.describe())
    #plotCorr(df)
    distance = gower.gower_matrix(df)
    #print(distance)

    '''
    for k in range(10, 21, 1):
        print(k)
        neigh = NearestNeighbors(n_neighbors=k, metric="precomputed").fit(distance)
        distances, indices = neigh.kneighbors(distance)
        distances = np.sort(distances, axis=0)
        distances = distances[:,1]
        
        plt.figure(figsize=(19.20,9.83))
        plt.title(f"kNN Distance plot")
        plt.plot(distances)
        plt.hlines(0.015, 0, len(distances))
        plt.xlabel("Points sorted by distance")
        plt.ylabel(f"{k}-NN distance")
        #plt.show()
        plt.savefig(f"{k}-NN distance.png", format='png')
    '''
    ranges = [range(10, 21, 1), range(100, 210, 10), range(1000, 2100, 100)]
    for idx, rng in enumerate(ranges):
        silh, n_clusters_ = [], []
        for k in rng:
            print(f"{k}")
            #model = DBSCAN(eps=0.015, min_samples=k, metric="precomputed").fit(distance)
            model = OPTICS(min_samples=k, max_eps = 10, metric="precomputed").fit(distance)
            labels = model.fit_predict(distance)
            n_clusters_.append( len(set(labels)) - (1 if -1 in labels else 0) )
            silh.append( metrics.silhouette_score(distance, labels, metric="precomputed") )
        plt.figure(figsize=(19.20,9.83))
        plt.title(f"optics")
        plt.plot(rng, silh)
        plt.xlabel("minSamples")
        plt.ylabel("silhouette")
        #plt.show()
        plt.savefig(f"silhouette_OPTICS_{idx}.png", format='png')

        plt.figure(figsize=(19.20,9.83))
        plt.title(f"optics")
        plt.plot(rng, n_clusters_)
        plt.xlabel("minSamples")
        plt.ylabel("Number of clusters")
        #plt.show()
        plt.savefig(f"clusterNumber_OPTICS_{idx}.png", format='png')