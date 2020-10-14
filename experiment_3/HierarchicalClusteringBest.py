# Run the hierarchical clustering for the best parameters
import pandas
import os
import gower
import pickle
from sklearn.cluster import AgglomerativeClustering
from sklearn import metrics

if __name__ == "__main__":
    print("Best of Hierarchical Clustering ...")
    current_directory = os.getcwd()
    # combinedDataset_sameCap.csv is the file created for the experiment one from 'output.py'
    df = pandas.read_csv(f"{current_directory}\\combinedDataset_sameCap.csv")
    
    df = df.drop(["level", "temperature", "voltage", "status", "health", "output"], axis=1) # I want Phone Usage
    df["Connectivity"] = df["Cellular"] | df["WiFi"]
    df = df.drop(["WiFi", "Cellular", "isInteractive"], axis=1) # Cause of correlation between columns
    
    # After the first run, you don't have to compute the distance matrix again. You can read it from the pickle file
    distance = gower.gower_matrix(df)
    with open("distance.pickle","wb") as f:
        pickle.dump(distance, f)
    #distance = pickle.load( open( "distance.pickle", "rb" ) )
    print("Done with distance!")
    del df
    
    modelAverage  = AgglomerativeClustering(n_clusters=5, affinity="precomputed", linkage='average').fit(distance)
    labels = modelAverage.fit_predict(distance)
    silhouette_score = metrics.silhouette_score(distance, labels, metric="precomputed")
    print(f"silhouette = {silhouette_score} for average and 5 clusters.")
    
    modelComplete = AgglomerativeClustering(n_clusters=5, affinity="precomputed", linkage='complete').fit(distance)
    labels = modelComplete.fit_predict(distance)
    silhouette_score = metrics.silhouette_score(distance, labels, metric="precomputed")
    print(f"silhouette = {silhouette_score} for complete and 5 clusters.")

    # Save models to keep the same numbering on clusters ...
    with open("modelAverage.pickle","wb") as f:
        pickle.dump(modelAverage, f)
    with open("modelComplete.pickle","wb") as f:
        pickle.dump(modelComplete, f)
