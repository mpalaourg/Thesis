# BatteryApp
![release](https://img.shields.io/github/v/release/mpalaourg/Thesis?color=orange&include_prereleases&style=flat-square) ![API](https://img.shields.io/badge/API-23-blue?style=flat-square) ![last commit](https://img.shields.io/github/last-commit/mpalaourg/Thesis/master?color=green&style=flat-square) <br><br>
<img src="https://github.com/mpalaourg/Thesis/blob/master/BatteryApp/app/src/main/ic_launcher-playstore.png" alt="app-icon" width="75" height="75">

A mobile app that collects data from the mobile phone’s usage and the battery status at regular intervals. 

---

## Requirements
BatteryApp can be installed on any smartphone with Android 6.0 Marshmallow or newer.

---

## Download 
The latest release version is available on Google Play: <br>
<a href='https://play.google.com/store/apps/details?id=gr.auth.ee.issel.batteryapp&pcampaignid=pcampaignidMKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'><img alt='Get it on Google Play' src='https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png' width="200"/></a>

---

## Architecture
<p align="center">
<img src="https://github.com/mpalaourg/Thesis/blob/master/data/images/app-communication.png" alt="app-communiation" width="600" height="450">
</p>

---

## Description
<p align=justify>
As part of my Thesis, I have developed the following Android application (BatteryApp), which during its operation collects data from the mobile phone’s usage and the battery status at regular intervals. The data collected is anonymous, as during the installation of the app you will be assigned a unique user code. The information collected is:
<ul>
<li> The unique ID that distinguishes you from other users. </li>
<li> The level, temperature, voltage, technology, status (charge/discharge), health (good/overheating) of the battery. </li>
<li> CPU usage. </li>
<li> If WiFi, Cellular Data, Bluetooth, Hotspot, GPS* of the mobile are activated. </li>
<li> The available RAM. </li>
<li> The screen brightness level. </li>
<li> If the phone is interactive (Screen is turned on or off). </li>
<li> Sampling frequency. </li>
<li> The model of the mobile and the android version. </li>
<li> The percentage remaining in the battery capacity. </li>
<li> The Timestamp of each sample. </li>
</ul>
<i> *Only if it is enabled, your location will NOT be logged. </i> <br>
<b>Thank you in advance for installing BatteryApp and for your contribution to my senior thesis. </b>
</p>

---

## App usage
<img src="https://github.com/mpalaourg/Thesis/blob/master/data/images/combined.gif" alt="app-usage" width="225" height="450" align="left" hspace="15">
<p align=justify>
BatteryApp <b>does not work</b> in the background, it collects data only when you activate it and there will be a notification in the Notification Shade the whole time you are using the app. To start a usage Session, open BatteryApp (e.g before you open YouTube or Instagram) and press the <ins>START SESSION</ins> button, with which BatteryApp will be minimized and data collection will begin. If you check your Notification Shade you should see a notification. To end the usage Session, return to BatteryApp and press the <ins>END SESSION</ins> button. The usage Sessions do not have to be long in duration, however, in the context of my Thesis, where the use of the battery is the main thing analyzed, the battery level must drop by at least 1% in each session in order to be of a greater value in the analysis. Finally, use the <ins>Upload Button</ins> to upload the files; uploading is not required after each use, as the Sessions are stored on the mobile and will be deleted after a successful upload.
<ul>
<li> You can change the sampling frequency (default is 1 sample every 10 seconds), at the number input box and via the <ins>SUBMIT</ins> button. </li>
<li> Files are uploaded by default only via WiFi. To upload while using Cellular data, you have to toggle the switch on the lower right corner. <i><ins>File size for a 30-minute usage Session is: ~228kB (sampling every 5 seconds), ~114kB (sampling every 10 seconds) </ins></i>. </li>
</ul>
</p>
<br clear="all">

---

## Contact
Do not hesitate to contact me for any matter, by sending an email to [batteryapp.help@gmail.com](mailto:batteryapp.help@gmail.com).
