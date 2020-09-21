import pandas
import numpy as np
import os
import gower
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet
from scipy.spatial.distance import squareform
from sklearn.cluster import AgglomerativeClustering
from sklearn import metrics

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

def plot_dendrogram(model, **kwargs):
    plt.figure(figsize=(19.20,9.83))
    plt.title(f"Hierarchical Clustering Linkage = {param}")
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack([model.children_, model.distances_,
                                      counts]).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    #plt.show()

def fullTree(param, distance):
    model = AgglomerativeClustering(distance_threshold=0, n_clusters=None, affinity="precomputed", linkage=param).fit(distance)
    # plot the top three levels of the dendrogram
    plot_dendrogram(model, truncate_mode='level', p=5)
    plt.savefig(f"{param}.png", format='png')

def plotSilhouette(param, distance):
    silh = []
    for cluster in range(2,20):
        model = AgglomerativeClustering(n_clusters=cluster, affinity="precomputed", linkage=param).fit(distance)
        labels = model.fit_predict(distance)
        silh.append( metrics.silhouette_score(distance, labels, metric="precomputed") )
        #silhouette_score = metrics.silhouette_score(distance, labels, metric="precomputed")
        #print(f"silhouette = {silhouette_score} for clusters = {cluster}")
    plt.figure(figsize=(19.20,9.83))
    plt.title(f"Linkage = {param}")
    plt.plot(range(2,20), silh)
    plt.xlabel("Number of clusters")
    plt.ylabel("silhouette")
    plt.savefig(f"{param}_silhouette.png", format='png')

if __name__ == "__main__":
    print("Clustering ...")
    current_directory = os.getcwd()
    df = pandas.read_csv(f"{current_directory}\\combinedTrain_csv.csv")
    df = df.drop(["level", "temperature", "voltage", "status", "health"], axis=1) # I want Phone Usage
    df["Connectivity"] = df["Cellular"] | df["WiFi"]
    df = df.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    #df = df.sample(frac=0.01) # Sample part of dataframe 
    print(df.describe())
    plotCorr(df)
    #distance = gower.gower_matrix(df)
    #print("Done with distance!")
    #del df
    #  scipy.cluster: The symmetric non-negative hollow observation matrix looks suspiciously like an uncondensed distance matrix
    #condensedDst = squareform(distance)
    #del distance
    ''' From the linkage function Definition
    Methods 'centroid', 'median' and 'ward' are correctly defined only if Euclidean pairwise metric is used. If `y` is passed as precomputed
    pairwise distances, then it is a user responsibility to assure that these distances are in fact Euclidean, otherwise the produced result
    will be incorrect.
    '''
    #modelAverage  = AgglomerativeClustering(n_clusters=9, affinity="precomputed", linkage='average').fit(distance)
    #labels = modelAverage.fit_predict(distance)
    #silhouette_score = metrics.silhouette_score(distance, labels, metric="precomputed")
    #print(f"silhouette = {silhouette_score} for average and 9 clusters.")
    
    #modelComplete = AgglomerativeClustering(n_clusters=6, affinity="precomputed", linkage='complete').fit(distance)
    #labels = modelComplete.fit_predict(distance)
    #silhouette_score = metrics.silhouette_score(distance, labels, metric="precomputed")
    #print(f"silhouette = {silhouette_score} for complete and 6 clusters.")

    # Save models to avoid training yet again
    #with open("modelAverage.pickle","wb") as f:
    #    pickle.dump(modelAverage, f)
    #with open("modelComplete.pickle","wb") as f:
    #    pickle.dump(modelComplete, f)
    
    '''
    params = ['single', 'complete', 'average']
    #params = ['average']
    for param in params:
        print(param)
        #fullTree(param, distance)
        Zd = linkage(condensedDst, method=param, metric='precomputed')
        cophe_dists = cophenet(Zd, condensedDst)  # The cophentic correlation distance.
        print(cophe_dists[0])
        #plotSilhouette(param, distance)
    '''