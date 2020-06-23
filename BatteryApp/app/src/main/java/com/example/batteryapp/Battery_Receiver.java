package com.example.batteryapp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.BatteryManager;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;

import android.os.Bundle;

public class Battery_Receiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        MainActivity currActivity = new MainActivity();
        String text = "";
        boolean isPresent = intent.getBooleanExtra(BatteryManager.EXTRA_PRESENT, false);
        String technology = intent.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY);
        int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1); // integer containing the maximum battery level.
        int health = intent.getIntExtra(BatteryManager.EXTRA_HEALTH, 0);
        int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, 0);
        int rawLevel = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1); // integer field containing the current battery level, from 0 to scale
        int level = 0;
        int rawVolt = intent.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1);
        int rawTemp = intent.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1);
        DateFormat df = new SimpleDateFormat("EEE, d MMM yyyy, HH:mm:ss");
        String date = df.format(Calendar.getInstance().getTime());
        // Unregister a previously registered BroadcastReceiver.  All filters that have been registered for this BroadcastReceiver will be removed.
        // context.unregisterReceiver(this);

        if (rawLevel >= 0 && scale > 0) {
            level = (rawLevel * 100) / scale;
            text = "Battery Level Remaining: " + level + "%";
            currActivity.setBatteryLevel(text);
        }

        if (rawTemp >=0){
            float temperature = (float) rawTemp / 10;
            text = "Battery Temperature: " + temperature+ " \u00B0" + "C";
            currActivity.setBatteryTemp(text);
        }

        if (rawVolt >=0){
            float voltage = (float) rawVolt / 1000;
            text = "Battery Voltage: " + voltage + " V";
            currActivity.setBatteryVolt(text);
        }

        currActivity.setBatteryTech("Battery Technology: " + technology);
        currActivity.setBatteryStatus("Battery Status: " + getStatusString(status));
        currActivity.setBatteryHealth("Battery Health: " + getHealthString(health));
        currActivity.setUpdateTime("Last Updated: " + date);
    }

    //Get Health of battery
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

    //Get Status of battery
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

}
