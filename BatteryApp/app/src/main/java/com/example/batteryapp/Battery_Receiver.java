package com.example.batteryapp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.BatteryManager;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

public class Battery_Receiver extends BroadcastReceiver {

    private int level = 0, status, health;
    private float temperature = 0.0f, voltage = 0.0f;
    private String technology;
    //private LocalBroadcastManager broadcaster;

    /** First, initialize the class variables from the (raw) values of the ACTION_BATTERY_CHANGED
     * received intent. Then, update the battery related TextViews of the UI.
     *
     * @param context -> The Context in which the receiver is running.
     * @param intent  -> The Intent being received.
     */
    @Override
    public void onReceive(Context context, Intent intent) {
        MainActivity currActivity = new MainActivity();
        //broadcaster = LocalBroadcastManager.getInstance(this);
        String text;

        // boolean isPresent = intent.getBooleanExtra(BatteryManager.EXTRA_PRESENT, false);
        technology = intent.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY);
        int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1); // integer containing the maximum battery level.
        health = intent.getIntExtra(BatteryManager.EXTRA_HEALTH, 0);
        status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, 0);
        int rawLevel = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1); // integer field containing the current battery level, from 0 to scale
        int rawVolt = intent.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1);
        int rawTemp = intent.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1);

        DateFormat df = new SimpleDateFormat("EEE, d MMM yyyy, HH:mm:ss", Locale.getDefault());
        String date = df.format(Calendar.getInstance().getTime());

        if (rawLevel >= 0 && scale > 0) {
            level = (rawLevel * 100) / scale;
            text = "Battery Level Remaining: " + level + "%";
            currActivity.setBatteryLevel(text);
        }

        if (rawTemp >=0){
            temperature = (float) rawTemp / 10;
            text = "Battery Temperature: " + temperature+ " \u00B0" + "C";
            currActivity.setBatteryTemp(text);
        }

        if (rawVolt >=0){
            voltage = (float) rawVolt / 1000;
            text = "Battery Voltage: " + voltage + " V";
            currActivity.setBatteryVolt(text);
        }

        /* Set the class variables */
        this.setStatus(status);
        this.setHealth(health);
        this.setTechnology(technology);
        this.setVoltage(voltage);
        this.setTemperature(temperature);
        this.setLevel(level);

        /* Update battery related TextViews in the UI */
        currActivity.setBatteryTech("Battery Technology: " + technology);
        currActivity.setBatteryStatus("Battery Status: " + getStatusString(status));
        currActivity.setBatteryHealth("Battery Health: " + getHealthString(health));
        currActivity.setUpdateTime("Last Updated: " + date);

        /* Send the intent to update the UI */
        /* Intent updateIntent = new Intent("UpdateBatteryIntent");
        updateIntent.putExtra("level", level);
        updateIntent.putExtra("temperature", temperature);
        updateIntent.putExtra("voltage", voltage);
        updateIntent.putExtra("technology", technology);
        updateIntent.putExtra("status", getStatusString(status));
        updateIntent.putExtra("health", getHealthString(health));
        updateIntent.putExtra("updateTime", date);

        broadcaster.sendBroadcast(updateIntent); */
    }

    /** Get the String representation of battery health.
     * @param health int value of the enum
     * @return String representation of battery health.
     */
    private String getHealthString(int health) {
        String healthString = "Unknown";

        switch (health) {
            case BatteryManager.BATTERY_HEALTH_DEAD:
                healthString = "Dead";
                break;
            case BatteryManager.BATTERY_HEALTH_GOOD:
                healthString = "Good";
                break;
            case BatteryManager.BATTERY_HEALTH_OVER_VOLTAGE:
                healthString = "Over Voltage";
                break;
            case BatteryManager.BATTERY_HEALTH_OVERHEAT:
                healthString = "Over Heat";
                break;
            case BatteryManager.BATTERY_HEALTH_UNSPECIFIED_FAILURE:
                healthString = "Failure";
                break;
        }
        return healthString;
    }

    /** Get the String representation of battery status.
     * @param status int value of the enum
     * @return String representation of battery status.
     */
    private String getStatusString(int status) {
        String statusString = "Unknown";

        switch (status) {
            case BatteryManager.BATTERY_STATUS_CHARGING:
                statusString = "Charging";
                break;
            case BatteryManager.BATTERY_STATUS_DISCHARGING:
                statusString = "Discharging";
                break;
            case BatteryManager.BATTERY_STATUS_FULL:
                statusString = "Full";
                break;
            case BatteryManager.BATTERY_STATUS_NOT_CHARGING:
                statusString = "Not Charging";
                break;
        }
        return statusString;
    }

    /** @param level -> Battery level to set (int values indicating percentage) */
    public void setLevel(int level) { this.level = level;}

    /** @param status -> Battery status to set (int values check for the mapping) */
    public void setStatus(int status) { this.status = status; }

    /** @param health -> Battery health to set (int values check for the mapping) */
    public void setHealth(int health) { this.health = health;}

    /** @param temperature -> Battery temperature to set (float values in Celsius) */
    public void setTemperature(float temperature) { this.temperature = temperature; }

    /** @param voltage -> Battery voltage to set (float values in Volt) */
    public void setVoltage(float voltage) { this.voltage = voltage; }

    /** @param technology -> Battery technology to set (String descriptions) */
    public void setTechnology(String technology) { this.technology = technology; }

    /** @return the current level of the battery (int values indicating percentage) */
    public int getLevel() { return level; }

    /** @return the current status of the battery (int values check for the mapping) */
    public int getStatus() { return status; }

    /** @return the current health of the battery (int values check for the mapping) */
    public int getHealth() { return health; }

    /** @return the current temperature of the battery (float values in Celsius) */
    public float getTemperature() { return temperature; }

    /** @return the current voltage of the battery (float values in Volt) */
    public float getVoltage() { return voltage; }

    /** @return the technology of the battery (String descriptions) */
    public String getTechnology() { return technology; }
}
