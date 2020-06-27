package com.example.batteryapp;

import android.app.ActivityManager;

import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.provider.Settings;

import java.text.DecimalFormat;

public class Other_Stats {
    private Context mContext;
    private final  int MB_CONVERSION = 1000 * 1000;
    private static boolean wifiConnected = false;   // Whether there is a Wi-Fi connection.
    private static boolean mobileConnected = false; // Whether there is a mobile connection.

    private static DecimalFormat df = new DecimalFormat("0.00");

    /**
     * Constructor for the Other_Stats class. Context must be initialized so getSystemService can run
     * outside the Main Activity.
     * @param mContext
     */
    public Other_Stats(Context mContext){
        this.mContext = mContext;
    }

    /* Check if the WiFi is enable OR the Cellular Data */
    public void getNetworkConnectivity() {
        MainActivity currActivity = new MainActivity();
        ConnectivityManager connMgr = (ConnectivityManager) mContext.getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeInfo = connMgr.getActiveNetworkInfo();

        if (activeInfo != null && activeInfo.isConnected()) {
            wifiConnected = activeInfo.getType() == ConnectivityManager.TYPE_WIFI;
            mobileConnected = activeInfo.getType() == ConnectivityManager.TYPE_MOBILE;
        } else {
            wifiConnected = false;
            mobileConnected = false;
        }
        if (wifiConnected) {
            currActivity.setWiFiConnectivity("WiFI Enable", Color.GREEN);
        }
        if (mobileConnected) {
            currActivity.setCellularConnectivity("Data Enable", Color.GREEN);
        }
    }

    /* See if a bluetooth adapter is present and then check if is enable. */
    /*public void getBluetoothConnectivity() {
        MainActivity currActivity = new MainActivity();
        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (mBluetoothAdapter == null) {
            currActivity.setBluetoothConnectivity("No Bluetooth Support", Color.RED);
        } else if (mBluetoothAdapter.isEnabled()){
            currActivity.setBluetoothConnectivity("Bluetooth Enable", Color.GREEN);
        }
    } */

    /* Read the available RAM for the system. */
    public void getAvailableRAM() {
        // RAM reading
        /* refer to: https://developer.android.com/reference/android/app/ActivityManager.MemoryInfo */
        /* The total memory accessible by the kernel. This is basically the RAM size of the device,
            not including below-kernel fixed allocations like DMA buffers, RAM for the baseband CPU, etc.
            The available memory on the system. This number should not be considered absolute: due to the nature of the kernel,
            a significant portion of this memory is actually in use and needed for the overall system to run well. */
        MainActivity currActivity = new MainActivity();

        ActivityManager.MemoryInfo myMemoryInfo = new ActivityManager.MemoryInfo();
        ActivityManager activityManager = (ActivityManager) mContext.getSystemService(Context.ACTIVITY_SERVICE);
        activityManager.getMemoryInfo(myMemoryInfo);
        double availMemMB = (double) myMemoryInfo.availMem / MB_CONVERSION;
        //Percentage can be calculated for API 16+ ~ TotalMem return bytes, convert to MBytes.
        double totalMemMB = (double) myMemoryInfo.totalMem / MB_CONVERSION;
        double percentAvail = availMemMB / totalMemMB  * 100.0;
        currActivity.setAvailableRam("Available RAM: " + df.format(availMemMB) + " MB (" + df.format(percentAvail) + "%)");
    }

    /* Get the screen current brightness */
    public void getBrightness() {
        MainActivity currActivity = new MainActivity();
        int brightness = Settings.System.getInt(
                mContext.getContentResolver(),
                Settings.System.SCREEN_BRIGHTNESS,
                0
        );
        currActivity.setBrightness("Current Brightness: " + brightness);
    }

}
