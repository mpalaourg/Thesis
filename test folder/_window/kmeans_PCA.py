import pandas
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pandas.api.types import is_bool_dtype

def choosePCADmn(df):
    model = PCA()             # Principal Compents same number as columns
    model.fit(df)
    explVar = model.explained_variance_ratio_
    #print(explVar)
    print(explVar.cumsum())   # Shows the variance explained until ith dimension
    print(f"Variance explained with 3 PC: {explVar.cumsum()[2]}")
    print(f"Info loss: {sum(explVar[3:])/sum(explVar)}")
    plt.bar(range(len(explVar)), explVar, 1)
    plt.show()
    

if __name__ == "__main__":
    print("PCAing ...")
    current_directory = os.getcwd()
    df = pandas.read_csv(f"{current_directory}\\combinedTrain_csv.csv")
    df = df.drop(["level", "status", "health"], axis=1)
    df *= 1 # Boolean to int
    
    #df = df.drop(["WiFi", "Cellular", "Hotspot", "GPS", "Bluetooth", "isInteractive"], axis=1)
    normalized_df=(df-df.min())/(df.max()-df.min())
    #print(df.describe())
    #choosePCADmn(normalized_df)
    model = PCA(n_components=3)             # Principal Compents same number as columns
    principalComponents = model.fit_transform(normalized_df)
    principalDf = pandas.DataFrame(data = principalComponents, 
                                columns = ['PC1', 'PC2', 'PC3'])
    '''
    # Get the avg silhouette
    for n_clusters in range(2,11):
        clusterer = KMeans(n_clusters=n_clusters, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0)
        cluster_labels = clusterer.fit_predict(principalDf)

        silhouette_avg = silhouette_score(principalDf, cluster_labels)
        print("For n_clusters =", n_clusters,
            "The average silhouette_score is :", silhouette_avg)
    '''
    
    SSE = []
    for i in range(1, 11):
        km = KMeans(n_clusters=i, init='random', n_init=10, max_iter=500, tol=1e-04, random_state=0)
        km.fit(principalDf)
        SSE.append(km.inertia_)
    #print(SSE) its huuuuge
    
    plt.plot(range(1, 11), SSE, marker='o')
    plt.xlabel('Number of clusters')
    plt.ylabel('SSE')
    plt.show()
    
    # Best model for k=2 | k=7 or 6 for booleans
    km = KMeans(n_clusters=7, init='random', n_init=10, max_iter=500, tol=1e-04, random_state=0)
    km.fit(principalDf)
    centroids = km.cluster_centers_
    print(centroids)
    ax = plt.axes(projection = '3d')
    ax.scatter(principalDf['PC1'], principalDf['PC2'], principalDf['PC3'], c= km.labels_.astype(float), s=50, alpha=0.5)
    
    for i in range(7):
        ax.scatter(centroids[i,0],centroids[i,1],centroids[i,2] ,c='r', s=50)
    plt.show()

    plt.scatter(principalDf['PC1'], principalDf['PC2'], c= km.labels_.astype(float), s=50, alpha=0.5)
    plt.show()
