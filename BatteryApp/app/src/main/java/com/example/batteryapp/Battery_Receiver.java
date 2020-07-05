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
    private String technology, date;

    /** Initialize the class variables from the (raw) values of the ACTION_BATTERY_CHANGED received intent.
     *
     * @param context -> The Context in which the receiver is running.
     * @param intent  -> The Intent being received.
     */
    @Override
    public void onReceive(Context context, Intent intent) {

        // boolean isPresent = intent.getBooleanExtra(BatteryManager.EXTRA_PRESENT, false);
        technology = intent.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY);
        int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1); // integer containing the maximum battery level.
        health = intent.getIntExtra(BatteryManager.EXTRA_HEALTH, 0);
        status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, 0);
        int rawLevel = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1); // integer field containing the current battery level, from 0 to scale
        int rawVolt = intent.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1);
        int rawTemp = intent.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1);

        DateFormat df = new SimpleDateFormat("EEE, d MMM yyyy, HH:mm:ss", Locale.getDefault());
        date = df.format(Calendar.getInstance().getTime());

        if (rawLevel >= 0 && scale > 0) { level = (rawLevel * 100) / scale; }

        if (rawTemp >=0){ temperature = (float) rawTemp / 10; }

        if (rawVolt >=0){ voltage = (float) rawVolt / 1000; }

    }

    /** Get the String representation of battery health.
     * @param health int value of the enum
     * @return String representation of battery health.
     */
    public String getHealthString(int health) {
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
    public String getStatusString(int status) {
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

    /** @return the Date of the latest battery intent (String representation) */
    public String getDate() { return date; }

}
