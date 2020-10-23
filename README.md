# Thesis

## Title
<b>Data Collection and Analysis of Energy Consumption of Mobile Phones using Machine Learning Techniques</b>

---

## Abstract
<p align=justify>
In a modern-day society there is the consensus that smartphones have a dominant role in everyday life. By just pressing a button, someone can not only get up to speed with the current events on a global scale, but also get in touch with people all over the world and find various forms of entertainment. In particular, one of the features that makes smartphones so attractive is the portability they offer, since they utilize batteries. However, batteries have a certain amount of charges in their disposal, consequently the lifespan of a device is directly correlated to its utilization, as well as its charging strategy. <br>
</p>
<p align=justify>
The current thesis focuses on the analysis of mobile phones’ usage and the prediction of the battery’s energy drain. To begin with, for data collection the application “BatteryApp”, which periodically keeps record of the device’s usage and the battery information, was developed. The next step is the grouping of similar uses of devices through Hierarchical Clustering, which does not require an a priori selection for a specific cluster number and does not set limitations regarding the chosen distance function. After that, it was assessed based on its content in order to select the clusters with the higher information value. Lastly, the prediction of the energy drain was constructed by employing a simple linear model, two variants of linear regression, where the penalty concept is introduced (Ridge and Lasso Regression), and a non-linear model, which belongs to the Ensemble Learning category (eXtreme Gradient Boosted trees), with the parameters’ learning procedure being applied to each selected cluster individually.
</p>
<p align=right>
<i>Georgios Balaouras <br>
Electrical & Computer Engineering Department <br>
Aristotle University of Thessaloniki, Greece <br>
October 2020 </i> <br>
</p>

---

## Dependecies 
```
pip install numpy
pip install pandas
pip install scikit-learn
pip install scipy
pip install gower
pip install seaborn
pip install matplotlib
pip install xgboost
```
---

## Raw data variables 
### Battery
| Name | Description |
|------|-------------|
|<p align=center> level </p>| The current battery level `[0-100]`.|
|<p align=center> temperature </p>| The current battery temperature in °C.|
|<p align=center> voltage </p>| The current battery voltage level in V.|
|<p align=center> technology </p>| String describing the technology of the current battery.|
|<p align=center> status </p>| [Categorical variable](https://developer.android.com/reference/android/os/BatteryManager#EXTRA_STATUS) for the current battery status.|
|<p align=center> health </p>| [Categorical variable](https://developer.android.com/reference/android/os/BatteryManager#EXTRA_HEALTH) for the current battery health.|
|<p align=center> availCapacityPercentage </p>| The current battery capacity remaining `[0-100]`.|

### Phone Usage
| Name | Description |
|------|-------------|
|<p align=center> usage </p>| The estimation of the current CPU load `[0-100]`.|
|<p align=center> WiFi </p>| Boolean variable if WiFi is enable.|
|<p align=center> Cellular </p>| Boolean variable if Cellular Data Connection is enable.|
|<p align=center> Hotspot </p>| Boolean variable if the device its used as a WiFi access point.|
|<p align=center> GPS </p>| Boolean variable if GPS is enable.|
|<p align=center> Bluetooth </p>| Boolean variable if Bluetooth is enable.|
|<p align=center> RAM </p>| The current percentage of available RAM `[0-100]`.|
|<p align=center> Brightness </p>| The current screen brightness.|
|<p align=center> isInteractive </p>| Boolean variable if the user interacts with the device.|

### Logistics
| Name | Description |
|------|-------------|
|<p align=center> _id </p>| Database `id` unique for each measurement.|
|<p align=center> ID </p>| The unique user `ID` used for anonymity reasons.|
|<p align=center> SampleFreq </p>| The user specified sampling frequency (`Default: 10 seconds`).|
|<p align=center> brandModel </p>| The brand and model of the device.|
|<p align=center> androidVersion </p>| The android version of the device.|
|<p align=center> Timestamp </p>| Unix timestamp of each measurement.|

---

## Directory Structure <br>
├── <b><ins>..</ins></b> <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>BatteryApp</ins></b>: Contains the source code of `BatteryApp`. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>experiment_1</ins></b>: Experiment based on <i>all</i> Sessions of <b>one user</b>. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>experiment_2</ins></b>: Experiment based on Sessions <i>under `30` minutes</i> of <b> all users with at least `20` files</b>. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>experiment_3</ins></b>: Experiment based on Sessions <i>under `30` minutes</i> of <b> all users with at least `20` files & same total battery capacity</b>. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>server</ins></b>: Contains the scripts for the server and the database. <br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>preprocessing</ins></b>: Contains the scripts for exporting and preprocessing the data.<br>
&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b><ins>data/csvFiles</ins></b>: Contains the files as exported and checked from the Database.<br>

---

## Tecnologies 

| |<img src="https://github.com/mpalaourg/Thesis/blob/master/data/images/java8%20icon.png" alt="Java" width="50" height="50"> | <img src="https://github.com/mpalaourg/Thesis/blob/master/data/images/python.png" alt="Python" width="50" height="50"> | <img src="https://github.com/mpalaourg/Thesis/blob/master/data/images/flask.png" alt="Flask" width="100" height="35"> & <img src="https://github.com/mpalaourg/Thesis/blob/master/data/images/waitress.png" alt="Waitress" width="100" height="35"> | <img src="https://github.com/mpalaourg/Thesis/blob/master/data/images/mongodb.jpg" alt="MongoDB" width="100" height="35">|
|-|-------------------------------------------------------------------------------------------------------------------------- |------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
|<p align=center> `__version__` </p>|<p align=center> `8` </p>|<p align=center> `3.7.7` </p>|<p align=center> `1.1.2` & `1.4.4` </p>|<p align=center> `4.4.0` </p>|

---

## Support 

Reach out to me:

- [mpalaourg's email](mailto:gbalaouras@gmail.com "gbalaouras@gmail.com")

---

## Licence 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/mpalaourg/Thesis/blob/master/LICENSE)
