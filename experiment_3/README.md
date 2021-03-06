# Third Experiment
>Group similar uses of the device and predict the energy drain, based on Sessions <i>under `30` minutes</i> of <b> all users with at least `20` files and the same total battery capacity</b>. 

## Directory Structure 
├── <b><ins>experiment_3</ins></b> <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>rawFiles</ins></b>: Contains the files as exported and checked from the Database. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>windowFiles</ins></b>: Contains the same files as <b><ins>rawFiles</ins></b>, but grouped in time windows for smoothing. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>normFiles</ins></b>: Contains the same files as <b><ins>windowFiles</ins></b>, but normalized between `[0, 1]`. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>outputFiles</ins></b>: Contains the same files as <b><ins>normFiles</ins></b> joined with an extra column for the output. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `windowUsage.py`: Group the measurements in `50` seconds (non-overlapping) time windows. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `normalize.py`: Normalize the files based on the sessions of each user. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `output.py`: Compute the extra column of <b><ins>outputFiles</ins></b> (<i>energy drain</i>). <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `createDataset.py`: Create the un-labeled dataset (`combinedDataset_sameCap.csv`) for the specific experiment. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `HierarchicalClusteringExploring.py`: Explore Hierarchical Clustering best linkage (single, complete, average) based on <i>CPCC</i>. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `HierarchicalClusteringBest.py`: Evaluate (<i>mean silhouette score</i>) the best cluster models and save them in pickle files. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `getLabels.py`: Create the labeled dataset (`labeled_combinedDataset.csv`) using one of the above pickle files.<br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `clusterEvaluation.py`: Evaluation of the created clusters based on the characteristics of the grouped time windows. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `plotMDS.py`: Multidimensional scaling (MDS) plot for the selected clusters. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `metrics.py`: Metrics being used in models evaluation. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `model_linear.py`: Linear model evaluation. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `model_ridge.py`: Ridge model hyperparameter tuning.  <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `model_lasso.py`: Lasso model hyperparameter tuning.  <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `model_xgboost.py`: Xgboost model hyperparameters tuning. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `model_best_xgboost.py`: Xgboost feature selection of initial best model. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `model_tune_xgboost.py`: Xgboost selected model hyperparameters tuning. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── `model_select_best_xgboost.py`: Xgboost best selected model evaluation.<br>
