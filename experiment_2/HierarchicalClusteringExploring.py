## Hierarchical Clustering exploring the best linkage

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

# Plot correlation for the columns of the dataframe
def plotCorr(df):
    numDF = df.copy()
    numDF = numDF.drop(["Hotspot"], axis=1)
    f = plt.figure(figsize=(11, 11))
    corr = numDF.corr()
    ax = sns.heatmap(corr, cmap = 'coolwarm', annot=True, annot_kws={"weight": "bold"})
    for label in ax.get_yticklabels():
      label.set_weight("bold")
    for label in ax.get_xticklabels():
      label.set_weight("bold")
    plt.show()
    print(corr)

# Compute the dendrogram and plot it ...
def plot_dendrogram(model, **kwargs):
    plt.figure(figsize=(19.20,9.83))
    plt.title(f"Dendrogram for linkage = {param}", fontsize=23, fontweight='bold')
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
    plt.xlabel("Number of points in node (or index of point if no parenthesis)", fontsize=20,fontweight='bold')
    plt.xticks(fontsize= 15)
    plt.ylabel("Distance", fontsize=20, fontweight='bold')
    plt.yticks(fontsize= 15)
    #plt.show()

# For a linkage parameter compute the dendogram, call plot_dendrogram and save the figure ...
def fullTree(param, distance):
    model = AgglomerativeClustering(distance_threshold=0, n_clusters=None, affinity="precomputed", linkage=param).fit(distance)
    # plot the top five levels of the dendrogram
    plot_dendrogram(model, truncate_mode='level', p=5)
    plt.savefig(f"{param}.png", format='png')

# Plot the mean silhouette for different number of clusters ...
def plotSilhouette(param, distance):
    silh = []
    for cluster in range(2,20):
        model = AgglomerativeClustering(n_clusters=cluster, affinity="precomputed", linkage=param).fit(distance)
        labels = model.fit_predict(distance)
        silh.append( metrics.silhouette_score(distance, labels, metric="precomputed") )
        #silhouette_score = metrics.silhouette_score(distance, labels, metric="precomputed")
        #print(f"silhouette = {silhouette_score} for clusters = {cluster}")
    plt.figure(figsize=(19.20,9.83))
    plt.title(f"Mean Silhouette for Linkage = {param}", fontsize=23, fontweight='bold')
    plt.plot(range(2,20), silh)
    plt.xlabel("Number of clusters", fontsize=20, fontweight='bold')
    plt.xticks(fontsize= 15)
    plt.ylabel("Mean Silhouette", fontsize=20, fontweight='bold')
    plt.yticks(fontsize= 15)
    plt.savefig(f"{param}_silhouette.png", format='png')

if __name__ == "__main__":
    print("Clustering ...")
    current_directory = os.getcwd()
    # combinedDataset_allUsers.csv if the file created for the experiment one from 'output.py'
    df = pandas.read_csv(f"{current_directory}\\combinedDataset_allUsers.csv")
        
    df = df.drop(["level", "temperature", "voltage", "status", "health", "output"], axis=1) # I want Phone Usage
    df["Connectivity"] = df["Cellular"] | df["WiFi"]
    df = df.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    
    # Uncomment for dataframe description #
    #print(df.describe())
    #plotCorr(df)

    # After the first run, you don't have to compute the distance matrix again. You can read it from the pickle file
    distance = gower.gower_matrix(df)
    with open("distance.pickle","wb") as f:
        pickle.dump(distance, f)
    #distance = pickle.load( open( "distance.pickle", "rb" ) )
    print("Done with distance!")
    del df

    # Compute the condensed distance matrix for the linkage and cophenetic
    condensedDst = squareform(distance)
    #del distance

    ''' From the linkage function Definition
    Methods 'centroid', 'median' and 'ward' are correctly defined only if Euclidean pairwise metric is used. If `y` is passed as precomputed
    pairwise distances, then it is a user responsibility to assure that these distances are in fact Euclidean, otherwise the produced result
    will be incorrect.
    '''

    params = ['single', 'complete', 'average']
    for param in params:
        print(param)
        fullTree(param, distance)
        Zd = linkage(condensedDst, method=param, metric='precomputed')
        cophe_dists = cophenet(Zd, condensedDst)  # The cophentic correlation distance.
        print(cophe_dists[0])
        plotSilhouette(param, distance)
