# Plot MDS 2D and 3D
import pandas
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from mpl_toolkits.mplot3d import Axes3D
import gower
import os
import pickle


def plotMDS(distance, labels, get3D=False, strModel='Complete'):
  cdict = {0: 'b', 1: 'g', 2: 'r', 3: 'c', 4: 'm', 5: 'y', 6: 'k'}
  
  if not get3D:
    fileName = f"mds_{strModel}_clusters_2d.png"
    distance_2d = MDS(n_components=2, random_state=0, dissimilarity="precomputed").fit_transform(distance)
    x = distance_2d[:,0]
    y = distance_2d[:,1]
    
    plt.title("Mobile usage Clusters", fontweight='bold')
    for label in np.unique(labels):
      if label == 0 or label == 1 or label == 2:
        ix = np.where(labels == label)
        plt.scatter(x[ix], y[ix], c=cdict[label], label = f"cluster_{label}", s = 100)
    plt.xlabel("Coordinate 1", fontweight='bold')
    plt.ylabel("Coordinate 2", fontweight='bold')

  else:
    fileName = f"mds_{strModel}_clusters_3d.png"
    distance_3d = MDS(n_components=3, random_state=0, dissimilarity="precomputed").fit_transform(distance)
    x = distance_3d[:,0]
    y = distance_3d[:,1]
    z = distance_3d[:,2]

    fig = plt.figure()
    ax = Axes3D(fig)
    ax.set_title("Mobile usage Clusters", fontweight='bold')
    for label in np.unique(labels):
      if label == 0 or label == 1 or label == 2:
        ix = np.where(labels == label)
        ax.scatter(x[ix], y[ix], z[ix], c=cdict[label], label = f"cluster_{label}", s = 100)
    ax.set_xlabel("Coordinate 1", fontweight='bold')
    ax.set_ylabel("Coordinate 2", fontweight='bold')
    ax.set_zlabel("Coordinate 3", fontweight='bold')
    ax.view_init(azim=0)
  plt.legend()
  plt.savefig(fileName, format='png')

if __name__ == "__main__":
    print("MDSing ...")
    
    current_directory = os.getcwd()
    df = pandas.read_csv(f"{current_directory}\\combinedDataset_allUsers.csv")
    df = df.drop(["level", "temperature", "voltage", "status", "health", "output"], axis=1) # I want Phone Usage
    df["Connectivity"] = df["Cellular"] | df["WiFi"]
    df = df.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    distance = gower.gower_matrix(df)

    # Use of previous distance NxN
    #modelAverage = pickle.load( open( "modelAverage.pickle", "rb" ) )
    #labels = modelAverage.fit_predict(distance)
    #del modelAverage
    modelComplete = pickle.load( open( "modelComplete.pickle", "rb" ) )
    labels = modelComplete.fit_predict(distance)
    del modelComplete

    # Print members of each class #
    df["label"] = labels
    print(df.shape)
    print(df["label"].value_counts())
    labels = df["label"].to_numpy()
    df = df.drop(["label"], axis=1)

    print("Begin with MDS!")    
    #plotMDS(distance, labels, get3D=False, strModel='Average') # 2D Version
    #plotMDS(distance, labels, get3D=True, strModel='Average') # 3D Version
    plotMDS(distance, labels, get3D=False, strModel='Complete') # 2D Version
    plotMDS(distance, labels, get3D=True, strModel='Complete') # 3D Version
    print("Done with MDS!")
    
